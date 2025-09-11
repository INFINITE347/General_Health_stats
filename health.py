# from flask import Flask, request, jsonify
# import requests
# from bs4 import BeautifulSoup
# from langdetect import detect, DetectorFactory
# import datetime

# app = Flask(__name__)

# # -------------------
# # Setup
# # -------------------
# DetectorFactory.seed = 0  # makes langdetect deterministic

# # List of Indian language codes
# INDIAN_LANGUAGES = [
#     "hi", "te", "ta", "kn", "bn", "mr", "gu", "ml", "ur", "pa", "or", "ks"
# ]

# # -------- Dynamic slugs source --------
# SLUGS_URL = "https://raw.githubusercontent.com/INFINITE347/General_Health_stats/main/slugs.json"


# def load_slugs():
#     try:
#         resp = requests.get(SLUGS_URL, timeout=10)
#         resp.raise_for_status()
#         return resp.json()
#     except Exception as e:
#         print(f"Error loading slugs.json: {e}")
#         return {}


# def get_slug(disease_param):
#     slugs = load_slugs()
#     key = disease_param.strip().lower()
#     return slugs.get(key)


# # -------------------
# # Translation helpers
# # -------------------
# def translate_to_english(disease_param, detected_lang):
#     if not disease_param.strip():
#         return disease_param
#     if detected_lang not in INDIAN_LANGUAGES:
#         return disease_param
#     try:
#         url = f"https://api.mymemory.translated.net/get?q={disease_param}&langpair={detected_lang}|en"
#         response = requests.get(url, timeout=10)
#         data = response.json()
#         translated = data.get("responseData", {}).get("translatedText")
#         return translated if translated else disease_param
#     except Exception as e:
#         print(f"MyMemory translation error: {e}")
#         return disease_param


# def translate_from_english(text, target_lang):
#     if target_lang not in INDIAN_LANGUAGES or not text.strip():
#         return text
#     try:
#         url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|{target_lang}"
#         response = requests.get(url, timeout=10)
#         data = response.json()
#         translated = data.get("responseData", {}).get("translatedText")
#         return translated if translated else text
#     except Exception as e:
#         print(f"MyMemory translation back error: {e}")
#         return text


# # -------------------
# # WHO scraping helpers
# # -------------------
# def fetch_overview(url):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")
#         heading = soup.find(lambda tag: tag.name in ["h2", "h3"] and "overview" in tag.get_text(strip=True).lower())
#         if not heading:
#             return None
#         paragraphs = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2", "h3"]: break
#             if sibling.name == "p":
#                 txt = sibling.get_text(strip=True)
#                 if txt: paragraphs.append(txt)
#         return " ".join(paragraphs) if paragraphs else None
#     except Exception:
#         return None


# def fetch_symptoms(url, disease_name):
#     try:
#         r = requests.get(url, timeout=10); r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")
#         heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "symptoms" in tag.get_text(strip=True).lower())
#         if not heading: return None
#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2","h3"]: break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt: points.append(f"- {txt}")
#         if not points:
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2","h3"]: break
#                 if sibling.name == "p":
#                     txt = sibling.get_text(strip=True)
#                     if txt: points.append(f"- {txt}")
#         return f"The common symptoms of {disease_name.capitalize()} are:\n" + "\n".join(points) if points else None
#     except Exception:
#         return None


# def fetch_treatment(url, disease_name):
#     try:
#         r = requests.get(url, timeout=10); r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")
#         heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "treatment" in tag.get_text(strip=True).lower())
#         if not heading: return None
#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2","h3"]: break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt: points.append(f"- {txt}")
#         if not points:
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2","h3"]: break
#                 if sibling.name == "p":
#                     txt = sibling.get_text(strip=True)
#                     if txt: points.append(f"- {txt}")
#         return f"The common treatments for {disease_name.capitalize()} are:\n" + "\n".join(points) if points else None
#     except Exception:
#         return None


# def fetch_prevention(url, disease_name):
#     try:
#         r = requests.get(url, timeout=10); r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")
#         heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "prevention" in tag.get_text(strip=True).lower())
#         if not heading: return None
#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2","h3"]: break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt: points.append(f"- {txt}")
#         if not points:
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2","h3"]: break
#                 if sibling.name == "p":
#                     txt = sibling.get_text(strip=True)
#                     if txt: points.append(f"- {txt}")
#         return f"The common prevention methods for {disease_name.capitalize()} are:\n" + "\n".join(points) if points else None
#     except Exception:
#         return None


# # ---------- WHO Outbreak API ----------
# WHO_API_URL = (
#     "https://www.who.int/api/emergencies/diseaseoutbreaknews"
#     "?sf_provider=dynamicProvider372&sf_culture=en"
#     "&$orderby=PublicationDateAndTime%20desc"
#     "&$expand=EmergencyEvent"
#     "&$select=Title,TitleSuffix,OverrideTitle,UseOverrideTitle,regionscountries,"
#     "ItemDefaultUrl,FormattedDate,PublicationDateAndTime"
#     "&%24format=json&%24top=10&%24count=true"
# )

