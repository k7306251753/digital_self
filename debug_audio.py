import pyttsx3

def list_audio_devices():
    engine = pyttsx3.init()
    print("Testing Audio Output...")
    try:
        engine.say("Testing audio output on default device.")
        engine.runAndWait()
        print("[OK] Default device test complete.")
    except Exception as e:
        print(f"[FAIL] Default device error: {e}")

    # pyttsx3 doesn't easily expose 'output devices' like pyaudio does, 
    # it relies on SAPI5 (Windows) or nsss (Mac).
    # On Windows, it uses the system default. 
    # We can try to check available voices to see if that gives a clue, but unexpected.
    
    voices = engine.getProperty('voices')
    print(f"\nAvailable Voices ({len(voices)}):")
    for v in voices:
        print(f" - {v.name} ({v.id})")

if __name__ == "__main__":
    list_audio_devices()
