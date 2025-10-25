import subprocess
import webbrowser
import time
import os

# Paths to each app
LOGIN_APP = os.path.join("webapp", "login_page.py")
LOG_READER = os.path.join("src", "log_reader.py")
DASHBOARD = os.path.join("src", "threat_dashboard.py")

# Launch Flask login app
print("Starting Login Page...")
subprocess.Popen(["python", LOGIN_APP], creationflags=subprocess.CREATE_NEW_CONSOLE)

time.sleep(2)

# Launch log reader
print("Starting Log Reader...")
subprocess.Popen(["python", LOG_READER], creationflags=subprocess.CREATE_NEW_CONSOLE)

time.sleep(2)

# Launch Streamlit dashboard
print("Starting Streamlit Dashboard...")
subprocess.Popen(["streamlit", "run", DASHBOARD], creationflags=subprocess.CREATE_NEW_CONSOLE)

# Open only the login page (Streamlit opens itself)
time.sleep(3)
print("Opening browser tabs...")
webbrowser.open("http://localhost:5000")

print("✅ SecureBox Testing Center launched.")
