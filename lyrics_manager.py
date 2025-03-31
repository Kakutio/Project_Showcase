from pathlib import Path

import json
import random
import re


# ------------ ALBUM DATA and ALBUM INFO ------------
def load_album(album_json_path: Path) -> dict:
    """Load and parse an album's JSON file."""
    with open(album_json_path) as json_file:
        album_data = json.load(json_file)
    return album_data

def get_album_name(album_data: dict) -> str:
    """Get the album name from album data."""
    album_name = album_data.get('name', 'Unknown Album')
    return album_name

def get_album_artist(album_data: dict) -> str:
    """Get the artist name from album data."""
    album_artist = album_data.get('artist',{}).get('name', 'Unknown Artist')
    return album_artist

def get_album_release_date(album_data: dict) -> str:
    """Get the release date from album data."""
    release_date = album_data.get('release_date_for_display', 'Unknown Release Date')
    return release_date

def print_album_info(album_path):
    # Now using module-level functions
    album_data = load_album(album_path)


    album_name = get_album_name(album_data)
    album_artist = get_album_artist(album_data)
    album_release_date = get_album_release_date(album_data)

    tracks = get_album_tracks(album_data)
    print('---------------------------------------------------------------')
    print('Artist:', album_artist)
    print('Album:', album_name)
    print('Release Date:', album_release_date)
    print('\n#Tracks:', len(tracks), '\n')

    for track in tracks:
        title = track['song']['title']
        lines = get_clean_lines_from_track(track)
        line_count = len(lines) if lines else 0

        # print with line count right aligned
        print(f'"{title}": {line_count} lines')
    print('---------------------------------------------------------------')


# ------------ ALBUM DATA - TRACKS - LINES ------------
def get_album_tracks(album_data: dict) -> list[dict]:
    try:
        tracks = [
        track
        for track in album_data["tracks"]
        if (track["song"]["lyrics"] != "")
        and "(Acapella)" not in track["song"]["title"]
        and "(A Cappella)" not in track["song"]["title"]
        and "Remix" not in track["song"]["title"]
        and "Instrumental" not in track["song"]["title"]
        ]
    except KeyError:
        return []

    return tracks


def get_track_lyrics(track: dict) -> str:
    """Extract lyrics from a track dictionary."""
    lyrics = track['song'].get('lyrics', '')
    return lyrics


def get_clean_lines_from_track(track: dict) -> list[str]:
    """Clean up lyrics and return a list of non-empty lines."""
    lyrics = get_track_lyrics(track)
    lines = lyrics.split('\n') # returns a list of lines
    clean_lines = []

    for line in lines:
        # skip lines that contain '[' or 'Contributors'
        if '[' in line or 'Contributors' in line:
            continue
        clean_line = line.strip()  # Remove leading/trailing whitespace
        if clean_line:  # Only add non-empty lines
            clean_lines.append(clean_line)

    return clean_lines

def get_clean_lines_from_album(tracks: list[dict]) -> list[list[str]]:
    # Now using the module-level function
    album_lines = [get_clean_lines_from_track(track) for track in tracks]
    return album_lines

# ------------ random, scoring, prompt functions ------------

def get_album_representation(album_lines: list[list[str]], count: int, seed: int) -> str:
    """
    Get a representation of an album as a string.
    """

    assert count > 25, "count must be greater than 25"

    # random seed
    random.seed(seed)

    # get an equal number of random lines from each track, to add up to count
    sample_quatrains = []

    # if we need 100 lines (count), and theres 10 tracks, we need to get 10 lines from each track
    # // is floor division, meaning it will return the integer part of the division
    line_count_track = count // len(album_lines)

    for track_lines in album_lines:
        random_start = random.randint(0, len(track_lines) - line_count_track)
        # make it one quatrain
        quatrain = track_lines[random_start:random_start+line_count_track]
        quatrain = "\n".join(quatrain)
        sample_quatrains.append(quatrain)

    return sample_quatrains