# def get_who_outbreak_data():
#     try:
#         response = requests.get(WHO_API_URL, timeout=10)
#         response.raise_for_status()
#         data = response.json()
#         if "value" not in data or not data["value"]:
#             return None
#         outbreaks = []
#         for item in data["value"][:5]:
#             title = item.get("OverrideTitle") or item.get("Title")
#             date = item.get("FormattedDate", "Unknown date")
#             url = "https://www.who.int" + item.get("ItemDefaultUrl", "")
#             outbreaks.append(f"🦠 {title} ({date})\n🔗 {url}")
#         return outbreaks
#     except Exception:
#         return None


# # -------------------
# # Polio Schedule Builder
# # -------------------
# def build_polio_schedule(birth_date):
#     schedule = []
#     schedule.append(("At Birth (within 15 days)", birth_date, "OPV-0"))
#     schedule.append(("6 Weeks", birth_date + datetime.timedelta(weeks=6), "OPV-1 + IPV-1"))
#     schedule.append(("10 Weeks", birth_date + datetime.timedelta(weeks=10), "OPV-2"))
#     schedule.append(("14 Weeks", birth_date + datetime.timedelta(weeks=14), "OPV-3 + IPV-2"))
#     schedule.append(("16–24 Months", birth_date + datetime.timedelta(weeks=72), "OPV + IPV Boosters"))
#     schedule.append(("5 Years", birth_date + datetime.timedelta(weeks=260), "OPV Booster"))
#     return schedule


# # -------- Flask webhook route --------
# @app.route('/webhook', methods=['POST'])
# def webhook():
#     req = request.get_json()
#     intent_name = req["queryResult"]["intent"]["displayName"]
#     params = req["queryResult"].get("parameters", {})
#     disease_input = params.get("disease", "").strip()
#     date_str = params.get("date", "")

#     # ✅ Detect language
#     try:
#         detected_lang = detect(disease_input) if disease_input else "en"
#     except Exception:
#         detected_lang = "en"

#     translated = translate_to_english(disease_input, detected_lang) or ""
#     disease_param = translated.strip().lower()
#     user_lang = detected_lang if detected_lang in INDIAN_LANGUAGES else "en"

#     response_text = "Sorry, I don't understand your request."

#     if intent_name == "get_disease_overview":
#         slug = get_slug(disease_param)
#         if slug:
#             url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#             overview = fetch_overview(url)
#             response_text = overview or f"Overview not found for {disease_param.capitalize()}. You can read more here: {url}"
#         else:
#             response_text = f"Disease not found. Make sure to use a valid disease name."

#     elif intent_name == "get_symptoms":
#         slug = get_slug(disease_param)
#         if slug:
#             url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#             symptoms = fetch_symptoms(url, disease_param)
#             response_text = symptoms or f"Symptoms not found for {disease_param.capitalize()}. You can read more here: {url}"
#         else:
#             response_text = f"Sorry, I don't have a URL for {disease_param.capitalize()}."

#     elif intent_name == "get_treatment":
#         slug = get_slug(disease_param)
#         if slug:
#             url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#             treatment = fetch_treatment(url, disease_param)
#             response_text = treatment or f"Treatment details not found for {disease_param.capitalize()}. You can read more here: {url}"
#         else:
#             response_text = f"Sorry, I don't have a URL for {disease_param.capitalize()}."

#     elif intent_name == "get_prevention":
#         slug = get_slug(disease_param)
#         if slug:
#             url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#             prevention = fetch_prevention(url, disease_param)
#             response_text = prevention or f"Prevention methods not found for {disease_param.capitalize()}. You can read more here: {url}"
#         else:
#             response_text = f"Sorry, I don't have a URL for {disease_param.capitalize()}."

#     elif intent_name == "disease_outbreak.general":
#         outbreaks = get_who_outbreak_data()
#         if not outbreaks:
#             response_text = "⚠️ Unable to fetch outbreak data right now."
#         else:
#             response_text = "🌍 Latest WHO Outbreak News:\n\n" + "\n\n".join(outbreaks)

#     elif intent_name == "get_vaccine":
#         # ✅ Use given date or today
#         if date_str:
#             try:
#                 birth_date = datetime.datetime.strptime(date_str.split("T")[0], "%Y-%m-%d").date()
#             except Exception:
#                 birth_date = datetime.date.today()
#         else:
#             birth_date = datetime.date.today()

#         schedule = build_polio_schedule(birth_date)

