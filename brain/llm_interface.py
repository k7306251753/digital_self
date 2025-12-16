import ollama

class LLMInterface:
    def __init__(self, model_name="llama3", system_prompt="You are a digital clone of the user."):
        self.model_name = model_name
        self.system_prompt = system_prompt

    def chat(self, prompt: str, stream: bool = False, model: str = None):
        """
        Generates a response from the LLM.
        """
        if not self.is_ollama_connected():
            return "Error: Could not connect to Ollama. Make sure it is running."

        try:
            # Use specific model if requested, otherwise default
            target_model = model if model else self.model_name
            print(f"[LLM] Requesting model: {target_model}")
            
            response = ollama.chat(
                model=target_model,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': prompt},
                ],
                stream=stream,
                options={
                    "num_ctx": 1024,       # Reduced context for speed
                    "num_predict": 70,     # HARD LIMIT: Stop generating after ~50 words.
                    "num_gpu": 1, 
                    "temperature": 0.7,
                    "stop": ["User:", "System:"] # Early stopping
                }
            )
            return response
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            # If streaming, we must return a generator that yields the error
            if stream:
                def error_gen():
                    yield error_msg
                return error_gen()
            return error_msg

    def is_ollama_connected(self):
        try:
            ollama.list()
            return True
        except:
            return False

    def update_system_prompt(self, new_prompt):
        self.system_prompt = new_prompt

