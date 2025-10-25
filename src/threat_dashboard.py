import streamlit as st
import pandas as pd
import json
import plotly.express as px
import os
from pathlib import Path
from datetime import datetime, timezone
from streamlit_autorefresh import st_autorefresh

# ---------------------------------------------------------------------
# 🔒 Helper functions for blocked IP management
# ---------------------------------------------------------------------
BLOCKED_FILE = os.path.join(os.path.dirname(__file__), 'blocked_ips.json')

def load_blocked_for_ui():
    """Safely load blocked IP list."""
    if not os.path.exists(BLOCKED_FILE):
        return []
    try:
        with open(BLOCKED_FILE, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
            if isinstance(data, dict) and "blocked" in data:
                return data["blocked"]
            elif isinstance(data, list):
                return data
    except Exception:
        pass
    return []

def save_blocked_from_ui(blocked_list):
    """Safely save blocked IP list."""
    payload = {"blocked": blocked_list}
    with open(BLOCKED_FILE, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

# ---------------------------------------------------------------------
# ⚙️ File paths
# ---------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
alerts_path = Path(os.path.join(BASE_DIR, "alerts", "alerts.json"))
brute_path = Path(os.path.join(BASE_DIR, "alerts", "brute_force.json"))

# ---------------------------------------------------------------------
# 🔁 Auto Refresh
# ---------------------------------------------------------------------
st.sidebar.header("🔁 Refresh Controls")

enable_auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=True)
refresh_interval = st.sidebar.slider("Auto Refresh Interval (seconds):", 2, 30, 5)

if enable_auto_refresh:
    st_autorefresh(interval=refresh_interval * 1000, key="auto_refresh")

# ---------------------------------------------------------------------
# 🧱 Title and Filters
# ---------------------------------------------------------------------
st.title("🛡️ SecureBox Threat Dashboard")

ip_filter = st.text_input("🔍 Filter by IP Address (optional):", "")
severity_filter = st.selectbox(
    "⚠️ Filter by Severity (optional):",
    ["", "Low", "Medium", "High", "Critical", "Unknown"]
)

# ---------------------------------------------------------------------
# 📈 Dashboard Stats
# ---------------------------------------------------------------------
now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
alert_count = sum(1 for _ in open(alerts_path, "r", encoding="utf-8")) if alerts_path.exists() else 0
brute_count = sum(1 for _ in open(brute_path, "r", encoding="utf-8")) if brute_path.exists() else 0

st.markdown(f"""
### 📊 Dashboard Stats:
- **Total Alerts:** `{alert_count}`
- **Brute Force Detections:** `{brute_count}`
- **Last Updated:** `{now}`
""")

# ---------------------------------------------------------------------
# 🚨 Load Alerts (Flexible JSON Loader)
# ---------------------------------------------------------------------
def load_json_flex(file_path):
    """Load JSON (handles list or newline-delimited formats)."""
    if not file_path.exists():
        return []
    raw = Path(file_path).read_text(encoding="utf-8").strip()
    if not raw:
        return []

    # try list first
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
    except Exception:
        pass

    # fallback to newline-delimited JSON
    records = []
    for line in raw.splitlines():
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                records.append(obj)
        except Exception:
            continue
    return records

# ---------------------------------------------------------------------
# 🚨 ALERTS
# ---------------------------------------------------------------------
df_alerts = pd.DataFrame()
if alerts_path.exists():
    alert_data = load_json_flex(alerts_path)
    clean = []
    for e in alert_data:
        if not isinstance(e, dict):
            continue
        e.setdefault("severity", "Unknown")
        e.setdefault("ip_address", e.get("source_ip") or e.get("ip") or "Unknown")
        e.setdefault("log_entry", e.get("log_entry") or e.get("description") or "No message")
        e.setdefault("timestamp", e.get("timestamp", ""))
        geo = e.get("geo") if isinstance(e.get("geo"), dict) else {}
        e["country"] = geo.get("country")
        e["city"] = geo.get("city")
        e["lat"] = geo.get("lat")
        e["lon"] = geo.get("lon")
        clean.append(e)
    df_alerts = pd.DataFrame(clean)

    if not df_alerts.empty:
        df_alerts['ip_address'] = df_alerts['ip_address'].fillna("Unknown")
        if ip_filter:
            df_alerts = df_alerts[df_alerts["ip_address"].str.contains(ip_filter, na=False)]
        if severity_filter:
            df_alerts = df_alerts[df_alerts["severity"] == severity_filter]

if not df_alerts.empty:
    st.subheader("🚨 All Alerts")
    st.dataframe(df_alerts[['timestamp', 'ip_address', 'log_entry', 'severity']], use_container_width=True)

    # -----------------------------------------------------------------
    # 🌍 Geo Map Visualization
    # -----------------------------------------------------------------
    geo_points = df_alerts.dropna(subset=["lat", "lon"])
    if not geo_points.empty:
        st.subheader("🌍 GeoIP Map (Alert Origins)")
        fig_geo = px.scatter_geo(
            geo_points,
            lat="lat", lon="lon",
            hover_name="ip_address",
            hover_data=["country", "city", "severity"],
            color="severity",
            color_discrete_sequence=px.colors.qualitative.Safe,
            title="Global Threat Locations"
        )
        fig_geo.update_layout(height=500, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_geo, use_container_width=True)
    else:
        st.info("🌍 No GeoIP data available yet. It will appear once log_reader writes geo info.")

    # -----------------------------------------------------------------
    # 💥 Top Offending IPs (slider, no zoom)
    # -----------------------------------------------------------------
    st.subheader("💥 Top Offending IPs")
    top_n = st.slider("Show top N IPs", min_value=3, max_value=30, value=8, step=1)
    ip_counts = df_alerts['ip_address'].value_counts().reset_index()
    ip_counts.columns = ['IP Address', 'Alert Count']
    ip_counts = ip_counts.head(top_n)

    if not ip_counts.empty:
        fig_bar = px.bar(
            ip_counts,
            x='Alert Count',
            y='IP Address',
            orientation='h',
            text='Alert Count',
            color='Alert Count',
            height=60 + 40 * len(ip_counts)
        )
        fig_bar.update_traces(textposition='outside', marker_line_width=0)
        fig_bar.update_xaxes(fixedrange=True)
        fig_bar.update_yaxes(fixedrange=True)
        fig_bar.update_layout(showlegend=False, margin=dict(l=80, r=40, t=20, b=40))
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No IPs found for chart.")

    # -----------------------------------------------------------------
    # ⏱️ Timeline
    # -----------------------------------------------------------------
    df_alerts['timestamp'] = pd.to_datetime(df_alerts['timestamp'], errors='coerce')
    timeline = df_alerts.groupby(pd.Grouper(key='timestamp', freq='1Min')).size().reset_index(name='Alerts')
    st.subheader("⏱️ Alert Timeline")
    fig2 = px.line(timeline, x='timestamp', y='Alerts', title='Alert Activity Over Time')
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

    # -----------------------------------------------------------------
    # 🧩 Severity Breakdown
    # -----------------------------------------------------------------
    severity_counts = df_alerts['severity'].value_counts().reset_index()
    severity_counts.columns = ['Severity', 'Count']
    st.subheader("🧩 Severity Breakdown")
    fig3 = px.pie(severity_counts, names='Severity', values='Count', title='Alert Severity Distribution')
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No alerts found. The dashboard will update when new data arrives.")

# ---------------------------------------------------------------------
# 💥 BRUTE FORCE SECTION
# ---------------------------------------------------------------------
df_brute = pd.DataFrame()
if brute_path.exists():
    brute_data = load_json_flex(brute_path)
    if brute_data:
        df_brute = pd.DataFrame(brute_data)
        if ip_filter and 'ip_address' in df_brute.columns:
            df_brute = df_brute[df_brute['ip_address'].astype(str).str.contains(ip_filter, na=False)]
        if not df_brute.empty:
            st.subheader("💥 Brute Force Detections")
            st.dataframe(df_brute, use_container_width=True)
        else:
            st.info("No brute-force alerts match the filter.")
    else:
        st.info("No brute-force alerts yet.")
else:
    st.info("Brute-force alert file not found.")

# ---------------------------------------------------------------------
# 🧱 BLOCKED IPs
# ---------------------------------------------------------------------
st.header("🧱 Blocked IPs")

blocked_list = load_blocked_for_ui()

if not blocked_list:
    st.info("No blocked IPs detected.")
else:
    rows = []
    for e in blocked_list:
        rows.append({
            "IP": e.get("ip") if isinstance(e, dict) else e,
            "Blocked At": e.get("blocked_at", "-") if isinstance(e, dict) else "-",
            "Reason": e.get("reason", "-") if isinstance(e, dict) else "-",
            "Last Seen": e.get("last_seen", "-") if isinstance(e, dict) else "-",
            "Expires": e.get("expires_at", "-") if isinstance(e, dict) else "-",
        })

    df_blocked = pd.DataFrame(rows)
    st.dataframe(df_blocked, use_container_width=True, height=220)

    for e in blocked_list:
        ip = e.get("ip") if isinstance(e, dict) else e
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{ip}** — {e.get('reason', '') if isinstance(e, dict) else ''}")
        with col2:
            if st.button(f"Unblock {ip}"):
                new_list = [x for x in blocked_list if (x.get("ip") if isinstance(x, dict) else x) != ip]
                save_blocked_from_ui(new_list)
                st.success(f"✅ Unblocked {ip}")
                st.rerun()

# ---------------------------------------------------------------------
# 📦 EXPORT
# ---------------------------------------------------------------------
st.markdown("---")
st.subheader("📦 Export Logs")

col1, col2 = st.columns(2)

with col1:
    if not df_alerts.empty:
        df_alerts.to_csv("alerts.csv", index=False)
        with open("alerts.csv", "rb") as f:
            st.download_button("Download Alerts CSV", f, "alerts.csv", "text/csv")

with col2:
    if not df_brute.empty:
        df_brute.to_csv("brute_force.csv", index=False)
        with open("brute_force.csv", "rb") as f:
            st.download_button("Download Brute Force CSV", f, "brute_force.csv", "text/csv")

if not df_alerts.empty or not df_brute.empty:
    df_alerts['Type'] = 'General Alert'
    df_brute['Type'] = 'Brute Force'
    combined = pd.concat([df_alerts, df_brute], ignore_index=True)
    combined = combined[['timestamp', 'ip_address', 'log_entry', 'Type']]
    combined.columns = ['Timestamp', 'IP Address', 'Log Entry', 'Type']
    combined['Timestamp'] = pd.to_datetime(combined['Timestamp'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M')
    combined.to_csv("all_logs.csv", index=False)
    with open("all_logs.csv", "rb") as f:
        st.download_button("Download All Logs", f, "all_logs.csv", "text/csv")
