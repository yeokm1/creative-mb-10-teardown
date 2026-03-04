import argparse
from midiutil import MIDIFile

# --- MIDI SETTINGS & CONSTANTS ---
CANARY_PITCH = 96          # MIDI Note 96 (C7) - High piercing test tone
FILLER_START_PITCH = 48    # MIDI Note 48 (C3) - Starting pitch for the background chord

CANARY_INSTRUMENT = 78     # General MIDI 78: Whistle
FILLER_INSTRUMENT = 89     # General MIDI 89: Warm Pad

TEMPO_BPM = 60             # 60 BPM means 1 beat = exactly 1 second


def generate_pyramid(filler_notes, file_name, priority_override):
    # Initialize MIDI object
    MyMIDI = MIDIFile(1)
    track = 0
    time = 0
    MyMIDI.addTempo(track, time, TEMPO_BPM) 

    # --- DYNAMIC CHANNELS & VOLUMES ---
    if priority_override:
        print("=> Priority Override ENABLED: Bypassing intelligent voice allocation...")
        canary_channel = 15 # MIDI Channel 15 (Lowest priority)
        canary_volume = 100   # Quieter volume
        filler_channel = 0  # MIDI Channel 1 (Highest priority)
        filler_volume = 100  # Maximum volume
    else:
        print("=> Standard Mode: Equal volume voice-stealing test...")
        canary_channel = 0   # MIDI Channel 1
        canary_volume = 100
        filler_channel = 1   # MIDI Channel 2
        filler_volume = 100

    print(f"=> Preparing a {filler_notes}-Note Polyphony Pyramid...")

    # --- 1. THE CANARY (The High Test Tone) ---
    MyMIDI.addProgramChange(track, canary_channel, time, CANARY_INSTRUMENT)

    # The Canary starts at Second 0 and holds for an extended time
    canary_hold_time = (filler_notes * 2) + 3
    MyMIDI.addNote(track, canary_channel, CANARY_PITCH, 0, canary_hold_time, canary_volume) 

    # --- 2. THE PYRAMID (Filler Notes) ---
    MyMIDI.addProgramChange(track, filler_channel, time, FILLER_INSTRUMENT)

    for i in range(filler_notes):
        pitch = FILLER_START_PITCH + i 
        
        # Climb up the pyramid
        start_time = 2 + i 
        
        # Climb down the pyramid (last note added stops first)
        end_time = 2 + (filler_notes * 2) - i
        duration = end_time - start_time 
        
        MyMIDI.addNote(track, filler_channel, pitch, start_time, duration, filler_volume)

    # Write it to disk
    with open(file_name, "wb") as output_file:
        MyMIDI.writeFile(output_file)

    print(f"=> Done! File saved as {file_name}\n")


if __name__ == "__main__":
    # Set up the command line argument parser
    parser = argparse.ArgumentParser(description="Generate a MIDI file to test synthesizer polyphony limits.")
    
    # Add the expected arguments
    parser.add_argument("fillers", type=int, help="The number of background filler notes to build.")
    parser.add_argument("filename", type=str, help="The name of the output MIDI file (e.g., test.mid)")
    
    # Add the optional Priority Override flag
    parser.add_argument("--priority-override", action="store_true", help="Enable 'Priority Override' (Channel 16, low vol) to bypass smart voice allocation on advanced synths.")
    
    # Parse the arguments and pass them to the generator function
    args = parser.parse_args()
    generate_pyramid(args.fillers, args.filename, args.priority_override)