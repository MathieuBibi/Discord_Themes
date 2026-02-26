import os
import json
import urllib.parse

BASE_URL = "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets"
REPO_PATH = "C:/Users/mathi/Programming Projects/Emoji Mapper/fluentui-emoji/assets"

THEME_HEADER = """/**
 * @name FluentEmojiMapper2
 * @author Mat, LunaticCat, GoogleGemini
 * @description Makes Emoji in Messages look like Microsoft Fluent 3D Emojis
 * @version 2.0.0
 */

"""

TONE_MAP = {
    "Light": "1f3fb",
    "Medium-Light": "1f3fc",
    "Medium": "1f3fd",
    "Medium-Dark": "1f3fe",
    "Dark": "1f3ff"
}

def generate_css():
    css_lines = []
    skipped_count = 0
    
    if not os.path.exists(REPO_PATH):
        print(f"Error: Path {REPO_PATH} not found.")
        return

    #Iterate through every folder in assets
    for emoji_folder in sorted(os.listdir(REPO_PATH)):
        emoji_path = os.path.join(REPO_PATH, emoji_folder)
        if not os.path.isdir(emoji_path): continue
            
        #Get Base Unicode from root metadata
        root_meta_path = os.path.join(emoji_path, "metadata.json")
        base_unicode = ""
        if os.path.exists(root_meta_path):
            with open(root_meta_path, 'r', encoding="utf-8") as f:
                try:
                    base_unicode = json.load(f).get("unicode", "")
                except: pass

        #Look into subfolders (Default, Light, etc.)
        subfolders = [d for d in os.listdir(emoji_path) if os.path.isdir(os.path.join(emoji_path, d))]
        
        if not subfolders:
            skipped_count += 1
            continue

        for tone_folder in subfolders:
            tone_path = os.path.join(emoji_path, tone_folder)
            
            #Recursive search for any png in 3D folders
            target_png = None
            found_dir = ""
            for root, dirs, files in os.walk(tone_path):
                if "3D" in root:
                    pngs = [f for f in files if f.endswith(".png")]
                    if pngs:
                        target_png = pngs[0]
                        found_dir = root.replace(emoji_path, "").strip("\\/").replace("\\", "/")
                        break
            
            if not target_png:
                continue 

            # Calculate Unicode based on TONE_MAP
            # Try to read metadata just in case it's a special ZWJ sequence
            # But prioritize Base + Modifier logic for tones
            final_unicode = ""
            
            if tone_folder == "Default":
                final_unicode = base_unicode
            elif tone_folder in TONE_MAP:
                modifier = TONE_MAP[tone_folder]
                parts = base_unicode.split()
                if parts:
                    # Insert modifier after the first codepoint (standard Unicode practice)
                    parts.insert(1, modifier)
                    final_unicode = " ".join(parts)
            
            #Old logic if folder name isn't in TONE MAP
            if not final_unicode:
                tone_meta_path = os.path.join(tone_path, "metadata.json")
                if os.path.exists(tone_meta_path):
                    with open(tone_meta_path, 'r', encoding="utf-8") as f:
                        try:
                            final_unicode = json.load(f).get("unicode", "")
                        except: pass
                
                if not final_unicode:
                    final_unicode = base_unicode

            if not final_unicode:
                skipped_count += 1
                continue

            #CSS line
            formatted_u = "\\" + "\\".join(final_unicode.split())
            url_part = f"{urllib.parse.quote(emoji_folder)}/{urllib.parse.quote(found_dir)}/{urllib.parse.quote(target_png)}"
            full_url = f"{BASE_URL}/{url_part}"
            
            line = f'img.emoji[alt="{formatted_u}"] {{ content: url("{full_url}") !important; display: inline-block !important; }}'
            css_lines.append(line)

    # Output
    output_file = "FluentEmojiMapper.theme.css"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(THEME_HEADER + "\n".join(css_lines))
    
    print(f"\n--- Process Finished ---")
    print(f"Successfully generated: {len(css_lines)} lines")

if __name__ == "__main__":
    generate_css()