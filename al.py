# from flask import Flask, request, jsonify
# import requests
# from bs4 import BeautifulSoup
# from langdetect import detect, DetectorFactory  # ✅ Auto language detection

# app = Flask(__name__)

# # -------------------
# # Setup
# # -------------------
# DetectorFactory.seed = 0   # makes langdetect deterministic

# # -------- Static mapping of diseases to WHO fact sheet URLs --------
# DISEASE_OVERVIEWS = {
#     "malaria": "https://www.who.int/news-room/fact-sheets/detail/malaria",
#     "influenza": "https://www.who.int/news-room/fact-sheets/detail/influenza-(seasonal)",
#     "dengue": "https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue",
#     "hiv": "https://www.who.int/news-room/fact-sheets/detail/hiv-aids",
#     "tuberculosis": "https://www.who.int/news-room/fact-sheets/detail/tuberculosis",
#     "covid-19": "https://www.who.int/news-room/fact-sheets/detail/coronavirus-disease-(covid-19)",
#     "cholera": "https://www.who.int/news-room/fact-sheets/detail/cholera",
#     "measles": "https://www.who.int/news-room/fact-sheets/detail/measles",
#     "ebola": "https://www.who.int/news-room/fact-sheets/detail/ebola-virus-disease",
#     "zika": "https://www.who.int/news-room/fact-sheets/detail/zika-virus",
#     "yellow fever": "https://www.who.int/news-room/fact-sheets/detail/yellow-fever",
#     "hepatitis b": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-b",
#     "hepatitis c": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-c",
#     "rabies": "https://www.who.int/news-room/fact-sheets/detail/rabies",
#     "meningitis": "https://www.who.int/news-room/fact-sheets/detail/meningitis",
#     "leprosy": "https://www.who.int/news-room/fact-sheets/detail/leprosy",
#     "schistosomiasis": "https://www.who.int/news-room/fact-sheets/detail/schistosomiasis",
#     "trypanosomiasis": "https://www.who.int/news-room/fact-sheets/detail/trypanosomiasis-(sleeping-sickness)",
#     "onchocerciasis": "https://www.who.int/news-room/fact-sheets/detail/onchocerciasis-(river-blindness)",
#     "lyme disease": "https://www.who.int/news-room/fact-sheets/detail/lyme-disease",
# }

# # -------------------
# # Translation helpers
# # -------------------
# def translate_to_english(disease_param):
#     """Auto-detect input language and translate disease_param to English using MyMemory."""
#     if not disease_param.strip():
#         return disease_param

#     try:
#         detected_lang = detect(disease_param)   # e.g., "te", "hi", "kn"
#     except Exception:
#         detected_lang = "en"

#     if detected_lang == "en":
#         return disease_param

#     try:
#         url = f"https://api.mymemory.translated.net/get?q={disease_param}&langpair={detected_lang}|en"
#         response = requests.get(url, timeout=10)
#         data = response.json()
#         translated = data.get("responseData", {}).get("translatedText")
#         if translated:
#             return translated
#         return disease_param
#     except Exception as e:
#         print(f"MyMemory translation error: {e}")
#         return disease_param


# def translate_from_english(disease_param, target_lang):
#     """Translate English disease_param back into the user’s original language."""
#     if target_lang == "en" or not disease_param.strip():
#         return disease_param

#     try:
#         url = f"https://api.mymemory.translated.net/get?q={disease_param}&langpair=en|{target_lang}"
#         response = requests.get(url, timeout=10)
#         data = response.json()
#         translated = data.get("responseData", {}).get("translatedText")
#         if translated:
#             return translated
#         return disease_param
#     except Exception as e:
#         print(f"MyMemory translation back error: {e}")
#         return disease_param


# # -------- Helper functions --------
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
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "p":
#                 disease_param = sibling.get_text(strip=True)
#                 if disease_param:
#                     paragraphs.append(disease_param)

#         if paragraphs:
#             return " ".join(paragraphs)
#         return None
#     except Exception:
#         return None


# def fetch_symptoms(url, disease_param):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")

#         heading = soup.find(
#             lambda tag: tag.name in ["h2", "h3"] 
#             and ("symptoms" in tag.get_text(strip=True).lower() 
#                  or "signs and symptoms" in tag.get_text(strip=True).lower())
#         )
#         if not heading:
#             return None

#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     disease_param = li.get_text(strip=True)
#                     if disease_param:
#                         points.append(f"- {disease_param}")

#         if not points:
#             paragraphs = []
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2", "h3"]:
#                     break
#                 if sibling.name == "p":
#                     disease_param = sibling.get_text(strip=True)
#                     if disease_param:
#                         paragraphs.append(f"- {disease_param}")
#             points = paragraphs

#         if points:
#             return f"The common symptoms of {disease_param.capitalize()} are:\n" + "\n".join(points)
#         return None
#     except Exception:
#         return None


# def fetch_treatment(url, disease_param):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")

#         heading = soup.find(
#             lambda tag: tag.name in ["h2", "h3"] 
#             and ("treatment" in tag.get_text(strip=True).lower() 
#                  or "management" in tag.get_text(strip=True).lower())
#         )
#         if not heading:
#             return None

#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     disease_param = li.get_text(strip=True)
#                     if disease_param:
#                         points.append(f"- {disease_param}")

#         if not points:
#             paragraphs = []
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2", "h3"]:
#                     break
#                 if sibling.name == "p":
#                     disease_param = sibling.get_text(strip=True)
#                     if disease_param:
#                         paragraphs.append(f"- {disease_param}")
#             points = paragraphs

