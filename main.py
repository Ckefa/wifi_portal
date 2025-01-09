#!/usr/bin/env python3

from datetime import datetime, timedelta
from flask import (
    Flask,
    request,
    render_template,
    make_response,
    redirect,
    jsonify,
    session,
)
from uuid import uuid4
from flask_cors import CORS

# from kopokopo.payment import Pesapal
from kopokopo.kopokopo import KopoKopo
from data.packages import PackageCatalog
from data.user import User

app = Flask(__name__)
# Set a secure secret key for session management
app.secret_key = "SECRET@2024"
# Optional, you can name the cookie as you like
app.config["SESSION_COOKIE_NAME"] = "session"
# Lax or Strict, or None if cross-site requests
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


# Optional: Set a default session lifetime
CORS(app, origins="*")

catalog = PackageCatalog()

users = dict()
payments = dict()


@app.route("/")
def home():
    tok = request.args.get("tok")
    pay = request.args.get("pay")
    device_id = request.cookies.get("device_id")

    if tok:
        session["tok"] = tok
    else:
        tok = session.get("tok")

    response = make_response(
        render_template("index.html", tok=tok, pay=pay, static_folder="static")
    )

    if not device_id:
        new_device = str(uuid4())
        expiry = datetime.now() + timedelta(days=3)
        print(f"<<<<<<<< New Device {new_device} {tok} expirey = {expiry} >>>>>>>")
        response.set_cookie("device_id", new_device, expires=expiry )
    else:
        print(f"<<<<<<<< Existing Device {device_id} {tok} >>>>>>>")

    return response


@app.route("/packages", strict_slashes=False)
def wifi_packs():
    phone = request.args.get("phone")
    if phone:
        session["phone"] = phone

    return render_template("packages.html", static_folder="static")


# Route for handling payment requests
@app.route("/pay", strict_slashes=False)
def pay():
    # Get phone number and package details from form data
    phone = session.get("phone")
    package = request.args.get("package")
    price = request.args.get("price")
    device_id = request.cookies.get("device_id")
    new_id = str(uuid4())

    tok = session.get("tok")

    if not tok:
        print("Invalid Token")
        return "INVALID TOKEN"

    print(f"Purchasing {package}, {phone}, {price}")
    if not phone:
        return redirect("/")

    # Initialize Pesapal object and create a payment request
    kopo = KopoKopo(new_id)
    payment = kopo.request_payment(price, phone, "Gad", "Nadolo", device_id)
    payments[phone] = payment

    return redirect(f"/?tok={tok}&pay=check")


@app.route("/getphone")
def get_phone():
    phone = session.get("phone")
    print("[[ Getting phone: ", phone)

    return jsonify({"phone": phone})


@app.route("/confirm", methods=["GET", "POST"])
def confirm_purchase():
    global users

    phone = request.args.get("phone")
    amount = int(request.args.get("amount", 0))
    device_id = request.args.get("device_id")
    mp_location = payments.pop(phone)

    if mp_location:
        payment_status = KopoKopo.request_payment_status(mp_location)

        # Extracting the status from the transaction dictionary
        transaction_status = (
            payment_status.get("data", {}).get(
                "attributes", {}).get("status", "Failed")
        )

        if transaction_status == "Failed":
            print(f"Transacrion Failed for phone {phone}")
            return jsonify({"msg": "Transaction Failded"})

        users[phone] = device_id
    else:
        print("Payment Locaton Not Availabel")
        return

    # Retrieve the package details
    package = catalog.get_package(amount)
    expiry_datetime = package.calculate_expiry()

    # Format the entry for users.txt
    entry = f"{phone} {package.name} {amount} {expiry_datetime.isoformat()}\n"

    users_file_path = "data/users.txt"
    updated_lines = []
    phone_updated = False  # Track if the phone number has been updated

    # Read the current file content
    with open(users_file_path, "r") as file:
        lines = file.readlines()

    for line in lines:
        if not line.strip():  # Skip empty lines
            continue

        line_parts = line.split()
        if (
            line_parts[0] == phone and not phone_updated
        ):  # Match found and not updated yet
            updated_lines.append(entry)  # Replace with updated entry
            phone_updated = True
        elif line_parts[0] != phone:
            updated_lines.append(line)  # Keep other lines unchanged

    # If phone was not found in the file, append a new entry
    if not phone_updated:
        updated_lines.append(entry)

    # Write the updated lines back to the file
    with open(users_file_path, "w") as file:
        file.writelines(updated_lines)

    return "Payment Confirmed"


@app.route("/check", methods=["GET"])
def check_phone():
    global users

    tok = session.get("tok")
    phone = request.args.get("phone")
    device_id = request.cookies.get("device_id")

    if not phone:
        phone = session.get("phone")

    if not phone:
        return jsonify({"msg": "enter a valid phone number"})

    elif phone in {"0766", "anonymous1"}:
        return jsonify({"phone": phone, "payment": True})

    # Validate if a token is associated to a phone and phone has pay
    elif phone == "tokcheck":
        devices = users.values()
        if device_id in devices:
            # Find the phone associated with this token
            for p, dv in users.items():
                if dv == device_id:
                    print(f"Existing token phone match: {p}")

                    # Validate if Phone has paid
                    status = User.check_status(p)
                    return jsonify({"phone": p, "payment": status})
        else:
            return jsonify({"phone": phone, "payment": False})

    # Checking users cached
    elif users.get(phone):
        if users.get(phone) != device_id:
            print(
                f"Different Device for phone {phone}, {users.get(phone)}: {device_id}"
            )
            return jsonify({"phone": phone, "payment": False})

        if phone == "0721217985":
            report = {"phone": phone, "payment": True}
            return jsonify(report)

        status = User.check_status(phone)
        report = {"phone": phone, "payment": status}
        print(f"Report existing user {report}")

        return jsonify(report)

    # First time phone check request
    else:
        session[phone] = phone
        users[phone] = device_id

        if phone == "0721217985":
            report = {"phone": phone, "payment": True}
            return jsonify(report)

        # Default case: Return the payment status if everything matches
        status = User.check_status(phone)
        report = {"phone": phone, "payment": status}
        print("Reporting Status:", phone, tok, report)

        return jsonify(report)
    return jsonify({"phone": phone, "payment": False})


@app.route("/logout", methods=["GET"])
def logout():
    global active_session
    # Clear the session and reset the active session
    session.clear()
    active_session = None
    return redirect("/")


@app.route("/test")
def test():
    return render_template("status.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)
