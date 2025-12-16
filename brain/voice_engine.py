import pyttsx3
import speech_recognition as sr
import threading
import queue
import time

class VoiceEngine:
    def __init__(self):
        # Initialize queue for non-blocking speech
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        
        # Start the speech worker thread
        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker_thread.start()

        self.recognizer = sr.Recognizer()
        # Optimize for faster interaction
        self.recognizer.energy_threshold = 300  # Default 300, lower -> more sensitive
        self.recognizer.pause_threshold = 0.6   # Default 0.8, lower -> faster cut-off
        self.recognizer.dynamic_energy_threshold = True
        
        self.microphone = sr.Microphone()
    
    def _speech_worker(self):
        """
        Daemon thread to process speech queue.
        """
        # Initialize engine within the thread to avoid COM/threading issues on Windows
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            # Try to select a good voice (Zira is usually 1 on Windows 10/11)
            if len(voices) > 1:
                # Often index 1 is a better female voice on Windows
                engine.setProperty('voice', voices[1].id)
            elif len(voices) > 0:
                engine.setProperty('voice', voices[0].id)
            
            engine.setProperty('rate', 170)
        except Exception as e:
            print(f"Error initializing TTS in thread: {e}")
            return

        while True:
            text = self.speech_queue.get()
            if text is None: break # Sentinel to stop
            
            self.is_speaking = True
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")
            finally:
                self.is_speaking = False
                self.speech_queue.task_done()

    def speak(self, text):
        """
        Queues text to be spoken non-blocking.
        """
        if text:
            # We can split long paragraphs if needed, but the main app handles sentences now.
            self.speech_queue.put(text)

    def listen(self):
        """
        Listens to microphone with a timeout to prevent freezing.
        """
        # If currently speaking, we might not want to listen to ourselves.
        # But blocking here might annoy the user if they want to interrupt.
        # For this version, we'll just listen.
        
        with self.microphone as source:
            print("Listening...")
            # We assume ambient noise is already adjusted or we do it quickly
            # self.recognizer.adjust_for_ambient_noise(source, duration=0.5) 
            
            try:
                # timeout=5 to wait for start, phrase_time_limit=10 for max duration
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            except sr.WaitTimeoutError:
                print("No speech detected (timeout).")
                return ""
        
        try:
            print("Transcribing...")
            text = self.recognizer.recognize_whisper(audio, model="base")
            return text
        except sr.RequestError as e:
            return f"Error: {e}"
        except sr.UnknownValueError:
            return ""