#         if points:
#             return f"The common treatments for {disease_param.capitalize()} are:\n" + "\n".join(points)
#         return None
#     except Exception:
#         return None


# def fetch_prevention(url, disease_param):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")

#         heading = soup.find(lambda tag: tag.name in ["h2", "h3"] and "prevention" in tag.get_text(strip=True).lower())
#         if not heading:
#             return None

#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     disease_param = li.get_text(strip=True)
#                     if disease_param:
#                         points.append(f"- {disease_param}")

#         if not points:
#             paragraphs = []
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2", "h3"]:
#                     break
#                 if sibling.name == "p":
#                     disease_param = sibling.get_text(strip=True)
#                     if disease_param:
#                         paragraphs.append(f"- {disease_param}")
#             points = paragraphs

#         if points:
#             return f"The common prevention methods for {disease_param.capitalize()} are:\n" + "\n".join(points)
#         return None
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


# # -------- Flask webhook route --------
# @app.route('/webhook', methods=['POST'])
# def webhook():
#     req = request.get_json()
#     intent_name = req["queryResult"]["intent"]["displayName"]
#     params = req["queryResult"].get("parameters", {})
#     disease_input = params.get("disease", "").strip()

#     # ✅ Detect user input language once
#     try:
#         user_lang = detect(disease_input) if disease_input else "en"
#     except Exception:
#         user_lang = "en"

#     # ✅ Translate disease_param into English first
#     disease_param = translate_to_english(disease_input).lower()

#     response_text = "Sorry, I don't understand your request."

#     if intent_name == "get_disease_overview":
#         url = DISEASE_OVERVIEWS.get(disease_param)
#         if url:
#             overview = fetch_overview(url)
#             response_text = overview or f"Overview not found for {disease_param.capitalize()}. You can read more here: {url}"
#         else:
#             response_text = f"Disease not found. Make sure to use a valid disease name."

#     elif intent_name == "get_symptoms":
#         url = DISEASE_OVERVIEWS.get(disease_param)
#         if url:
#             symptoms = fetch_symptoms(url, disease_param)
#             response_text = symptoms or f"Symptoms not found for {disease_param.capitalize()}. You can read more here: {url}"
#         else:
#             response_text = f"Sorry, I don't have a URL for {disease_param.capitalize()}."

#     elif intent_name == "get_treatment":
#         url = DISEASE_OVERVIEWS.get(disease_param)
#         if url:
#             treatment = fetch_treatment(url, disease_param)
#             response_text = treatment or f"Treatment details not found for {disease_param.capitalize()}. You can read more here: {url}"
#         else:
#             response_text = f"Sorry, I don't have a URL for {disease_param.capitalize()}."

#     elif intent_name == "get_prevention":
#         url = DISEASE_OVERVIEWS.get(disease_param)
#         if url:
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

#     # ✅ Translate final response back to user’s language
#     response_text = translate_from_english(response_text, user_lang)

#     return jsonify({"fulfillmentText": response_text})


# if __name__ == '__main__':
#     app.run(debug=True)










# from flask import Flask, request, jsonify
# import requests
# from bs4 import BeautifulSoup
# from langdetect import detect, DetectorFactory  # ✅ Auto language detection

# app = Flask(__name__)

# # -------------------
# # Setup
# # -------------------
# DetectorFactory.seed = 0   # makes langdetect deterministic

# # List of Indian language codes
# INDIAN_LANGUAGES = [
#     "hi",  # Hindi
#     "te",  # Telugu
#     "ta",  # Tamil
#     "kn",  # Kannada
#     "bn",  # Bengali
#     "mr",  # Marathi
#     "gu",  # Gujarati
#     "ml",  # Malayalam
#     "ur",  # Urdu
#     "pa",  # Punjabi
#     "or",  # Odia
#     "ks"   # Kashmiri
# ]

# # -------- Static mapping of diseases to WHO fact sheet URLs --------
# DISEASE_OVERVIEWS = {
#     "malaria": "https://www.who.int/news-room/fact-sheets/detail/malaria",
#     "influenza": "https://www.who.int/news-room/fact-sheets/detail/influenza-(seasonal)",
#     "dengue": "https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue",
#     "hiv": "https://www.who.int/news-room/fact-sheets/detail/hiv-aids",
#     "tuberculosis": "https://www.who.int/news-room/fact-sheets/detail/tuberculosis",
#     "covid-19": "https://www.who.int/news-room/fact-sheets/detail/coronavirus-disease-(covid-19)",
#     "cholera": "https://www.who.int/news-room/fact-sheets/detail/cholera",
#     "measles": "https://www.who.int/news-room/fact-sheets/detail/measles",
#     "ebola": "https://www.who.int/news-room/fact-sheets/detail/ebola-virus-disease",
#     "zika": "https://www.who.int/news-room/fact-sheets/detail/zika-virus",
#     "yellow fever": "https://www.who.int/news-room/fact-sheets/detail/yellow-fever",
#     "hepatitis b": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-b",
#     "hepatitis c": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-c",
#     "rabies": "https://www.who.int/news-room/fact-sheets/detail/rabies",
#     "meningitis": "https://www.who.int/news-room/fact-sheets/detail/meningitis",
#     "leprosy": "https://www.who.int/news-room/fact-sheets/detail/leprosy",
#     "schistosomiasis": "https://www.who.int/news-room/fact-sheets/detail/schistosomiasis",
#     "trypanosomiasis": "https://www.who.int/news-room/fact-sheets/detail/trypanosomiasis-(sleeping-sickness)",
#     "onchocerciasis": "https://www.who.int/news-room/fact-sheets/detail/onchocerciasis-(river-blindness)",
#     "lyme disease": "https://www.who.int/news-room/fact-sheets/detail/lyme-disease",
# }

