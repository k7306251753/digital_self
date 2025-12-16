from . import db

class MemoryController:
    def __init__(self):
        # We could initialize an LLM here for classification if we wanted strictly local-first neural classification
        # For now, we'll use rule-based + fallback to default category
        self.categories = ["FACT", "PREFERENCE", "BELIEF", "IDEOLOGY", "SKILL", "PERSONAL_CONTEXT"]

    def _extract_fact(self, text: str) -> str:
        """
        Extracts the core fact from user input by removing filler words and command prefixes.
        """
        cleaned = text.strip()
        lower_text = cleaned.lower()
        
        # Remove common filler/command words from the beginning
        filler_prefixes = [
            "just remember", "ok remember", "okay remember", "please remember",
            "remember that", "remember:", "remember",
            "just", "ok", "okay", "please", "so", "well"
        ]
        
        for prefix in filler_prefixes:
            if lower_text.startswith(prefix):
                # Remove the prefix and any following whitespace
                cleaned = cleaned[len(prefix):].strip()
                lower_text = cleaned.lower()
        
        # Normalize common patterns
        # "my X was Y" -> "X is Y"
        if lower_text.startswith("my "):
            cleaned = cleaned[3:]  # Remove "my "
            # Replace "was" with "is" for present tense normalization
            cleaned = cleaned.replace(" was ", " is ")
            cleaned = cleaned.replace(" were ", " are ")
        
        # "I got X" patterns - keep as is but clean up
        # "I am X" -> "am X" or keep contextually
        
        return cleaned.strip()

    def process_input(self, user_input: str):
        """
        Analyzes input for memory commands.
        Returns: (is_command, response_message)
        """
        normalized = user_input.strip()
        lower_input = normalized.lower()
        
        # explicit command detection
        command_prefixes = ["remember that", "remember:", "learn that", "store this:"]
        
        for prefix in command_prefixes:
            if lower_input.startswith(prefix):
                 content = normalized[len(prefix):].strip()
                 if not content:
                     return True, "I need something to remember."
                 
                 # Extract clean fact
                 fact = self._extract_fact(content)
                 category = self._classify(fact)
                 db.add_memory(category, fact)
                 return True, f"I have stored that in my memory as a {category}."
        
        if lower_input.startswith("remember "):
             content = normalized[9:].strip() 
             if content:
                 # Extract clean fact
                 fact = self._extract_fact(content)
                 category = self._classify(fact)
                 db.add_memory(category, fact)
                 return True, f"I have put '{fact}' into long-term memory."

        return False, None

    def store_observation(self, content: str):
        """
        Implicitly stores an observation/fact from the user.
        We only store if it looks informative (simple heuristic).
        """
        if len(content.split()) < 3: return # Skip short greetings like "hi"
        
        # Avoid storing questions as facts
        if "?" in content: return
        
        # Extract clean fact before storing
        fact = self._extract_fact(content)
        if not fact or len(fact.split()) < 2:
            return  # Skip if extraction results in too short content
        
        category = self._classify(fact)
        db.add_memory(category, fact)

    def _classify(self, content: str) -> str:
        """
        Classifies the memory content into one of the types.
        """
        content_lower = content.lower()
        if "like" in content_lower or "love" in content_lower or "hate" in content_lower or "prefer" in content_lower:
            return "PREFERENCE"
        if "can" in content_lower or "know how" in content_lower:
            return "SKILL"
        if "believe" in content_lower or "think that" in content_lower:
            return "BELIEF"
        if "always" in content_lower or "never" in content_lower: # basic ideology heuristic
            return "IDEOLOGY"
        
        return "FACT" # Default

    def retrieve_context(self, query: str) -> str:
        """
        Retrieves relevant memories for a prompt.
        """
        memories = db.search_memories(query)
        if not memories:
            return ""
        
        context_lines = ["Relevant Memories:"]
        for m in memories:
            context_lines.append(f"- [{m['category']}] {m['content']}")
        
        return "\n".join(context_lines)

    def get_all_memories(self):
        return db.get_memories(limit=100) # limit for safety
