
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory
import datetime

app = Flask(__name__)

# -------------------
# Setup
# -------------------
DetectorFactory.seed = 0
INDIAN_LANGUAGES = ["hi","te","ta","kn","bn","mr","gu","ml","ur","pa","or","ks"]
SLUGS_URL = "https://raw.githubusercontent.com/INFINITE347/General_Health_stats/main/slugs.json"

# -------------------
# Slug Helpers
# -------------------
def load_slugs():
    try:
        resp = requests.get(SLUGS_URL, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except:
        return {}

def get_slug(disease_param):
    slugs = load_slugs()
    return slugs.get(disease_param.strip().lower())

# -------------------
# Translation Helpers
# -------------------
def translate_to_english(text, detected_lang):
    if detected_lang not in INDIAN_LANGUAGES: return text
    try:
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair={detected_lang}|en"
        r = requests.get(url, timeout=10).json()
        return r.get("responseData", {}).get("translatedText", text)
    except:
        return text

def translate_from_english(text, target_lang):
    if target_lang not in INDIAN_LANGUAGES: return text
    try:
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|{target_lang}"
        r = requests.get(url, timeout=10).json()
        return r.get("responseData", {}).get("translatedText", text)
    except:
        return text

# -------------------
# WHO Scrapers
# -------------------
def fetch_overview(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text,"html.parser")
        h = soup.find(lambda tag: tag.name in ["h2","h3"] and "overview" in tag.get_text(strip=True).lower())
        if not h: return None
        paras = []
        for sib in h.find_next_siblings():
            if sib.name in ["h2","h3"]: break
            if sib.name=="p": paras.append(sib.get_text(strip=True))
        return " ".join(paras) if paras else None
    except: return None

def fetch_points(url, keyword, disease_name, title_prefix):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text,"html.parser")
        h = soup.find(lambda tag: tag.name in ["h2","h3"] and keyword in tag.get_text(strip=True).lower())
        if not h: return None
        points = []
        for sib in h.find_next_siblings():
            if sib.name in ["h2","h3"]: break
            if sib.name=="ul":
                for li in sib.find_all("li"):
                    txt = li.get_text(strip=True)
                    if txt: points.append(f"- {txt}")
            elif sib.name=="p":
                txt = sib.get_text(strip=True)
                if txt: points.append(f"- {txt}")
        return f"{title_prefix} {disease_name.capitalize()}:\n" + "\n".join(points) if points else None
    except: return None

def fetch_symptoms(url,disease_name): return fetch_points(url,"symptoms",disease_name,"The common symptoms of")
def fetch_treatment(url,disease_name): return fetch_points(url,"treatment",disease_name,"The common treatments for")
def fetch_prevention(url,disease_name): return fetch_points(url,"prevention",disease_name,"The common prevention methods for")

# -------------------
# WHO Outbreak
# -------------------
WHO_API_URL = (
    "https://www.who.int/api/emergencies/diseaseoutbreaknews"
    "?sf_provider=dynamicProvider372&sf_culture=en"
    "&$orderby=PublicationDateAndTime%20desc"
    "&$expand=EmergencyEvent"
    "&$select=Title,TitleSuffix,OverrideTitle,UseOverrideTitle,regionscountries,"
    "ItemDefaultUrl,FormattedDate,PublicationDateAndTime"
    "&%24format=json&%24top=10&%24count=true"
)
def get_who_outbreak_data():
    try:
        r = requests.get(WHO_API_URL, timeout=10)
        r.raise_for_status()
        data = r.json()
        if "value" not in data or not data["value"]: return None
        out = []
        for item in data["value"][:5]:
            title = item.get("OverrideTitle") or item.get("Title")
            date = item.get("FormattedDate","Unknown date")
            url = "https://www.who.int"+item.get("ItemDefaultUrl","")
            out.append(f"🦠 {title} ({date})\n🔗 {url}")
        return out
    except: return None

# -------------------
# Polio Schedule
# -------------------
def build_polio_schedule(birth_date):
    sched=[]
    sched.append(("At Birth (within 15 days)", birth_date, "OPV-0"))
    sched.append(("6 Weeks", birth_date + datetime.timedelta(weeks=6), "OPV-1 + IPV-1"))
    sched.append(("10 Weeks", birth_date + datetime.timedelta(weeks=10), "OPV-2"))
    sched.append(("14 Weeks", birth_date + datetime.timedelta(weeks=14), "OPV-3 + IPV-2"))
    sched.append(("16–24 Months", birth_date + datetime.timedelta(weeks=72), "OPV + IPV Boosters"))
    sched.append(("5 Years", birth_date + datetime.timedelta(weeks=260), "OPV Booster"))
    return sched

