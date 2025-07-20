from flask import Flask, request, send_from_directory, redirect, url_for
from kiteconnect import KiteConnect
from dotenv import load_dotenv
import os


app = Flask(__name__)

load_dotenv('.env')

# Replace with your API Key and Secret
API_KEY = os.getenv("KITE_API_KEY")
API_SECRET = os.getenv("KITE_API_SECRET")

kite = KiteConnect(api_key=API_KEY)


def remove_last_line_from_env(filepath=".env"):
    with open(filepath, "r") as file:
        lines = file.readlines()

    if not lines:
        return  # file is empty

    # Remove the last line
    lines = lines[:-1]

    lines = [line for line in lines if line.strip()]

    with open(filepath, "w") as file:
        file.writelines(lines)


@app.route("/")
def home():
    return redirect(url_for('login'))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/login")
def login():
    login_url = kite.login_url()
    return f"<a href='{login_url}'>Login to Zerodha</a>"


@app.route("/redirect")
def redirect_handler():
    request_token = request.args.get("request_token")
    if not request_token:
        return "Error: request_token not found", 400

    try:
        # Exchange request_token for access_token
        data = kite.generate_session(request_token, api_secret=API_SECRET)
        access_token = data["access_token"]

        remove_last_line_from_env()

        with open(".env", 'a') as f:
            f.write(f"\nKITE_ACCESS_TOKEN={access_token}")
        load_dotenv(override=True)

        return f"Access Token: {access_token}"
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    app.run(port=3000)
