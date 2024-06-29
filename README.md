# AI Piano Composer

This project uses AI to generate piano compositions based on user prompts. It includes two main components:

1. `audio_gen.py`: Generates and plays AI-composed piano music.
2. `visualise_db.py`: Visualizes the database of compositions.

## Features

- Generate piano compositions using GPT-4
- Convert AI responses to MIDI files
- Play generated music
- Store compositions in a SQLite database
- Visualize and explore stored compositions

## Usage

0. Make a venv and install `requirements.txt`

1. Run `audio_gen.py` to create and play AI-generated piano compositions:
   ```
   python audio_gen.py
   ```

2. Run `visualise_db.py` to view and explore stored compositions:
   ```
   python visualise_db.py
   ```

## Requirements

See `requirements.txt` for a list of required Python packages.

## Note

Make you have a valid OpenAI API key set up before running `audio_gen.py`.
