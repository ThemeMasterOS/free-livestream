import requests
import time

API_URL = "https://api.laut.fm/station/ncs/current_song"
TEXT_FILE = "current_song.txt"

# Set this to match FFmpeg's normal audio delay (usually ~13 to 15 seconds)
BUFFER_DELAY = 13  

def update_text(message: str):
    try:
        with open(TEXT_FILE, "w", encoding="utf-8") as f:
            f.write(message)
        print(f"[TRACKER] Overlay Updated:\n{message}")
    except Exception as e:
        print(f"[ERROR] Could not write file: {e}")

def format_song_display(title: str, artist: str) -> str:
    if not title:
        return "Searching song..."
        
    # Filter station/ad labels
    combined = f"{artist} {title}".lower()
    ad_keywords = ["werbung", "advertisement", "spinquest", "shopify", "laut.fm", "preroll"]
    if any(keyword in combined for keyword in ad_keywords):
        return "Sponsor"

    clean_title = (
        title.replace("[NCS Release]", "")
             .replace("(NCS Release)", "")
             .replace("[NCS]", "")
             .strip()
    )
    
    if artist and artist.lower() not in ["unknown", "", "none"]:
        single_line = f"{artist.strip()} - {clean_title} [NCS]"
        if len(single_line) > 35:
            return f"{artist.strip()}\n{clean_title} [NCS]"
        return single_line
        
    return f"{clean_title} [NCS]"

def main():
    last_display = ""
    
    while True:
        try:
            res = requests.get(API_URL, timeout=5)
            if res.status_code == 200:
                data = res.json()
                title = data.get("title", "").strip()
                artist = data.get("artist", {}).get("name", "").strip()
                
                formatted = format_song_display(title, artist)
            else:
                formatted = "Searching song..."
        except Exception:
            formatted = "Searching song..."

        if formatted != last_display:
            if last_display != "":
                print(f"[TRACKER] Song change detected. Waiting {BUFFER_DELAY}s for FFmpeg buffer...")
                time.sleep(BUFFER_DELAY)
                
            update_text(formatted)
            last_display = formatted

        time.sleep(5)

if __name__ == "__main__":
    update_text("Searching song...")
    main()
