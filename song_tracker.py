import time
import requests

TEXT_FILE = "current_song.txt"
API_URL = "https://api.laut.fm/station/ncs/current_song"


def update_text(message: str):
    try:
        with open(TEXT_FILE, "w", encoding="utf-8") as f:
            f.write(message)
        print(f"[SONG TRACKER] Updated overlay:\n{message}")
    except Exception as e:
        print(f"[ERROR] Failed to write file: {e}")


def format_song_display(title: str, artist: str) -> str:
    """Formats the song text. 
    If it's longer than 35 chars, it splits onto 2 lines so FFmpeg centers it cleanly.
    """
    if title and artist:
        single_line = f"{title} - {artist} [NCS]"
        # If text length exceeds 35 characters, split across two lines
        if len(single_line) > 35:
            return f"{title}\n{artist} [NCS]"
        return single_line
    elif title:
        return f"{title} [NCS]"
    
    return "Song not found"


def main():
    last_song = ""
    
    while True:
        try:
            res = requests.get(API_URL, timeout=5)
            if res.status_code == 200:
                data = res.json()
                title = data.get("title", "").strip()
                artist = data.get("artist", {}).get("name", "").strip()

                current = format_song_display(title, artist)
            else:
                current = "Searching song..."
        except Exception:
            current = "Searching song..."

        if current != last_song:
            update_text(current)
            last_song = current

        time.sleep(5)


if __name__ == "__main__":
    update_text("Searching song...")
    main()