#         lines = ["🧾 POLIO VACCINATION SCHEDULE"]
#         lines.append("\n1️⃣ Vaccine Name 🧪\n👉 Oral Polio Vaccine (OPV) + Injectable Polio Vaccine (IPV)")
#         lines.append("\n2️⃣ Period of Time / Age ⏳\n👉 From birth up to 5 years")
#         lines.append("\n3️⃣ Vaccination Date & Last Date 📅")
#         for period, date, vaccine in schedule:
#             lines.append(f"- {period}: {date.strftime('%d-%b-%Y')} → {vaccine}")
#         lines.append("\n4️⃣ Disease & Symptoms ⚠️\n👉 Polio causes fever 🤒, weakness 😴, headache 🤕, vomiting 🤮, stiffness 🧍‍♂️, paralysis 🚶‍♂️❌")
#         lines.append("\n5️⃣ About the Vaccine ℹ️\n👉 OPV (oral drops) 👅, IPV (injection) 💉, free under Govt.")
#         lines.append("\n6️⃣ Purpose 🎯\n👉 Prevents life-long paralysis & disability.")
#         lines.append("\n7️⃣ Gender 👦👧\n👉 For all children.")
#         lines.append("\n8️⃣ Where to Get 🏥\n👉 Govt hospitals, PHCs, Anganwadis, ASHA workers.")
#         lines.append("\n9️⃣ Side Effects ⚠️\n👉 Safe 👍; rarely mild fever. Consult doctor if severe 🚑")
#         lines.append("\n🔟 After Vaccination ✅\n👉 Feed normally 🍼, stay 30 mins at centre, don’t skip future doses.")
#         lines.append(f"\n1️⃣1️⃣ Next Dose Reminder ⏰\n👉 Next after birth dose: {schedule[1][1].strftime('%d-%b-%Y')} (OPV-1 + IPV-1)")
#         lines.append("\n1️⃣2️⃣ Pulse Polio Campaign 📢\n👉 Even if vaccinated, attend Pulse Polio days.")

#         response_text = "\n".join(lines)

#     # ✅ Translate back if needed
#     response_text = translate_from_english(response_text, user_lang)

#     return jsonify({"fulfillmentText": response_text})


# from flask import Flask, request, jsonify
# import requests
# from bs4 import BeautifulSoup
# from langdetect import detect, DetectorFactory
# import datetime

# app = Flask(__name__)

# # -------------------
# # Setup
# # -------------------
# DetectorFactory.seed = 0  # makes langdetect deterministic

# # List of Indian language codes
# INDIAN_LANGUAGES = [
#     "hi", "te", "ta", "kn", "bn", "mr", "gu", "ml", "ur", "pa", "or", "ks"
# ]

# # -------- Dynamic slugs source --------
# SLUGS_URL = "https://raw.githubusercontent.com/INFINITE347/General_Health_stats/main/slugs.json"

# def load_slugs():
#     try:
#         resp = requests.get(SLUGS_URL, timeout=10)
#         resp.raise_for_status()
#         return resp.json()
#     except Exception as e:
#         print(f"Error loading slugs.json: {e}")
#         return {}

# def get_slug(disease_param):
#     slugs = load_slugs()
#     key = disease_param.strip().lower()
#     return slugs.get(key)

# # -------------------
# # Translation helpers
# # -------------------
# def translate_to_english(disease_param, detected_lang):
#     if not disease_param.strip():
#         return disease_param
#     if detected_lang not in INDIAN_LANGUAGES:
#         return disease_param
#     try:
#         url = f"https://api.mymemory.translated.net/get?q={disease_param}&langpair={detected_lang}|en"
#         response = requests.get(url, timeout=10)
#         data = response.json()
#         translated = data.get("responseData", {}).get("translatedText")
#         return translated if translated else disease_param
#     except Exception as e:
#         print(f"MyMemory translation error: {e}")
#         return disease_param

# def translate_from_english(text, target_lang):
#     if target_lang not in INDIAN_LANGUAGES or not text.strip():
#         return text
#     try:
#         url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|{target_lang}"
#         response = requests.get(url, timeout=10)
#         data = response.json()
#         translated = data.get("responseData", {}).get("translatedText")
#         return translated if translated else text
#     except Exception as e:
#         print(f"MyMemory translation back error: {e}")
#         return text

# # -------------------
# # WHO scraping helpers
# # -------------------
# def fetch_overview(url):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")
#         heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "overview" in tag.get_text(strip=True).lower())
#         if not heading: return None
#         paragraphs = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2","h3"]: break
#             if sibling.name == "p":
#                 txt = sibling.get_text(strip=True)
#                 if txt: paragraphs.append(txt)
#         if not paragraphs: return None
#         text = " ".join(paragraphs)
#         # Extract 5 key sentences (max 490 chars)
#         points = []
#         for sentence in text.split(". "):
#             if sentence.strip():
#                 points.append(f"📌 {sentence.strip()}")
#             if len(" ".join(points)) > 490 or len(points) >= 5:
#                 break
#         return "\n".join(points)
#     except Exception:
#         return None

# def fetch_symptoms(url, disease_name):
#     try:
#         r = requests.get(url, timeout=10); r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")
#         heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "symptoms" in tag.get_text(strip=True).lower())
#         if not heading: return None
#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2","h3"]: break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt: points.append(f"🔹 {txt}")
#         if not points:
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2","h3"]: break
#                 if sibling.name == "p":
#                     txt = sibling.get_text(strip=True)
#                     if txt: points.append(f"🔹 {txt}")
#         return f"Symptoms for {disease_name.capitalize()}:\n" + "\n".join(points) if points else None
#     except Exception:
#         return None

