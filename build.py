# Sequential Cloze Revealer Packaging Script
# Compiles the add-on folder into an installable ".ankiaddon" file.

import os
import zipfile

ADDON_NAME = "sequential_cloze_revealer"
OUTPUT_FILENAME = "sequential_cloze_revealer.ankiaddon"

def package_addon():
    print(f"Packaging '{ADDON_NAME}'...")
    
    # Files to include in the package
    files_to_pack = [
        "__init__.py",
        "config.json",
        "note_type.py",
        "reviewer.py",
        "renderer.py",
        "manifest.json",
        "styles/sequential.css",
        "js/cloze.js",
        "templates/note_type.json"
    ]
    
    try:
        with zipfile.ZipFile(OUTPUT_FILENAME, 'w', zipfile.ZIP_DEFLATED) as addon_zip:
            for file_path in files_to_pack:
                if os.path.exists(file_path):
                    addon_zip.write(file_path)
                    print(f" -> Added: {file_path}")
                else:
                    print(f" [!] Warning: File {file_path} not found. Skipping...")
                    
        print(f"\nSuccess! Built package: {OUTPUT_FILENAME}")
        print("To install, open Anki -> Tools -> Add-ons -> Install from file... and select this file.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    package_addon()
