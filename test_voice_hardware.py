import sys
import os
import speech_recognition as sr

def test_microphone():
    print("Initializing Microphone Test...")
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("[OK] Microphone detected.")
            print("Adjusting for ambient noise (1 sec)...")
            r.adjust_for_ambient_noise(source, duration=1)
            
            print("Listening for 3 seconds (please speak)...")
            try:
                # timout=3 means wait max 3 secs for speech to start
                # phrase_time_limit=3 means cut off after 3 secs of speech
                audio = r.listen(source, timeout=3, phrase_time_limit=3)
                print("[OK] Audio captured.")
                
                try:
                    print("Attempting recognition (Whisper)...")
                    # We'll use google for a quick check if whisper is heavy/slow, 
                    # but the app uses whisper. Let's try to mimic app if possible.
                    # But verifying 'capture' is enough for hardware check.
                    text = r.recognize_google(audio)
                    print(f"[OK] Recognized: '{text}'")
                except sr.UnknownValueError:
                    print("[WARN] Audio captured but not understood (Silence?).")
                except sr.RequestError as e:
                    print(f"[WARN] Recognition service error: {e}")
                    
            except sr.WaitTimeoutError:
                print("[WARN] No speech detected within timeout (Microphone works, but no input).")
                
    except OSError as e:
        print(f"[FAIL] Could not access microphone: {e}")
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")

if __name__ == "__main__":
    test_microphone()
