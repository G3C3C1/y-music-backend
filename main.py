import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

# Render'daki URL yapısına uygun prefix
PREFIX = "/muzik"

# YouTube bot engelini aşmak için kritik ayarlar
YDL_OPTS = {
    "cookiefile": "cookies.txt",  # GitHub'a yüklediğin çerez dosyasını okur
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    "format": "bestaudio/best",
    "noplaylist": True,
    # Gerçek bir tarayıcı gibi görünmek için User-Agent
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

@app.route(f"{PREFIX}/ara")
def ara():
    # Arama terimini al (Örn: /muzik/ara?q=numb)
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"hata": "Lütfen bir arama terimi gir Yusuf!"}), 400

    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            # YouTube'da ilk 5 sonucu ara
            info = ydl.extract_info(f"ytsearch5:{q}", download=False)
            
        entries = info.get("entries", [])
        sonuclar = []

        for entry in entries:
            if not entry: continue
            
            # Doğrudan oynatılabilir ses URL'sini bul
            audio_url = None
            if "formats" in entry:
                # Sadece ses (audio) olan formatları filtrele
                for f in entry["formats"]:
                    if f.get("acodec") != "none" and f.get("vcodec") == "none":
                        audio_url = f.get("url")
                        break
            
            # Eğer yukarıda bulunamazsa genel URL'yi dene
            if not audio_url:
                audio_url = entry.get("url")

            if audio_url:
                sonuclar.append({
                    "title": entry.get("title", "Bilinmeyen Şarkı"),
                    "url": audio_url,
                    "thumbnail": entry.get("thumbnail", ""),
                    "duration": entry.get("duration", 0)
                })

        return jsonify({"sonuclar": sonuclar})

    except Exception as e:
        # Hata olursa tarayıcıda gördüğün o siyah ekrandaki mesajı döner
        return jsonify({"hata": str(e)}), 500

# Render için port ayarı
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
