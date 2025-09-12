# from flask import Flask, request, jsonify
# import requests
# from bs4 import BeautifulSoup
# from langdetect import detect, DetectorFactory
# import datetime
# from psycopg2.extras import Json
# import psycopg2
# import os

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

# # -------------------
# # Helper for safe truncation
# # -------------------
# def truncate_response(text, limit=480):
#     if not text:
#         return text
#     if len(text) <= limit:
#         return text
#     truncated = text[:limit]
#     if "." in truncated:
#         truncated = truncated.rsplit(".", 1)[0] + "."
#     return truncated

# # -------------------
# # WHO scraping helpers
# # -------------------
# def fetch_overview(url, disease_name=""):
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
#         final_text = f"📖 Overview of {disease_name.capitalize()}:\n\n{text}"
#         return truncate_response(final_text, 480)
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
#         final_text = f"🤒 Symptoms of {disease_name.capitalize()}:\n\n" + "\n".join(points) if points else None
#         return truncate_response(final_text, 480) if final_text else None
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
#         final_text = f"💊 Treatment of {disease_name.capitalize()}:\n\n" + "\n".join(points) if points else None
#         return truncate_response(final_text, 480) if final_text else None
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
#         final_text = f"🛡️ Prevention of {disease_name.capitalize()}:\n\n" + "\n".join(points) if points else None
#         return truncate_response(final_text, 480) if final_text else None
#     except Exception:
#         return None


# # def fetch_overview(url):
# #     try:
# #         r = requests.get(url, timeout=10)
# #         r.raise_for_status()
# #         soup = BeautifulSoup(r.text, "html.parser")
# #         heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "overview" in tag.get_text(strip=True).lower())
# #         if not heading: return None
# #         paragraphs = []
# #         for sibling in heading.find_next_siblings():
# #             if sibling.name in ["h2","h3"]: break
# #             if sibling.name == "p":
# #                 txt = sibling.get_text(strip=True)
# #                 if txt: paragraphs.append(txt)
# #         if not paragraphs: return None
# #         text = " ".join(paragraphs)
# #         # Extract 5 key sentences (max 490 chars)
# #         points = []
# #         for sentence in text.split(". "):
# #             if sentence.strip():
# #                 points.append(f"📌 {sentence.strip()}")
# #             if len(" ".join(points)) > 490 or len(points) >= 5:
# #                 break
# #         return "\n".join(points)
# #     except Exception:
# #         return None

# # def fetch_symptoms(url, disease_name):
# #     try:
# #         r = requests.get(url, timeout=10); r.raise_for_status()
# #         soup = BeautifulSoup(r.text, "html.parser")
# #         heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "symptoms" in tag.get_text(strip=True).lower())
# #         if not heading: return None
# #         points = []
# #         for sibling in heading.find_next_siblings():
# #             if sibling.name in ["h2","h3"]: break
# #             if sibling.name == "ul":
# #                 for li in sibling.find_all("li"):
# #                     txt = li.get_text(strip=True)
# #                     if txt: points.append(f"🔹 {txt}")
# #         if not points:
# #             for sibling in heading.find_next_siblings():
# #                 if sibling.name in ["h2","h3"]: break
# #                 if sibling.name == "p":
# #                     txt = sibling.get_text(strip=True)
# #                     if txt: points.append(f"🔹 {txt}")
# #         return f"Symptoms for {disease_name.capitalize()}:\n\n" + "\n\n".join(points) if points else None
# #     except Exception:
# #         return None

# # def fetch_treatment(url, disease_name):
# #     try:
# #         r = requests.get(url, timeout=10); r.raise_for_status()
# #         soup = BeautifulSoup(r.text, "html.parser")
# #         heading = soup.find(lambda tag: tag.name in ["h2","h3"] and ("treatment" in tag.get_text(strip=True).lower() or "management" in tag.get_text(strip=True).lower()))
# #         if not heading: return None
# #         points = []
# #         for sibling in heading.find_next_siblings():
# #             if sibling.name in ["h2","h3"]: break
# #             if sibling.name == "ul":
# #                 for li in sibling.find_all("li"):
# #                     txt = li.get_text(strip=True)
# #                     if txt: points.append(f"💊 {txt}")
# #         if not points:
# #             for sibling in heading.find_next_siblings():
# #                 if sibling.name in ["h2","h3"]: break
# #                 if sibling.name == "p":
# #                     txt = sibling.get_text(strip=True)
# #                     if txt: points.append(f"💊 {txt}")
# #         return f"Treatment for {disease_name.capitalize()}:\n\n" + "\n\n".join(points) if points else None
# #     except Exception:
# #         return None