# # -------------------
# # Translation helpers
# # -------------------
# def translate_to_english(disease_param):
#     """Auto-detect input language and translate disease_param to English using MyMemory."""
#     if not disease_param.strip():
#         return disease_param

#     try:
#         detected_lang = detect(disease_param)   # e.g., "te", "hi", "kn"
#     except Exception:
#         detected_lang = "en"

#     if detected_lang == "en":
#         return disease_param

#     try:
#         url = f"https://api.mymemory.translated.net/get?q={disease_param}&langpair={detected_lang}|en"
#         response = requests.get(url, timeout=10)
#         data = response.json()
#         translated = data.get("responseData", {}).get("translatedText")
#         if translated:
#             return translated
#         return disease_param
#     except Exception as e:
#         print(f"MyMemory translation error: {e}")
#         return disease_param


# def translate_from_english(disease_param, target_lang):
#     """Translate English disease_param back into the user’s original language."""
#     if target_lang == "en" or not disease_param.strip():
#         return disease_param

#     try:
#         url = f"https://api.mymemory.translated.net/get?q={disease_param}&langpair=en|{target_lang}"
#         response = requests.get(url, timeout=10)
#         data = response.json()
#         translated = data.get("responseData", {}).get("translatedText")
#         if translated:
#             return translated
#         return disease_param
#     except Exception as e:
#         print(f"MyMemory translation back error: {e}")
#         return disease_param


# # -------- Helper functions --------
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
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "p":
#                 disease_param = sibling.get_text(strip=True)
#                 if disease_param:
#                     paragraphs.append(disease_param)

#         if paragraphs:
#             return " ".join(paragraphs)
#         return None
#     except Exception:
#         return None


# def fetch_symptoms(url, disease_param):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")

#         heading = soup.find(
#             lambda tag: tag.name in ["h2", "h3"] 
#             and ("symptoms" in tag.get_text(strip=True).lower() 
#                  or "signs and symptoms" in tag.get_text(strip=True).lower())
#         )
#         if not heading:
#             return None

#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     disease_param = li.get_text(strip=True)
#                     if disease_param:
#                         points.append(f"- {disease_param}")

#         if not points:
#             paragraphs = []
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2", "h3"]:
#                     break
#                 if sibling.name == "p":
#                     disease_param = sibling.get_text(strip=True)
#                     if disease_param:
#                         paragraphs.append(f"- {disease_param}")
#             points = paragraphs

#         if points:
#             return f"The common symptoms of {disease_param.capitalize()} are:\n" + "\n".join(points)
#         return None
#     except Exception:
#         return None


# def fetch_treatment(url, disease_param):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")

#         heading = soup.find(
#             lambda tag: tag.name in ["h2", "h3"] 
#             and ("treatment" in tag.get_text(strip=True).lower() 
#                  or "management" in tag.get_text(strip=True).lower())
#         )
#         if not heading:
#             return None

#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     disease_param = li.get_text(strip=True)
#                     if disease_param:
#                         points.append(f"- {disease_param}")

#         if not points:
#             paragraphs = []
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2", "h3"]:
#                     break
#                 if sibling.name == "p":
#                     disease_param = sibling.get_text(strip=True)
#                     if disease_param:
#                         paragraphs.append(f"- {disease_param}")
#             points = paragraphs

#         if points:
#             return f"The common treatments for {disease_param.capitalize()} are:\n" + "\n".join(points)
#         return None
#     except Exception:
#         return None


# def fetch_prevention(url, disease_param):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")

#         heading = soup.find(lambda tag: tag.name in ["h2", "h3"] and "prevention" in tag.get_text(strip=True).lower())
#         if not heading:
#             return None

#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     disease_param = li.get_text(strip=True)
#                     if disease_param:
#                         points.append(f"- {disease_param}")

#         if not points:
#             paragraphs = []
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2", "h3"]:
#                     break
#                 if sibling.name == "p":
#                     disease_param = sibling.get_text(strip=True)
#                     if disease_param:
#                         paragraphs.append(f"- {disease_param}")
#             points = paragraphs

#         if points:
#             return f"The common prevention methods for {disease_param.capitalize()} are:\n" + "\n".join(points)
#         return None
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


# # -------- Flask webhook route --------
# @app.route('/webhook', methods=['POST'])
# def webhook():
#     req = request.get_json()
#     intent_name = req["queryResult"]["intent"]["displayName"]
#     params = req["queryResult"].get("parameters", {})
#     disease_input = params.get("disease", "").strip()

#     # ✅ Detect user input language once
#     try:
#         detected_lang = detect(disease_input) if disease_input else "en"
#     except Exception:
#         detected_lang = "en"

#     # Only translate back if detected language is an Indian language
#     user_lang = detected_lang if detected_lang in INDIAN_LANGUAGES else "en"

#     # ✅ Translate disease_param into English first
#     disease_param = translate_to_english(disease_input).lower()


#     response_text = "Sorry, I don't understand your request."

#     if intent_name == "get_disease_overview":
#         url = DISEASE_OVERVIEWS.get(disease_param)
#         if url:
#             overview = fetch_overview(url)
#             response_text = overview or f"Overview not found for {disease_param.capitalize()}. You can read more here: {url}"
#         else:
#             response_text = f"Disease not found. Make sure to use a valid disease name."

