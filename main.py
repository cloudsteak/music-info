import os
from mutagen.easyid3 import EasyID3, EasyID3KeyError
import musicbrainzngs
import argparse
import logging

# Configure the logging settings
logging.basicConfig(filename='error.log', 
                    level=logging.WARNING, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Add support for the comment tag in EasyID3
if 'comment' not in EasyID3.valid_keys.keys():
    EasyID3.RegisterTextKey('comment', 'COMM')

# Configure MusicBrainz access
musicbrainzngs.set_useragent("ExampleMusicApp", "0.1", "your-email@example.com")


def find_music_info(artist, title):
        result = musicbrainzngs.search_recordings(
            artist=artist, recording=title, limit=1
        )
        info = {}
        
        for recording in result["recording-list"]:
            try: 
                if "release-list" in recording:
                    info["date"] = str(int(recording["release-list"][0]["date"][:4]))
            except Exception as e:
                logging.error("Error finding music date for %s %s : %s", artist, title, e, exc_info=True)
            
            try:
                if "tag-list" in recording:
                    # Collect all genre tags (could be more than one)
                    genres = [
                        normalize_genre(tag["name"])
                        for tag in recording["tag-list"]
                        if tag["name"]
                    ]
                    info["genre"] = ", ".join(genres)
            except Exception as e:
                logging.error("Error finding music genre for %s %s : %s", artist, title, e, exc_info=True)
        return info
    


def update_mp3_tags(file_path, info, default_genre, comment):
    try:
        audio = EasyID3(file_path)
        isUpdated = False
        if "date" in info:
            audio["date"] = info["date"]
            isUpdated = True
        if "genre" in info:
            audio["genre"] = info["genre"]
            isUpdated = True
        elif default_genre:
            audio["genre"] = default_genre
            info["genre"] = default_genre
            isUpdated = True
        if comment:
            audio["comment"] = comment
            info["comment"] = comment
            isUpdated = True
        if isUpdated:
            print("Updating tags for", file_path.split("/")[-1], ":", info)
            audio.save()
        else:
            print("Skipped", file_path)
    except Exception as e:
        logging.error("Error updating tags for %s : %s", file_path.split("/")[-1], e, exc_info=True)


# Normalize the genre names
def normalize_genre(genre):
    normalized_genre = genre.lower()
    normalized_genre = normalized_genre.replace("r&b", "RnB")
    normalized_genre = normalized_genre.replace("r b", "RnB")
    normalized_genre = normalized_genre.replace("top 40", "pop")
    normalized_genre = normalized_genre.replace("contemporary ", "")
    normalized_genre = capitalize_first_letter(normalized_genre)
    return normalized_genre

# Capitalize the first letter of the string
def capitalize_first_letter(s):
    return "".join([s[:1].upper(), s[1:]])


# Process each file in the directory
def update_genre(path, default_genre, comment):
    # Define the directory path
    music_directory = path

    # Check if the directory exists
    if not os.path.exists(music_directory):
        raise Exception("The specified music directory does not exist: " + music_directory)
    
    files = os.listdir(music_directory)
    item_count = len(files)
    current_item = 0
    for file_name in files:
        current_item += 1
        print("#####", current_item, "of", item_count, "(", file_name, ")")
        if file_name.endswith(".mp3"):
            try:
                file_path = os.path.join(music_directory, file_name)
                audio = EasyID3(file_path)
                artist = audio.get("artist", ["Unknown Artist"])[0]
                title = audio.get("title", ["Unknown Title"])[0]
                music_info = find_music_info(artist, title)
                update_mp3_tags(file_path, music_info, default_genre, comment)
            except Exception as e:
                logging.error("Error updating file %s : %s", file_name, e, exc_info=True)

def main():
    parser = argparse.ArgumentParser(description="Update MP3 tags (Release date, Genre, Comment)")
    parser.add_argument('-p', '--path', type=str, required=True, help="Directory path containing MP3 files")
    parser.add_argument('-g', '--default_genre', type=str, required=False, help="Default genre to apply to all MP3 files where we cannot find genre information")
    parser.add_argument('-c', '--comment', type=str, required=False, help="Comment to apply to all MP3 files")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        logging.error("The specified path does not exist. %s", e, exc_info=True)
        return

    logging.warning("######################################")
    logging.warning("Updating MP3 tags for %s", args.path)
    update_genre(args.path, args.default_genre, args.comment)

if __name__ == "__main__":
    main()