# # def fetch_prevention(url, disease_name):
# #     try:
# #         r = requests.get(url, timeout=10); r.raise_for_status()
# #         soup = BeautifulSoup(r.text, "html.parser")
# #         heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "prevention" in tag.get_text(strip=True).lower())
# #         if not heading: return None
# #         points = []
# #         for sibling in heading.find_next_siblings():
# #             if sibling.name in ["h2","h3"]: break
# #             if sibling.name == "ul":
# #                 for li in sibling.find_all("li"):
# #                     txt = li.get_text(strip=True)
# #                     if txt: points.append(f"🛡️ {txt}")
# #         if not points:
# #             for sibling in heading.find_next_siblings():
# #                 if sibling.name in ["h2","h3"]: break
# #                 if sibling.name == "p":
# #                     txt = sibling.get_text(strip=True)
# #                     if txt: points.append(f"🛡️ {txt}")
# #         return f"Prevention for {disease_name.capitalize()}:\n\n" + "\n\n".join(points) if points else None
# #     except Exception:
# #         return None

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
#             outbreaks.append(f"🦠 {title} ({date})")
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

# # -------------------
# # PostgreSQL Memory Setup
# # -------------------
# DATABASE_URL = os.environ.get("DATABASE_URL")
# conn = psycopg2.connect(DATABASE_URL)

# def create_users_table():
#     try:
#         cur = conn.cursor()
#         cur.execute("""
#             CREATE TABLE IF NOT EXISTS users (
#                 user_id TEXT PRIMARY KEY,
#                 context JSONB NOT NULL DEFAULT '{}'::jsonb,
#                 last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             );
#         """)
#         conn.commit()
#         cur.close()
#         print("✅ users table is ready")
#     except Exception as e:
#         print(f"Error creating users table: {e}")

# create_users_table()

# def get_user_memory(user_id):
#     cur = conn.cursor()
#     cur.execute("SELECT context FROM users WHERE user_id = %s", (user_id,))
#     row = cur.fetchone()
#     cur.close()
#     return row[0] if row else {}

# def save_user_memory(user_id, context):
#     cur = conn.cursor()
#     cur.execute("""
#         INSERT INTO users (user_id, context, last_updated)
#         VALUES (%s, %s, NOW())
#         ON CONFLICT (user_id) 
#         DO UPDATE SET context = EXCLUDED.context, last_updated = NOW()
#     """, (user_id, Json(context)))
#     conn.commit()
#     cur.close()

# # -------- Flask webhook route --------
# @app.route('/webhook', methods=['POST'])
# def webhook():
#     req = request.get_json()
#     user_id = req.get("originalDetectIntentRequest", {}).get("payload", {}).get("user", {}).get("userId") \
#               or req.get("session")
#     intent_name = req["queryResult"]["intent"]["displayName"]
#     params = req["queryResult"].get("parameters", {})
#     date_str = params.get("date", "")
#     disease_input = params.get("disease", "").strip() or params.get("any", "").strip()

#     # Fetch previous memory
#     memory = get_user_memory(user_id)
#     if "last_disease" not in memory:
#         memory["last_disease"] = ""
#     if "user_lang" not in memory:
#         memory["user_lang"] = "en"
#     if "last_queries" not in memory:
#         memory["last_queries"] = []

#     # Detect language
#     try:
#         detected_lang = detect(disease_input) if disease_input else memory.get("user_lang", "en")
#     except Exception:
#         detected_lang = memory.get("user_lang", "en")

#     translated = translate_to_english(disease_input, detected_lang) if disease_input else memory.get("last_disease", "")
#     disease_param = translated.strip().lower()
#     user_lang = detected_lang if detected_lang in INDIAN_LANGUAGES else "en"

#     # Update memory
#     if disease_param:
#         memory["last_disease"] = disease_param
#     memory["user_lang"] = user_lang

#     # Keep last 5 queries
#     memory["last_queries"].append({"intent": intent_name, "disease": disease_param, "timestamp": str(datetime.datetime.now())})
#     memory["last_queries"] = memory["last_queries"][-5:]

#     response_text = "Sorry, I don't understand your request."

#     # ----- Existing intent handling -----
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
#         updates_input = params.get("any", "").strip()
#         try:
#             updates_lang = detect(updates_input) if updates_input else memory.get("user_lang", "en")
#         except Exception:
#             updates_lang = memory.get("user_lang", "en")

#         response_text = "🌍 LATEST OUTBREAK NEWS\n\n"
#         outbreaks = get_who_outbreak_data()
#         if not outbreaks:
#             response_text += "⚠️ Unable to fetch outbreak data."
#         else:
#             response_text += "🦠 Latest WHO Outbreak News:\n\n" + "\n\n".join(outbreaks)

#         response_text = translate_from_english(response_text, updates_lang)

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

#     # Translate final response to user language
#     response_text = translate_from_english(response_text, user_lang)

#     # Save updated memory
#     save_user_memory(user_id, memory)

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
# from psycopg2.extras import Json
# import psycopg2
# import os
# import traceback

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
#     key = (disease_param or "").strip().lower()
#     return slugs.get(key)

