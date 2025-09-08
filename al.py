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










from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory  # ✅ Auto language detection

app = Flask(__name__)

# -------------------
# Setup
# -------------------
DetectorFactory.seed = 0   # makes langdetect deterministic

# List of Indian language codes
INDIAN_LANGUAGES = [
    "hi",  # Hindi
    "te",  # Telugu
    "ta",  # Tamil
    "kn",  # Kannada
    "bn",  # Bengali
    "mr",  # Marathi
    "gu",  # Gujarati
    "ml",  # Malayalam
    "ur",  # Urdu
    "pa",  # Punjabi
    "or",  # Odia
    "ks"   # Kashmiri
]

# -------- Static mapping of diseases to WHO fact sheet URLs --------
DISEASE_OVERVIEWS = {
    "malaria": "https://www.who.int/news-room/fact-sheets/detail/malaria",
    "influenza": "https://www.who.int/news-room/fact-sheets/detail/influenza-(seasonal)",
    "dengue": "https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue",
    "hiv": "https://www.who.int/news-room/fact-sheets/detail/hiv-aids",
    "tuberculosis": "https://www.who.int/news-room/fact-sheets/detail/tuberculosis",
    "covid-19": "https://www.who.int/news-room/fact-sheets/detail/coronavirus-disease-(covid-19)",
    "cholera": "https://www.who.int/news-room/fact-sheets/detail/cholera",
    "measles": "https://www.who.int/news-room/fact-sheets/detail/measles",
    "ebola": "https://www.who.int/news-room/fact-sheets/detail/ebola-virus-disease",
    "zika": "https://www.who.int/news-room/fact-sheets/detail/zika-virus",
    "yellow fever": "https://www.who.int/news-room/fact-sheets/detail/yellow-fever",
    "hepatitis b": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-b",
    "hepatitis c": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-c",
    "rabies": "https://www.who.int/news-room/fact-sheets/detail/rabies",
    "meningitis": "https://www.who.int/news-room/fact-sheets/detail/meningitis",
    "leprosy": "https://www.who.int/news-room/fact-sheets/detail/leprosy",
    "schistosomiasis": "https://www.who.int/news-room/fact-sheets/detail/schistosomiasis",
    "trypanosomiasis": "https://www.who.int/news-room/fact-sheets/detail/trypanosomiasis-(sleeping-sickness)",
    "onchocerciasis": "https://www.who.int/news-room/fact-sheets/detail/onchocerciasis-(river-blindness)",
    "lyme disease": "https://www.who.int/news-room/fact-sheets/detail/lyme-disease",
}

# -------------------
# Translation helpers
# -------------------
def translate_to_english(disease_param):
    """Auto-detect input language and translate disease_param to English using MyMemory."""
    if not disease_param.strip():
        return disease_param

    try:
        detected_lang = detect(disease_param)   # e.g., "te", "hi", "kn"
    except Exception:
        detected_lang = "en"

    if detected_lang == "en":
        return disease_param

    try:
        url = f"https://api.mymemory.translated.net/get?q={disease_param}&langpair={detected_lang}|en"
        response = requests.get(url, timeout=10)
        data = response.json()
        translated = data.get("responseData", {}).get("translatedText")
        if translated:
            return translated
        return disease_param
    except Exception as e:
        print(f"MyMemory translation error: {e}")
        return disease_param


def translate_from_english(disease_param, target_lang):
    """Translate English disease_param back into the user’s original language."""
    if target_lang == "en" or not disease_param.strip():
        return disease_param

    try:
        url = f"https://api.mymemory.translated.net/get?q={disease_param}&langpair=en|{target_lang}"
        response = requests.get(url, timeout=10)
        data = response.json()
        translated = data.get("responseData", {}).get("translatedText")
        if translated:
            return translated
        return disease_param
    except Exception as e:
        print(f"MyMemory translation back error: {e}")
        return disease_param