# def fetch_treatment(url, disease_name):
#     try:
#         r = requests.get(url, timeout=10); r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")
#         heading = soup.find(lambda tag: tag.name in ["h2","h3"] and ("treatment" in tag.get_text(strip=True).lower() or "management" in tag.get_text(strip=True).lower()))
#         if not heading: return None
#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2","h3"]: break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt: points.append(f"💊 {txt}")
#         if not points:
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2","h3"]: break
#                 if sibling.name == "p":
#                     txt = sibling.get_text(strip=True)
#                     if txt: points.append(f"💊 {txt}")
#         return f"Treatment for {disease_name.capitalize()}:\n" + "\n".join(points) if points else None
#     except Exception:
#         return None

# def fetch_prevention(url, disease_name):
#     try:
#         r = requests.get(url, timeout=10); r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")
#         heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "prevention" in tag.get_text(strip=True).lower())
#         if not heading: return None
#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2","h3"]: break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt: points.append(f"🛡️ {txt}")
#         if not points:
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2","h3"]: break
#                 if sibling.name == "p":
#                     txt = sibling.get_text(strip=True)
#                     if txt: points.append(f"🛡️ {txt}")
#         return f"Prevention for {disease_name.capitalize()}:\n" + "\n".join(points) if points else None
#     except Exception:
#         return None

# # ---------- WHO Outbreak API ----------
# WHO_API_URL = (
#     "https://www.who.int/api/emergencies/diseaseoutbreaknews"
#     "?sf_provider=dynamicProvider372&sf_culture=en"
#     "&$orderby=PublicationDateAndTime%20desc"
#     "&$expand=EmergencyEvent"
#     "&$select=Title,TitleSuffix,OverrideTitle,UseOverrideTitle,regionscountries,"
#     "ItemDefaultUrl,FormattedDate,PublicationDateAndTime"
#     "&%24format=json&%24top=10&%24count=true"
# )

# def get_who_outbreak_data():
#     try:
#         response = requests.get(WHO_API_URL, timeout=10)
#         response.raise_for_status()
#         data = response.json()
#         if "value" not in data or not data["value"]: return None
#         outbreaks = []
#         for item in data["value"][:5]:
#             title = item.get("OverrideTitle") or item.get("Title")
#             date = item.get("FormattedDate", "Unknown date")
#             url = "https://www.who.int" + item.get("ItemDefaultUrl", "")
#             outbreaks.append(f"🦠 {title} ({date})\n🔗 {url}")
#         return outbreaks
#     except Exception:
#         return None

# # -------------------
# # Polio Schedule Builder
# # -------------------
# VACC_EMOJIS = ["💉","🕒","📅","⚠️","ℹ️","🎯","👶","🏥","⚕️","✅","⏰","📢"]

# def build_polio_schedule(birth_date):
#     schedule = []
#     schedule.append(("At Birth (within 15 days)", birth_date, "OPV-0"))
#     schedule.append(("6 Weeks", birth_date + datetime.timedelta(weeks=6), "OPV-1 + IPV-1"))
#     schedule.append(("10 Weeks", birth_date + datetime.timedelta(weeks=10), "OPV-2"))
#     schedule.append(("14 Weeks", birth_date + datetime.timedelta(weeks=14), "OPV-3 + IPV-2"))
#     schedule.append(("16–24 Months", birth_date + datetime.timedelta(weeks=72), "OPV + IPV Boosters"))
#     schedule.append(("5 Years", birth_date + datetime.timedelta(weeks=260), "OPV Booster"))
#     return schedule

# # -------- Flask webhook route --------
# @app.route('/webhook', methods=['POST'])
# def webhook():
#     req = request.get_json()
#     intent_name = req["queryResult"]["intent"]["displayName"]
#     params = req["queryResult"].get("parameters", {})
#     disease_input = params.get("disease", "").strip()
#     date_str = params.get("date", "")

#     # Detect language
#     try:
#         detected_lang = detect(disease_input) if disease_input else "en"
#     except Exception:
#         detected_lang = "en"

#     translated = translate_to_english(disease_input, detected_lang) or ""
#     disease_param = translated.strip().lower()
#     user_lang = detected_lang if detected_lang in INDIAN_LANGUAGES else "en"

#     response_text = "Sorry, I don't understand your request."

#     # ----- Intents -----
#     if intent_name == "get_disease_overview":
#         slug = get_slug(disease_param)
#         if slug:
#             url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#             overview = fetch_overview(url)
#             response_text = overview or f"Overview not found for {disease_param.capitalize()}. Read more here: {url}"
#         else:
#             response_text = f"Disease not found. Make sure to use a valid disease name."

#     elif intent_name == "get_symptoms":
#         slug = get_slug(disease_param)
#         if slug:
#             url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#             response_text = fetch_symptoms(url, disease_param) or f"Symptoms not found for {disease_param.capitalize()}"
#         else:
#             response_text = f"Sorry, I don't have a URL for {disease_param.capitalize()}."

