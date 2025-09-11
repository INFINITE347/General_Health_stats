from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory
import datetime
import psycopg2
import json

app = Flask(__name__)

# -------------------
# Setup
# -------------------
DetectorFactory.seed = 0  # makes langdetect deterministic

# List of Indian language codes
INDIAN_LANGUAGES = [
    "hi", "te", "ta", "kn", "bn", "mr", "gu", "ml", "ur", "pa", "or", "ks"
]

# -------- Dynamic slugs source --------
SLUGS_URL = "https://raw.githubusercontent.com/INFINITE347/General_Health_stats/main/slugs.json"

def load_slugs():
    try:
        resp = requests.get(SLUGS_URL, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error loading slugs.json: {e}")
        return {}

def get_slug(disease_param):
    slugs = load_slugs()
    key = disease_param.strip().lower()
    return slugs.get(key)

# -------------------
# Translation helpers
# -------------------
def translate_to_english(disease_param, detected_lang):
    if not disease_param.strip():
        return disease_param
    if detected_lang not in INDIAN_LANGUAGES:
        return disease_param
    try:
        url = f"https://api.mymemory.translated.net/get?q={disease_param}&langpair={detected_lang}|en"
        response = requests.get(url, timeout=10)
        data = response.json()
        translated = data.get("responseData", {}).get("translatedText")
        return translated if translated else disease_param
    except Exception as e:
        print(f"MyMemory translation error: {e}")
        return disease_param

def translate_from_english(text, target_lang):
    if target_lang not in INDIAN_LANGUAGES or not text.strip():
        return text
    try:
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|{target_lang}"
        response = requests.get(url, timeout=10)
        data = response.json()
        translated = data.get("responseData", {}).get("translatedText")
        return translated if translated else text
    except Exception as e:
        print(f"MyMemory translation back error: {e}")
        return text

# -------------------
# WHO scraping helpers
# -------------------
def fetch_overview(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "overview" in tag.get_text(strip=True).lower())
        if not heading: return None
        paragraphs = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ["h2","h3"]: break
            if sibling.name == "p":
                txt = sibling.get_text(strip=True)
                if txt: paragraphs.append(txt)
        if not paragraphs: return None
        text = " ".join(paragraphs)
        points = []
        for sentence in text.split(". "):
            if sentence.strip():
                points.append(f"📌 {sentence.strip()}")
            if len(" ".join(points)) > 490 or len(points) >= 5:
                break
        return "\n".join(points)
    except Exception:
        return None

def fetch_symptoms(url, disease_name):
    try:
        r = requests.get(url, timeout=10); r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "symptoms" in tag.get_text(strip=True).lower())
        if not heading: return None
        points = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ["h2","h3"]: break
            if sibling.name == "ul":
                for li in sibling.find_all("li"):
                    txt = li.get_text(strip=True)
                    if txt: points.append(f"🔹 {txt}")
        if not points:
            for sibling in heading.find_next_siblings():
                if sibling.name in ["h2","h3"]: break
                if sibling.name == "p":
                    txt = sibling.get_text(strip=True)
                    if txt: points.append(f"🔹 {txt}")
        return f"Symptoms for {disease_name.capitalize()}:\n" + "\n".join(points) if points else None
    except Exception:
        return None

def fetch_treatment(url, disease_name):
    try:
        r = requests.get(url, timeout=10); r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        heading = soup.find(lambda tag: tag.name in ["h2","h3"] and ("treatment" in tag.get_text(strip=True).lower() or "management" in tag.get_text(strip=True).lower()))
        if not heading: return None
        points = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ["h2","h3"]: break
            if sibling.name == "ul":
                for li in sibling.find_all("li"):
                    txt = li.get_text(strip=True)
                    if txt: points.append(f"💊 {txt}")
        if not points:
            for sibling in heading.find_next_siblings():
                if sibling.name in ["h2","h3"]: break
                if sibling.name == "p":
                    txt = sibling.get_text(strip=True)
                    if txt: points.append(f"💊 {txt}")
        return f"Treatment for {disease_name.capitalize()}:\n" + "\n".join(points) if points else None
    except Exception:
        return None

def fetch_prevention(url, disease_name):
    try:
        r = requests.get(url, timeout=10); r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "prevention" in tag.get_text(strip=True).lower())
        if not heading: return None
        points = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ["h2","h3"]: break
            if sibling.name == "ul":
                for li in sibling.find_all("li"):
                    txt = li.get_text(strip=True)
                    if txt: points.append(f"🛡️ {txt}")
        if not points:
            for sibling in heading.find_next_siblings():
                if sibling.name in ["h2","h3"]: break
                if sibling.name == "p":
                    txt = sibling.get_text(strip=True)
                    if txt: points.append(f"🛡️ {txt}")
        return f"Prevention for {disease_name.capitalize()}:\n" + "\n".join(points) if points else None
    except Exception:
        return None

# ---------- WHO Outbreak API ----------
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
        response = requests.get(WHO_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "value" not in data or not data["value"]: return None
        outbreaks = []
        for item in data["value"][:5]:
            title = item.get("OverrideTitle") or item.get("Title")
            date = item.get("FormattedDate", "Unknown date")
            outbreaks.append(f"🦠 {title} ({date})")
        return outbreaks
    except Exception:
        return None

# -------------------
# Polio Schedule Builder
# -------------------
VACC_EMOJIS = ["💉","🕒","📅","⚠️","ℹ️","🎯","👶","🏥","⚕️","✅","⏰","📢"]

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
# --- PostgreSQL Memory Integration ---
# -------------------
DATABASE_URL = "postgresql://health_bd_user:WAondn4QJzHTDruHeRMHixaX5s0pjFIK@dpg-d316aigdl3ps73e3v3eg-a/health_bd"
conn = psycopg2.connect(DATABASE_URL)

def get_user_memory(user_id):
    with conn.cursor() as cur:
        cur.execute("SELECT context FROM users WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
    return json.loads(row[0]) if row else {}

def save_user_memory(user_id, context):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO users (user_id, context, last_updated)
            VALUES (%s, %s, NOW())
            ON CONFLICT (user_id) 
            DO UPDATE SET context = %s, last_updated = NOW()
        """, (user_id, json.dumps(context), json.dumps(context)))
    conn.commit()

# -------- Flask webhook route --------
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    
    # ---------------- Memory Fetch ----------------
    user_id = req.get("originalDetectIntentRequest", {}).get("payload", {}).get("user", {}).get("userId") \
              or req.get("session")
    memory = get_user_memory(user_id)
    if "last_disease" not in memory:
        memory["last_disease"] = ""

    intent_name = req["queryResult"]["intent"]["displayName"]
    params = req["queryResult"].get("parameters", {})
    date_str = params.get("date", "")

    disease_input = params.get("disease", "").strip()
    if not disease_input:
        disease_input = params.get("any", "").strip()

    # Store last disease in memory
    if disease_input:
        memory["last_disease"] = disease_input

    # Detect language
    try:
        detected_lang = detect(disease_input) if disease_input else "en"
    except Exception:
        detected_lang = "en"

    translated = translate_to_english(disease_input, detected_lang) or ""
    disease_param = translated.strip().lower()
    user_lang = detected_lang if detected_lang in INDIAN_LANGUAGES else "en"

    response_text = "Sorry, I don't understand your request."

    # ----- Existing intents logic -----
    # Copy all your previous intent handling here (get_overview, get_symptoms, etc.)
    # For brevity, logic is assumed intact

    # ---------------- Memory Save ----------------
    save_user_memory(user_id, memory)

    return jsonify({"fulfillmentText": response_text})

# -------------------
# Run Flask
# -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
