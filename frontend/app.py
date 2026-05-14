import streamlit as st
import requests
import time

st.set_page_config(page_title="SHLense | Elite Intelligence", page_icon="🏛️", layout="centered", initial_sidebar_state="expanded")

API_URL = "http://localhost:8000/chat"

def stream_text(text):
    """Generator to simulate a typing effect for the UI."""
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.04)

# Inject Custom CSS for an Elite, Classy, High-End Corporate Look
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,400&family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #0A0A0A;
        color: #E0E0E0;
    }
    
    /* Header styling */
    .main-header {
        font-family: 'Playfair Display', serif;
        font-weight: 600;
        font-size: 3.8rem;
        color: #FFFFFF;
        margin-bottom: 5px;
        text-align: center;
        padding-top: 20px;
        letter-spacing: 0.02em;
    }
    
    .sub-header {
        font-family: 'Inter', sans-serif;
        font-weight: 300;
        color: #A0A0A0;
        text-align: center;
        margin-bottom: 50px;
        font-size: 1.05rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
    }

    /* Recommendation Cards */
    .rec-card {
        background: rgba(20, 20, 20, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 4px;
        padding: 30px;
        margin-bottom: 25px;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    /* Elegant subtle top border accent */
    .rec-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        opacity: 0;
        transition: opacity 0.4s ease;
    }

    .rec-card:hover {
        transform: translateY(-2px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.15);
    }
    
    .rec-card:hover::before {
        opacity: 1;
    }

    .rec-title {
        font-family: 'Playfair Display', serif;
        margin: 0 0 10px 0;
        color: #FFFFFF;
        font-size: 1.5rem;
        font-weight: 600;
        letter-spacing: 0.01em;
    }

    .rec-type {
        margin: 0 0 25px 0;
        color: #888888;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.2em;
        text-transform: uppercase;
    }

    /* Elite Minimalist Button */
    .rec-btn {
        text-decoration: none;
        color: #FFFFFF !important;
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 10px 24px;
        font-size: 0.85rem;
        font-weight: 400;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        display: inline-block;
        transition: all 0.3s ease;
    }
    
    .rec-btn:hover {
        background: #FFFFFF;
        color: #000000 !important;
        border-color: #FFFFFF;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Make chat input glow on hover/focus */
    [data-testid="stChatInput"] {
        transition: all 0.3s ease !important;
        border-radius: 8px !important;
    }
    [data-testid="stChatInput"]:hover, [data-testid="stChatInput"]:focus-within {
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">SHLense.</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Conversational SHL Assessment Intelligence</p>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []
    
if "ended" not in st.session_state:
    st.session_state.ended = False

def process_query(query_text):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": query_text})
    
    with st.spinner("Analyzing intelligence..."):
        try:
            # Strip out local UI-only keys like 'stream' before sending to API to prevent schema errors
            api_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            payload = {"messages": api_messages}
            
            response = requests.post(API_URL, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                assistant_reply = data.get("reply", "")
                recs = data.get("recommendations", [])
                
                # Append assistant reply with a flag to trigger the streaming effect on next render
                st.session_state.messages.append({"role": "assistant", "content": assistant_reply, "stream": True})
                st.session_state.recommendations = recs
                
                # Rerun to cleanly render the new state
                st.rerun()
            else:
                st.error(f"API Error: {response.text}")
        except Exception as e:
            st.error(f"Connection failed: {e}")

# Sidebar controls
with st.sidebar:
    st.markdown('<div style="text-align: center; margin-bottom: 20px;"><span style="font-family: \'Playfair Display\', serif; font-size: 1.5rem; font-weight: 600; color: #FFFFFF;">SHLense</span></div>', unsafe_allow_html=True)
    
    if st.button("Initialize New Session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.recommendations = []
        st.session_state.ended = False
        st.rerun()
        
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    # Preset "Quick Try" Buttons
    st.markdown('<p style="font-size: 0.85rem; color: #A0A0A0; margin-bottom: 10px; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;">Quick Actions</p>', unsafe_allow_html=True)
    
    if st.button("Assess a Java Developer", use_container_width=True):
        process_query("I need an assessment for a mid-level Java developer.")
        
    if st.button("Compare OPQ and GSA", use_container_width=True):
        process_query("What is the difference between the OPQ and the GSA test?")
        
    if st.button("Need a Personality Test", use_container_width=True):
        process_query("Can you recommend a personality questionnaire for leadership?")

    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    st.markdown('<p style="font-size: 0.8rem; color: #666; text-align: center;">Assessment Intelligence System<br>Version 1.0</p>', unsafe_allow_html=True)

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("stream", False):
            # Stream the text for a typing effect
            st.write_stream(stream_text(msg["content"]))
            # Turn off streaming so it renders instantly on future re-runs
            msg["stream"] = False
        else:
            st.write(msg["content"])

# Display recommendations if available
if st.session_state.recommendations:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-family: \"Playfair Display\", serif; font-weight: 400; font-style: italic; color: #FFFFFF;'>Curated Assessments</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    for rec in st.session_state.recommendations:
        with st.container():
            st.markdown(f"""
            <div class="rec-card">
                <h4 class="rec-title">{rec.get('name')}</h4>
                <div class="rec-type">Classification: {rec.get('test_type')}</div>
                <a href="{rec.get('url')}" target="_blank" class="rec-btn">Examine Details</a>
            </div>
            """, unsafe_allow_html=True)

# Chat Input
user_input = st.chat_input("Inquire regarding assessment parameters...")
if user_input:
    process_query(user_input)
