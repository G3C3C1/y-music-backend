import os
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

PREFIX = "/muzik"

# YouTube bot engellerini ve format hatalarını aşmak için optimize ayarlar
YDL_OPTS = {
    "cookiefile": "cookies.txt",
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    "format": "best", # En esnek format seçeneği
    "noplaylist": True,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
    "ignoreerrors": True,
    "geo_bypass": True,
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

        # Boş dönen sonuçları ayıkla
        entries = [e for e in info.get("entries", []) if e is not None]
        sonuclar = []

        for entry in entries:
            audio_url = entry.get("url")
            # Link yoksa formatlar arasından ilkini zorla al
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
        # HATA YAKALAMA: Hatayı detaylandırıp JavaScript'e gönderir
        hata_metni = traceback.format_exc()
        print(f"HATA OLUŞTU:\n{hata_metni}")
        return jsonify({
            "hata": str(e),
            "detay": hata_metni
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
