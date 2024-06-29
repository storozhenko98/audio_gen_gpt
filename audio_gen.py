import os
import random
from midiutil import MIDIFile
import pygame
from openai import OpenAI
import json
import sqlite3
import hashlib


# Database setup
def setup_database():
    conn = sqlite3.connect('piano_compositions.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS compositions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  prompt TEXT,
                  gpt_response TEXT,
                  midi_filename TEXT,
                  parent_id INTEGER,
                  is_original BOOLEAN,
                  FOREIGN KEY(parent_id) REFERENCES compositions(id))''')
    conn.commit()
    return conn

def insert_composition(conn, prompt, gpt_response, midi_filename, parent_id=None, is_original=True):
    c = conn.cursor()
    c.execute("INSERT INTO compositions (prompt, gpt_response, midi_filename, parent_id, is_original) VALUES (?, ?, ?, ?, ?)",
              (prompt, gpt_response, midi_filename, parent_id, is_original))
    conn.commit()
    return c.lastrowid

# OpenAI client
client = OpenAI(api_key="put-key-here")
# Messages 
messages = [
        {"role": "system", "content": """You are a music composition assistant. Based on the user's input, create a piano composition of at least 15 seconds in length. Provide ONLY the following JSON format without any additional text or explanations:
        {
            "tempo": <integer between 60-180>,
            "time_signature": "<string, either '4/4' or '3/4'>",
            "notes": [
                {
                    "pitch": "<string, e.g., 'C4', 'D4', etc.>",
                    "duration": <float, in beats>,
                    "time": <float, start time in beats>,
                    "track": <integer, 0 for melody, 1 for chords>
                },
                ...
            ]
        }
        Example of a composition:
         
        {
            "tempo": 120,
            "time_signature": "4/4",
            "notes": [
                {"pitch": "E4", "duration": 1.0, "time": 0.0, "track": 0},
                {"pitch": "D4", "duration": 1.0, "time": 1.0, "track": 0},
                {"pitch": "C4", "duration": 1.0, "time": 2.0, "track": 0},
                {"pitch": "D4", "duration": 1.0, "time": 3.0, "track": 0},
                {"pitch": "E4", "duration": 1.0, "time": 4.0, "track": 0},
                {"pitch": "E4", "duration": 1.0, "time": 5.0, "track": 0},
                {"pitch": "E4", "duration": 2.0, "time": 6.0, "track": 0},
                {"pitch": "D4", "duration": 1.0, "time": 8.0, "track": 0},
                {"pitch": "D4", "duration": 1.0, "time": 9.0, "track": 0},
                {"pitch": "D4", "duration": 2.0, "time": 10.0, "track": 0},
                {"pitch": "E4", "duration": 1.0, "time": 12.0, "track": 0},
                {"pitch": "G4", "duration": 1.0, "time": 13.0, "track": 0},
                {"pitch": "G4", "duration": 2.0, "time": 14.0, "track": 0},
                {"pitch": "C3", "duration": 2.0, "time": 0.0, "track": 1},
                {"pitch": "G3", "duration": 2.0, "time": 2.0, "track": 1},
                {"pitch": "C3", "duration": 2.0, "time": 4.0, "track": 1},
                {"pitch": "G3", "duration": 2.0, "time": 6.0, "track": 1},
                {"pitch": "D3", "duration": 2.0, "time": 8.0, "track": 1},
                {"pitch": "G3", "duration": 2.0, "time": 10.0, "track": 1},
                {"pitch": "C3", "duration": 2.0, "time": 12.0, "track": 1},
                {"pitch": "G3", "duration": 2.0, "time": 14.0, "track": 1}
            ]
        }
         
        Aim for a composition of at least 60 notes to ensure a minimum length of 15 seconds."""},
        #{"role": "user", "content": prompt}
]

# Append to messages
def append_to_messages(message):
    messages.append(message)

# Get AI composition 
def get_ai_composition(msgs):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=msgs
    )
    return response.choices[0].message.content

# Parse AI composition
def parse_ai_composition(response):
    try:
        # Find the start and end of the JSON data
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            raise ValueError("No valid JSON data found in the response")
        
        # Extract the JSON part of the response
        json_str = response[json_start:json_end]
        
        # Remove any markdown formatting
        json_str = json_str.replace('```json\n', '').replace('\n```', '')
        
        composition = json.loads(json_str)
        
        # Validate the composition structure
        required_keys = ['tempo', 'time_signature', 'notes']
        for key in required_keys:
            if key not in composition:
                raise ValueError(f"Missing required key: {key}")
        
        for note in composition['notes']:
            required_note_keys = ['pitch', 'duration', 'time', 'track']
            for key in required_note_keys:
                if key not in note:
                    raise ValueError(f"Missing required key in note: {key}")
        
        return composition
    except json.JSONDecodeError as e:
        print(f"Error parsing AI response: {e}")
        print("AI response:", response)
    except ValueError as e:
        print(f"Invalid composition structure: {e}")
        print("AI response:", response)
    
    print("Using default composition.")

    # Default composition
    return {
        "tempo": 120,
        "time_signature": "4/4",
        "notes": [
            {"pitch": "C4", "duration": 1, "time": 0, "track": 0},
            {"pitch": "E4", "duration": 1, "time": 1, "track": 0},
            {"pitch": "G4", "duration": 1, "time": 2, "track": 0},
            {"pitch": "C5", "duration": 1, "time": 3, "track": 0},
            {"pitch": "G4", "duration": 1, "time": 4, "track": 0},
            {"pitch": "E4", "duration": 1, "time": 5, "track": 0},
            {"pitch": "C4", "duration": 2, "time": 6, "track": 0},
            {"pitch": "D4", "duration": 1, "time": 8, "track": 0},
            {"pitch": "F4", "duration": 1, "time": 9, "track": 0},
            {"pitch": "A4", "duration": 1, "time": 10, "track": 0},
            {"pitch": "D5", "duration": 1, "time": 11, "track": 0},
            {"pitch": "A4", "duration": 1, "time": 12, "track": 0},
            {"pitch": "F4", "duration": 1, "time": 13, "track": 0},
            {"pitch": "D4", "duration": 2, "time": 14, "track": 0},
            {"pitch": "C3", "duration": 4, "time": 0, "track": 1},
            {"pitch": "G3", "duration": 4, "time": 4, "track": 1},
            {"pitch": "D3", "duration": 4, "time": 8, "track": 1},
            {"pitch": "G3", "duration": 4, "time": 12, "track": 1}
        ]
    }

# Create MIDI file
def create_midi(composition, prompt, is_original):
    midi = MIDIFile(2)  # 2 tracks: melody and chords
    
    # Setup tracks
    for track in range(2):
        midi.addTrackName(track, 0, f"Track {track + 1}")
        midi.addTempo(track, 0, int(composition['tempo']))
    
    # Add notes
    for note in composition['notes']:
        midi.addNote(note['track'], 0, note_to_midi(note['pitch']), note['time'], note['duration'], 100)
    
    # Save the MIDI file
    os.makedirs("./midi", exist_ok=True)
    prefix = "original" if is_original else "followup"
    midi_filename = f"{prefix}_{hashlib.md5(prompt.encode()).hexdigest()}.mid"
    midi_path = os.path.join("./midi", midi_filename)
    with open(midi_path, "wb") as f:
        midi.writeFile(f)
    
    return midi_path, midi_filename

# Convert note to MIDI (In future, expand beyond just basic notes)
def note_to_midi(note):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = int(note[-1])
    pitch_class = note[:-1]
    return notes.index(pitch_class) + (octave + 1) * 12

# Play MIDI file
def play_midi(filename):
    pygame.init()
    pygame.mixer.init()
    clock = pygame.time.Clock()
    
    try:
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    return
    except pygame.error as e:
        print(f"Error playing MIDI: {e}")
    finally:
        pygame.quit()

# Main Loop
def main():
    conn = setup_database()
    print("Welcome to the AI Piano Composer.")
    print("Describe the kind of piano music you want to hear.")
    print("You can mention mood, tempo, style, or any other preferences.")
    user_prompt = input("Your music description: ")
    append_to_messages({"role": "user", "content": user_prompt})
    ai_response = get_ai_composition(messages)
    append_to_messages({"role": "assistant", "content": ai_response})
    composition = parse_ai_composition(ai_response)
    print("AI-generated composition:", json.dumps(composition, indent=2))
    
    midi_path, midi_filename = create_midi(composition, user_prompt, is_original=True)
    
    print(f"Generated MIDI file: {midi_path}")
    print("Playing the generated music...")
    play_midi(midi_path)
    
    id = insert_composition(conn, user_prompt, ai_response, midi_filename, is_original=True)
    
    while True:
        choice = input("Enter 'f' to follow up, 'p' to play again, or 'q' to quit: ").lower()
        if choice == 'p':
            print("Playing the music again...")
            play_midi(midi_path)
        elif choice == 'f':
            print("Follow up with more details...")
            followup_prompt = input("Your follow-up description: ")
            full_prompt = f"Original prompt: {user_prompt}\nOriginal MIDI: {midi_filename}\nFollow-up: {followup_prompt}"
            append_to_messages({"role": "user", "content": full_prompt})
            ai_response = get_ai_composition(messages)
            append_to_messages({"role": "assistant", "content": ai_response})
            composition = parse_ai_composition(ai_response)
            midi_path, midi_filename = create_midi(composition, followup_prompt, is_original=False)
            
            print("Playing the new music...")
            play_midi(midi_path)
            id = insert_composition(conn, full_prompt, ai_response, midi_filename, parent_id=id, is_original=False)
        elif choice == 'q':
            print("See ya")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
