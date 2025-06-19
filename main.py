
from flask import Flask, render_template, request
import yt_dlp

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    video_info = None
    download_links = []
    error = None

    if request.method == "POST":
        query = request.form["query"]
        format_type = request.form["format"]

        try:
            ydl_opts = {
                'quiet': True,
                'noplaylist': True,
                'default_search': 'ytsearch',
                'skip_download': True,
                'simulate': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                if 'entries' in info:
                    info = info['entries'][0]

                video_info = {
                    "title": info.get("title"),
                    "duration": info.get("duration_string", ""),
                    "thumbnail": info.get("thumbnail"),
                    "channel": info.get("uploader"),
                    "link": info.get("webpage_url"),
                    "description": info.get("description", "No description available.")[:300],
                }

                formats = info.get("formats", [])
                for f in formats:
                    filesize = f.get('filesize') or f.get('filesize_approx') or 0
                    size_mb = round(filesize / 1024 / 1024, 2) if filesize else "?"

                    if format_type == 'mp4' and f.get("vcodec") != "none":
                        download_links.append({
                            "format": f"{f.get('format_note', 'MP4')} - {size_mb} MB",
                            "url": f.get("url")
                        })
                    elif format_type == 'mp3' and f.get("acodec") != "none" and f.get("vcodec") == "none":
                        download_links.append({
                            "format": f"{f.get('abr', 'MP3')} - {size_mb} MB",
                            "url": f.get("url")
                        })

        except Exception as e:
            error = f"Error: {str(e)}"

    return render_template("index.html", video=video_info, downloads=download_links, error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