#     elif intent_name == "get_symptoms":
#         url = DISEASE_OVERVIEWS.get(disease_param)
#         if url:
#             symptoms = fetch_symptoms(url, disease_param)
#             response_text = symptoms or f"Symptoms not found for {disease_param.capitalize()}. You can read more here: {url}"
#         else:
#             response_text = f"Sorry, I don't have a URL for {disease_param.capitalize()}."

#     elif intent_name == "get_treatment":
#         url = DISEASE_OVERVIEWS.get(disease_param)
#         if url:
#             treatment = fetch_treatment(url, disease_param)
#             response_text = treatment or f"Treatment details not found for {disease_param.capitalize()}. You can read more here: {url}"
#         else:
#             response_text = f"Sorry, I don't have a URL for {disease_param.capitalize()}."

#     elif intent_name == "get_prevention":
#         url = DISEASE_OVERVIEWS.get(disease_param)
#         if url:
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

#     # ✅ Translate final response back to user’s language only if it is an Indian language
#     response_text = translate_from_english(response_text, user_lang)

#     return jsonify({"fulfillmentText": response_text})


# if __name__ == '__main__':
#     app.run(debug=True)


#     MAIN WEBHOOK CODE

# from flask import Flask, request, jsonify
# import requests
# from bs4 import BeautifulSoup
# from langdetect import detect, DetectorFactory  # ✅ Auto language detection

# app = Flask(__name__)

# # -------------------
# # Setup
# # -------------------
# DetectorFactory.seed = 0   # makes langdetect deterministic

# # List of Indian language codes
# INDIAN_LANGUAGES = [
#     "hi",  # Hindi
#     "te",  # Telugu
#     "ta",  # Tamil
#     "kn",  # Kannada
#     "bn",  # Bengali
#     "mr",  # Marathi
#     "gu",  # Gujarati
#     "ml",  # Malayalam
#     "ur",  # Urdu
#     "pa",  # Punjabi
#     "or",  # Odia
#     "ks"   # Kashmiri
# ]

# # -------- Static mapping of diseases to WHO fact sheet URLs --------
# DISEASE_OVERVIEWS = {
#     "malaria": "https://www.who.int/news-room/fact-sheets/detail/malaria",
#     "influenza": "https://www.who.int/news-room/fact-sheets/detail/influenza-(seasonal)",
#     "dengue": "https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue",
#     "hiv": "https://www.who.int/news-room/fact-sheets/detail/hiv-aids",
#     "tuberculosis": "https://www.who.int/news-room/fact-sheets/detail/tuberculosis",
#     "covid-19": "https://www.who.int/news-room/fact-sheets/detail/coronavirus-disease-(covid-19)",
#     "cholera": "https://www.who.int/news-room/fact-sheets/detail/cholera",
#     "measles": "https://www.who.int/news-room/fact-sheets/detail/measles",
#     "ebola": "https://www.who.int/news-room/fact-sheets/detail/ebola-virus-disease",
#     "zika": "https://www.who.int/news-room/fact-sheets/detail/zika-virus",
#     "yellow fever": "https://www.who.int/news-room/fact-sheets/detail/yellow-fever",
#     "hepatitis b": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-b",
#     "hepatitis c": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-c",
#     "rabies": "https://www.who.int/news-room/fact-sheets/detail/rabies",
#     "meningitis": "https://www.who.int/news-room/fact-sheets/detail/meningitis",
#     "leprosy": "https://www.who.int/news-room/fact-sheets/detail/leprosy",
#     "schistosomiasis": "https://www.who.int/news-room/fact-sheets/detail/schistosomiasis",
#     "trypanosomiasis": "https://www.who.int/news-room/fact-sheets/detail/trypanosomiasis-(sleeping-sickness)",
#     "onchocerciasis": "https://www.who.int/news-room/fact-sheets/detail/onchocerciasis-(river-blindness)",
#     "lyme disease": "https://www.who.int/news-room/fact-sheets/detail/lyme-disease",
# }

# # -------------------
# # Translation helpers
# # -------------------
# def translate_to_english(disease_param, detected_lang):
#     """Translate disease_param to English only if detected_lang is Indian."""
#     if not disease_param.strip():
#         return disease_param

#     if detected_lang not in INDIAN_LANGUAGES:
#         return disease_param  # keep as-is for English or other languages

#     try:
#         url = f"https://api.mymemory.translated.net/get?q={disease_param}&langpair={detected_lang}|en"
#         response = requests.get(url, timeout=10)
#         data = response.json()
#         translated = data.get("responseData", {}).get("translatedText")
#         if translated:
#             return translated
#         return disease_param
#     except Exception as e:
#         print(f"MyMemory translation error: {e}")
#         return disease_param


# def translate_from_english(text, target_lang):
#     """Translate text back only if target_lang is an Indian language."""
#     if target_lang not in INDIAN_LANGUAGES or not text.strip():
#         return text

#     try:
#         url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|{target_lang}"
#         response = requests.get(url, timeout=10)
#         data = response.json()
#         translated = data.get("responseData", {}).get("translatedText")
#         if translated:
#             return translated
#         return text
#     except Exception as e:
#         print(f"MyMemory translation back error: {e}")
#         return text


# # -------- Helper functions --------
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
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "p":
#                 txt = sibling.get_text(strip=True)
#                 if txt:
#                     paragraphs.append(txt)

