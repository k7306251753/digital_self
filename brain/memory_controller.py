from . import db
import re

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
        
        # Strip trailing punctuation which might be left over (like "2022?")
        # We keep some like ')' if it matches '(' but for now just aggressive right strip of sentence enders
        cleaned = cleaned.rstrip('.?!,;:')
        
        return cleaned.strip()

    def process_input(self, user_input: str, user_id=None):
        """
        Analyzes input for memory commands.
        Returns: (is_command, response_message)
        """
        normalized = user_input.strip()
        lower_input = normalized.lower()
        
        # 1. Clean starting punctuation like "Remember," -> "remember"
        # We want to check prefixes against a version that has no leading non-alphanumeric chars (except space)
        clean_start = re.sub(r'^[^a-zA-Z0-9\s]+', '', lower_input).strip()
        
        # Explicit command prefixes
        command_prefixes = [
            "remember that", "remember:", "learn that", "store this:", 
            "can you remember", "please remember", "could you remember",
            "i want you to remember", "make a note that"
        ]
        
        # Check explicit long prefixes first
        for prefix in command_prefixes:
            if clean_start.startswith(prefix):
                 # Find approximate location in original string to preserve case in content
                 # We look for the prefix in the lower_input
                 idx = lower_input.find(prefix)
                 if idx == -1: continue # Should not happen if startswith matches, unless punctuation logic differs
                 
                 content = normalized[idx + len(prefix):].strip()
                 # Clean leading punctuation from content like ": " or ", " or " that"
                 content = re.sub(r'^[\s,:]+', '', content)
                 
                 if not content:
                     return True, "I need something to remember."
                 
                 # Extract clean fact
                 fact = self._extract_fact(content)
                 category = self._classify(fact)
                 db.add_memory(category, fact, user_id=user_id)
                 return True, f"I have stored that in my memory as a {category}."
        
        # Catch basic "Remember X" if not caught above
        if clean_start.startswith("remember") and not clean_start.startswith("remembering"):
             idx = lower_input.find("remember")
             if idx != -1:
                 content = normalized[idx + 8:].strip()
                 content = re.sub(r'^[\s,:]+', '', content)
                 
                 if content:
                     fact = self._extract_fact(content)
                     category = self._classify(fact)
                     db.add_memory(category, fact, user_id=user_id)
                     return True, f"I have put '{fact}' into long-term memory."

        return False, None

    def store_observation(self, content: str, user_id=None):
        """
        Implicitly stores an observation/fact from the user.
        We only store if it looks informative (simple heuristic).
        """
        if len(content.split()) < 3: return # Skip short greetings like "hi"
        
        # Avoid storing questions as facts
        # However, if input was "Can you remember X?" and fell through, we might want it? 
        # But process_input should catch that now.
        if "?" in content: return
        
        # Don't store if it looks like a command/navigation that wasn't caught
        if content.lower().startswith("when") or content.lower().startswith("what") or content.lower().startswith("how"):
             return
        
        # Extract clean fact before storing
        fact = self._extract_fact(content)
        if not fact or len(fact.split()) < 2:
            return  # Skip if extraction results in too short content
        
        category = self._classify(fact)
        db.add_memory(category, fact, user_id=user_id)
        return f"Memory added: {fact} ({category})"

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

    def retrieve_context(self, query: str, user_id=None) -> str:
        """
        Retrieves relevant memories for a prompt.
        """
        memories = db.search_memories(query, user_id=user_id)
        if not memories:
            return ""
        
        context_lines = ["Relevant Memories:"]
        for m in memories:
            context_lines.append(f"- [{m['category']}] {m['content']}")
        
        return "\n".join(context_lines)

    def get_all_memories(self, user_id=None):
        return db.get_memories(user_id=user_id, limit=100) # limit for safety
