🧠 SecureBox — A Lightweight Threat Detection \& Response System

Author: Gerges Shehata



GitHub: https://github.com/G3rges2025/SecureBox-SOC



Type: Real-Time SOC Simulation for Small Networks







🎯 Overview



SecureBox is a self-contained Security Operations Center (SOC) dashboard designed for small networks and academic environments.

It simulates real-world threat detection, alert classification, and firewall response in real-time using Python and Streamlit.



This project demonstrates how you can:



Detect suspicious log activity (like brute-force or repeated login failures)



Automatically classify and block high-risk IPs



Visualize live threats using an interactive dashboard



Export all alert data for analysis



Built completely from scratch, SecureBox bridges defensive SOC operations with hands-on cybersecurity analytics.







⚙️ Features



✅ Real-Time Log Monitoring



Watches active log files (sample.log)



Detects multiple failed logins per IP in under 60 seconds



✅ Threat Classification



Low (1–2 attempts) – harmless



Medium (3–4 attempts) – watch closely



High (5+) – triggers brute-force detection and IP blocking



✅ Automatic Blocking



Writes to blocked\_ips.json once 5+ failures are seen



Stores reason, timestamp, and “blocked” status



✅ GeoIP Tracking



Uses IP geolocation to map each alert on a live world map



Country, city, latitude, and longitude displayed in the dashboard



✅ Streamlit Dashboard



Displays alerts, severity charts, and live refresh



Horizontal scroll removed (auto-expanding graph layout)



Exports CSVs for alerts, brute-force, and all logs



✅ Simulation Suite



simulate\_single\_fail.py → creates a normal failed attempt



simulate\_bruteforce.py → triggers high-severity blocking



simulate\_attack.py → spawns multiple global IPs for demo



✅ Auto-Refresh Engine



Refreshes every few seconds with toggle control



Full UTF-8 encoding compatibility for all JSON/CSV



✅ Firewall Simulation



Fake IP blocks logged for demonstration



Easily adaptable to real firewall commands (e.g. iptables or Windows Defender rules)







🧱 Technology Stack



Component	Tool



Log Reader	Python (watchdog, JSON)



Dashboard	Streamlit + Plotly



Backend	Flask (login simulation)



Visualization	GeoIP + Plotly Scatter Maps



Exporting	Pandas CSV/JSON



Automation	Simulated firewall block system



Version Control	Git + GitHub





🚀 How to Run SecureBox



1️⃣ Launch the SOC Environment

cd C:\\Projects\\SecureBox

python src\\log\_reader.py



2️⃣ Open the Dashboard

cd C:\\Projects\\SecureBox\\src

streamlit run threat\_dashboard.py





Keep both windows running side-by-side.

You’ll now see:



Alerts populate in real-time



New IPs appear on the map



Brute-force attempts trigger automatic blocking



🧪 Simulated Attacks

➤ Run Single Failure

python src\\simulate\_single\_fail.py



➤ Run Brute Force

python src\\simulate\_bruteforce.py



➤ Run Global Attack Simulation

python src\\simulate\_attack.py





This script generates 4 fake attackers across the U.S., two of which become blocked IPs.



📊 Dashboard Sections

Section	Description

All Alerts	Full alert log feed

Top Offending IPs	Scrollable list of most active attackers

GeoIP Map	World map with dots showing live origin

Brute Force Detections	Table of IPs hitting 5+ failures

Blocked IPs	Auto-blocked sources

Export Logs	Download CSVs instantly

📁 File Outputs

File	Description

alerts.json	General alerts

brute\_force.json	High-severity brute-force alerts

blocked\_ips.json	Auto-blocked IPs

all\_logs.csv	Combined dataset

sample.log	Primary log monitored

🧩 Real Server Integration (for future)



To integrate SecureBox into a real SOC or server:



Redirect SSH or Apache logs to the logs/ folder:



tail -f /var/log/auth.log >> logs/sample.log





Schedule SecureBox scripts as background services.



Add real firewall rules in log\_reader.py (replace fake block line with system call):



os.system(f"netsh advfirewall firewall add rule name='Block {ip}' dir=in action=block remoteip={ip}")





Enable email/SIEM forwarding to alert security admins.



🧠 CherryTree Integration (Local Reference Folder)



A second folder named /cherry\_tree/ contains your complete manual command library for:



setup



troubleshooting



Git pushes



Streamlit, Flask, and simulation commands



Backup/restore instructions

Each node has labeled “topics” like:



📁 Installation Process

&nbsp; ├── Flask Setup

&nbsp; ├── Streamlit Setup

&nbsp; ├── UTF-8 Fix Commands

📁 Backup \& Restore

&nbsp; ├── PowerShell Restore Command

&nbsp; ├── Creating Restore Points

📁 Testing Panel

&nbsp; ├── simulate\_bruteforce.py

&nbsp; ├── simulate\_single\_fail.py

&nbsp; ├── simulate\_attack.py

📁 GitHub Commands

&nbsp; ├── git add .

&nbsp; ├── git commit -m “update”

&nbsp; ├── git push origin main





At the end of the project, the CherryTree file (SecureBox.cherry) becomes your personal offline command reference, so you never need to recall commands again.



🏁 Summary



SecureBox proves your ability to:



Architect and deploy an end-to-end SOC system



Handle both red and blue team concepts



Automate cybersecurity monitoring with professional-grade visualization



Work like a real analyst using open-source tools



This project is portfolio-ready — for GitHub, LinkedIn, and interviews.

It shows that you don’t just understand cybersecurity; you build it. 🧠💻

