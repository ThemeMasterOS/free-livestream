import time
import requests

TEXT_FILE = "current_song.txt"
API_URL = "https://api.laut.fm/station/ncs/current_song"

def update_text(message: str):
    try:
        with open(TEXT_FILE, "w", encoding="utf-8") as f:
            f.write(message)
        print(f"[SONG TRACKER] Updated overlay: {message}")
    except Exception as e:
        print(f"[ERROR] Failed to write file: {e}")

def main():
    last_song = ""
    
    while True:
        try:
            res = requests.get(API_URL, timeout=5)
            if res.status_code == 200:
                data = res.json()
                title = data.get("title", "").strip()
                artist = data.get("artist", {}).get("name", "").strip()

                if title and artist:
                    current = f"{title} - {artist} [NCS]"
                elif title:
                    current = f"{title} [NCS]"
                else:
                    current = "Song not found"
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
