import unittest
from unittest.mock import MagicMock, patch
import time
import os
import sys

# Ensure brain modules can be found
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from brain import db
    # brain is a package, so we can import submodules
    import brain.voice_engine
    from brain.memory_controller import MemoryController
    from brain.llm_interface import LLMInterface
    from digital_self import DigitalSelf
except ImportError as e:
    print(f"Import failed: {e}")
    exit(1)

class TestDigitalSelfOptimization(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        print("\n[Setup] Initializing DB...")
        db.init_db()

    @classmethod
    def tearDownClass(cls):
        print("\n[Teardown] Closing DB Pool...")
        db.close_pool()

    def test_database_performance_functionality(self):
        """Verify connection pooling handles rapid requests."""
        print("\n[Test] Database Pooling...")
        start_time = time.time()
        for i in range(20):
            db.add_memory("TEST_CHUNK", f"Rapid memory {i}")
        duration = time.time() - start_time
        print(f"   20 writes took {duration:.4f}s")
        self.assertLess(duration, 1.0, "Writing should be very fast with pooling")

        # Cleanup
        mems = db.search_memories("Rapid memory")
        for m in mems:
            if m['category'] == "TEST_CHUNK":
                db.delete_memory(m['id'])

    def test_voice_engine_optimization(self):
        """Verify VoiceEngine accepts new parameters."""
        print("\n[Test] Voice Engine Signatures...")
        
        # Patch dependencies where they are imported IN brain.voice_engine
        # i.e. brain.voice_engine.pyttsx3
        with patch('brain.voice_engine.pyttsx3') as mock_tts, \
             patch('brain.voice_engine.sr') as mock_sr:
            
            # Setup mock recognizer
            mock_recognizer_instance = MagicMock()
            mock_sr.Recognizer.return_value = mock_recognizer_instance
            mock_recognizer_instance.recognize_whisper.return_value = "Test transcript"

            from brain.voice_engine import VoiceEngine
            engine = VoiceEngine()
            
            # Check if listen method accepts 'model'
            import inspect
            sig = inspect.signature(engine.listen)
            self.assertTrue('model' in sig.parameters, "listen() should have 'model' param")
            
            # Test calling listen with param
            # Mock the microphone context manager
            mock_mic_instance = MagicMock()
            mock_sr.Microphone.return_value = mock_mic_instance
            mock_mic_instance.__enter__.return_value = MagicMock()
            
            res = engine.listen(model="tiny")
            
            # Verify it called recognize_whisper with model="tiny"
            mock_recognizer_instance.recognize_whisper.assert_called_with(unittest.mock.ANY, model="tiny")
            print("   VoiceEngine.listen(model='tiny') verified.")

    @patch('brain.voice_engine.VoiceEngine')
    def test_full_flow(self, MockVoice):
        """Test the DigitalSelf class with mocked voice but real DB/LLM."""
        print("\n[Test] Full DigitalSelf Flow...")
        bot = DigitalSelf()
        
        print("   Sending: 'remember that integration testing is key'")
        responses = list(bot.chat("remember that integration testing is key"))
        response_text = "".join(str(r) for r in responses)
        
        self.assertTrue("memory" in response_text.lower() or "store" in response_text.lower(),
                        f"Bot should confirm memory storage. Got: {response_text}")
        
        context = bot.memory_controller.retrieve_context("integration testing")
        self.assertTrue("integration testing" in context, "Context should retrieve the memory")
        print("   Memory verified in DB.")

if __name__ == '__main__':
    unittest.main()
