import os
import re
import shutil
import tempfile
from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(
    app,
    origins="*",
    methods=["GET", "POST", "OPTIONS", "HEAD"],
    allow_headers=["*", "Content-Type", "Authorization", "X-Requested-With", "Range"],
    expose_headers=["Content-Disposition", "Content-Length", "Content-Type", "Content-Range"],
    max_age=600,
)

PREFIX = "/muzik"

YDL_SEARCH_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
    "nocheckcertificate": True,
    "format": "bestaudio[ext=m4a]/bestaudio",
    "noplaylist": True,
}


def ensure_https(url: str) -> str:
    if url and url.startswith("http://"):
        return "https://" + url[7:]
    return url


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.strip(". ")
    return name or "ses"


@app.route(f"{PREFIX}/ara")
def ara():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"hata": "q parametresi gerekli"}), 400

    try:
        with yt_dlp.YoutubeDL(YDL_SEARCH_OPTS) as ydl:
            info = ydl.extract_info(f"ytsearch5:{q}", download=False)
    except Exception as e:
        return jsonify({"hata": str(e)}), 500

    entries = info.get("entries", [])
    sonuclar = []

    for entry in entries:
        if not entry:
            continue

        video_id = entry.get("id", "")
        title = entry.get("title", "Bilinmiyor")
        thumbnail = ensure_https(
            entry.get("thumbnail") or f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
        )

        audio_url = None
        requested_formats = entry.get("requested_formats") or []
        formats = entry.get("formats") or []

        for fmt in requested_formats:
            if fmt.get("url"):
                audio_url = ensure_https(fmt["url"])
                break

        if not audio_url:
            for fmt in reversed(formats):
                ext = fmt.get("ext", "")
                acodec = fmt.get("acodec", "none")
                vcodec = fmt.get("vcodec", "none")
                if ext == "m4a" and acodec != "none":
                    audio_url = ensure_https(fmt["url"])
                    break
                if acodec != "none" and vcodec == "none" and fmt.get("url"):
                    audio_url = ensure_https(fmt["url"])

        if not audio_url and entry.get("url"):
            audio_url = ensure_https(entry["url"])

        if not audio_url:
            continue

        sonuclar.append({
            "title": title,
            "url": audio_url,
            "thumbnail": thumbnail,
        })

    return jsonify({"sonuclar": sonuclar})


@app.route(f"{PREFIX}/indir")
def indir():
    url = request.args.get("url", "").strip()
    if not url:
        return jsonify({"hata": "url parametresi gerekli"}), 400

    tmp_dir = tempfile.mkdtemp()

    @after_this_request
    def temizle(response):
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass
        return response

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "format": "bestaudio[ext=m4a]/bestaudio",
        "noplaylist": True,
        "outtmpl": os.path.join(tmp_dir, "%(title)s.%(ext)s"),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except Exception as e:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return jsonify({"hata": str(e)}), 500

    title = info.get("title", "ses")
    ext = info.get("ext", "m4a")
    safe_title = sanitize_filename(title)
    download_name = f"{safe_title}.{ext}"

    dosyalar = os.listdir(tmp_dir)
    if not dosyalar:
        return jsonify({"hata": "Dosya indirilemedi"}), 500

    dosya_yolu = os.path.join(tmp_dir, dosyalar[0])
    mimetype = "audio/mp4" if ext == "m4a" else "audio/mpeg"

    return send_file(
        dosya_yolu,
        mimetype=mimetype,
        as_attachment=True,
        download_name=download_name,
    )


@app.route(f"{PREFIX}/saglik")
def saglik():
    return jsonify({"durum": "calisiyor"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