#     elif intent_name == "get_treatment":
#         slug = get_slug(disease_param)
#         if slug:
#             url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#             response_text = fetch_treatment(url, disease_param) or f"Treatment not found for {disease_param.capitalize()}"
#         else:
#             response_text = f"Sorry, I don't have a URL for {disease_param.capitalize()}."

#     elif intent_name == "get_prevention":
#         slug = get_slug(disease_param)
#         if slug:
#             url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#             response_text = fetch_prevention(url, disease_param) or f"Prevention not found for {disease_param.capitalize()}"
#         else:
#             response_text = f"Sorry, I don't have a URL for {disease_param.capitalize()}."

#     elif intent_name == "disease_outbreak.general":
#         outbreaks = get_who_outbreak_data()
#         response_text = "⚠️ Unable to fetch outbreak data." if not outbreaks else "🦠 Latest WHO Outbreak News:\n\n" + "\n\n".join(outbreaks)

#     elif intent_name == "get_vaccine":
#         if date_str:
#             try:
#                 birth_date = datetime.datetime.strptime(date_str.split("T")[0], "%Y-%m-%d").date()
#             except Exception:
#                 birth_date = datetime.date.today()
#         else:
#             birth_date = datetime.date.today()

#         schedule = build_polio_schedule(birth_date)
#         lines = ["💉 POLIO VACCINATION SCHEDULE"]
#         for idx, (period, date, vaccine) in enumerate(schedule):
#             emoji = VACC_EMOJIS[idx]
#             lines.append(f"{emoji} {period}: {date.strftime('%d-%b-%Y')} → {vaccine}")
#         # Additional info
#         extra_steps = [
#             ("⚠️", "Disease & Symptoms: Polio causes fever, weakness, headache, vomiting, stiffness, paralysis"),
#             ("ℹ️", "About the Vaccine: OPV (oral drops), IPV (injection), free under Govt."),
#             ("🎯", "Purpose: Prevents life-long paralysis & disability"),
#             ("👶", "Gender: For all children"),
#             ("🏥", "Where to Get: Govt hospitals, PHCs, Anganwadis, ASHA workers"),
#             ("⚕️", "Side Effects: Safe; rarely mild fever. Consult doctor if severe"),
#             ("✅", "After Vaccination: Feed normally, stay 30 mins at centre, don’t skip future doses"),
#             ("⏰", f"Next Dose Reminder: Next after birth dose: {schedule[1][1].strftime('%d-%b-%Y')} ({schedule[1][2]})"),
#             ("📢", "Pulse Polio Campaign: Even if vaccinated, attend Pulse Polio days")
#         ]
#         for emoji, text in extra_steps:
#             lines.append(f"{emoji} {text}")
#         response_text = "\n".join(lines)

#     # Translate back if needed
#     response_text = translate_from_english(response_text, user_lang)
#     return jsonify({"fulfillmentText": response_text})

# # -------------------
# # Run Flask
# # -------------------
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)


# from flask import Flask, request, jsonify
# import requests
# from bs4 import BeautifulSoup
# from langdetect import detect, DetectorFactory
# import datetime

# app = Flask(__name__)

# # -------------------
# # Setup
# # -------------------
# DetectorFactory.seed = 0  # makes langdetect deterministic

# # List of Indian language codes
# INDIAN_LANGUAGES = [
#     "hi", "te", "ta", "kn", "bn", "mr", "gu", "ml", "ur", "pa", "or", "ks"
# ]

# # -------- Dynamic slugs source --------
# SLUGS_URL = "https://raw.githubusercontent.com/INFINITE347/General_Health_stats/main/slugs.json"

# def load_slugs():
#     try:
#         resp = requests.get(SLUGS_URL, timeout=10)
#         resp.raise_for_status()
#         return resp.json()
#     except Exception as e:
#         print(f"Error loading slugs.json: {e}")
#         return {}

# def get_slug(disease_param):
#     slugs = load_slugs()
#     key = disease_param.strip().lower()
#     return slugs.get(key)

# # -------------------
# # Translation helpers
# # -------------------
# def translate_to_english(disease_param, detected_lang):
#     if not disease_param.strip():
#         return disease_param
#     if detected_lang not in INDIAN_LANGUAGES:
#         return disease_param
#     try:
#         url = f"https://api.mymemory.translated.net/get?q={disease_param}&langpair={detected_lang}|en"
#         response = requests.get(url, timeout=10)
#         data = response.json()
#         translated = data.get("responseData", {}).get("translatedText")
#         return translated if translated else disease_param
#     except Exception as e:
#         print(f"MyMemory translation error: {e}")
#         return disease_param

# def translate_from_english(text, target_lang):
#     if target_lang not in INDIAN_LANGUAGES or not text.strip():
#         return text
#     try:
#         url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|{target_lang}"
#         response = requests.get(url, timeout=10)
#         data = response.json()
#         translated = data.get("responseData", {}).get("translatedText")
#         return translated if translated else text
#     except Exception as e:
#         print(f"MyMemory translation back error: {e}")
#         return text