# -------------------
# Flask Webhook
# -------------------
@app.route('/webhook',methods=['POST'])
def webhook():
    req=request.get_json()
    intent=req.get("queryResult", {}).get("intent", {}).get("displayName","")
    params=req.get("queryResult", {}).get("parameters",{})
    disease=params.get("disease","").strip()

    try: detected_lang=detect(disease) if disease else "en"
    except: detected_lang="en"

    disease_en=translate_to_english(disease, detected_lang).strip().lower()
    user_lang=detected_lang if detected_lang in INDIAN_LANGUAGES else "en"
    response_text="Sorry, I don't understand your request."

    # --- Overview ---
    if intent=="get_disease_overview":
        slug=get_slug(disease_en)
        if slug:
            url=f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
            response_text=fetch_overview(url) or f"Overview not found for {disease_en.capitalize()}. More: {url}"
        else: response_text=f"Disease not found."

    # --- Symptoms ---
    elif intent=="get_symptoms":
        slug=get_slug(disease_en)
        if slug:
            url=f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
            response_text=fetch_symptoms(url,disease_en) or f"Symptoms not found for {disease_en.capitalize()}. More: {url}"

    # --- Treatment ---
    elif intent=="get_treatment":
        slug=get_slug(disease_en)
        if slug:
            url=f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
            response_text=fetch_treatment(url,disease_en) or f"Treatment not found for {disease_en.capitalize()}. More: {url}"

    # --- Prevention ---
    elif intent=="get_prevention":
        slug=get_slug(disease_en)
        if slug:
            url=f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
            response_text=fetch_prevention(url,disease_en) or f"Prevention not found for {disease_en.capitalize()}. More: {url}"

    # --- Outbreak ---
    elif intent=="disease_outbreak.general":
        outbreaks=get_who_outbreak_data()
        response_text="⚠️ Unable to fetch outbreak data." if not outbreaks else "🌍 Latest WHO Outbreak News:\n\n"+ "\n\n".join(outbreaks)

    # --- Vaccine ---
    elif intent=="get_vaccine":
        birth_date_str=params.get("date")
        birth_date=datetime.date.today()  # default to today
        if birth_date_str:
            try:
                birth_date=datetime.datetime.strptime(birth_date_str[:10],"%Y-%m-%d").date()
            except:
                pass

        sched=build_polio_schedule(birth_date)
        lines=["🧾 POLIO VACCINATION SCHEDULE"]
        lines.append("\n1️⃣ Vaccine Name 🧪\n👉 Oral Polio Vaccine (OPV) + Injectable Polio Vaccine (IPV)")
        lines.append("\n2️⃣ Period of Time / Age ⏳\n👉 From birth up to 5 years")
        lines.append("\n3️⃣ Vaccination Date & Last Date 📅")
        for period,date,vaccine_name in sched:
            lines.append(f"- {period}: {date.strftime('%d-%b-%Y')} → {vaccine_name}")
        lines.append("\n4️⃣ Disease & Symptoms ⚠️\n👉 Polio causes fever 🤒, weakness 😴, headache 🤕, vomiting 🤮, stiffness 🧍‍♂️, paralysis 🚶‍♂️❌")
        lines.append("\n5️⃣ About the Vaccine ℹ️\n👉 OPV (oral drops) 👅, IPV (injection) 💉, free under Govt.")
        lines.append("\n6️⃣ Purpose 🎯\n👉 Prevents life-long paralysis & disability.")
        lines.append("\n7️⃣ Gender 👦👧\n👉 For all children.")
        lines.append("\n8️⃣ Where to Get 🏥\n👉 Govt hospitals, PHCs, Anganwadis, ASHA workers.")
        lines.append("\n9️⃣ Side Effects ⚠️\n👉 Safe 👍; rarely mild fever. Consult doctor if severe 🚑")
        lines.append("\n🔟 After Vaccination ✅\n👉 Feed normally 🍼, stay 30 mins at centre, don’t skip future doses.")
        lines.append(f"\n1️⃣1️⃣ Next Dose Reminder ⏰\n👉 Next after birth dose: {sched[1][1].strftime('%d-%b-%Y')} (OPV-1 + IPV-1)")
        lines.append("\n1️⃣2️⃣ Pulse Polio Campaign 📢\n👉 Even if vaccinated, attend Pulse Polio days.")
        response_text="\n".join(lines)
        response_text=translate_from_english(response_text,user_lang)

    return jsonify({"fulfillmentText": response_text})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