#         if paragraphs:
#             return " ".join(paragraphs)
#         return None
#     except Exception:
#         return None


# def fetch_symptoms(url, disease_name):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")

#         heading = soup.find(
#             lambda tag: tag.name in ["h2", "h3"]
#             and ("symptoms" in tag.get_text(strip=True).lower()
#                  or "signs and symptoms" in tag.get_text(strip=True).lower())
#         )
#         if not heading:
#             return None

#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt:
#                         points.append(f"- {txt}")

#         if not points:
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2", "h3"]:
#                     break
#                 if sibling.name == "p":
#                     txt = sibling.get_text(strip=True)
#                     if txt:
#                         points.append(f"- {txt}")

#         if points:
#             return f"The common symptoms of {disease_name.capitalize()} are:\n" + "\n".join(points)
#         return None
#     except Exception:
#         return None


# def fetch_treatment(url, disease_name):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")

#         heading = soup.find(
#             lambda tag: tag.name in ["h2", "h3"]
#             and ("treatment" in tag.get_text(strip=True).lower()
#                  or "management" in tag.get_text(strip=True).lower())
#         )
#         if not heading:
#             return None

#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt:
#                         points.append(f"- {txt}")

#         if not points:
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2", "h3"]:
#                     break
#                 if sibling.name == "p":
#                     txt = sibling.get_text(strip=True)
#                     if txt:
#                         points.append(f"- {txt}")

#         if points:
#             return f"The common treatments for {disease_name.capitalize()} are:\n" + "\n".join(points)
#         return None
#     except Exception:
#         return None


# def fetch_prevention(url, disease_name):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")

#         heading = soup.find(lambda tag: tag.name in ["h2", "h3"] and "prevention" in tag.get_text(strip=True).lower())
#         if not heading:
#             return None

#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt:
#                         points.append(f"- {txt}")

#         if not points:
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2", "h3"]:
#                     break
#                 if sibling.name == "p":
#                     txt = sibling.get_text(strip=True)
#                     if txt:
#                         points.append(f"- {txt}")

#         if points:
#             return f"The common prevention methods for {disease_name.capitalize()} are:\n" + "\n".join(points)
#         return None
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


# # -------- Flask webhook route --------
# @app.route('/webhook', methods=['POST'])
# def webhook():
#     req = request.get_json()
#     intent_name = req["queryResult"]["intent"]["displayName"]
#     params = req["queryResult"].get("parameters", {})
#     disease_input = params.get("disease", "").strip()

#     # ✅ Detect user input language
#     try:
#         detected_lang = detect(disease_input) if disease_input else "en"
#     except Exception:
#         detected_lang = "en"

#     # ✅ Translate to English only if Indian language
#     disease_param = translate_to_english(disease_input, detected_lang).lower()
#     user_lang = detected_lang if detected_lang in INDIAN_LANGUAGES else "en"

#     response_text = "Sorry, I don't understand your request."

#     if intent_name == "get_disease_overview":
#         url = DISEASE_OVERVIEWS.get(disease_param)
#         if url:
#             overview = fetch_overview(url)
#             response_text = overview or f"Overview not found for {disease_param.capitalize()}. You can read more here: {url}"
#         else:
#             response_text = f"Disease not found. Make sure to use a valid disease name."

#     elif intent_name == "get_symptoms":
#         url = DISEASE_OVERVIEWS.get(disease_param)
#         if url:
#             symptoms = fetch_symptoms(url, disease_param)
#             response_text = symptoms or f"Symptoms not found for {disease_param.capitalize()}. You can read more here: {url}"
#         else:
#             response_text = f"Sorry, I don't have a URL for {disease_param.capitalize()}."

#     elif intent_name == "get_treatment":
#         url = DISEASE_OVERVIEWS.get(disease_param)
#         if url:
#             treatment = fetch_treatment(url, disease_param)
#             response_text = treatment or f"Treatment details not found for {disease_param.capitalize()}. You can read more here: {url}"
#         else:
#             response_text = f"Sorry, I don't have a URL for {disease_param.capitalize()}."

#     elif intent_name == "get_prevention":
#         url = DISEASE_OVERVIEWS.get(disease_param)
#         if url:
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

#     # ✅ Translate response back only if user used Indian language
#     response_text = translate_from_english(response_text, user_lang)

#     return jsonify({"fulfillmentText": response_text})


# if __name__ == '__main__':
#     app.run(debug=True)




















# from flask import Flask, request, jsonify
# import requests
# from bs4 import BeautifulSoup
# from langdetect import detect, DetectorFactory

# app = Flask(__name__)

# # -------------------
# # Setup
# # -------------------
# DetectorFactory.seed = 0  # makes langdetect deterministic

# # List of Indian language codes
# INDIAN_LANGUAGES = [
#     "hi",  # Hindi
#     "te",  # Telugu
#     "ta",  # Tamil
#     "kn",  # Kannada
#     "bn",  # Bengali
#     "mr",  # Marathi
#     "gu",  # Gujarati
#     "ml",  # Malayalam
#     "ur",  # Urdu
#     "pa",  # Punjabi
#     "or",  # Odia
#     "ks"   # Kashmiri
# ]

# # -------- Dynamic slugs source --------
# SLUGS_URL = "https://raw.githubusercontent.com/INFINITE347/General_Health_stats/main/slugs.json"