# # -------------------
# # Translation helpers
# # -------------------
# def translate_to_english(disease_param, detected_lang):
#     """Translate incoming user param to English if it's one of the Indian languages."""
#     if not disease_param or not disease_param.strip():
#         return disease_param
#     if detected_lang not in INDIAN_LANGUAGES:
#         return disease_param
#     try:
#         resp = requests.get(
#             "https://api.mymemory.translated.net/get",
#             params={"q": disease_param, "langpair": f"{detected_lang}|en"},
#             timeout=10,
#         )
#         resp.raise_for_status()
#         data = resp.json()
#         translated = data.get("responseData", {}).get("translatedText")
#         return translated if translated else disease_param
#     except Exception as e:
#         print(f"MyMemory translation error (to English): {e}")
#         return disease_param

# def translate_from_english(text, target_lang):
#     """Translate an English response into target_lang if that lang is supported."""
#     if not text or not text.strip():
#         return text
#     if target_lang not in INDIAN_LANGUAGES:
#         return text
#     try:
#         resp = requests.get(
#             "https://api.mymemory.translated.net/get",
#             params={"q": text, "langpair": f"en|{target_lang}"},
#             timeout=10,
#         )
#         resp.raise_for_status()
#         data = resp.json()
#         translated = data.get("responseData", {}).get("translatedText")
#         return translated if translated else text
#     except Exception as e:
#         print(f"MyMemory translation error (from English): {e}")
#         return text

# # -------------------
# # Helper for safe truncation (<= limit chars)
# # -------------------
# def truncate_response(text, limit=500):
#     """
#     Truncate text to <= limit chars, preferring to cut at the last full sentence (last '.') before limit.
#     If no '.' is found, fallback to the last space and add '...'.
#     """
#     if not text:
#         return text
#     if len(text) <= limit:
#         return text
#     head = text[:limit]
#     last_dot = head.rfind('.')
#     if last_dot != -1:
#         # return up to and including the last period
#         return text[: last_dot + 1]
#     # fallback: cut at last space and append ellipsis
#     last_space = head.rfind(' ')
#     if last_space != -1 and last_space > int(limit * 0.3):
#         return head[:last_space] + "..."
#     # as a last-resort hard cut
#     return head

# # -------------------
# # WHO scraping helpers (all return English results)
# # Each returns a heading "Intent of <DiseaseName>:\n\n" + content, truncated to 500 chars
# # -------------------
# def fetch_overview(url, disease_name=""):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")
#         heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "overview" in tag.get_text(strip=True).lower())
#         if not heading:
#             return None
#         paragraphs = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2","h3"]:
#                 break
#             if sibling.name == "p":
#                 txt = sibling.get_text(strip=True)
#                 if txt:
#                     paragraphs.append(txt)
#         if not paragraphs:
#             return None
#         text = " ".join(paragraphs).strip()
#         final_text = f"Intent of {disease_name.capitalize()}:\n\n{text}"
#         return truncate_response(final_text, 500)
#     except Exception:
#         # log for debugging
#         traceback.print_exc()
#         return None

# def fetch_symptoms(url, disease_name):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")
#         heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "symptoms" in tag.get_text(strip=True).lower())
#         if not heading:
#             return None
#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2","h3"]:
#                 break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt:
#                         points.append(f"🔹 {txt}")
#         if not points:
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2","h3"]:
#                     break
#                 if sibling.name == "p":
#                     txt = sibling.get_text(strip=True)
#                     if txt:
#                         points.append(f"🔹 {txt}")
#         if not points:
#             return None
#         body = "\n\n".join(points)
#         final_text = f"Intent of {disease_name.capitalize()}:\n\n{body}"
#         return truncate_response(final_text, 500)
#     except Exception:
#         traceback.print_exc()
#         return None

# def fetch_treatment(url, disease_name):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")
#         heading = soup.find(lambda tag: tag.name in ["h2","h3"] and ("treatment" in tag.get_text(strip=True).lower() or "management" in tag.get_text(strip=True).lower()))
#         if not heading:
#             return None
#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2","h3"]:
#                 break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt:
#                         points.append(f"💊 {txt}")
#         if not points:
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2","h3"]:
#                     break
#                 if sibling.name == "p":
#                     txt = sibling.get_text(strip=True)
#                     if txt:
#                         points.append(f"💊 {txt}")
#         if not points:
#             return None
#         body = "\n\n".join(points)
#         final_text = f"Intent of {disease_name.capitalize()}:\n\n{body}"
#         return truncate_response(final_text, 500)
#     except Exception:
#         traceback.print_exc()
#         return None

