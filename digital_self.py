from brain.llm_interface import LLMInterface
from brain.memory_controller import MemoryController
from brain import db

class DigitalSelf:
    def __init__(self):
        # Initialize DB if not exists
        try:
            db.init_db()
        except:
            pass # Already done or error handled in db

        # Load identity from DB
        identity = db.get_identity()
        identity_prompt = f"You are {identity.get('name', 'Digital Self')}. {identity.get('core_description', '')}"
        # Extreme Brevity & Memory Priority
        identity_prompt += "\nINSTRUCTION: You are in 'Chat Mode'. Respond in 10-20 words MAX. match the user's length. Be casual."
        identity_prompt += "\nCRITICAL: If 'Relevant Memories' are provided, YOU MUST USE THEM. They are facts about the user. Do not hallucinate dates."
        
        self.brain = LLMInterface(system_prompt=identity_prompt)
        self.memory_controller = MemoryController()

    def chat(self, user_input: str, model: str = None):
        """
        Main chat interface.
        1. Checks for explicit memory commands via MemoryController.
        2. Retrieves context from long-term memory.
        3. Generates response via LLM.
        """
        # 1. Check for Memory Command
        is_command, response = self.memory_controller.process_input(user_input)
        if is_command:
            # If it was a command, we just yield the confirmation
            def confirmation_gen():
                yield response
            return confirmation_gen()

        # 2. Retrieve Context
        context_str = self.memory_controller.retrieve_context(user_input)
        
        # 3. Implicit Learning (Store the user's statement for future)
        print(f"[DEBUG] Attempting to store observation: {user_input}")
        try:
            self.memory_controller.store_observation(user_input)
            print("[DEBUG] Stored successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to store observation: {e}") 

        # 3. Inject context into message
        # We constructed the prompt: System + Context + User
        full_input = f"{context_str}\nUser: {user_input}"
        try:
            print(f"\n[DEBUG] FULL PROMPT:\n{full_input}\n[DEBUG] END PROMPT\n")
        except UnicodeEncodeError:
            print("[DEBUG] FULL PROMPT contains Unicode characters (not displayed)")
        
        # 4. Chat with Streaming
        # Pass the specific model if provided
        generator = self.brain.chat(full_input, stream=True, model=model)
        
        return generator

    def learn(self, text: str) -> str:
        """
        Explicitly add a piece of information to long-term memory.
        """
        try:
            self.memory_controller.store_observation(text)
            return "Memory added."
        except Exception as e:
            return f"Error adding memory: {e}"