# def load_slugs():
#     """Fetch disease slugs from remote JSON file."""
#     try:
#         resp = requests.get(SLUGS_URL, timeout=10)
#         resp.raise_for_status()
#         return resp.json()
#     except Exception as e:
#         print(f"Error loading slugs.json: {e}")
#         return {}


# def get_slug(disease_param):
#     """Return slug for a given normalized disease name."""
#     slugs = load_slugs()
#     key = disease_param.strip().lower()
#     return slugs.get(key)


# # -------------------
# # Translation helpers
# # -------------------
# def translate_to_english(disease_param, detected_lang):
#     """Translate disease_param to English only if detected_lang is Indian."""
#     if not disease_param.strip():
#         return disease_param

#     if detected_lang not in INDIAN_LANGUAGES:
#         return disease_param  # keep as-is for English or other languages

#     try:
#         url = f"https://api.mymemory.translated.net/get?q={disease_param}&langpair={detected_lang}|en"
#         response = requests.get(url, timeout=10)
#         data = response.json()
#         translated = data.get("responseData", {}).get("translatedText")
#         if translated:
#             return translated
#         return disease_param
#     except Exception as e:
#         print(f"MyMemory translation error: {e}")
#         return disease_param


# def translate_from_english(text, target_lang):
#     """Translate text back only if target_lang is an Indian language."""
#     if target_lang not in INDIAN_LANGUAGES or not text.strip():
#         return text

#     try:
#         url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|{target_lang}"
#         response = requests.get(url, timeout=10)
#         data = response.json()
#         translated = data.get("responseData", {}).get("translatedText")
#         if translated:
#             return translated
#         return text
#     except Exception as e:
#         print(f"MyMemory translation back error: {e}")
#         return text


# # -------- Helper functions to scrape WHO --------
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
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "p":
#                 txt = sibling.get_text(strip=True)
#                 if txt:
#                     paragraphs.append(txt)

#         if paragraphs:
#             return " ".join(paragraphs)
#         return None
#     except Exception:
#         return None


# def fetch_symptoms(url, disease_name):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")

#         heading = soup.find(
#             lambda tag: tag.name in ["h2", "h3"]
#             and ("symptoms" in tag.get_text(strip=True).lower()
#                  or "signs and symptoms" in tag.get_text(strip=True).lower())
#         )
#         if not heading:
#             return None

#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt:
#                         points.append(f"- {txt}")

#         if not points:
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2", "h3"]:
#                     break
#                 if sibling.name == "p":
#                     txt = sibling.get_text(strip=True)
#                     if txt:
#                         points.append(f"- {txt}")

#         if points:
#             return f"The common symptoms of {disease_name.capitalize()} are:\n" + "\n".join(points)
#         return None
#     except Exception:
#         return None


# def fetch_treatment(url, disease_name):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")

#         heading = soup.find(
#             lambda tag: tag.name in ["h2", "h3"]
#             and ("treatment" in tag.get_text(strip=True).lower()
#                  or "management" in tag.get_text(strip=True).lower())
#         )
#         if not heading:
#             return None

#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt:
#                         points.append(f"- {txt}")

#         if not points:
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2", "h3"]:
#                     break
#                 if sibling.name == "p":
#                     txt = sibling.get_text(strip=True)
#                     if txt:
#                         points.append(f"- {txt}")

#         if points:
#             return f"The common treatments for {disease_name.capitalize()} are:\n" + "\n".join(points)
#         return None
#     except Exception:
#         return None


# def fetch_prevention(url, disease_name):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")

#         heading = soup.find(lambda tag: tag.name in ["h2", "h3"] and "prevention" in tag.get_text(strip=True).lower())
#         if not heading:
#             return None

#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt:
#                         points.append(f"- {txt}")

#         if not points:
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2", "h3"]:
#                     break
#                 if sibling.name == "p":
#                     txt = sibling.get_text(strip=True)
#                     if txt:
#                         points.append(f"- {txt}")

#         if points:
#             return f"The common prevention methods for {disease_name.capitalize()} are:\n" + "\n".join(points)
#         return None
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


# # -------- Flask webhook route --------
# @app.route('/webhook', methods=['POST'])
# def webhook():
#     req = request.get_json()
#     intent_name = req["queryResult"]["intent"]["displayName"]
#     params = req["queryResult"].get("parameters", {})
#     disease_input = params.get("disease", "").strip()

#     # ✅ Detect user input language
#     try:
#         detected_lang = detect(disease_input) if disease_input else "en"
#     except Exception:
#         detected_lang = "en"

#     # ✅ Translate and normalize
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

#     # ✅ Translate response back only if user used Indian language
#     response_text = translate_from_english(response_text, user_lang)

#     return jsonify({"fulfillmentText": response_text})














from flask import Flask, request, jsonify, send_from_directory
import requests
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os, datetime, uuid

app = Flask(__name__)

# -------------------
# Setup
# -------------------
DetectorFactory.seed = 0
INDIAN_LANGUAGES = ["hi","te","ta","kn","bn","mr","gu","ml","ur","pa","or","ks"]
SLUGS_URL = "https://raw.githubusercontent.com/INFINITE347/General_Health_stats/main/slugs.json"

