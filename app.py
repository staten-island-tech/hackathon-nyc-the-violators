from flask import Flask, render_template, request, redirect, session, url_for
import random
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

with open('events.json') as f:
    events = json.load(f)

homes = [
    {"type": "Shared Apartment", "borough": "Bronx", "rent": 1600},
    {"type": "Studio", "borough": "Brooklyn", "rent": 2300},
    {"type": "1-Bedroom", "borough": "Manhattan", "rent": 3200},
    {"type": "Basement Apartment", "borough": "Queens", "rent": 1900},
    {"type": "Small Home", "borough": "Staten Island", "rent": 1400}
]

jobs = [
    {"title": "Barista", "pay": 450, "hours": 30, "happiness": -15},
    {"title": "Delivery Person", "pay": 500, "hours": 40, "happiness": -20},
    {"title": "Retail Associate", "pay": 550, "hours": 35, "happiness": -15},
    {"title": "Janitor", "pay": 400, "hours": 20, "happiness": -10}
]

better_jobs = [
    {"title": "Software Developer", "pay": 2000, "hours": 40, "happiness": 8},
    {"title": "Financial Analyst", "pay": 1800, "hours": 45, "happiness": 9},
    {"title": "Nurse", "pay": 1700, "hours": 40, "happiness": 10}
]

JOB_OFFER_INTERVAL = 20  # weeks interval for new job offers
WINNING_BALANCE = 100000

@app.route('/')
def index():
    return render_template("index.html", homes=homes, jobs=jobs)

@app.route('/start_game', methods=["POST"])
def start_game():
    home_index = int(request.form["home"])
    job_index = int(request.form["job"])

    session["home"] = homes[home_index]
    session["job"] = jobs[job_index]
    session["balance"] = 300
    session["happiness"] = 50
    session["hunger"] = 20
    session["week"] = 1
    session["log"] = []
    session["job_offer_available"] = False
    session["job_offers"] = []

    return redirect(url_for("week"))

@app.route('/week')
def week():
    if "week" not in session:
        return redirect(url_for("index"))
    if "job_offer_available" not in session:
        session["job_offer_available"] = False

    if session["job_offer_available"]:
        job_offers = session["job_offers"]
    else:
        # Generate new offers only on the correct week interval
        if session["week"] % JOB_OFFER_INTERVAL == 0:
            current_job_title = session["job"]["title"]
            job_offers = [job for job in better_jobs if job["title"] != current_job_title]
            session["job_offer_available"] = True
            session["job_offers"] = job_offers
        else:
            job_offers = []
            session["job_offer_available"] = False
            session["job_offers"] = []

    current_event = random.choice(events)
    session["current_event"] = current_event

    return render_template(
        "week.html",
        event=current_event,
        week=session["week"],
        balance=session["balance"],
        happiness=session["happiness"],
        hunger=session["hunger"],
        home=session["home"],
        job=session["job"],
        log=session["log"][::-1],
        job_offer_available=session["job_offer_available"],
        job_offers=job_offers,
    )

@app.route('/make_decision', methods=["POST"])
def make_decision():
    choice = request.form["choice"]
    event = session.get("current_event", None)

    if not event:
        return redirect(url_for("week"))

    effect = event["effects"][choice]

    # Apply job income first
    income = session["job"]["pay"]
    session["balance"] += income
    session["log"].append(f"Paycheck: +${income}")

    # Deduct weekly rent
    rent = int(session["home"]["rent"] / 4)
    session["balance"] -= rent
    session["log"].append(f"Rent: -${rent}")

    # Apply event effects (money, happiness, hunger)
    session["balance"] += effect.get("money", 0)
    session["happiness"] += effect.get("happiness", 0)
    session["hunger"] += effect.get("hunger", 0)

    # Log money change from event if any
    if effect.get("money", 0) != 0:
        sign = "+" if effect["money"] > 0 else ""
        session["log"].append(f"{choice.title()}: {sign}${effect['money']}")

    # Apply special effects (new_rent, new_job, bonus)
    effect = event["effects"][choice]  # Already defined, but repeat for clarity

    if "rent_multiplier" in effect:
        current_rent = session["home"]["rent"]
        new_rent = int(current_rent * effect["rent_multiplier"])
        session["home"]["rent"] = new_rent
        session["log"].append(f"Rent adjusted to ${new_rent} due to event")


    if "new_job" in effect:
        old_job_title = session["job"]["title"]
        session["job"] = effect["new_job"]
        session["log"].append(f"Got a new job: {session['job']['title']} (Previous: {old_job_title})")

    if "bonus" in effect:
        session["balance"] += effect["bonus"]
        session["log"].append(f"Bonus received: +${effect['bonus']}")

    # Clamp stats
    session["happiness"] = min(max(session["happiness"], 0), 100)
    session["hunger"] = min(max(session["hunger"], 0), 100)

    # Check game over conditions
    if session["balance"] < 0:
        return render_template("game_over.html", reason="You ran out of money.")
    if session["happiness"] <= 0:
        return render_template("game_over.html", reason="Your happiness dropped to zero.")
    if session["hunger"] >= 100:
        return render_template("game_over.html", reason="You starved to death.")
    if session["balance"] >= WINNING_BALANCE:
        return render_template("victory.html", reason="Congratulations! You became financially successful and won the game!")

    session["week"] += 1
    return redirect(url_for("week"))

@app.route('/accept_job', methods=["POST"])
def accept_job():
    if not session.get("job_offer_available", False):
        return redirect(url_for("week"))

    job_index = int(request.form["job_index"])
    new_job = session["job_offers"][job_index]
    old_job = session["job"]

    session["job"] = new_job
    session["job_offer_available"] = False
    session["job_offers"] = []

    session["log"].append(f"Accepted new job: {new_job['title']} (Previous: {old_job['title']})")

    return redirect(url_for("week"))

@app.route('/decline_job', methods=["POST"])
def decline_job():
    session["job_offer_available"] = False
    session["job_offers"] = []

    session["log"].append("Declined new job offer")

    return redirect(url_for("week"))

if __name__ == '__main__':
    app.run(debug=True)