import os
from flask import Flask, redirect, request, jsonify
import requests
from dotenv import load_dotenv
from agent.standup_agent import run_standup_agent  # Import your function

app = Flask(__name__)
load_dotenv()

SLACK_CLIENT_ID = os.environ.get("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = os.environ.get("SLACK_CLIENT_SECRET")
SLACK_REDIRECT_URI = os.environ.get("SLACK_REDIRECT_URI")

@app.route("/slack/install")
def install():
    slack_auth_url = (
        f"https://slack.com/oauth/v2/authorize?client_id={SLACK_CLIENT_ID}"
        f"&scope=commands,chat:write,users:read,channels:read,channels:join,chat:write.public"
        f"&redirect_uri={SLACK_REDIRECT_URI}"
    )
    return redirect(slack_auth_url)

@app.route("/slack/oauth_redirect")
from flask import redirect
def oauth_redirect():
    code = request.args.get("code")
    if not code:
        return "Missing code parameter", 400
    data = {
        "client_id": SLACK_CLIENT_ID,
        "client_secret": SLACK_CLIENT_SECRET,
        "code": code,
        "redirect_uri": SLACK_REDIRECT_URI,
    }
    response = requests.post("https://slack.com/api/oauth.v2.access", data=data)
    resp_json = response.json()

    access_token = resp_json.get("access_token")
    if access_token:
        with open("slack_access_token.txt", "w") as f:
            f.write(access_token)
        # Redirect to Slack success URL
        return redirect("https://slack.com/app_redirect")  # or any Slack confirmation URL

    # If error, redirect to Slack error page or show a message
    return "OAuth failed, please try again.", 400


@app.route("/run-standup", methods=["GET"])
def run_standup():
    try:
        result = run_standup_agent()  # This should execute your Slack posting logic
        return jsonify({"status": "success", "result": result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port)
