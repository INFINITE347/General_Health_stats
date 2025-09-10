from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

# -------------------
# Polio Schedule Builder
# -------------------
def build_polio_schedule(birth_date):
    schedule = []
    schedule.append(("At Birth (within 15 days)", birth_date, "OPV-0"))
    schedule.append(("6 Weeks", birth_date + datetime.timedelta(weeks=6), "OPV-1 + IPV-1"))
    schedule.append(("10 Weeks", birth_date + datetime.timedelta(weeks=10), "OPV-2"))
    schedule.append(("14 Weeks", birth_date + datetime.timedelta(weeks=14), "OPV-3 + IPV-2"))
    schedule.append(("16–24 Months", birth_date + datetime.timedelta(weeks=72), "OPV + IPV Boosters"))
    schedule.append(("5 Years", birth_date + datetime.timedelta(weeks=260), "OPV Booster"))
    return schedule

# -------------------
# Webhook Route
# -------------------
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    print("Received request:", req)  # Debugging

    intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName")
    params = req.get("queryResult", {}).get("parameters", {})

    disease = params.get("disease", "").lower()
    date_str = params.get("date")  # Example: '2006-11-22T12:00:00+05:30'

    if intent_name != "get_vaccine" or disease != "polio":
        return jsonify({"fulfillmentText": "Sorry, I can only provide Polio vaccine schedule."})

    if not date_str:
        return jsonify({"fulfillmentText": "Please provide the child's date of birth."})

    # Parse date from Dialogflow format (YYYY-MM-DDTHH:MM:SS+TZ)
    try:
        birth_date = datetime.datetime.fromisoformat(date_str.split("T")[0]).date()
    except Exception as e:
        return jsonify({"fulfillmentText": f"Invalid date format: {date_str}"})

    # Build schedule
    schedule = build_polio_schedule(birth_date)

    # Create response
    lines = ["🧾 POLIO VACCINATION SCHEDULE"]
    lines.append("1️⃣ Vaccine Name 🧪: Oral Polio Vaccine (OPV) + Injectable Polio Vaccine (IPV)")
    lines.append("2️⃣ Period of Time / Age ⏳: From birth up to 5 years")
    lines.append("3️⃣ Vaccination Date & Last Date 📅")
    for period, date, vaccine in schedule:
        lines.append(f"- {period}: {date.strftime('%d-%b-%Y')} → {vaccine}")
    lines.append("4️⃣ Disease & Symptoms ⚠️: Polio causes fever 🤒, weakness 😴, headache 🤕, vomiting 🤮, stiffness 🧍‍♂️, paralysis 🚶‍♂️❌")
    lines.append("5️⃣ About the Vaccine ℹ️: OPV (oral drops) 👅, IPV (injection) 💉, free under Govt.")
    lines.append("6️⃣ Purpose 🎯: Prevents life-long paralysis & disability.")
    lines.append("7️⃣ Gender 👦👧: For all children.")
    lines.append("8️⃣ Where to Get 🏥: Govt hospitals, PHCs, Anganwadis, ASHA workers.")
    lines.append("9️⃣ Side Effects ⚠️: Safe 👍; rarely mild fever. Consult doctor if severe 🚑")
    lines.append("🔟 After Vaccination ✅: Feed normally 🍼, stay 30 mins at centre, don’t skip future doses.")
    lines.append(f"1️⃣1️⃣ Next Dose Reminder ⏰: Next after birth dose: {schedule[1][1].strftime('%d-%b-%Y')} (OPV-1 + IPV-1)")
    lines.append("1️⃣2️⃣ Pulse Polio Campaign 📢: Even if vaccinated, attend Pulse Polio days.")

    response_text = "\n".join(lines)
    return jsonify({"fulfillmentText": response_text})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