# # -------------------
# # WHO scraping helpers
# # -------------------
# def fetch_overview(url):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")
#         heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "overview" in tag.get_text(strip=True).lower())
#         if not heading: return None
#         paragraphs = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2","h3"]: break
#             if sibling.name == "p":
#                 txt = sibling.get_text(strip=True)
#                 if txt: paragraphs.append(txt)
#         if not paragraphs: return None
#         text = " ".join(paragraphs)
#         # Extract 5 key sentences (max 490 chars)
#         points = []
#         for sentence in text.split(". "):
#             if sentence.strip():
#                 points.append(f"📌 {sentence.strip()}")
#             if len(" ".join(points)) > 490 or len(points) >= 5:
#                 break
#         return "\n".join(points)
#     except Exception:
#         return None

# def fetch_symptoms(url, disease_name):
#     try:
#         r = requests.get(url, timeout=10); r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")
#         heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "symptoms" in tag.get_text(strip=True).lower())
#         if not heading: return None
#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2","h3"]: break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt: points.append(f"🔹 {txt}")
#         if not points:
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2","h3"]: break
#                 if sibling.name == "p":
#                     txt = sibling.get_text(strip=True)
#                     if txt: points.append(f"🔹 {txt}")
#         return f"Symptoms for {disease_name.capitalize()}:\n" + "\n".join(points) if points else None
#     except Exception:
#         return None

# def fetch_treatment(url, disease_name):
#     try:
#         r = requests.get(url, timeout=10); r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")
#         heading = soup.find(lambda tag: tag.name in ["h2","h3"] and ("treatment" in tag.get_text(strip=True).lower() or "management" in tag.get_text(strip=True).lower()))
#         if not heading: return None
#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2","h3"]: break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt: points.append(f"💊 {txt}")
#         if not points:
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2","h3"]: break
#                 if sibling.name == "p":
#                     txt = sibling.get_text(strip=True)
#                     if txt: points.append(f"💊 {txt}")
#         return f"Treatment for {disease_name.capitalize()}:\n" + "\n".join(points) if points else None
#     except Exception:
#         return None

# def fetch_prevention(url, disease_name):
#     try:
#         r = requests.get(url, timeout=10); r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")
#         heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "prevention" in tag.get_text(strip=True).lower())
#         if not heading: return None
#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2","h3"]: break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt: points.append(f"🛡️ {txt}")
#         if not points:
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2","h3"]: break
#                 if sibling.name == "p":
#                     txt = sibling.get_text(strip=True)
#                     if txt: points.append(f"🛡️ {txt}")
#         return f"Prevention for {disease_name.capitalize()}:\n" + "\n".join(points) if points else None
#     except Exception:
#         return None

# # ---------- WHO Outbreak API ----------
# WHO_API_URL = (
#     "https://www.who.int/api/emergencies/diseaseoutbreaknews"
#     "?sf_provider=dynamicProvider372&sf_culture=en"
#     "&$orderby=PublicationDateAndTime%20desc"
#     "&$expand=EmergencyEvent"
#     "&$select=Title,TitleSuffix,OverrideTitle,UseOverrideTitle,regionscountries,"
#     "ItemDefaultUrl,FormattedDate,PublicationDateAndTime"
#     "&%24format=json&%24top=10&%24count=true"
# )

# def get_who_outbreak_data():
#     try:
#         response = requests.get(WHO_API_URL, timeout=10)
#         response.raise_for_status()
#         data = response.json()
#         if "value" not in data or not data["value"]: return None
#         outbreaks = []
#         for item in data["value"][:5]:
#             title = item.get("OverrideTitle") or item.get("Title")
#             date = item.get("FormattedDate", "Unknown date")
#             url = "https://www.who.int" + item.get("ItemDefaultUrl", "")
#             outbreaks.append(f"🦠 {title} ({date})\n")
#         return outbreaks
#     except Exception:
#         return None

# # -------------------
# # Polio Schedule Builder
# # -------------------
# VACC_EMOJIS = ["💉","🕒","📅","⚠️","ℹ️","🎯","👶","🏥","⚕️","✅","⏰","📢"]

# def build_polio_schedule(birth_date):
#     schedule = []
#     schedule.append(("At Birth (within 15 days)", birth_date, "OPV-0"))
#     schedule.append(("6 Weeks", birth_date + datetime.timedelta(weeks=6), "OPV-1 + IPV-1"))
#     schedule.append(("10 Weeks", birth_date + datetime.timedelta(weeks=10), "OPV-2"))
#     schedule.append(("14 Weeks", birth_date + datetime.timedelta(weeks=14), "OPV-3 + IPV-2"))
#     schedule.append(("16–24 Months", birth_date + datetime.timedelta(weeks=72), "OPV + IPV Boosters"))
#     schedule.append(("5 Years", birth_date + datetime.timedelta(weeks=260), "OPV Booster"))
#     return schedule