# def fetch_prevention(url, disease_name):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")
#         heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "prevention" in tag.get_text(strip=True).lower())
#         if not heading:
#             return None
#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2","h3"]:
#                 break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt:
#                         points.append(f"🛡️ {txt}")
#         if not points:
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2","h3"]:
#                     break
#                 if sibling.name == "p":
#                     txt = sibling.get_text(strip=True)
#                     if txt:
#                         points.append(f"🛡️ {txt}")
#         if not points:
#             return None
#         body = "\n\n".join(points)
#         final_text = f"Intent of {disease_name.capitalize()}:\n\n{body}"
#         return truncate_response(final_text, 500)
#     except Exception:
#         traceback.print_exc()
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
#             outbreaks.append(f"🦠 {title} ({date})")
#         return outbreaks
#     except Exception:
#         traceback.print_exc()
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

# # -------------------
# # PostgreSQL Memory Setup (with in-memory fallback)
# # -------------------
# DATABASE_URL = os.environ.get("DATABASE_URL")
# if not DATABASE_URL:
#     print("⚠️ DATABASE_URL not set. Using in-memory store (non-persistent).")
#     conn = None
#     _in_memory_store = {}
# else:
#     try:
#         conn = psycopg2.connect(DATABASE_URL)
#     except Exception as e:
#         print(f"Error connecting to DATABASE_URL: {e}")
#         conn = None
#         _in_memory_store = {}

# def create_users_table():
#     if not conn:
#         return
#     try:
#         cur = conn.cursor()
#         cur.execute("""
#             CREATE TABLE IF NOT EXISTS users (
#                 user_id TEXT PRIMARY KEY,
#                 context JSONB NOT NULL DEFAULT '{}'::jsonb,
#                 last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             );
#         """)
#         conn.commit()
#         cur.close()
#         print("✅ users table is ready")
#     except Exception as e:
#         print(f"Error creating users table: {e}")

# create_users_table()

# def get_user_memory(user_id):
#     """Return the stored JSON context for the user (or empty dict)."""
#     if not user_id:
#         return {}
#     if not conn:
#         return _in_memory_store.get(user_id, {}).copy()
#     try:
#         cur = conn.cursor()
#         cur.execute("SELECT context FROM users WHERE user_id = %s", (user_id,))
#         row = cur.fetchone()
#         cur.close()
#         return row[0] if row else {}
#     except Exception as e:
#         print(f"DB error on get_user_memory: {e}")
#         return {}

# def save_user_memory(user_id, context):
#     """Save the context JSONB for the user (upsert)."""
#     if not user_id:
#         return
#     if not conn:
#         _in_memory_store[user_id] = context.copy()
#         return
#     try:
#         cur = conn.cursor()
#         cur.execute("""
#             INSERT INTO users (user_id, context, last_updated)
#             VALUES (%s, %s, NOW())
#             ON CONFLICT (user_id)
#             DO UPDATE SET context = EXCLUDED.context, last_updated = NOW()
#         """, (user_id, Json(context)))
#         conn.commit()
#         cur.close()
#     except Exception as e:
#         print(f"DB error on save_user_memory: {e}")

# # -------- Flask webhook route --------
# @app.route('/webhook', methods=['POST'])
# def webhook():
#     req = request.get_json(silent=True)
#     if not req:
#         return jsonify({"fulfillmentText": "Invalid request"}), 400

#     # Identify user (Dialogflow payload userId or session)
#     user_id = req.get("originalDetectIntentRequest", {}).get("payload", {}).get("user", {}).get("userId") \
#               or req.get("session")
#     intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
#     params = req.get("queryResult", {}).get("parameters", {}) or {}
#     date_str = params.get("date", "")
#     # prefer slot 'disease' then fallback to 'any'
#     disease_input = (params.get("disease", "") or "").strip()
#     if not disease_input:
#         disease_input = (params.get("any", "") or "").strip()

#     # Load memory (English stored)
#     memory = get_user_memory(user_id) or {}
#     if "last_disease" not in memory:
#         memory["last_disease"] = ""
#     if "user_lang" not in memory:
#         memory["user_lang"] = "en"
#     if "last_queries" not in memory or not isinstance(memory.get("last_queries"), list):
#         memory["last_queries"] = []

#     # Detect language
#     try:
#         if disease_input:
#             detected_lang = detect(disease_input)
#         else:
#             detected_lang = memory.get("user_lang", "en")
#     except Exception:
#         detected_lang = memory.get("user_lang", "en")

#     # If user provided a param, translate it to English (store in DB). If not, retrieve from memory.
#     if disease_input:
#         translated = translate_to_english(disease_input, detected_lang) or disease_input
#         disease_param = (translated or "").strip().lower()
#         # user_lang should be the original language code (only if it's Indian lang, else 'en')
#         user_lang = detected_lang if detected_lang in INDIAN_LANGUAGES else "en"
#     else:
#         # no param provided -> use last stored disease and language
#         disease_param = memory.get("last_disease", "") or ""
#         user_lang = memory.get("user_lang", "en")

