import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

PREFIX = "/muzik"

# YouTube'un yeni korumalarını aşmak için optimize edilmiş ayarlar
YDL_OPTS = {
    "cookiefile": "cookies.txt",
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    "format": "bestaudio/best",
    "noplaylist": True,
    # YouTube'un gerçek uygulama gibi görmesi için User-Agent ve Client ayarları
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "web"],
            "skip": ["dash", "hls"]
        }
    },
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
            # YouTube'da arama yap ve video bilgilerini çek
            info = ydl.extract_info(f"ytsearch5:{q}", download=False)
            
        if not info or 'entries' not in info:
            return jsonify({"sonuclar": []})

        # Boş sonuçları temizle
        entries = [e for e in info.get("entries", []) if e is not None]
        sonuclar = []

        for entry in entries:
            # Oynatılabilir direkt linki bulma mantığı
            audio_url = entry.get("url")
            
            if not audio_url and "formats" in entry:
                # Önce sadece ses (audio) olan kaliteli formatları ara
                formats = entry.get("formats", [])
                for f in formats:
                    if f.get("acodec") != "none" and f.get("vcodec") == "none":
                        audio_url = f.get("url")
                        break
                # Bulamazsa çalışan ilk linki al
                if not audio_url and formats:
                    audio_url = formats[0].get("url")

            if audio_url:
                sonuclar.append({
                    "title": entry.get("title", "Müzik"),
                    "url": audio_url,
                    "thumbnail": entry.get("thumbnail", ""),
                    "duration": entry.get("duration", 0)
                })

        return jsonify({"sonuclar": sonuclar})

    except Exception as e:
        # Hata olursa detaylı mesaj gönder
        return jsonify({"hata": str(e)}), 500

if __name__ == "__main__":
    # Render'ın dinamik port ayarı
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
