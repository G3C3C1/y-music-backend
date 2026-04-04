import os
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

PREFIX = "/muzik"

# COOKIES DOSYASI BURADA GERİ GELDİ 🚀
YDL_OPTS = {
    "cookiefile": "cookies.txt",  # GitHub'daki cookies.txt dosyasını kullanır
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    "format": "bestaudio/best",
    "noplaylist": True,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "ios"],
            "skip": ["dash", "hls"]
        }
    },
    "socket_timeout": 15,
    "retries": 5,
    "ignoreerrors": True
}

@app.route("/")
def home():
    try:
        return app.send_static_file("index.html")
    except Exception:
        return "Y Music Sunucusu Aktif! index.html bulunamadı.", 200

@app.route(f"{PREFIX}/ara")
def ara():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"sonuclar": []})

    try:
        # Her aramada yeni bir nesne oluşturmak bazen engelleri aşmaya yardımcı olur
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(f"ytsearch5:{q}", download=False)
            
        if not info or 'entries' not in info:
            return jsonify({"sonuclar": []})

        entries = [e for e in info.get("entries", []) if e is not None]
        sonuclar = []

        for entry in entries:
            audio_url = entry.get("url")
            if not audio_url and "formats" in entry:
                audio_url = entry["formats"][0].get("url")

            if audio_url:
                sonuclar.append({
                    "title": entry.get("title", "Müzik"),
                    "url": audio_url,
                    "thumbnail": entry.get("thumbnail", ""),
                })

        return jsonify({"sonuclar": sonuclar})

    except Exception as e:
        print(f"HATA: {str(e)}")
        return jsonify({
            "hata": "YouTube Engelini Aşamadık!",
            "detay": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