#     # Update memory only in English (store last_disease and user_lang). Always store the fact of the call in last_queries
#     if disease_param:
#         memory["last_disease"] = disease_param
#     memory["user_lang"] = user_lang

#     # Append the current query to last_queries (store English param and user_lang)
#     now_iso = datetime.datetime.utcnow().isoformat()
#     memory.setdefault("last_queries", [])
#     memory["last_queries"].append({
#         "intent": intent_name,
#         "disease": disease_param,
#         "user_lang": user_lang,
#         "timestamp": now_iso
#     })
#     # keep only last 5
#     memory["last_queries"] = memory["last_queries"][-5:]

#     # Build response in English first
#     response_text = "Sorry, I don't understand your request."
#     try:
#         # ----- Intent handling -----
#         if intent_name == "get_disease_overview":
#             response_text = ""
#             if not disease_param:
#                 response_text = "📖 DISEASE OVERVIEW\n\nNo disease provided and no history available."
#             else:
#                 response_text = "📖 DISEASE OVERVIEW\n\n"
#                 slug = get_slug(disease_param)
#                 if slug:
#                     url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#                     overview = fetch_overview(url, disease_param) or None
#                     if overview:
#                         response_text += overview
#                     else:
#                         response_text += f"Overview not found for {disease_param.capitalize()}. Read more here: {url}"
#                 else:
#                     response_text += f"Disease not found. Make sure to use a valid disease name."

#         elif intent_name == "get_symptoms":
#             response_text = ""
#             if not disease_param:
#                 response_text = "🤒 SYMPTOMS\n\nNo disease provided and no history available."
#             else:
#                 response_text = "🤒 SYMPTOMS\n\n"
#                 slug = get_slug(disease_param)
#                 if slug:
#                     url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#                     symptoms = fetch_symptoms(url, disease_param)
#                     response_text += symptoms or f"Symptoms not found for {disease_param.capitalize()}."
#                 else:
#                     response_text += f"Sorry, I don't have a URL for {disease_param.capitalize()}."

#         elif intent_name == "get_treatment":
#             response_text = ""
#             if not disease_param:
#                 response_text = "💊 TREATMENT\n\nNo disease provided and no history available."
#             else:
#                 response_text = "💊 TREATMENT\n\n"
#                 slug = get_slug(disease_param)
#                 if slug:
#                     url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#                     treatment = fetch_treatment(url, disease_param)
#                     response_text += treatment or f"Treatment not found for {disease_param.capitalize()}."
#                 else:
#                     response_text += f"Sorry, I don't have a URL for {disease_param.capitalize()}."

#         elif intent_name == "get_prevention":
#             response_text = ""
#             if not disease_param:
#                 response_text = "🛡️ PREVENTION\n\nNo disease provided and no history available."
#             else:
#                 response_text = "🛡️ PREVENTION\n\n"
#                 slug = get_slug(disease_param)
#                 if slug:
#                     url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#                     prevention = fetch_prevention(url, disease_param)
#                     response_text += prevention or f"Prevention not found for {disease_param.capitalize()}."
#                 else:
#                     response_text += f"Sorry, I don't have a URL for {disease_param.capitalize()}."

#         elif intent_name == "disease_outbreak.general":
#             # take "any" param as updates input (but primary function is WHO outbreak)
#             updates_input = (params.get("any", "") or "").strip()
#             try:
#                 updates_lang = detect(updates_input) if updates_input else memory.get("user_lang", "en")
#             except Exception:
#                 updates_lang = memory.get("user_lang", "en")

#             response_text = "🌍 LATEST OUTBREAK NEWS\n\n"
#             outbreaks = get_who_outbreak_data()
#             if not outbreaks:
#                 response_text += "⚠️ Unable to fetch outbreak data."
#             else:
#                 response_text += "🦠 Latest WHO Outbreak News:\n\n" + "\n\n".join(outbreaks)

#             # translate outbreak response back to user's language
#             response_text = translate_from_english(response_text, updates_lang)

#         elif intent_name == "get_vaccine":
#             response_text = "💉 POLIO VACCINATION SCHEDULE\n\n"
#             if date_str:
#                 try:
#                     birth_date = datetime.datetime.strptime(date_str.split("T")[0], "%Y-%m-%d").date()
#                 except Exception:
#                     birth_date = datetime.date.today()
#             else:
#                 birth_date = datetime.date.today()