def distribute_score(total_score: int, max_score: int = 7) -> list[int]:
    """Distribute total score among 5 items with maximum individual score"""
    
    scores = [0 for _ in range(5)]
    remaining = total_score
    
    variance = random.randint(0, 5)
    remaining -= variance


    # First pass: distribute randomly but respect max_score
    while remaining > 0:
        idx = random.randint(0, 4)
        if scores[idx] < max_score:
            scores[idx] += 1
            remaining -= 1
            
    return scores    


def score_quatrains_random(quatrains: list[str], total_score: int) -> list[str]:
    """Score a line based on the score"""

    scored_quatrains = []

    for quatrain in quatrains:
        scores = distribute_score(total_score)
        scores = [str(score) for score in scores]
        temp = "\n [" + ", ".join(scores) + "] : \n" + quatrain 
        scored_quatrains.append(temp)

    return scored_quatrains

def word_scoring(input, x2x) -> str:
    """Define the scoring system for words"""

    mapping = {
        "trash": "1",
        "bad": "2",
        "basic": "3",
        "passable": "4",
        "engaging": "5",
        "captivating": "6",
        "masterful": "7",
    }

    assert x2x in ["w2s", "s2w"], "x2x must be 'w2s' or 's2w'"

    if input not in mapping.keys() and input not in mapping.values():
        pass

    if x2x == "w2s":
        return mapping[input]
    elif x2x == "s2w":
        # get the key with the value that matches input
        return [k for k, v in mapping.items() if v == input][0]
    

def word_scored_quatrains(quatrains: list[str]) -> list[str]:

    worded_quatrains = []
    repl_count = 0

    # match /d and use the the first 5
    for quatrain in quatrains:

        #replace using function
        worded_quatrain = re.sub(r'\d', lambda x: word_scoring(x.group(0), "s2w"), quatrain)
        worded_quatrains.append(worded_quatrain)
        repl_count += 1
        if repl_count > 5:
            break

    return worded_quatrains


# ------------ LyricsManager class ------------


class LyricsManager:

    def __init__(self):
        self.album_paths_dict = self._generate_album_paths_dict()

    def _get_file_paths_from_folder(self, folder_path) -> list[Path]:
        album_list = []
        p = folder_path.glob('*')
        album_list = [x for x in p if x.is_file()]

        return album_list

    def _generate_album_paths_dict(self) -> dict:

        # Hardcoding the paths we need
        data_dir = Path("lyrics")

        sub_sub_path_1 = data_dir / 'metal' / 'de'
        sub_sub_path_2 = data_dir / 'metal' / 'en'
        sub_sub_path_3 = data_dir / 'pop_rock' / 'en'
        sub_sub_path_4 = data_dir / 'rap' / 'de'
        sub_sub_path_5 = data_dir / 'rap' / 'en'
        sub_sub_path_6 = data_dir / 'rap' / 'ro'
        sub_sub_path_7 = data_dir / 'rap' / 'ru'

        album_paths_dict = {}
        
        album_paths_dict['metal'] = {}
        album_paths_dict['pop_rock'] = {}
        album_paths_dict['rap'] = {}
        
        album_paths_dict['metal']['de'] = self._get_file_paths_from_folder(sub_sub_path_1)
        album_paths_dict['metal']['en'] = self._get_file_paths_from_folder(sub_sub_path_2)
        album_paths_dict['pop_rock']['en'] = self._get_file_paths_from_folder(sub_sub_path_3)
        album_paths_dict['rap']['de'] = self._get_file_paths_from_folder(sub_sub_path_4)
        album_paths_dict['rap']['en'] = self._get_file_paths_from_folder(sub_sub_path_5)
        album_paths_dict['rap']['ro'] = self._get_file_paths_from_folder(sub_sub_path_6)
        album_paths_dict['rap']['ru'] = self._get_file_paths_from_folder(sub_sub_path_7)

        return album_paths_dict



    # -------------------------------------------------------------------------------------------