# -------- Helper functions --------
def fetch_overview(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        heading = soup.find(lambda tag: tag.name in ["h2", "h3"] and "overview" in tag.get_text(strip=True).lower())
        if not heading:
            return None

        paragraphs = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ["h2", "h3"]:
                break
            if sibling.name == "p":
                disease_param = sibling.get_text(strip=True)
                if disease_param:
                    paragraphs.append(disease_param)

        if paragraphs:
            return " ".join(paragraphs)
        return None
    except Exception:
        return None


def fetch_symptoms(url, disease_param):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        heading = soup.find(
            lambda tag: tag.name in ["h2", "h3"] 
            and ("symptoms" in tag.get_text(strip=True).lower() 
                 or "signs and symptoms" in tag.get_text(strip=True).lower())
        )
        if not heading:
            return None

        points = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ["h2", "h3"]:
                break
            if sibling.name == "ul":
                for li in sibling.find_all("li"):
                    disease_param = li.get_text(strip=True)
                    if disease_param:
                        points.append(f"- {disease_param}")

        if not points:
            paragraphs = []
            for sibling in heading.find_next_siblings():
                if sibling.name in ["h2", "h3"]:
                    break
                if sibling.name == "p":
                    disease_param = sibling.get_text(strip=True)
                    if disease_param:
                        paragraphs.append(f"- {disease_param}")
            points = paragraphs

        if points:
            return f"The common symptoms of {disease_param.capitalize()} are:\n" + "\n".join(points)
        return None
    except Exception:
        return None


def fetch_treatment(url, disease_param):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        heading = soup.find(
            lambda tag: tag.name in ["h2", "h3"] 
            and ("treatment" in tag.get_text(strip=True).lower() 
                 or "management" in tag.get_text(strip=True).lower())
        )
        if not heading:
            return None

        points = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ["h2", "h3"]:
                break
            if sibling.name == "ul":
                for li in sibling.find_all("li"):
                    disease_param = li.get_text(strip=True)
                    if disease_param:
                        points.append(f"- {disease_param}")

        if not points:
            paragraphs = []
            for sibling in heading.find_next_siblings():
                if sibling.name in ["h2", "h3"]:
                    break
                if sibling.name == "p":
                    disease_param = sibling.get_text(strip=True)
                    if disease_param:
                        paragraphs.append(f"- {disease_param}")
            points = paragraphs

        if points:
            return f"The common treatments for {disease_param.capitalize()} are:\n" + "\n".join(points)
        return None
    except Exception:
        return None


def fetch_prevention(url, disease_param):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        heading = soup.find(lambda tag: tag.name in ["h2", "h3"] and "prevention" in tag.get_text(strip=True).lower())
        if not heading:
            return None

        points = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ["h2", "h3"]:
                break
            if sibling.name == "ul":
                for li in sibling.find_all("li"):
                    disease_param = li.get_text(strip=True)
                    if disease_param:
                        points.append(f"- {disease_param}")

        if not points:
            paragraphs = []
            for sibling in heading.find_next_siblings():
                if sibling.name in ["h2", "h3"]:
                    break
                if sibling.name == "p":
                    disease_param = sibling.get_text(strip=True)
                    if disease_param:
                        paragraphs.append(f"- {disease_param}")
            points = paragraphs

        if points:
            return f"The common prevention methods for {disease_param.capitalize()} are:\n" + "\n".join(points)
        return None
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

        if "value" not in data or not data["value"]:
            return None

        outbreaks = []
        for item in data["value"][:5]:
            title = item.get("OverrideTitle") or item.get("Title")
            date = item.get("FormattedDate", "Unknown date")
            url = "https://www.who.int" + item.get("ItemDefaultUrl", "")
            outbreaks.append(f"🦠 {title} ({date})\n🔗 {url}")

        return outbreaks
    except Exception:
        return None


# -------- Flask webhook route --------
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent_name = req["queryResult"]["intent"]["displayName"]
    params = req["queryResult"].get("parameters", {})
    disease_input = params.get("disease", "").strip()

    # ✅ Detect user input language once
    try:
        detected_lang = detect(disease_input) if disease_input else "en"
    except Exception:
        detected_lang = "en"

    # Only translate back if detected language is an Indian language
    user_lang = detected_lang if detected_lang in INDIAN_LANGUAGES else "en"

    # ✅ Translate disease_param into English first
    disease_param = translate_to_english(disease_input).lower()


    response_text = "Sorry, I don't understand your request."

    if intent_name == "get_disease_overview":
        url = DISEASE_OVERVIEWS.get(disease_param)
        if url:
            overview = fetch_overview(url)
            response_text = overview or f"Overview not found for {disease_param.capitalize()}. You can read more here: {url}"
        else:
            response_text = f"Disease not found. Make sure to use a valid disease name."

    elif intent_name == "get_symptoms":
        url = DISEASE_OVERVIEWS.get(disease_param)
        if url:
            symptoms = fetch_symptoms(url, disease_param)
            response_text = symptoms or f"Symptoms not found for {disease_param.capitalize()}. You can read more here: {url}"
        else:
            response_text = f"Sorry, I don't have a URL for {disease_param.capitalize()}."

    elif intent_name == "get_treatment":
        url = DISEASE_OVERVIEWS.get(disease_param)
        if url:
            treatment = fetch_treatment(url, disease_param)
            response_text = treatment or f"Treatment details not found for {disease_param.capitalize()}. You can read more here: {url}"
        else:
            response_text = f"Sorry, I don't have a URL for {disease_param.capitalize()}."

    elif intent_name == "get_prevention":
        url = DISEASE_OVERVIEWS.get(disease_param)
        if url:
            prevention = fetch_prevention(url, disease_param)
            response_text = prevention or f"Prevention methods not found for {disease_param.capitalize()}. You can read more here: {url}"
        else:
            response_text = f"Sorry, I don't have a URL for {disease_param.capitalize()}."

    elif intent_name == "disease_outbreak.general":
        outbreaks = get_who_outbreak_data()
        if not outbreaks:
            response_text = "⚠️ Unable to fetch outbreak data right now."
        else:
            response_text = "🌍 Latest WHO Outbreak News:\n\n" + "\n\n".join(outbreaks)

    # ✅ Translate final response back to user’s language only if it is an Indian language
    response_text = translate_from_english(response_text, user_lang)

    return jsonify({"fulfillmentText": response_text})


if __name__ == '__main__':
    app.run(debug=True)
