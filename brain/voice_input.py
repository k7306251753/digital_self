import json
import queue
import sys
import sounddevice as sd
from vosk import Model, KaldiRecognizer

class VoiceInput:
    def __init__(self, model_path="model"):
        self.model_path = model_path
        self.model = None
        self.q = queue.Queue()
        self.enabled = False

    def initialize(self):
        try:
            if not os.path.exists(self.model_path):
                print(f"VOSK model not found at '{self.model_path}'. Please download a model from https://alphacephei.com/vosk/models and unpack as '{self.model_path}' in the current folder.")
                return False
            
            self.model = Model(self.model_path)
            self.enabled = True
            print("VOSK model loaded.")
            return True
        except Exception as e:
            print(f"Failed to load VOSK model: {e}")
            return False

    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(bytes(indata))

    def listen_loop(self, context=None):
        if not self.enabled:
            return

        with sd.RawInputStream(samplerate=16000, blocksize=8000, device=None, dtype='int16',
                               channels=1, callback=self.callback):
            print('#' * 80)
            print('Press Ctrl+C to stop the recording')
            print('#' * 80)

            rec = KaldiRecognizer(self.model, 16000)
            while True:
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    result_json = rec.Result()
                    result = json.loads(result_json)
                    text = result.get('text', '')
                    if text:
                        yield text
                else:
                    # Partial result
                    pass

if __name__ == "__main__":
    # Test script
    import os
    vi = VoiceInput()
    if vi.initialize():
        for text in vi.listen_loop():
            print(f"Recognized: {text}")
