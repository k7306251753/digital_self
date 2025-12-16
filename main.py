import streamlit as st
from digital_self import DigitalSelf
from brain.voice_engine import VoiceEngine

# Page Config
st.set_page_config(page_title="Digital Self", layout="wide")

def init_session_state():
    """Initialize necessary session state variables."""
    if "agent" not in st.session_state:
        st.session_state.agent = DigitalSelf()
        
    if "voice" not in st.session_state:
        try:
            st.session_state.voice = VoiceEngine()
            st.session_state.voice_available = True
        except Exception as e:
            st.error(f"Voice engine failed to init: {e}")
            st.session_state.voice_available = False
            
    if "messages" not in st.session_state:
        st.session_state.messages = []

def check_health():
    """Run critical health checks."""
    # DEBUG
    print("DEBUG: Checking brain connection...")
    try:
        print(f"DEBUG: Methods on brain: {dir(st.session_state.agent.brain)}")
    except:
        pass

    if not st.session_state.agent.brain.is_ollama_connected():
        st.error("⚠️ **Ollama is not reachable.** Please ensure Ollama is installed and running (`ollama serve`).")
        st.stop()


def sidebar_ui():
    """Render sidebar."""
    with st.sidebar:
        st.header("Settings")
        enable_voice = st.checkbox("Enable Voice Output", value=False)
        st.caption("Tip: Say 'Remember ...' to teach me new things.")
        return enable_voice

def chat_ui(enable_voice):
    """Render main chat interface."""
    st.title("Digital Self AI")
    
    # Display history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Voice Input Control
    voice_btn = st.button("🎤 Listen")
    
    user_input = st.chat_input("Say something...")
    
    # Handle Voice Input
    if voice_btn and st.session_state.voice_available:
        with st.spinner("Listening..."):
            text = st.session_state.voice.listen()
            if text:
                user_input = text
                st.info(f"Heard: {text}")
    
    # Handle Processing
    if user_input:
        process_input(user_input, enable_voice)

def process_input(user_input, enable_voice):
    """Process user input and generate response."""
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Get stream
        stream = st.session_state.agent.chat(user_input)
        
        sentence_buffer = ""
        
        # Check if it's a generator or direct string (error)
        if hasattr(stream, '__iter__') and not isinstance(stream, str):
             for chunk in stream:
                # Handle Ollama chunk object or simple string yield
                content = ""
                if hasattr(chunk, 'message') and hasattr(chunk.message, 'content'):
                    content = chunk.message.content
                elif isinstance(chunk, dict) and 'message' in chunk:
                    content = chunk['message'].get('content', '')
                elif isinstance(chunk, str):
                    content = chunk
                
                full_response += content
                sentence_buffer += content
                
                # Check for sentence endings to stream voice
                if enable_voice and st.session_state.voice_available:
                    if any(punct in sentence_buffer for punct in ['.', '?', '!']):
                        # Find the last punctuation index
                        import re
                        match = re.search(r'[.?!]', sentence_buffer)
                        if match:
                            end_idx = match.end()
                            sentence = sentence_buffer[:end_idx]
                            remaining = sentence_buffer[end_idx:]
                            
                            st.session_state.voice.speak(sentence)
                            sentence_buffer = remaining
                
                response_placeholder.markdown(full_response + "▌")
        else:
             full_response = str(stream)
            
        response_placeholder.markdown(full_response)
        
        # Speak any remaining text
        if enable_voice and st.session_state.voice_available and sentence_buffer.strip():
             st.session_state.voice.speak(sentence_buffer)
    
    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Removed post-loop speak call since we stream now

def main():
    init_session_state()
    check_health()
    enable_voice = sidebar_ui()
    chat_ui(enable_voice)

if __name__ == "__main__":
    main()