#             schedule = build_polio_schedule(birth_date)
#             lines = []
#             for idx, (period, date, vaccine) in enumerate(schedule):
#                 emoji = VACC_EMOJIS[idx]
#                 lines.append(f"{emoji} {period}: {date.strftime('%d-%b-%Y')} → {vaccine}")
#             extra_steps = [
#                 ("⚠️", "Disease & Symptoms: Polio causes fever, weakness, headache, vomiting, stiffness, paralysis"),
#                 ("ℹ️", "About the Vaccine: OPV (oral drops), IPV (injection), free under Govt."),
#                 ("🎯", "Purpose: Prevents life-long paralysis & disability"),
#                 ("👶", "Gender: For all children"),
#                 ("🏥", "Where to Get: Govt hospitals, PHCs, Anganwadis, ASHA workers"),
#                 ("⚕️", "Side Effects: Safe; rarely mild fever. Consult doctor if severe"),
#                 ("✅", "After Vaccination: Feed normally, stay 30 mins at centre, don’t skip future doses"),
#                 ("⏰", f"Next Dose Reminder: Next after birth dose: {schedule[1][1].strftime('%d-%b-%Y')} ({schedule[1][2]})"),
#                 ("📢", "Pulse Polio Campaign: Even if vaccinated, attend Pulse Polio days")
#             ]
#             for emoji, text in extra_steps:
#                 lines.append(f"{emoji} {text}")
#             response_text += "\n".join(lines)

#         elif intent_name == "get_last_queries":
#             # optional helper intent: return last 5 stored queries (in user's language)
#             saved = memory.get("last_queries", [])
#             if not saved:
#                 response_text = "No past queries stored for you."
#             else:
#                 lines = []
#                 for q in saved:
#                     lines.append(f"{q.get('timestamp','')} · {q.get('intent','')} · {q.get('disease','')}")
#                 response_text = "Your last queries (most recent last):\n\n" + "\n".join(lines)

#         elif intent_name == "Default Fallback Intent":
#             response_text = "🤔 Sorry, I couldn't understand that. Please provide a disease name or try rephrasing your question."

#         # translate final response to user language (unless already translated above)
#         # (We translated outbreaks earlier)
#         if intent_name != "disease_outbreak.general":
#             response_text = translate_from_english(response_text, user_lang)

#     except Exception:
#         traceback.print_exc()
#         response_text = "⚠️ An error occurred while processing your request."

#     # Save updated memory only if we have a DB or in-memory store
#     try:
#         save_user_memory(user_id, memory)
#     except Exception as e:
#         print(f"Failed to save memory: {e}")

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
from psycopg2.extras import Json
import psycopg2
import os
import traceback
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# -------------------
# Setup
# -------------------
DetectorFactory.seed = 0  # makes langdetect deterministic

INDIAN_LANGUAGES = ["hi", "te", "ta", "kn", "bn", "mr", "gu", "ml", "ur", "pa", "or", "ks"]
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
    key = (disease_param or "").strip().lower()
    return slugs.get(key)

# -------------------
# Translation helpers
# -------------------
def translate_to_english(disease_param, detected_lang):
    if not disease_param or not disease_param.strip():
        return disease_param
    if detected_lang not in INDIAN_LANGUAGES:
        return disease_param
    try:
        resp = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": disease_param, "langpair": f"{detected_lang}|en"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        translated = data.get("responseData", {}).get("translatedText")
        return translated if translated else disease_param
    except Exception as e:
        print(f"MyMemory translation error (to English): {e}")
        return disease_param

def translate_from_english(text, target_lang):
    if not text or not text.strip():
        return text
    if target_lang not in INDIAN_LANGUAGES:
        return text
    try:
        resp = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": text, "langpair": f"en|{target_lang}"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        translated = data.get("responseData", {}).get("translatedText")
        return translated if translated else text
    except Exception as e:
        print(f"MyMemory translation error (from English): {e}")
        return text

# -------------------
# Helper for safe truncation
# -------------------
def truncate_response(text, limit=500):
    if not text:
        return text
    if len(text) <= limit:
        return text
    head = text[:limit]
    last_dot = head.rfind('.')
    if last_dot != -1:
        return text[: last_dot + 1]
    last_space = head.rfind(' ')
    if last_space != -1 and last_space > int(limit * 0.3):
        return head[:last_space] + "..."
    return head

# -------------------
# WHO scraping helpers
# -------------------
def fetch_overview(url, disease_name=""):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "overview" in tag.get_text(strip=True).lower())
        if not heading:
            return None
        paragraphs = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ["h2","h3"]:
                break
            if sibling.name == "p":
                txt = sibling.get_text(strip=True)
                if txt:
                    paragraphs.append(txt)
        if not paragraphs:
            return None
        text = " ".join(paragraphs).strip()
        final_text = f"Intent of {disease_name.capitalize()}:\n\n{text}"
        return truncate_response(final_text, 500)
    except Exception:
        traceback.print_exc()
        return None

def fetch_symptoms(url, disease_name):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "symptoms" in tag.get_text(strip=True).lower())
        if not heading:
            return None
        points = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ["h2","h3"]:
                break
            if sibling.name == "ul":
                for li in sibling.find_all("li"):
                    txt = li.get_text(strip=True)
                    if txt:
                        points.append(f"🔹 {txt}")
        if not points:
            for sibling in heading.find_next_siblings():
                if sibling.name in ["h2","h3"]:
                    break
                if sibling.name == "p":
                    txt = sibling.get_text(strip=True)
                    if txt:
                        points.append(f"🔹 {txt}")
        if not points:
            return None
        body = "\n\n".join(points)
        final_text = f"Intent of {disease_name.capitalize()}:\n\n{body}"
        return truncate_response(final_text, 500)
    except Exception:
        traceback.print_exc()
        return None

