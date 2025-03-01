from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from googletrans import Translator, LANGUAGES
from gtts import gTTS, lang as gtts_lang
import os

app = Flask(__name__, template_folder="VortexApplication", static_folder="vortex-assets")
CORS(app)

translator = Translator()

GTTS_SUPPORTED_LANGUAGES = set(gtts_lang.tts_langs().keys())

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPEECH_DIR = os.path.join(BASE_DIR, "speeches")

if not os.path.exists(SPEECH_DIR):
    os.makedirs(SPEECH_DIR)

@app.route("/")
def home():
    return render_template("vortex.html")

@app.route("/translate")
def translate_text():
    referer = request.headers.get("Referer")

    if not referer or "/" not in referer:
        return "Method Not Allowed", 405

    from_lang = request.args.get("from")
    to_lang = request.args.get("to")
    text = request.args.get("text")

    if not from_lang or not to_lang or not text:
        return "Missing required parameters: 'from', 'to', 'text'", 400

    try:
        translated = translator.translate(text, src=from_lang, dest=to_lang)
        return translated.text
    except Exception as e:
        return str(e), 500

@app.route("/speech-api")
def speak_mp4():
    referer = request.headers.get("Referer")

    if not referer or "/" not in referer:
        return "Method Not Allowed", 405
        
    text = request.args.get("speak")
    lang = request.args.get("lang", "en")

    if not text:
        return "Missing required parameter: 'speak'", 400

    if lang not in GTTS_SUPPORTED_LANGUAGES:
        lang = "en"

    try:
        file_name = f"speech_{lang}.mp3"
        file_path = os.path.join(SPEECH_DIR, file_name)

        tts = gTTS(text=text, lang=lang)
        tts.save(file_path)

        return send_file(file_path, mimetype="audio/mpeg", as_attachment=False)

    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
