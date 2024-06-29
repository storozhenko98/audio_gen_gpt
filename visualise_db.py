import sqlite3
import os
from tabulate import tabulate

def connect_to_db():
    db_path = 'piano_compositions.db'
    if not os.path.exists(db_path):
        print(f"Database file '{db_path}' not found.")
        return None
    return sqlite3.connect(db_path)

def fetch_compositions(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, prompt, midi_filename, parent_id, is_original
        FROM compositions
        ORDER BY id
    """)
    return cursor.fetchall()

def display_compositions(compositions):
    headers = ["ID", "Prompt", "MIDI Filename", "Parent ID", "Is Original"]
    table_data = []
    
    for comp in compositions:
        id, prompt, midi_filename, parent_id, is_original = comp
        prompt_preview = (prompt[:50] + '...') if len(prompt) > 50 else prompt
        table_data.append([id, prompt_preview, midi_filename, parent_id or "N/A", "Yes" if is_original else "No"])
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def display_composition_details(conn, comp_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM compositions WHERE id = ?", (comp_id,))
    comp = cursor.fetchone()
    
    if comp:
        id, prompt, gpt_response, midi_filename, parent_id, is_original = comp
        print("\nComposition Details:")
        print(f"ID: {id}")
        print(f"Prompt: {prompt}")
        print(f"GPT Response: {gpt_response[:200]}..." if len(gpt_response) > 200 else gpt_response)
        print(f"MIDI Filename: {midi_filename}")
        print(f"Parent ID: {parent_id or 'N/A'}")
        print(f"Is Original: {'Yes' if is_original else 'No'}")
    else:
        print(f"No composition found with ID {comp_id}")

def main():
    conn = connect_to_db()
    if not conn:
        return
    
    while True:
        compositions = fetch_compositions(conn)
        display_compositions(compositions)
        
        choice = input("\nEnter a composition ID to view details, or 'q' to quit: ")
        if choice.lower() == 'q':
            break
        
        try:
            comp_id = int(choice)
            display_composition_details(conn, comp_id)
        except ValueError:
            print("Invalid input. Please enter a valid composition ID or 'q' to quit.")
        
        input("\nPress Enter to continue...")
    
    conn.close()

if __name__ == "__main__":
    main()
