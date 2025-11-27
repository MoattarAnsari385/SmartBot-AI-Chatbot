import streamlit as st
import google.generativeai as genai
from datetime import datetime
import os
import json
import hashlib

# Page config with custom theme
st.set_page_config(
    page_title="SmartBot AI",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    /* Chat container */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Fix chat message text color */
    .stChatMessage p, .stChatMessage span, .stChatMessage div {
        color: #1a202c !important;
    }
    
    /* User message styling */
    [data-testid="stChatMessageContent"] {
        color: #1a202c !important;
    }
    
    /* Chat message markdown */
    .stChatMessage .stMarkdown {
        color: #1a202c !important;
    }
    
    .stChatMessage .stMarkdown p {
        color: #1a202c !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    /* Chat history item styling */
    .chat-history-item {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 12px;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .chat-history-item:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateX(5px);
    }
    
    /* Input styling */
    .stChatInputContainer {
        background-color: white;
        border-radius: 25px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
    }
    
    /* Title styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-align: center;
        padding: 20px 0;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 24px;
        color: #667eea !important;
    }
    
    /* Caption styling */
    .stCaption {
        font-size: 0.75rem;
        opacity: 0.7;
        color: #4a5568 !important;
    }
    
    /* Chat message captions */
    .stChatMessage .stCaption {
        color: #718096 !important;
    }
    
    /* Chat avatar background fix - More specific selectors */
    .stChatMessage img[alt="assistant"] {
        background-color: #667eea !important;
        border-radius: 50% !important;
        padding: 10px !important;
    }
    
    .stChatMessage img[alt="user"] {
        background-color: #48bb78 !important;
        border-radius: 50% !important;
        padding: 10px !important;
    }
    
    /* Alternative avatar fix */
    [data-testid="stChatMessageAvatarAssistant"] {
        background-color: #667eea !important;
        border-radius: 50% !important;
    }
    
    [data-testid="stChatMessageAvatarUser"] {
        background-color: #48bb78 !important;
        border-radius: 50% !important;
    }
    
    /* Force avatar container background */
    .stChatMessage > div:first-child {
        background-color: transparent !important;
    }
    
    .stChatMessage[data-testid*="assistant"] > div:first-child > div {
        background-color: #667eea !important;
        border-radius: 50% !important;
        padding: 8px !important;
    }
    
    .stChatMessage[data-testid*="user"] > div:first-child > div {
        background-color: #48bb78 !important;
        border-radius: 50% !important;
        padding: 8px !important;
    }
    
    /* Selectbox styling */
    .stSelectbox {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    /* Header styling in sidebar */
    [data-testid="stSidebar"] h2 {
        color: #667eea !important;
        font-weight: 700;
        margin-top: 10px;
    }
    
    /* Success/Info messages */
    .stSuccess, .stInfo {
        background-color: rgba(102, 126, 234, 0.1);
        border-radius: 10px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

def get_user_session_id():
    """Generate unique session ID for each user"""
    try:
        if 'user_id' not in st.session_state:
            st.session_state.user_id = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:10]
        return st.session_state.user_id
    except:
        return "default_user"

def load_chat_history(user_id, chat_id=None):
    """Load chat history from file"""
    try:
        if chat_id:
            filename = f"chat_history_{user_id}_{chat_id}.json"
        else:
            filename = f"chat_history_{user_id}.json"
            
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading chat: {str(e)}")
    return []

def save_chat_history(user_id, messages, chat_id=None):
    """Save chat history to file"""
    try:
        if chat_id:
            filename = f"chat_history_{user_id}_{chat_id}.json"
        else:
            filename = f"chat_history_{user_id}.json"
            
        with open(filename, 'w') as f:
            json.dump(messages, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving chat: {str(e)}")
        return False

def get_all_chat_sessions(user_id):
    """Get list of all chat sessions with preview"""
    chat_sessions = []
    try:
        # Get all chat files for this user
        chat_files = [f for f in os.listdir('.') if f.startswith(f"chat_history_{user_id}_")]
        
        for chat_file in chat_files:
            try:
                with open(chat_file, 'r') as f:
                    messages = json.load(f)
                    
                if messages:
                    # Extract chat ID from filename
                    chat_id = chat_file.replace(f"chat_history_{user_id}_", "").replace('.json', '')
                    
                    # Get first user message as preview
                    first_user_msg = next((msg for msg in messages if msg["role"] == "user"), None)
                    preview = first_user_msg['content'][:35] + "..." if first_user_msg and len(first_user_msg['content']) > 35 else first_user_msg['content'] if first_user_msg else "Empty Chat"
                    
                    # Get last message timestamp
                    last_msg = messages[-1] if messages else None
                    last_time = last_msg.get('timestamp', 'Unknown') if last_msg else 'Unknown'
                    
                    chat_sessions.append({
                        "id": chat_id,
                        "preview": preview,
                        "message_count": len(messages),
                        "last_updated": last_time,
                        "filename": chat_file
                    })
            except Exception as e:
                continue
    except Exception as e:
        st.error(f"Error reading chat sessions: {str(e)}")
    
    # Sort by chat ID (newest first based on timestamp in ID)
    chat_sessions.sort(key=lambda x: x.get('id', ''), reverse=True)
    return chat_sessions

def get_working_model(api_key: str):
    """Get a working Gemini model with fallback options"""
    genai.configure(api_key=api_key)
    model_names = [
        'gemini-1.5-pro',           
        'gemini-1.5-flash',         
        'gemini-1.0-pro',     
        'models/gemini-1.0-pro',
        'models/gemini-2.0-flash-exp',
        'models/gemini-1.5-flash-latest'
    ]
    
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hi")
            return model
        except Exception:
            continue
    
    try:
        models = genai.list_models()
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                try:
                    test_model = genai.GenerativeModel(model.name)
                    response = test_model.generate_content("Test")
                    return test_model
                except:
                    continue
    except Exception:
        pass
    
    return None

def initialize_gemini():
    """Initialize Gemini API"""
    api_key = st.secrets.get("GEMINI_API_KEY") if hasattr(st, 'secrets') else os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        st.error("⚠️ Gemini API key not found. Please set GEMINI_API_KEY in secrets or environment.")
        return None
    
    try:
        model = get_working_model(api_key)
        if model:
            return model
        else:
            st.error("❌ No working Gemini model found!")
            return None
    except Exception as e:
        st.error(f"Error initializing Gemini: {str(e)}")
        return None

def initialize_session_state():
    """Initialize session state with persistent chat history"""
    user_id = get_user_session_id()
    
    if 'chat_initialized' not in st.session_state:
        st.session_state.chat_initialized = True
        st.session_state.user_id = user_id
        st.session_state.personality = "Friendly Assistant"
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        
        # Try to load existing chat
        st.session_state.messages = load_chat_history(user_id, st.session_state.current_chat_id)

def start_new_chat():
    """Start a new chat session"""
    user_id = get_user_session_id()
    
    # Save current chat before starting new (if it has messages)
    if st.session_state.messages:
        save_chat_history(user_id, st.session_state.messages, st.session_state.current_chat_id)
    
    # Start fresh
    st.session_state.messages = []
    st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.success("✅ New chat started!")
    st.rerun()

def load_selected_chat(chat_id):
    """Load a selected chat from history - FIXED VERSION"""
    user_id = get_user_session_id()
    
    # Save current chat first (if it has messages)
    if st.session_state.messages and st.session_state.current_chat_id != chat_id:
        save_chat_history(user_id, st.session_state.messages, st.session_state.current_chat_id)
    
    # Load selected chat
    messages = load_chat_history(user_id, chat_id)
    
    if messages:
        st.session_state.messages = messages
        st.session_state.current_chat_id = chat_id
        st.success(f"✅ Loaded chat with {len(messages)} messages")
    else:
        st.error(f"❌ Could not load chat {chat_id}")
    
    st.rerun()

def clear_current_chat():
    """Clear current chat only"""
    user_id = get_user_session_id()
    
    # Delete current chat file
    filename = f"chat_history_{user_id}_{st.session_state.current_chat_id}.json"
    try:
        if os.path.exists(filename):
            os.remove(filename)
    except:
        pass
    
    st.session_state.messages = []
    st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.success("✅ Current chat cleared!")
    st.rerun()

def clear_all_chats():
    """Clear all chat history"""
    user_id = get_user_session_id()
    try:
        chat_files = [f for f in os.listdir('.') if f.startswith(f"chat_history_{user_id}_")]
        for chat_file in chat_files:
            os.remove(chat_file)
        st.session_state.messages = []
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.success("✅ All chat history cleared!")
        st.rerun()
    except Exception as e:
        st.error(f"❌ Error clearing chats: {str(e)}")

def get_gemini_response(model, user_message, personality):
    """Get response from Gemini"""
    try:
        personality_instructions = {
            "Friendly Assistant": "You are a friendly and helpful assistant. Keep responses conversational, warm, and engaging.",
            "Professional Advisor": "You are a professional advisor. Provide clear, structured, and authoritative advice.",
            "Funny Companion": "You are a witty and humorous companion. Add clever humor and fun to your responses.",
            "Technical Expert": "You are a technical expert. Explain concepts clearly with examples and precision."
        }
        
        instruction = personality_instructions.get(personality, "Respond helpfully and concisely.")
        
        prompt = f"{instruction}\n\nUser: {user_message}\n\nAssistant:"
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error generating response: {str(e)}"

def main():
    initialize_session_state()
    model = initialize_gemini()
    
    # Header
    st.title("🤖 SmartBot AI")
    st.markdown("*Your intelligent conversation companion*")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Chat Settings")
        
        # New Chat Button - Prominent
        if st.button("🆕 Start New Chat", use_container_width=True, type="primary"):
            start_new_chat()
        
        st.markdown("")
        
        # Personality selector
        st.session_state.personality = st.selectbox(
            "🎭 Chat Personality:",
            ["Friendly Assistant", "Professional Advisor", "Funny Companion", "Technical Expert"],
            index=["Friendly Assistant", "Professional Advisor", "Funny Companion", "Technical Expert"].index(st.session_state.personality)
        )
        
        st.markdown("")
        
        # Clear buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Current", use_container_width=True):
                clear_current_chat()
        with col2:
            if st.button("🗑️ Clear All", use_container_width=True):
                clear_all_chats()
        
        st.markdown("---")
        
        # Chat History Section
        st.markdown("## 📝 Chat History")
        
        user_id = get_user_session_id()
        chat_sessions = get_all_chat_sessions(user_id)
        
        if chat_sessions:
            for idx, session in enumerate(chat_sessions):
                # Highlight current chat
                is_current = session['id'] == st.session_state.current_chat_id
                
                # Create container for each chat
                with st.container():
                    # Chat button with unique key
                    button_label = f"{'🔵' if is_current else '💬'} {session['preview']}"
                    
                    if st.button(
                        button_label,
                        key=f"load_chat_{session['id']}_{idx}",
                        use_container_width=True,
                        type="primary" if is_current else "secondary"
                    ):
                        if not is_current:
                            load_selected_chat(session['id'])
                    
                    # Show metadata
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.caption(f"📊 {session['message_count']} messages")
                    with col2:
                        st.caption(f"🕐 {session['last_updated']}")
                    
                    st.markdown("")
        else:
            st.info("💡 No previous chats found. Start chatting to create history!")
        
        st.markdown("---")
        
        # About section
        st.markdown("## ℹ️ About")
        st.markdown("""
        **SmartBot AI Features:**
        
        ✨ Smart conversational AI  
        🎭 Multiple personalities  
        💾 Auto-saved chat history  
        🔄 Switch between chats  
        ⚡ Real-time responses  
        
        **Tips:**
        - Click any chat to load it
        - Current chat is marked with 🔵
        - All chats are auto-saved
        """)
        
        # Current stats
        if st.session_state.messages:
            st.metric("💬 Current Messages", len(st.session_state.messages))
    
    # Main chat area
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.messages:
            st.info("👋 Welcome to SmartBot AI! Start a conversation below.")
        
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message['content'])
                    st.caption(f"You • {message['timestamp']}")
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(message['content'])
                    st.caption(f"SmartBot • {message['timestamp']}")
    
    # Input field
    user_input = st.chat_input("💭 Type your message here...")
    
    if user_input:
        if model is None:
            st.error("⚠️ Please configure your Gemini API key first.")
            return
        
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": current_time
        })
        
        # Save after user message
        user_id = get_user_session_id()
        save_chat_history(user_id, st.session_state.messages, st.session_state.current_chat_id)
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
            st.caption(f"You • {current_time}")
        
        # Get bot response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🤔 SmartBot is thinking..."):
                bot_response = get_gemini_response(model, user_input, st.session_state.personality)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": bot_response,
                    "timestamp": current_time
                })
                
                # Save after bot response
                save_chat_history(user_id, st.session_state.messages, st.session_state.current_chat_id)
                
                st.markdown(bot_response)
                st.caption(f"SmartBot • {current_time}")
        
        st.rerun()

if __name__ == "__main__":
    main()