import urllib.request
import re
import time

STREAM_URL = "https://stream.laut.fm/ncs"  # Stream audio URL
TEXT_FILE = "current_song.txt"
FFMPEG_BUFFER_DELAY = 13  # Delay in seconds to match FFmpeg's audio buffer

def update_text(message: str):
    try:
        with open(TEXT_FILE, "w", encoding="utf-8") as f:
            f.write(message)
        print(f"[ICY TRACKER] Overlay Updated:\n{message}")
    except Exception as e:
        print(f"[ERROR] Failed to write file: {e}")

def format_song_display(raw_title: str) -> str:
    """Formats the track name or sets display to 'Sponsor' during ad breaks."""
    if not raw_title:
        return "Sponsor"
        
    title_lower = raw_title.lower().strip()
    
    # 1. Detect Ad / Commercial / Station Spot Metadata
    ad_keywords = ["werbung", "advertisement", "sponsor", "laut.fm", "preroll"]
    if any(keyword in title_lower for keyword in ad_keywords):
        return "Sponsor"

    # 2. Clean up regular song titles
    clean = (
        raw_title.replace("[NCS Release]", "")
                 .replace("(NCS Release)", "")
                 .replace("[NCS]", "")
                 .strip()
    )
    
    if " - " not in clean:
        return "Sponsor" if len(clean) < 3 else f"{clean} [NCS]"
    
    artist, title = clean.split(" - ", 1)
    artist_clean = artist.strip()
    title_clean = title.strip()
    
    if not artist_clean or not title_clean:
        return "Sponsor"

    single_line = f"{artist_clean} - {title_clean} [NCS]"
    
    if len(single_line) > 35:
        return f"{artist_clean}\n{title_clean} [NCS]"
        
    return single_line

def parse_icy_stream():
    req = urllib.request.Request(STREAM_URL, headers={'Icy-MetaData': '1'})
    
    print(f"[ICY TRACKER] Connecting to stream: {STREAM_URL}")
    with urllib.request.urlopen(req) as response:
        metaint = int(response.headers.get('icy-metaint', 0))
        
        if metaint == 0:
            print("[ERROR] Stream does not support ICY metadata!")
            return

        print(f"[ICY TRACKER] Connected! Metadata interval: {metaint} bytes")
        last_display = ""

        while True:
            response.read(metaint)
            
            meta_len_byte = response.read(1)
            if not meta_len_byte:
                break
                
            meta_len = ord(meta_len_byte) * 16
            
            if meta_len > 0:
                meta_data = response.read(meta_len).decode('utf-8', errors='ignore')
                
                match = re.search(r"StreamTitle='(.*?)';", meta_data)
                if match:
                    raw_title = match.group(1).strip()
                    formatted = format_song_display(raw_title)
                    
                    if formatted != last_display:
                        # Don't delay on initial script startup
                        if last_display != "":
                            print(f"[ICY TRACKER] Track change detected. Delaying {FFMPEG_BUFFER_DELAY}s for FFmpeg audio buffer...")
                            time.sleep(FFMPEG_BUFFER_DELAY)
                            
                        update_text(formatted)
                        last_display = formatted

def main():
    while True:
        try:
            parse_icy_stream()
        except Exception as e:
            print(f"[WARN] Connection dropped: {e}. Reconnecting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    update_text("Searching song...")
    main()