def fetch_treatment(url, disease_name):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        heading = soup.find(lambda tag: tag.name in ["h2","h3"] and ("treatment" in tag.get_text(strip=True).lower() or "management" in tag.get_text(strip=True).lower()))
        if not heading:
            return None
        points = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ["h2","h3"]:
                break
            if sibling.name == "ul":
                for li in sibling.find_all("li"):
                    txt = li.get_text(strip=True)
                    if txt:
                        points.append(f"💊 {txt}")
        if not points:
            for sibling in heading.find_next_siblings():
                if sibling.name in ["h2","h3"]:
                    break
                if sibling.name == "p":
                    txt = sibling.get_text(strip=True)
                    if txt:
                        points.append(f"💊 {txt}")
        if not points:
            return None
        body = "\n\n".join(points)
        final_text = f"Intent of {disease_name.capitalize()}:\n\n{body}"
        return truncate_response(final_text, 500)
    except Exception:
        traceback.print_exc()
        return None

def fetch_prevention(url, disease_name):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "prevention" in tag.get_text(strip=True).lower())
        if not heading:
            return None
        points = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ["h2","h3"]:
                break
            if sibling.name == "ul":
                for li in sibling.find_all("li"):
                    txt = li.get_text(strip=True)
                    if txt:
                        points.append(f"🛡️ {txt}")
        if not points:
            for sibling in heading.find_next_siblings():
                if sibling.name in ["h2","h3"]:
                    break
                if sibling.name == "p":
                    txt = sibling.get_text(strip=True)
                    if txt:
                        points.append(f"🛡️ {txt}")
        if not points:
            return None
        body = "\n\n".join(points)
        final_text = f"Intent of {disease_name.capitalize()}:\n\n{body}"
        return truncate_response(final_text, 500)
    except Exception:
        traceback.print_exc()
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
        if "value" not in data or not data["value"]:
            return None
        outbreaks = []
        for item in data["value"][:5]:
            title = item.get("OverrideTitle") or item.get("Title")
            date = item.get("FormattedDate", "Unknown date")
            outbreaks.append(f"🦠 {title} ({date})")
        return outbreaks
    except Exception:
        traceback.print_exc()
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
# Memory (DB or in-memory)
# -------------------
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("⚠️ DATABASE_URL not set. Using in-memory store.")
    conn = None
    _in_memory_store = {}
else:
    try:
        conn = psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"Error connecting to DATABASE_URL: {e}")
        conn = None
        _in_memory_store = {}

def create_users_table():
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                context JSONB NOT NULL DEFAULT '{}'::jsonb,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        print("✅ users table is ready")
    except Exception as e:
        print(f"Error creating users table: {e}")

create_users_table()

