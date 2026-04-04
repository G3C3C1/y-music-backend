import os
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

PREFIX = "/muzik"

# Senin çalışan kodundan aldığımız ayarların Render uyarlaması
def get_ydl_opts():
    return {
        "format": "bestaudio/best", # En iyi ses kalitesini zorla
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "cookiefile": "cookies.txt", # Bu dosya GitHub'da MUTLAKA olmalı
        "noplaylist": True,
        # Render için ekstra "insan" taklidi
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "ios"],
                "skip": ["dash", "hls"]
            }
        }
    }

@app.route("/")
def home():
    return app.send_static_file("index.html")

@app.route(f"{PREFIX}/ara")
def ara():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"sonuclar": []})

    try:
        # Senin kodundaki extract_info mantığı
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            # Arama yaparken skip_download: True ekliyoruz (senin koddaki gibi)
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)
            
        if not info or 'entries' not in info:
            return jsonify({"sonuclar": []})

        sonuclar = []
        for entry in info.get("entries", []):
            if entry:
                # Oynatılabilir direkt URL'i çekiyoruz
                audio_url = entry.get("url")
                
                # Eğer url yoksa formatlar içinden en iyisini seç (Senin sarki_link_al mantığı)
                if not audio_url and "formats" in entry:
                    audio_url = entry["formats"][0].get("url")

                sonuclar.append({
                    "title": entry.get("title", "Bilinmeyen"),
                    "url": audio_url,
                    "thumbnail": entry.get("thumbnail", ""),
                    # Süre formatını senin koddaki gibi hesaplıyoruz
                    "duration": f"{entry.get('duration', 0)//60}:{entry.get('duration', 0)%60:02d}"
                })

        return jsonify({"sonuclar": sonuclar})

    except Exception as e:
        return jsonify({
            "hata": "YouTube erişim hatası!",
            "detay": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
