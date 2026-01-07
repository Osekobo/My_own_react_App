from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import africastalking

# ----------------- CONFIG -----------------
MODE = "live"  # Must be "live" to send real SMS

# Africa's Talking credentials
username = "sandbox"  # e.g., "myapp"
# e.g., "xxxxxxxxxxxxxxxxxxxx"
api_key = "atsk_114f01019c73104d92c15cf0ea2fd7109ba6b55432943312f4ed9501d735620aa7a51e11"
africastalking.initialize(username, api_key)
sms = africastalking.SMS

# ----------------- APP SETUP -----------------
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# ----------------- OTP Storage -----------------
otp_store = {}  # In-memory OTP storage

# ----------------- Helper -----------------


def generate_otp(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

# ----------------- ROUTES -----------------


@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.get_json()
    if not data or "phone" not in data:
        return jsonify({"error": "Phone number is required"}), 400

    phone_number = data["phone"]
    otp = generate_otp()
    otp_store[phone_number] = otp
    message = f"Your verification OTP is: {otp}"

    try:
        response = sms.send(message, [phone_number])
        return jsonify({
            "success": True,
            "message": f"OTP sent to {phone_number}",
            "response": response
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    if not data or "phone" not in data or "otp" not in data:
        return jsonify({"error": "Phone and OTP are required"}), 400

    phone_number = data["phone"]
    otp_input = data["otp"]

    if phone_number in otp_store and otp_store[phone_number] == otp_input:
        del otp_store[phone_number]
        return jsonify({"success": True, "message": "OTP verified successfully!"})
    else:
        return jsonify({"success": False, "message": "Invalid OTP"}), 400


# ----------------- RUN APP -----------------
if __name__ == "__main__":
    app.run(debug=True)
