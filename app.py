import json
import os
import urllib.parse
from pathlib import Path

from flask import Flask, redirect, request, render_template_string
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

PINTEREST_APP_ID = os.getenv("PINTEREST_APP_ID", "YOUR_APP_ID")
PINTEREST_REDIRECT_URI = os.getenv(
    "PINTEREST_REDIRECT_URI",
    "http://localhost:8080/callback"
)

SCOPES = "boards:read,pins:read,pins:write"


def load_pin():
    pins_path = Path("pins.json")
    if not pins_path.exists():
        raise FileNotFoundError("pins.json not found")

    pins = json.loads(pins_path.read_text(encoding="utf-8"))
    if not pins:
        raise ValueError("pins.json is empty")

    return pins[0]


HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>SnoozeSavvy Pin Scheduler Demo</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {
      margin: 0;
      font-family: Arial, sans-serif;
      background: #f5f7fc;
      color: #101c36;
    }
    .wrap {
      max-width: 1100px;
      margin: 0 auto;
      padding: 36px 20px 70px;
    }
    .hero {
      background: linear-gradient(135deg, #101c36, #263d77);
      color: white;
      padding: 36px;
      border-radius: 28px;
      box-shadow: 0 24px 60px rgba(16,28,54,.18);
      margin-bottom: 28px;
    }
    .hero p {
      color: rgba(255,255,255,.86);
      line-height: 1.7;
      max-width: 820px;
    }
    .badge {
      display: inline-block;
      background: #d9b56f;
      color: #101c36;
      padding: 8px 12px;
      border-radius: 999px;
      font-weight: 800;
      font-size: 13px;
      margin-bottom: 12px;
    }
    .grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 22px;
    }
    .card {
      background: #fff;
      border: 1px solid #e6eaf3;
      border-radius: 24px;
      padding: 24px;
      box-shadow: 0 12px 34px rgba(16,28,54,.06);
    }
    .pin-image {
      width: 100%;
      border-radius: 18px;
      border: 1px solid #e6eaf3;
      display: block;
      background: #eef3ff;
    }
    .label {
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .12em;
      color: #667085;
      font-weight: 800;
      margin-top: 18px;
      margin-bottom: 6px;
    }
    .value {
      background: #f5f7fc;
      border: 1px solid #e6eaf3;
      padding: 12px 14px;
      border-radius: 14px;
      line-height: 1.55;
      word-break: break-word;
    }
    .btn {
      display: inline-block;
      border: none;
      background: #bd081c;
      color: white;
      padding: 13px 18px;
      border-radius: 999px;
      text-decoration: none;
      font-weight: 900;
      cursor: pointer;
      margin-right: 10px;
      margin-top: 12px;
    }
    .btn.secondary {
      background: #101c36;
    }
    .status {
      background: #ecfdf3;
      border: 1px solid #abefc6;
      color: #067647;
      padding: 12px 14px;
      border-radius: 14px;
      line-height: 1.6;
      margin-top: 14px;
      font-weight: 700;
    }
    .console {
      background: #101c36;
      color: #d7e3ff;
      padding: 18px;
      border-radius: 18px;
      font-family: Consolas, monospace;
      font-size: 14px;
      line-height: 1.65;
      white-space: pre-wrap;
      margin-top: 18px;
    }
    @media (max-width: 850px) {
      .grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <main class="wrap">
    <section class="hero">
      <div class="badge">Internal Publishing Workflow Demo</div>
      <h1>SnoozeSavvy Pin Scheduler</h1>
      <p>
        This demo shows how SnoozeSavvy prepares approved organic Pins for its own sleep-related articles and tools.
        The workflow uses Pinterest OAuth, approved Pin metadata, board selection, and a publish step designed to call
        the official Pinterest Create Pin API once write access is approved.
      </p>
    </section>

    <section class="grid">
      <div class="card">
        <h2>Approved Pin Preview</h2>
        <img class="pin-image" src="/{{ pin.image }}" alt="{{ pin.alt_text }}">

        <div class="label">Status</div>
        <div class="status">Approved by SnoozeSavvy team</div>

        <div class="label">Title</div>
        <div class="value">{{ pin.title }}</div>

        <div class="label">Description</div>
        <div class="value">{{ pin.description }}</div>

        <div class="label">Destination Link</div>
        <div class="value">{{ pin.link }}</div>

        <div class="label">Alt Text</div>
        <div class="value">{{ pin.alt_text }}</div>
      </div>

      <div class="card">
        <h2>Pinterest Publishing Controls</h2>

        <div class="label">Board</div>
        <div class="value">{{ pin.board_name }}</div>

        <div class="label">OAuth Scopes Requested</div>
        <div class="value">boards:read, pins:read, pins:write</div>

        <a class="btn" href="/connect">Connect Pinterest with OAuth</a>
        <a class="btn secondary" href="/publish-demo">Publish Approved Pin Demo</a>

        {% if message %}
          <div class="status">{{ message }}</div>
        {% endif %}

        <div class="console">{{ console }}</div>
      </div>
    </section>
  </main>
</body>
</html>
"""


@app.route("/")
def index():
    pin = load_pin()
    return render_template_string(
        HTML,
        pin=pin,
        message=None,
        console=(
            "Ready.\\n"
            "1. Connect Pinterest using OAuth.\\n"
            "2. Confirm board and approved Pin content.\\n"
            "3. Publish approved Pin using the official Create Pin API once pins:write is approved."
        )
    )


@app.route("/connect")
def connect():
    params = {
        "client_id": PINTEREST_APP_ID,
        "redirect_uri": PINTEREST_REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "state": "snoozesavvy-demo"
    }

    url = "https://www.pinterest.com/oauth/?" + urllib.parse.urlencode(params)
    return redirect(url)


@app.route("/callback")
def callback():
    code = request.args.get("code")
    error = request.args.get("error")
    pin = load_pin()

    if error:
      message = f"OAuth returned an error: {error}"
      console = "Pinterest OAuth did not complete. This may happen if pins:write is not yet approved."
    elif code:
      message = "OAuth callback received successfully."
      console = (
          "Authorization code received.\\n"
          "In production, the app exchanges this code for an access token.\\n"
          "The token will then be used to create approved Pins on SnoozeSavvy boards."
      )
    else:
      message = "OAuth callback reached without a code."
      console = "No code was returned."

    return render_template_string(HTML, pin=pin, message=message, console=console)


@app.route("/publish-demo")
def publish_demo():
    pin = load_pin()

    payload = {
        "board_id": "selected_snoozesavvy_board_id",
        "title": pin["title"],
        "description": pin["description"],
        "link": pin["link"],
        "alt_text": pin["alt_text"],
        "media_source": {
            "source_type": "image_url",
            "url": "https://snoozesavvy.com/path-to-approved-pin-image.png"
        }
    }

    console = (
        "Demo publish action prepared.\\n\\n"
        "This is the approved Create Pin API payload that will be sent after pins:write is approved:\\n\\n"
        + json.dumps(payload, indent=2)
    )

    return render_template_string(
        HTML,
        pin=pin,
        message="Approved Pin is ready for Pinterest API publishing.",
        console=console
    )


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)