
from flask import Flask, render_template, request
from pathlib import Path
from datetime import datetime
import json

app = Flask(__name__)

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REGISTRATIONS_FILE = DATA_DIR / "registrations.json"

# Create the data directory and registration file if needed
DATA_DIR.mkdir(parents=True, exist_ok=True)

if not REGISTRATIONS_FILE.exists():
    REGISTRATIONS_FILE.write_text("[]", encoding="utf-8")


# Available medical camps
ALLOWED_CAMPS = {
    "General Health Checkup Camp",
    "Eye Care Camp",
    "Diabetes Awareness Camp",
    "Women's Health Camp",
}


def load_registrations():
    """Load saved registrations from the JSON file."""
    try:
        with REGISTRATIONS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        app.logger.exception("Could not read registration data.")
        return []


def save_registration(registration):
    """Save a registration without overwriting existing entries."""
    registrations = load_registrations()
    registrations.append(registration)

    with REGISTRATIONS_FILE.open("w", encoding="utf-8") as file:
        json.dump(registrations, file, indent=4, ensure_ascii=False)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/camps")
def camps():
    return render_template("camps.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        age = request.form.get("age", "").strip()
        contact_number = request.form.get("contact", "").strip()
        email = request.form.get("email", "").strip()
        camp = request.form.get("camp", "").strip()
        address = request.form.get("address", "").strip()

        # Validate required fields
        if not full_name or not age or not contact_number or not camp:
            return "Please complete all required fields.", 400

        # Validate age
        try:
            age_value = int(age)
        except ValueError:
            return "Please enter a valid age.", 400

        if not 1 <= age_value <= 120:
            return "Age must be between 1 and 120.", 400

        # Validate contact number
        if len(contact_number) != 10 or not contact_number.isdigit():
            return "Please enter a valid 10-digit contact number.", 400

        # Validate selected camp
        if camp not in ALLOWED_CAMPS:
            return "Please select a valid medical camp.", 400

        # Prepare registration record
        registration = {
            "full_name": full_name,
            "age": age_value,
            "contact": contact_number,
            "email": email,
            "camp": camp,
            "address": address,
            "registered_at": datetime.now().isoformat(
                timespec="seconds"
            ),
        }

        # Save registration
        try:
            save_registration(registration)
        except OSError:
            app.logger.exception("Could not save registration.")
            return "Registration could not be saved. Please try again.", 500

        # Show confirmation page
        return render_template(
            "success.html",
            full_name=full_name,
            camp=camp,
        )

    return render_template("register.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/admin/registrations")
def admin_registrations():
    """Display saved registrations for development/testing."""
    registrations = load_registrations()

    return render_template(
        "admin_registrations.html",
        registrations=registrations,
    )


@app.errorhandler(404)
def page_not_found(error):
    return "Page not found. Please check the URL.", 404


@app.errorhandler(500)
def internal_server_error(error):
    return "An internal server error occurred. Check the Flask terminal for details.", 500


if __name__ == "__main__":
    print("\nMedical Camp Registration Portal")
    print("Starting Flask server...")
    app.run(host="127.0.0.1", port=5000, debug=True)

