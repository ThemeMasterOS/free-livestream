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
    """Formats track as 'Artist - Song name [NCS]'.
    Strips out extra tags like '[NCS Release]' so titles stay clean.
    """
    if artist and title:
        # 1. Clean up extra tag bloat from the title
        title = (
            title.replace("[NCS Release]", "")
                 .replace("(NCS Release)", "")
                 .strip()
        )
        
        # 2. Build the display string
        single_line = f"{artist} - {title} [NCS]"
        
        # Optional: Split long titles into 2 lines if still > 35 chars
        if len(single_line) > 35:
            return f"{artist}\n{title} [NCS]"
            
        return single_line
        
    elif title:
        title = (
            title.replace("[NCS Release]", "")
                 .replace("(NCS Release)", "")
                 .strip()
        )
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