def get_user_memory(user_id):
    if not user_id:
        return {}
    if not conn:
        return _in_memory_store.get(user_id, {}).copy()
    try:
        cur = conn.cursor()
        cur.execute("SELECT context FROM users WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
        cur.close()
        return row[0] if row else {}
    except Exception as e:
        print(f"DB error on get_user_memory: {e}")
        return {}

def save_user_memory(user_id, context):
    if not user_id:
        return
    if not conn:
        _in_memory_store[user_id] = context.copy()
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (user_id, context, last_updated)
            VALUES (%s, %s, NOW())
            ON CONFLICT (user_id)
            DO UPDATE SET context = EXCLUDED.context, last_updated = NOW()
        """, (user_id, Json(context)))
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"DB error on save_user_memory: {e}")

# -------------------
# Dialogflow / API Webhook
# -------------------
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True)
    if not req:
        return jsonify({"fulfillmentText": "Invalid request"}), 400

    # Extract info
    user_id = req.get("originalDetectIntentRequest", {}).get("payload", {}).get("user", {}).get("userId") \
              or req.get("session")
    intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    params = req.get("queryResult", {}).get("parameters", {}) or {}
    date_str = params.get("date", "")
    disease_input = (params.get("disease", "") or "").strip()
    if not disease_input:
        disease_input = (params.get("any", "") or "").strip()

    # Load memory
    memory = get_user_memory(user_id) or {}
    if "last_disease" not in memory:
        memory["last_disease"] = ""
    if "user_lang" not in memory:
        memory["user_lang"] = "en"
    if "last_queries" not in memory or not isinstance(memory.get("last_queries"), list):
        memory["last_queries"] = []

    # Detect language
    try:
        if disease_input:
            detected_lang = detect(disease_input)
        else:
            detected_lang = memory.get("user_lang", "en")
    except Exception:
        detected_lang = memory.get("user_lang", "en")

    # Translate if needed
    if disease_input:
        translated = translate_to_english(disease_input, detected_lang) or disease_input
        disease_param = (translated or "").strip().lower()
        user_lang = detected_lang if detected_lang in INDIAN_LANGUAGES else "en"
    else:
        disease_param = memory.get("last_disease", "") or ""
        user_lang = memory.get("user_lang", "en")

    # Update memory
    if disease_param:
        memory["last_disease"] = disease_param
    memory["user_lang"] = user_lang
    now_iso = datetime.datetime.utcnow().isoformat()
    memory.setdefault("last_queries", [])
    memory["last_queries"].append({
        "intent": intent_name,
        "disease": disease_param,
        "user_lang": user_lang,
        "timestamp": now_iso
    })
    memory["last_queries"] = memory["last_queries"][-5:]

    # Build response
    response_text = "Sorry, I don't understand your request."
    try:
        if intent_name == "get_disease_overview":
            response_text = ""
            if not disease_param:
                response_text = "📖 DISEASE OVERVIEW\n\nNo disease provided."
            else:
                response_text = "📖 DISEASE OVERVIEW\n\n"
                slug = get_slug(disease_param)
                if slug:
                    url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
                    overview = fetch_overview(url, disease_param) or None
                    response_text += overview or f"Overview not found for {disease_param.capitalize()}."
                else:
                    response_text += f"Disease not found. Use a valid name."

        elif intent_name == "get_symptoms":
            response_text = ""
            if not disease_param:
                response_text = "🤒 SYMPTOMS\n\nNo disease provided."
            else:
                response_text = "🤒 SYMPTOMS\n\n"
                slug = get_slug(disease_param)
                if slug:
                    url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
                    symptoms = fetch_symptoms(url, disease_param)
                    response_text += symptoms or f"Symptoms not found for {disease_param.capitalize()}."
                else:
                    response_text += f"No URL for {disease_param.capitalize()}."

        elif intent_name == "get_treatment":
            response_text = ""
            if not disease_param:
                response_text = "💊 TREATMENT\n\nNo disease provided."
            else:
                response_text = "💊 TREATMENT\n\n"
                slug = get_slug(disease_param)
                if slug:
                    url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
                    treatment = fetch_treatment(url, disease_param)
                    response_text += treatment or f"Treatment not found for {disease_param.capitalize()}."
                else:
                    response_text += f"No URL for {disease_param.capitalize()}."

        elif intent_name == "get_prevention":
            response_text = ""
            if not disease_param:
                response_text = "🛡️ PREVENTION\n\nNo disease provided."
            else:
                response_text = "🛡️ PREVENTION\n\n"
                slug = get_slug(disease_param)
                if slug:
                    url = f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
                    prevention = fetch_prevention(url, disease_param)
                    response_text += prevention or f"Prevention not found for {disease_param.capitalize()}."
                else:
                    response_text += f"No URL for {disease_param.capitalize()}."

        elif intent_name == "disease_outbreak.general":
            updates_input = (params.get("any", "") or "").strip()
            try:
                updates_lang = detect(updates_input) if updates_input else memory.get("user_lang", "en")
            except Exception:
                updates_lang = memory.get("user_lang", "en")
            response_text = "🌍 LATEST OUTBREAK NEWS\n\n"
            outbreaks = get_who_outbreak_data()
            if not outbreaks:
                response_text += "⚠️ Unable to fetch outbreak data."
            else:
                response_text += "🦠 Latest WHO Outbreak News:\n\n" + "\n\n".join(outbreaks)
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
            for label, d, vac in schedule:
                response_text += f"{VACC_EMOJIS[0]} {label}: {vac}\n"
            response_text = translate_from_english(response_text, user_lang)

    except Exception:
        traceback.print_exc()
        response_text = "❌ Something went wrong while fetching data."

    # Save memory
    save_user_memory(user_id, memory)

    return jsonify({"fulfillmentText": response_text})

# -------------------
# Twilio SMS Integration
# -------------------
@app.route('/sms', methods=['POST'])
def sms_webhook():
    incoming_msg = request.form.get('Body', '').strip()
    from_number = request.form.get('From', '')

    pseudo_req = {
        "queryResult": {
            "parameters": {"any": incoming_msg},
            "intent": {"displayName": "Default Fallback Intent"}
        },
        "originalDetectIntentRequest": {
            "payload": {"user": {"userId": from_number}}
        },
        "session": from_number
    }

    # Call webhook logic
    with app.test_request_context('/webhook', method='POST', json=pseudo_req):
        resp_json = webhook().get_json()
        reply_text = resp_json.get("fulfillmentText", "Sorry, I couldn't process your request.")

    twilio_resp = MessagingResponse()
    twilio_resp.message(reply_text)
    return str(twilio_resp)

# -------------------
# Run Flask
# -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