# # -------- Flask webhook route --------
# @app.route('/webhook', methods=['POST'])
# def webhook():
#     req = request.get_json()
#     intent_name = req["queryResult"]["intent"]["displayName"]
#     params = req["queryResult"].get("parameters", {})
#     # disease_input = params.get("disease", "").strip()
#     date_str = params.get("date", "")

#     # params = req["queryResult"].get("parameters", {})
#     disease_input = params.get("disease", "").strip()

#     # fallback to @sys.any if disease is not given
#     if not disease_input:
#         disease_input = params.get("any", "").strip()


#     # Detect language
#     try:
#         detected_lang = detect(disease_input) if disease_input else "en"
#     except Exception:
#         detected_lang = "en"

#     translated = translate_to_english(disease_input, detected_lang) or ""
#     disease_param = translated.strip().lower()
#     user_lang = detected_lang if detected_lang in INDIAN_LANGUAGES else "en"

#     response_text = "Sorry, I don't understand your request."

#     # ----- Intents -----
#     if intent_name == "get_disease_overview":
#         response_text = "📖 DISEASE OVERVIEW\n\n"
#         slug = get_slug(disease_param)
#         if slug:
#             url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#             overview = fetch_overview(url)
#             response_text += overview or f"Overview not found for {disease_param.capitalize()}. Read more here: {url}"
#         else:
#             response_text += "Disease not found. Make sure to use a valid disease name."

#     elif intent_name == "get_symptoms":
#         response_text = "🤒 SYMPTOMS\n\n"
#         slug = get_slug(disease_param)
#         if slug:
#             url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#             response_text += fetch_symptoms(url, disease_param) or f"Symptoms not found for {disease_param.capitalize()}"
#         else:
#             response_text += f"Sorry, I don't have a URL for {disease_param.capitalize()}."

#     elif intent_name == "get_treatment":
#         response_text = "💊 TREATMENT\n\n"
#         slug = get_slug(disease_param)
#         if slug:
#             url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#             response_text += fetch_treatment(url, disease_param) or f"Treatment not found for {disease_param.capitalize()}"
#         else:
#             response_text += f"Sorry, I don't have a URL for {disease_param.capitalize()}."

#     elif intent_name == "get_prevention":
#         response_text = "🛡️ PREVENTION\n\n"
#         slug = get_slug(disease_param)
#         if slug:
#             url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#             response_text += fetch_prevention(url, disease_param) or f"Prevention not found for {disease_param.capitalize()}"
#         else:
#             response_text += f"Sorry, I don't have a URL for {disease_param.capitalize()}."

#     elif intent_name == "disease_outbreak.general":
#         response_text = "🌍 LATEST OUTBREAK NEWS\n\n"
#         outbreaks = get_who_outbreak_data()
#         response_text += "⚠️ Unable to fetch outbreak data." if not outbreaks else "🦠 Latest WHO Outbreak News:\n\n" + "\n\n".join(outbreaks)

#     elif intent_name == "get_vaccine":
#         response_text = "💉 POLIO VACCINATION SCHEDULE\n\n"
#         if date_str:
#             try:
#                 birth_date = datetime.datetime.strptime(date_str.split("T")[0], "%Y-%m-%d").date()
#             except Exception:
#                 birth_date = datetime.date.today()
#         else:
#             birth_date = datetime.date.today()

#         schedule = build_polio_schedule(birth_date)
#         lines = []
#         for idx, (period, date, vaccine) in enumerate(schedule):
#             emoji = VACC_EMOJIS[idx]
#             lines.append(f"{emoji} {period}: {date.strftime('%d-%b-%Y')} → {vaccine}")
#         # Additional info
#         extra_steps = [
#             ("⚠️", "Disease & Symptoms: Polio causes fever, weakness, headache, vomiting, stiffness, paralysis"),
#             ("ℹ️", "About the Vaccine: OPV (oral drops), IPV (injection), free under Govt."),
#             ("🎯", "Purpose: Prevents life-long paralysis & disability"),
#             ("👶", "Gender: For all children"),
#             ("🏥", "Where to Get: Govt hospitals, PHCs, Anganwadis, ASHA workers"),
#             ("⚕️", "Side Effects: Safe; rarely mild fever. Consult doctor if severe"),
#             ("✅", "After Vaccination: Feed normally, stay 30 mins at centre, don’t skip future doses"),
#             ("⏰", f"Next Dose Reminder: Next after birth dose: {schedule[1][1].strftime('%d-%b-%Y')} ({schedule[1][2]})"),
#             ("📢", "Pulse Polio Campaign: Even if vaccinated, attend Pulse Polio days")
#         ]
#         for emoji, text in extra_steps:
#             lines.append(f"{emoji} {text}")
#         response_text += "\n".join(lines)

#     elif intent_name == "Default Fallback Intent":
#         response_text = "🤔 Sorry, I couldn't understand that. Please provide a disease name or try rephrasing your question."

#     # Translate back if needed
#     response_text = translate_from_english(response_text, user_lang)
#     return jsonify({"fulfillmentText": response_text})

# # -------------------
# # Run Flask
# # -------------------
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)