# Render-safe temp directory
PDF_DIR = "/tmp/generated_pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

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
# PDF Generator
# -------------------
def generate_pdf(filename,schedule):
    filepath=os.path.join(PDF_DIR,filename)
    doc=SimpleDocTemplate(filepath,pagesize=A4)
    styles=getSampleStyleSheet()
    elements=[]
    elements.append(Paragraph("Polio Vaccination Schedule",styles['Title']))
    elements.append(Spacer(1,12))
    data=[["Period","Date","Vaccine"]]
    for period,date,vaccine in schedule:
        data.append([period,date.strftime("%d-%b-%Y"),vaccine])
    table=Table(data,colWidths=[150,150,150])
    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.lightblue),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('BOTTOMPADDING',(0,0),(-1,0),12),
        ('GRID',(0,0),(-1,-1),1,colors.black)
    ]))
    elements.append(table)
    doc.build(elements)
    return filepath

# -------------------
# Flask Routes
# -------------------
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(PDF_DIR, filename, as_attachment=True)

@app.route('/webhook',methods=['POST'])
def webhook():
    req=request.get_json()
    intent=req["queryResult"]["intent"]["displayName"]
    params=req["queryResult"].get("parameters",{})
    disease=params.get("disease","").strip()
    try: detected_lang=detect(disease) if disease else "en"
    except: detected_lang="en"
    disease_en=translate_to_english(disease, detected_lang).strip().lower()
    user_lang = detected_lang if detected_lang in INDIAN_LANGUAGES else "en"
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
        vaccine=params.get("vaccine_name","").lower()
        date_str=params.get("date")
        if vaccine=="polio" and date_str:
            birth_date=datetime.datetime.strptime(date_str[:10],"%Y-%m-%d").date()
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
            filename=f"polio_schedule_{birth_date}_{uuid.uuid4().hex[:6]}.pdf"
            generate_pdf(filename,sched)
            download_link=f"{request.host_url}download/{filename}"
            lines.append(f"\n📄 Download PDF: {download_link}")
            response_text="\n".join(lines)
            response_text=translate_from_english(response_text,user_lang)

    return jsonify({"fulfillmentText": response_text})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)




# from flask import Flask, request, jsonify
# import requests
# from bs4 import BeautifulSoup
# from langdetect import detect, DetectorFactory
# import datetime

# app = Flask(__name__)

# # -------------------
# # Setup
# # -------------------
# DetectorFactory.seed = 0
# INDIAN_LANGUAGES = ["hi","te","ta","kn","bn","mr","gu","ml","ur","pa","or","ks"]
# SLUGS_URL = "https://raw.githubusercontent.com/INFINITE347/General_Health_stats/main/slugs.json"

# # -------------------
# # Slug Helpers
# # -------------------
# def load_slugs():
#     try:
#         resp = requests.get(SLUGS_URL, timeout=10)
#         resp.raise_for_status()
#         return resp.json()
#     except:
#         return {}

# def get_slug(disease_param):
#     slugs = load_slugs()
#     return slugs.get(disease_param.strip().lower())

# # -------------------
# # Translation Helpers
# # -------------------
# def translate_to_english(text, detected_lang):
#     if detected_lang not in INDIAN_LANGUAGES: return text
#     try:
#         url = f"https://api.mymemory.translated.net/get?q={text}&langpair={detected_lang}|en"
#         r = requests.get(url, timeout=10).json()
#         return r.get("responseData", {}).get("translatedText", text)
#     except:
#         return text

# def translate_from_english(text, target_lang):
#     if target_lang not in INDIAN_LANGUAGES: return text
#     try:
#         url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|{target_lang}"
#         r = requests.get(url, timeout=10).json()
#         return r.get("responseData", {}).get("translatedText", text)
#     except:
#         return text

# # -------------------
# # WHO Scrapers
# # -------------------
# def fetch_overview(url):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text,"html.parser")
#         h = soup.find(lambda tag: tag.name in ["h2","h3"] and "overview" in tag.get_text(strip=True).lower())
#         if not h: return None
#         paras = []
#         for sib in h.find_next_siblings():
#             if sib.name in ["h2","h3"]: break
#             if sib.name=="p": paras.append(sib.get_text(strip=True))
#         return " ".join(paras) if paras else None
#     except: return None

# def fetch_points(url, keyword, disease_name, title_prefix):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text,"html.parser")
#         h = soup.find(lambda tag: tag.name in ["h2","h3"] and keyword in tag.get_text(strip=True).lower())
#         if not h: return None
#         points = []
#         for sib in h.find_next_siblings():
#             if sib.name in ["h2","h3"]: break
#             if sib.name=="ul":
#                 for li in sib.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt: points.append(f"- {txt}")
#             elif sib.name=="p":
#                 txt = sib.get_text(strip=True)
#                 if txt: points.append(f"- {txt}")
#         return f"{title_prefix} {disease_name.capitalize()}:\n" + "\n".join(points) if points else None
#     except: return None

# def fetch_symptoms(url,disease_name): return fetch_points(url,"symptoms",disease_name,"The common symptoms of")
# def fetch_treatment(url,disease_name): return fetch_points(url,"treatment",disease_name,"The common treatments for")
# def fetch_prevention(url,disease_name): return fetch_points(url,"prevention",disease_name,"The common prevention methods for")

# # -------------------
# # WHO Outbreak
# # -------------------
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
#         r = requests.get(WHO_API_URL, timeout=10)
#         r.raise_for_status()
#         data = r.json()
#         if "value" not in data or not data["value"]: return None
#         out = []
#         for item in data["value"][:5]:
#             title = item.get("OverrideTitle") or item.get("Title")
#             date = item.get("FormattedDate","Unknown date")
#             url = "https://www.who.int"+item.get("ItemDefaultUrl","")
#             out.append(f"🦠 {title} ({date})\n🔗 {url}")
#         return out
#     except: return None

