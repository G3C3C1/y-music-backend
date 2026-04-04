import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

PREFIX = "/muzik"

YDL_OPTS = {
    "cookiefile": "cookies.txt",
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    # Hata veren spesifik format yerine en geniş seçeneği kullanıyoruz
    "format": "best", 
    "noplaylist": True,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "web"],
            "skip": ["dash", "hls"]
        }
    },
    "ignoreerrors": True,
}

@app.route(f"{PREFIX}/ara")
def ara():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"sonuclar": []})

    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            # YouTube araması yap
            info = ydl.extract_info(f"ytsearch5:{q}", download=False)
            
        if not info or 'entries' not in info:
            return jsonify({"sonuclar": []})

        entries = [e for e in info.get("entries", []) if e is not None]
        sonuclar = []

        for entry in entries:
            # Format hatası almamak için bulabildiği en iyi direkt linki alıyoruz
            audio_url = entry.get("url")
            
            # Eğer ana URL yoksa format listesindeki ilk çalışan linki al
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
        return jsonify({"hata": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
