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
# Flask Webhook Route
# -------------------
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent_name = req["queryResult"]["intent"]["displayName"]
    params = req["queryResult"].get("parameters", {})
    
    disease_input = params.get("disease", "").strip().lower()
    date_str = params.get("date")  # e.g., "2006-11-22T12:00:00+05:30"

    response_text = "Sorry, I don't understand your request."

    if intent_name == "get_vaccine" and disease_input == "polio" and date_str:
        # Only take the date portion
        birth_date = datetime.datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        schedule = build_polio_schedule(birth_date)

        # Build response
        lines = ["🧾 POLIO VACCINATION SCHEDULE"]
        lines.append("\n1️⃣ Vaccine Name 🧪\n👉 Oral Polio Vaccine (OPV) + Injectable Polio Vaccine (IPV)")
        lines.append("\n2️⃣ Period of Time / Age ⏳\n👉 From birth up to 5 years")
        lines.append("\n3️⃣ Vaccination Date & Last Date 📅")
        for period, date, vaccine in schedule:
            lines.append(f"- {period}: {date.strftime('%d-%b-%Y')} → {vaccine}")
        lines.append("\n4️⃣ Disease & Symptoms ⚠️\n👉 Polio causes fever 🤒, weakness 😴, headache 🤕, vomiting 🤮, stiffness 🧍‍♂️, paralysis 🚶‍♂️❌")
        lines.append("\n5️⃣ About the Vaccine ℹ️\n👉 OPV (oral drops) 👅, IPV (injection) 💉, free under Govt.")
        lines.append("\n6️⃣ Purpose 🎯\n👉 Prevents life-long paralysis & disability.")
        lines.append("\n7️⃣ Gender 👦👧\n👉 For all children.")
        lines.append("\n8️⃣ Where to Get 🏥\n👉 Govt hospitals, PHCs, Anganwadis, ASHA workers.")
        lines.append("\n9️⃣ Side Effects ⚠️\n👉 Safe 👍; rarely mild fever. Consult doctor if severe 🚑")
        lines.append("\n🔟 After Vaccination ✅\n👉 Feed normally 🍼, stay 30 mins at centre, don’t skip future doses.")
        lines.append(f"\n1️⃣1️⃣ Next Dose Reminder ⏰\n👉 Next after birth dose: {schedule[1][1].strftime('%d-%b-%Y')} (OPV-1 + IPV-1)")
        lines.append("\n1️⃣2️⃣ Pulse Polio Campaign 📢\n👉 Even if vaccinated, attend Pulse Polio days.")

        response_text = "\n".join(lines)

    return jsonify({"fulfillmentText": response_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
