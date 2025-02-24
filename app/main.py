#!/usr/bin/env python2
from datetime import datetime, timedelta
from threading import Thread
from time import sleep
from uuid import uuid4

from flask import (
    Flask,
    request,
    render_template,
    make_response,
    redirect,
    jsonify,
    session,
)
from flask_cors import CORS

from kopokopo.kopokopo import KopoKopo  # Assuming this is used for payments
from models.packages import PackageCatalog  # Package model
from models.user import User  # Improved User model
from db.db import SessionLocal, create_tables  # DB session and table creation

# Create the tables upon application start
create_tables()

# Initialize the Flask application
app = Flask(__name__)

# Set a secure secret key for session management
app.secret_key = "SECRET@2024"
app.config["SESSION_COOKIE_NAME"] = "session"
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # Controls cross-site cookie behavior

# Enable CORS to allow requests from any origin
CORS(app, origins="*")

# Initialize the package catalog for use in the app
catalog = PackageCatalog()

# Dictionaries to store user data and payment details in memory
users = dict()
payments = dict()


def remove_expired_user(phone, expiry):
    """Remove expired user after the specified expiration time."""
    # Calculate the time remaining until expiry
    sleep_time = (expiry - datetime.now()).total_seconds()
    print(f"Subscription {phone} Expires in {sleep_time} Seconds")
    if sleep_time > 0:
        sleep(sleep_time)
    # Remove the user from the in-memory dictionary
    try:
        with SessionLocal() as db_session:
            user, _ = User.get_or_create(phone, db_session)
            user.status = "expired"
            user.save()

        users.pop(phone, None)
        print(f"Removed expired Subscription {phone}")
    except Exception as e:
        raise e


@app.route("/")
def home():
    """Home route: Handles user sessions, cookies, and displays the home page."""
    tok = request.args.get("tok")  # Get token from URL parameters
    pay = request.args.get("pay")  # Get payment status from URL parameters
    device_id = request.cookies.get("device_id")  # Get device_id from cookies

    if tok:
        session["tok"] = tok  # Store token in session
    else:
        tok = session.get("tok")  # Get token from session

    response = make_response(
        render_template("index.html", tok=tok, pay=pay, static_folder="static")
    )

    # If no device ID exists, create one and set it in cookies
    if not device_id:
        new_device = str(uuid4())
        expiry = datetime.now() + timedelta(days=3)
        print(f"<<<<<<<< New Device {new_device} {tok} expiry = {expiry} >>>>>>>")
        response.set_cookie("device_id", new_device, expires=expiry)
    else:
        print(f"<<<<<<<< Existing Device {device_id} {tok} >>>>>>>")

    return response


@app.route("/packages", strict_slashes=False)
def wifi_packs():
    """Route to display available packages."""
    phone = request.args.get("phone")
    if phone:
        session["phone"] = phone  # Store phone number in session
    return render_template("packages.html", static_folder="static")


@app.route("/pay", strict_slashes=False)
def pay():
    """Route to handle payment requests."""
    phone = session.get("phone")  # Get phone number from session
    package = request.args.get("package")  # Get package info from query params
    price = request.args.get("price")  # Get price from query params
    device_id = request.cookies.get("device_id")  # Get device ID from cookies
    new_id = str(uuid4())  # Generate a new unique transaction ID
    tok = session.get("tok")  # Get token from session

    # Validate token and phone presence
    if not tok or not phone:
        print("Invalid Token or Phone")
        return redirect("/")

    print(f"Purchasing {package}, {phone}, {price}")

    # Create a payment request using KopoKopo API
    kopo = KopoKopo(new_id)
    payment = kopo.request_payment(price, phone, "Gad", "Nadolo", device_id)
    payments[phone] = payment  # Store payment info in memory

    return redirect(f"/?tok={tok}&pay=check")


@app.route("/getphone")
def get_phone():
    """Route to get phone number stored in the session."""
    phone = session.get("phone")
    print("[[ Getting phone:", phone)
    return jsonify({"phone": phone})


@app.route("/confirm", methods=["GET", "POST"])
def confirm_purchase():
    """Route to confirm purchase after payment."""
    phone = request.args.get("phone")
    amount = int(request.args.get("amount", 0))
    device_id = request.args.get("device_id")

    # Confirm with kopopo payment Status
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
        print("Payment Locaton Not Availabe")
        return

    # Retrieve package details and calculate expiry date
    package = catalog.get_package(amount)
    expiry_datetime = package.calculate_expiry()

    # Use a new session from our SessionLocal
    with SessionLocal() as db_session:
        # Use the get_or_create method of User model.
        user, created = User.get_or_create(phone, db_session)
        # If the user already exists, refresh it to ensure attributes are loaded
        if not created:
            db_session.refresh(user)
        # Update user details regardless of creation status.
        user.expiry = expiry_datetime
        user.package = package.name
        user.amount = package.price
        user.status = "active"
        user.total += package.price
        print(f"Updated user package price {user.amount}, {user.package}")
        user.save(db_session)

    # Start a thread to remove the user from the in-memory dict after expiry
    thread = Thread(target=remove_expired_user, args=[phone, expiry_datetime])
    thread.start()

    # add device id to active Users
    users[phone] = device_id

    return "Payment Confirmed"


@app.route("/check", methods=["GET"])
def check_phone():
    """Route to check payment status for a phone number."""
    tok = session.get("tok")
    phone = request.args.get("phone") or session.get("phone")
    device_id = request.cookies.get("device_id")

    if not phone:
        return jsonify({"msg": "Enter a valid phone number"})

    # Special cases for certain phone values
    if phone == "anonymous1":
        return jsonify({"phone": phone, "payment": True})
    elif phone == "tokcheck":
        devices = users.values()
        if device_id in devices:
            for p, dv in users.items():
                if dv == device_id:
                    print(f"Existing token phone match: {p}")
                    # Retrieve user status from the DB using a different variable name
                    with SessionLocal() as db_session:
                        user, _ = User.get_or_create(p, db_session)
                        status = user.check_status() if user else False
                    return jsonify({"phone": p, "payment": status})
        else:
            return jsonify({"phone": phone, "payment": False})
    elif phone in users:
        if users.get(phone) != device_id:
            print(f"Different Device for phone {phone}: {users.get(phone)} vs {device_id}")
            return jsonify({"phone": phone, "payment": False})
        with SessionLocal() as db_session:
            # Use get_or_create to retrieve the user from the DB
            user, _ = User.get_or_create(phone, db_session)
            status = user.check_status()
            report = {"phone": phone, "payment": status}
            print(f"Report existing user {report}")
        return jsonify(report)
    else:
        # First-time user: store phone-device relation in memory and create new user in DB
        session["phone"] = phone
        users[phone] = device_id
        with SessionLocal() as db_session:
            user = User(phone)  # create a new User object
            # Save the new user in the DB
            user.save(db_session)
            status = user.check_status()
        report = {"phone": phone, "payment": status}
        print("Reporting Status:", phone, tok, report)
        return jsonify(report)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)

