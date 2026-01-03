from brain.llm_interface import LLMInterface
from brain.memory_controller import MemoryController
from brain.user_service import UserServiceConnector
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
        self.user_service = UserServiceConnector()

    def chat(self, user_input: str, model: str = None, user_id=None):
        """
        Main chat interface.
        """
        # Get user info if ID provided
        current_user = None
        # Normalize user_id: handle empty strings or JS null/undefined strings
        if user_id and str(user_id).lower() not in ["", "null", "undefined"]:
            current_user = self.user_service.get_user_by_id(user_id)
            user_name = current_user.get('userName', 'Unknown') if current_user else 'Unknown'
            # Log User Message
            self.user_service.log_message(user_id, user_name, 'user', user_input)
        else:
            # Important to clear it if it was something else, though user_id is the source of truth
            user_id = None

        # 1. Check for Memory Command
        is_command, response = self.memory_controller.process_input(user_input)
        if is_command:
            if user_id: self.user_service.log_message(user_id, current_user.get('userName'), 'assistant', response)
            def confirmation_gen(): yield response
            return confirmation_gen()

        # 1b. Check for User Service Intent
        print(f"[DEBUG] Processing intents for: '{user_input}' | UserID: {user_id}")
        user_intent_detected, user_response = self._process_user_intents(user_input, user_id)
        if user_intent_detected:
            print(f"[DEBUG] Intent detected: {user_response}")
            if user_id: self.user_service.log_message(user_id, current_user.get('userName'), 'assistant', user_response)
            def user_gen(): yield user_response
            return user_gen()
        print("[DEBUG] No intent detected, falling through to LLM.")

        # 2. Retrieve Context
        context_str = self.memory_controller.retrieve_context(user_input)
        
        # 3. Inject context into message
        full_input = f"{context_str}\nUser: {user_input}"
        
        # 4. Chat with Streaming
        generator = self.brain.chat(full_input, stream=True, model=model)
        
        # Wrap generator to log response once finished
        def log_wrapper():
            full_response = ""
            for chunk in generator:
                try:
                    # Handle object (new ollama lib)
                    if hasattr(chunk, 'message'):
                        content = chunk.message.content
                    # Handle dict (old ollama lib or fallback)
                    elif isinstance(chunk, dict) and 'message' in chunk:
                        content = chunk['message']['content']
                    elif isinstance(chunk, str):
                        content = chunk
                    else:
                        content = str(chunk)
                    
                    full_response += content
                    yield content
                except Exception as e:
                    print(f"[DEBUG] Error extracting content: {e}")
                    yield ""
            
            if user_id:
                self.user_service.log_message(user_id, current_user.get('userName'), 'assistant', full_response)
        
        return log_wrapper()

    def _process_user_intents(self, user_input: str, user_id=None):
        """
        Detects if the user is asking for user-related data (including recognitions).
        """
        input_lower = user_input.lower()
        
        # 1. Recognize Intent: "recognize/recognise [name] [comment]"
        import re
        rec_match = re.search(r"\brecogni[sz]e\b", input_lower)
        if rec_match:
            print(f"[DEBUG] Recognition Keyword matched. UserID: {user_id}")
            if not user_id:
                return True, "I need to know who you are before you can recognize someone. Please select a user in the sidebar."
            
            # Much more flexible regex: recognize followed by a name (can be multiple words) and then a comment
            users = self.user_service.get_all_users()
            target_username = None
            comment = "Excellent work!"
            
            # Extract text after the keyword
            text_after_recognize = input_lower[rec_match.end():].strip()
            
            for u in users:
                full_name = u.get('fullName', '').lower()
                u_name = u.get('userName', '').lower()
                
                # Check for exact Match or partial match
                # Use first word of full name if it's long
                first_name = full_name.split()[0] if full_name else ""
                
                # Logic: Is the full name, username, or first name present after 'recognize'?
                # Or is the text after 'recognize' STARTING with something similar?
                if (full_name and full_name in text_after_recognize) or \
                   (u_name and u_name in text_after_recognize) or \
                   (first_name and len(first_name) > 3 and first_name in text_after_recognize):
                    
                    target_username = u.get('userName')
                    # Find which one matched to extract comment
                    match_str = full_name if full_name in text_after_recognize else \
                                (u_name if u_name in text_after_recognize else first_name)
                    
                    comment_area = text_after_recognize.replace(match_str, "", 1).strip()
                    if comment_area:
                        # Handle "120 points" logic - the user said "120 points"
                        # My backend currently doesn't support variable points in this call (fixed at 100)
                        # but I should at least save it in the comment or log it.
                        comment = re.sub(r'^(with|comment|comments|message|saying|for|along with)?\s*', '', comment_area, flags=re.IGNORECASE).strip()
                    break
                
                # Handling typos like "NEET" for "Neeli"
                # If the first word of text_after_recognize is very similar to first_name
                words_after = text_after_recognize.split()
                if words_after and first_name:
                    first_word_input = words_after[0]
                    # Simple similarity: if they share 3+ characters and are same length-ish
                    if len(first_word_input) > 3 and first_word_input[:3] == first_name[:3]:
                        target_username = u.get('userName')
                        comment_area = " ".join(words_after[1:])
                        comment = re.sub(r'^(with|comment|comments|message|saying|for|along with)?\s*', '', comment_area, flags=re.IGNORECASE).strip() or "Excellent work!"
                        break

            if target_username:
                result = self.user_service.recognize(user_id, target_username, comment)
                return True, result
            
            return True, "Who should I recognize? Please provide their full name or username."

        # 2. Recognition History Intent
        if any(keyword in input_lower for keyword in ["how many recognition", "show my recognitions", "received recognition"]):
            if not user_id:
                return True, "Please select a user in the sidebar to see recognition history."
            
            recognitions = self.user_service.get_recognition_history(user_id)
            if not recognitions:
                return True, "You haven't received any recognitions yet."
            
            response = "Here are the recognitions you've received:\n"
            for rec in recognitions:
                sender_name = rec.get('sender', {}).get('fullName', 'Someone')
                response += f"- {rec.get('points')} pts from {sender_name}: \"{rec.get('comment')}\" ({rec.get('timestamp')[:10]})\n"
            return True, response

        # 3. List Users
        if any(keyword in input_lower for keyword in ["get all users", "list users", "show participants"]):
            users = self.user_service.get_all_users()
            if not users: return True, "I couldn't find any users."
            
            response = "Participants:\n"
            for user in users:
                response += f"- {user.get('fullName')} (@{user.get('userName')}) | Points: {user.get('points')}\n"
            return True, response
        
        if "get user" in input_lower or "show user" in input_lower:
            # Try to extract an ID
            import re
            match = re.search(r'\d+', user_input)
            if match:
                user_id = match.group()
                user = self.user_service.get_user_by_id(user_id)
                if user:
                    return True, f"Found user: {user.get('fullName')} from {user.get('department')} department."
                else:
                    return True, f"I couldn't find a user with ID {user_id}."
            return True, "Which user ID should I look for?"

        return False, None

    def list_users(self):
        """Direct access to user list for API endpoints."""
        return self.user_service.get_all_users()
