from flask import Flask, jsonify, request
import yt_dlp
import os
import base64

app = Flask(__name__)

# Get YouTube cookies from Render Environment Variable
cookies_b64 = os.environ.get("YOUTUBE_COOKIES_B64")

if cookies_b64:
    try:
        with open("/tmp/cookies.txt", "wb") as f:
            f.write(base64.b64decode(cookies_b64))
    except Exception as e:
        print("Cookie file creation failed:", e)


@app.route("/get-audio", methods=["GET"])
def get_audio():
    query = request.args.get("q")

    if not query:
        return jsonify({
            "error": "Query parameter 'q' is required"
        }), 400

    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "default_search": "ytsearch1",
        "cookiefile": "/tmp/cookies.txt",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)

            if "entries" in info:
                entries = info.get("entries")

                if not entries:
                    return jsonify({
                        "error": "No results found on YouTube"
                    }), 404

                info = entries[0]

            audio_url = info.get("url")
            title = info.get("title")
            thumbnail = info.get("thumbnail")

            if not audio_url:
                return jsonify({
                    "error": "Could not extract audio stream URL"
                }), 500

            return jsonify({
                "title": title,
                "audio_url": audio_url,
                "thumbnail": thumbnail
            })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )