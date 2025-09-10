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
    print(req)  # Debug: see full payload

    intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    params = req.get("queryResult", {}).get("parameters", {})

    disease = params.get("disease", "").lower()

    # Default to today if date not provided
    birth_date = datetime.date.today()

    # --- Only handle get_vaccine for Polio ---
    if intent_name == "get_vaccine":
        schedule = build_polio_schedule(birth_date)

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
    else:
        response_text = "❌ Sorry, vaccination info not available for this request."

    return jsonify({"fulfillmentText": response_text})

# -------------------
# Run Flask
# -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