# # -------------------
# # Polio Schedule
# # -------------------
# def build_polio_schedule(birth_date):
#     sched=[]
#     sched.append(("At Birth (within 15 days)", birth_date, "OPV-0"))
#     sched.append(("6 Weeks", birth_date + datetime.timedelta(weeks=6), "OPV-1 + IPV-1"))
#     sched.append(("10 Weeks", birth_date + datetime.timedelta(weeks=10), "OPV-2"))
#     sched.append(("14 Weeks", birth_date + datetime.timedelta(weeks=14), "OPV-3 + IPV-2"))
#     sched.append(("16–24 Months", birth_date + datetime.timedelta(weeks=72), "OPV + IPV Boosters"))
#     sched.append(("5 Years", birth_date + datetime.timedelta(weeks=260), "OPV Booster"))
#     return sched

# # -------------------
# # Flask Webhook
# # -------------------
# @app.route('/webhook',methods=['POST'])
# def webhook():
#     req=request.get_json()
#     intent=req.get("queryResult", {}).get("intent", {}).get("displayName","")
#     params=req.get("queryResult", {}).get("parameters",{})
#     disease=params.get("disease","").strip()

#     try: detected_lang=detect(disease) if disease else "en"
#     except: detected_lang="en"

#     disease_en=translate_to_english(disease, detected_lang).strip().lower()
#     user_lang=detected_lang if detected_lang in INDIAN_LANGUAGES else "en"
#     response_text="Sorry, I don't understand your request."

#     # --- Overview ---
#     if intent=="get_disease_overview":
#         slug=get_slug(disease_en)
#         if slug:
#             url=f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#             response_text=fetch_overview(url) or f"Overview not found for {disease_en.capitalize()}. More: {url}"
#         else: response_text=f"Disease not found."

#     # --- Symptoms ---
#     elif intent=="get_symptoms":
#         slug=get_slug(disease_en)
#         if slug:
#             url=f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#             response_text=fetch_symptoms(url,disease_en) or f"Symptoms not found for {disease_en.capitalize()}. More: {url}"

#     # --- Treatment ---
#     elif intent=="get_treatment":
#         slug=get_slug(disease_en)
#         if slug:
#             url=f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#             response_text=fetch_treatment(url,disease_en) or f"Treatment not found for {disease_en.capitalize()}. More: {url}"

#     # --- Prevention ---
#     elif intent=="get_prevention":
#         slug=get_slug(disease_en)
#         if slug:
#             url=f"https://www.who.int/news-room/fact-sheets/detail/{slug}"
#             response_text=fetch_prevention(url,disease_en) or f"Prevention not found for {disease_en.capitalize()}. More: {url}"

#     # --- Outbreak ---
#     elif intent=="disease_outbreak.general":
#         outbreaks=get_who_outbreak_data()
#         response_text="⚠️ Unable to fetch outbreak data." if not outbreaks else "🌍 Latest WHO Outbreak News:\n\n"+ "\n\n".join(outbreaks)

#     # --- Vaccine ---
#     elif intent=="get_vaccine":
#         birth_date_str=params.get("date")
#         birth_date=datetime.date.today()  # default to today
#         if birth_date_str:
#             try:
#                 birth_date=datetime.datetime.strptime(birth_date_str[:10],"%Y-%m-%d").date()
#             except:
#                 pass

#         sched=build_polio_schedule(birth_date)
#         lines=["🧾 POLIO VACCINATION SCHEDULE"]
#         lines.append("\n1️⃣ Vaccine Name 🧪\n👉 Oral Polio Vaccine (OPV) + Injectable Polio Vaccine (IPV)")
#         lines.append("\n2️⃣ Period of Time / Age ⏳\n👉 From birth up to 5 years")
#         lines.append("\n3️⃣ Vaccination Date & Last Date 📅")
#         for period,date,vaccine_name in sched:
#             lines.append(f"- {period}: {date.strftime('%d-%b-%Y')} → {vaccine_name}")
#         lines.append("\n4️⃣ Disease & Symptoms ⚠️\n👉 Polio causes fever 🤒, weakness 😴, headache 🤕, vomiting 🤮, stiffness 🧍‍♂️, paralysis 🚶‍♂️❌")
#         lines.append("\n5️⃣ About the Vaccine ℹ️\n👉 OPV (oral drops) 👅, IPV (injection) 💉, free under Govt.")
#         lines.append("\n6️⃣ Purpose 🎯\n👉 Prevents life-long paralysis & disability.")
#         lines.append("\n7️⃣ Gender 👦👧\n👉 For all children.")
#         lines.append("\n8️⃣ Where to Get 🏥\n👉 Govt hospitals, PHCs, Anganwadis, ASHA workers.")
#         lines.append("\n9️⃣ Side Effects ⚠️\n👉 Safe 👍; rarely mild fever. Consult doctor if severe 🚑")
#         lines.append("\n🔟 After Vaccination ✅\n👉 Feed normally 🍼, stay 30 mins at centre, don’t skip future doses.")
#         lines.append(f"\n1️⃣1️⃣ Next Dose Reminder ⏰\n👉 Next after birth dose: {sched[1][1].strftime('%d-%b-%Y')} (OPV-1 + IPV-1)")
#         lines.append("\n1️⃣2️⃣ Pulse Polio Campaign 📢\n👉 Even if vaccinated, attend Pulse Polio days.")
#         response_text="\n".join(lines)
#         response_text=translate_from_english(response_text,user_lang)

#     return jsonify({"fulfillmentText": response_text})

# if __name__=="__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)