from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory
import datetime

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
        # Extract 5 key sentences (max 490 chars)
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

# -------- Flask webhook route --------
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent_name = req["queryResult"]["intent"]["displayName"]
    params = req["queryResult"].get("parameters", {})
    date_str = params.get("date", "")

    disease_input = params.get("disease", "").strip()

    # fallback to @sys.any if disease is not given
    if not disease_input:
        disease_input = params.get("any", "").strip()

    # Detect language
    try:
        detected_lang = detect(disease_input) if disease_input else "en"
    except Exception:
        detected_lang = "en"

    translated = translate_to_english(disease_input, detected_lang) or ""
    disease_param = translated.strip().lower()
    user_lang = detected_lang if detected_lang in INDIAN_LANGUAGES else "en"

    response_text = "Sorry, I don't understand your request."

    # ----- Intents -----
    if intent_name == "get_disease_overview":
        response_text = "📖 DISEASE OVERVIEW\n\n"
        slug = get_slug(disease_param)
        if slug:
            url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
            overview = fetch_overview(url)
            response_text += overview or f"Overview not found for {disease_param.capitalize()}. Read more here: {url}"
        else:
            response_text += "Disease not found. Make sure to use a valid disease name."

    elif intent_name == "get_symptoms":
        response_text = "🤒 SYMPTOMS\n\n"
        slug = get_slug(disease_param)
        if slug:
            url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
            response_text += fetch_symptoms(url, disease_param) or f"Symptoms not found for {disease_param.capitalize()}"
        else:
            response_text += f"Sorry, I don't have a URL for {disease_param.capitalize()}."

    elif intent_name == "get_treatment":
        response_text = "💊 TREATMENT\n\n"
        slug = get_slug(disease_param)
        if slug:
            url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
            response_text += fetch_treatment(url, disease_param) or f"Treatment not found for {disease_param.capitalize()}"
        else:
            response_text += f"Sorry, I don't have a URL for {disease_param.capitalize()}."

    elif intent_name == "get_prevention":
        response_text = "🛡️ PREVENTION\n\n"
        slug = get_slug(disease_param)
        if slug:
            url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
            response_text += fetch_prevention(url, disease_param) or f"Prevention not found for {disease_param.capitalize()}"
        else:
            response_text += f"Sorry, I don't have a URL for {disease_param.capitalize()}."

    elif intent_name == "disease_outbreak.general":
        # take "any" param as updates input
        updates_input = params.get("any", "").strip()
        try:
            updates_lang = detect(updates_input) if updates_input else "en"
        except Exception:
            updates_lang = "en"

        response_text = "🌍 LATEST OUTBREAK NEWS\n\n"
        outbreaks = get_who_outbreak_data()
        if not outbreaks:
            response_text += "⚠️ Unable to fetch outbreak data."
        else:
            response_text += "🦠 Latest WHO Outbreak News:\n\n" + "\n\n".join(outbreaks)

        # Translate back to local language
        response_text = translate_from_english(response_text, updates_lang)

    elif intent_name == "get_vaccine":
        response_text = "💉 POLIO VACCINATION SCHEDULE\n\n"
        if date_str:
            try:
                birth_date = datetime.datetime.strptime(date_str.split("T")[0], "%Y-%m-%d").date()
            except Exception:
                birth_date = datetime.date.today()
        else:
            birth_date = datetime.date.today()

        schedule = build_polio_schedule(birth_date)
        lines = []
        for idx, (period, date, vaccine) in enumerate(schedule):
            emoji = VACC_EMOJIS[idx]
            lines.append(f"{emoji} {period}: {date.strftime('%d-%b-%Y')} → {vaccine}")
        # Additional info
        extra_steps = [
            ("⚠️", "Disease & Symptoms: Polio causes fever, weakness, headache, vomiting, stiffness, paralysis"),
            ("ℹ️", "About the Vaccine: OPV (oral drops), IPV (injection), free under Govt."),
            ("🎯", "Purpose: Prevents life-long paralysis & disability"),
            ("👶", "Gender: For all children"),
            ("🏥", "Where to Get: Govt hospitals, PHCs, Anganwadis, ASHA workers"),
            ("⚕️", "Side Effects: Safe; rarely mild fever. Consult doctor if severe"),
            ("✅", "After Vaccination: Feed normally, stay 30 mins at centre, don’t skip future doses"),
            ("⏰", f"Next Dose Reminder: Next after birth dose: {schedule[1][1].strftime('%d-%b-%Y')} ({schedule[1][2]})"),
            ("📢", "Pulse Polio Campaign: Even if vaccinated, attend Pulse Polio days")
        ]
        for emoji, text in extra_steps:
            lines.append(f"{emoji} {text}")
        response_text += "\n".join(lines)

    elif intent_name == "Default Fallback Intent":
        response_text = "🤔 Sorry, I couldn't understand that. Please provide a disease name or try rephrasing your question."

    # Translate back if needed
    response_text = translate_from_english(response_text, user_lang)
    return jsonify({"fulfillmentText": response_text})

# -------------------
# Run Flask
# -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
