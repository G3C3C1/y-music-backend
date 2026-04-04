import os
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

# Flask'ı statik dosyaları (HTML/CSS/JS) görecek şekilde yapılandırıyoruz
app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

PREFIX = "/muzik"

# YouTube engellerini aşmak için en güncel ve hafif ayarlar
YDL_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    "format": "bestaudio/best", # Sadece ses çekerek hızı artırır
    "noplaylist": True,
    # Render IP engellerini aşmak için kritik User-Agent
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "ios"], # Mobil istemci gibi davranır (daha az engel yer)
            "skip": ["dash", "hls"]
        }
    },
    "socket_timeout": 10,
    "retries": 3
}

# ANA SAYFA: https://y-music-backend.onrender.com/ adresine girince index.html'i açar
@app.route("/")
def home():
    try:
        return app.send_static_file("index.html")
    except Exception:
        return "Ana sayfa (index.html) bulunamadı ama sunucu aktif!", 200

# ARAMA MOTORU: Müzik arama işlemini yapar
@app.route(f"{PREFIX}/ara")
def ara():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"sonuclar": []})

    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            # YouTube'da ilk 5 sonucu ara
            info = ydl.extract_info(f"ytsearch5:{q}", download=False)
            
        if not info or 'entries' not in info:
            return jsonify({"sonuclar": []})

        entries = [e for e in info.get("entries", []) if e is not None]
        sonuclar = []

        for entry in entries:
            # Doğrudan ses linkini al
            audio_url = entry.get("url")
            if not audio_url and "formats" in entry:
                # Eğer ana url yoksa formatlar içinden en uygununu seç
                audio_url = entry["formats"][0].get("url")

            if audio_url:
                sonuclar.append({
                    "title": entry.get("title", "Bilinmeyen Parça"),
                    "url": audio_url,
                    "thumbnail": entry.get("thumbnail", ""),
                    "duration": entry.get("duration")
                })

        return jsonify({"sonuclar": sonuclar})

    except Exception as e:
        hata_detay = traceback.format_exc()
        print(f"HATA OLUŞTU:\n{hata_detay}")
        return jsonify({
            "hata": "YouTube erişiminde bir sorun oluştu.",
            "detay": str(e)
        }), 500

# Render'ın atadığı portu yakala
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
