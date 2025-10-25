from flask import Flask, request, render_template_string
from datetime import datetime
import os

app = Flask(__name__)

# Absolute path to sample.log
LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "sample.log"))

# Styled login form
login_html = """
<!doctype html>
<html>
<head>
  <title>Secure Login</title>
  <style>
    body {
      background-color: #f5f5f5;
      font-family: Arial, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    }
    .login-box {
      background-color: white;
      padding: 40px;
      border-radius: 10px;
      box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
      width: 400px;
    }
    h2 {
      text-align: center;
      font-size: 28px;
      margin-bottom: 30px;
    }
    input[type="text"],
    input[type="password"] {
      width: 100%;
      padding: 12px;
      margin-bottom: 20px;
      font-size: 16px;
      border: 1px solid #ccc;
      border-radius: 5px;
    }
    input[type="submit"] {
      width: 100%;
      padding: 12px;
      background-color: #007bff;
      color: white;
      font-size: 16px;
      border: none;
      border-radius: 5px;
      cursor: pointer;
    }
    p {
      margin-top: 20px;
      text-align: center;
      color: red;
      font-weight: bold;
    }
  </style>
</head>
<body>
  <div class="login-box">
    <h2>Secure Login</h2>
    <form method="POST">
      <input type="text" name="username" placeholder="Username" required><br>
      <input type="password" name="password" placeholder="Password" required><br>
      <input type="submit" value="Login">
    </form>
    {% if result %}<p>{{ result }}</p>{% endif %}
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def login():
    result = ""
    if request.method == "POST":
        username = request.form.get("username")
        now = datetime.now().strftime("%b %d %H:%M:%S")
        ip = request.remote_addr or "127.0.0.1"
        port = 5000

        # Log format compatible with log_reader.py
        log_line = f"{now} login-system[1234]: Failed password for user {username} from {ip} port {port}\n"

        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

        with open(LOG_PATH, "a") as f:
            f.write(log_line)

        result = f"Login failed for user '{username}' — attempt logged."

    return render_template_string(login_html, result=result)

if __name__ == "__main__":
    app.run(port=5000)
