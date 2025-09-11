from pathlib import Path

path_data = Path("data")
path_drum_sounds = path_data / "drum_sounds"
path_patterns = path_data / "patterns"
path_data.mkdir(exist_ok=True)
path_drum_sounds.mkdir(exist_ok=True)
path_patterns.mkdir(exist_ok=True)
