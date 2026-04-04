import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

PREFIX = "/muzik"

# YouTube'u ikna etmek için en esnek ayarlar
YDL_OPTS = {
    "cookiefile": "cookies.txt",
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    # "bestaudio" bulamazsan en iyi formatı seç (format hatasını önler)
    "format": "bestaudio/best",
    "noplaylist": True,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "ignoreerrors": True, # Hatalı videoları atla, durma
    "geo_bypass": True,    # Bölge kısıtlamalarını aşmaya çalış
}

@app.route(f"{PREFIX}/ara")
def ara():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"hata": "Lütfen arama terimi gir Yusuf!"}), 400

    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            # YouTube'da arama yap
            info = ydl.extract_info(f"ytsearch5:{q}", download=False)
            
        if not info or 'entries' not in info:
            return jsonify({"sonuclar": []})

        entries = info.get("entries", [])
        sonuclar = []

        for entry in entries:
            if not entry: continue
            
            # Ses linkini bulmak için en garanti yöntem
            audio_url = None
            
            # 1. Yöntem: Doğrudan URL'ye bak
            audio_url = entry.get("url")
            
            # 2. Yöntem: Eğer yukarıdaki yoksa formatlar içinde en iyisini ara
            if not audio_url and "formats" in entry:
                for f in entry["formats"]:
                    # Sadece ses olanı yakalamaya çalış
                    if f.get("acodec") != "none" and f.get("vcodec") == "none":
                        audio_url = f.get("url")
                        break
                # Hala yoksa ilk bulduğun formatı al
                if not audio_url:
                    audio_url = entry["formats"][0].get("url")

            if audio_url:
                sonuclar.append({
                    "title": entry.get("title", "Bilinmeyen Şarkı"),
                    "url": audio_url,
                    "thumbnail": entry.get("thumbnail", ""),
                    "duration": entry.get("duration", 0)
                })

        return jsonify({"sonuclar": sonuclar})

    except Exception as e:
        return jsonify({"hata": f"Bir şeyler ters gitti Yusuf: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
