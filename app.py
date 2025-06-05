import streamlit as st

# Page config MUST be the first Streamlit command
st.set_page_config(
    page_title="EquityTool: Research Assistant", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import authentication functions


import fitz  # PyMuPDF
import pandas as pd
import google.generativeai as genai
from langdetect import detect
import requests
from bs4 import BeautifulSoup
import time

# ------------------ CONFIG ------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Initialize theme in session state
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# ------------------ THEME-BASED CSS ------------------
def get_custom_css(theme="Light"):
    if theme == "Light":
        # Improved Light theme colors
        main_bg = "#f8fafb"
        content_bg = "#ffffff"
        card_bg = "#ffffff"
        text_color = "#2c3e50"
        border_color = "#e1e8ed"
        input_bg = "#ffffff"
        input_text = "#2c3e50"
        sidebar_bg = "linear-gradient(180deg, #ffffff 0%, #f8fafb 100%)"
        user_msg_bg = "#f0f9ff"
        assistant_msg_bg = "#ffffff"
        system_msg_bg = "rgba(0, 166, 125, 0.08)"
        system_msg_text = "#1a5f53"
        placeholder_color = "#6b7280"
        
    else:  # Dark theme
        # Dark theme colors
        main_bg = "#1a1a1a"
        content_bg = "#2d2d2d"
        card_bg = "#2d2d2d"
        text_color = "#e0e0e0"
        border_color = "#404040"
        input_bg = "#2b303b"
        input_text = "#ffffff"
        sidebar_bg = "linear-gradient(180deg, #2d2d2d 0%, #1a1a1a 100%)"
        user_msg_bg = "#3a4a3d"
        assistant_msg_bg = "#2d2d2d"
        system_msg_bg = "rgba(0, 166, 125, 0.2)"
        system_msg_text = "#4dc3a0"
        placeholder_color = "#aaa"
    
    return f"""
<style>
/* Google Fonts Import */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=DM+Sans:wght@400;500;700&display=swap');

/* Main container styling with font family */
.main {{
    padding-top: 1rem;
    background-color: {main_bg} !important;
    color: {text_color};
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
}}

/* Base font for all elements */
* {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
}}

/* Main content area background */
[data-testid="stAppViewContainer"] {{
    background-color: {main_bg} !important;
}}

/* Hide streamlit style */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}

/* Custom header with specific font */
.custom-header {{
    background: linear-gradient(135deg, #00a67d 0%, #00c49a 100%);
    padding: 1rem 0;
    border-radius: 10px;
    margin-bottom: 2rem;
    text-align: center;
    color: white;
    box-shadow: 0 4px 12px rgba(0, 166, 125, 0.15);
    font-family: 'DM Sans', 'Inter', sans-serif;
}}

.custom-header h1 {{
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
    font-family: 'DM Sans', 'Inter', sans-serif;
}}

.custom-header p {{
    margin: 0.5rem 0 0 0;
    font-size: 1rem;
    opacity: 0.9;
    font-family: 'DM Sans', 'Inter', sans-serif;
    font-weight: 400;
}}

/* Chat container */
.chat-container {{
    max-width: 800px;
    margin: 0 auto;
    padding: 1rem;
}}

/* Chat messages */
.chat-message {{
    padding: 1.5rem;
    margin: 1rem 0;
    border-radius: 15px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    animation: fadeIn 0.5s ease-in;
    border: 1px solid {border_color};
    line-height: 1.5;
    font-size: 1rem;
}}

.user-message {{
    background: {user_msg_bg};
    color: {text_color};
    margin-left: 2rem;
    border: 1px solid #e0f2fe;
    border-bottom-right-radius: 5px;
    position: relative;
}}

.assistant-message {{
    background: {assistant_msg_bg};
    color: {text_color};
    margin-right: 2rem;
    border: 1px solid {border_color};
    border-bottom-left-radius: 5px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}}

.system-message {{
    background: {system_msg_bg};
    color: {system_msg_text};
    text-align: center;
    margin: 0.5rem 2rem;
    border: 1px solid rgba(0, 166, 125, 0.15);
    font-weight: 500;
}}

/* Strong text in messages */
.chat-message strong {{
    font-weight: 600;
}}

/* Input styling */
.stTextInput > div > div > input {{
    border-radius: 12px;
    border: 2px solid {border_color};
    padding: 1rem 1.25rem;
    font-size: 1rem;
    background-color: {input_bg};
    color: {input_text};
    transition: all 0.3s ease;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    font-family: 'Inter', sans-serif;
}}

.stTextInput > div > div > input:focus {{
    border-color: #00a67d;
    box-shadow: 0 0 0 3px rgba(0, 166, 125, 0.1);
    outline: none;
}}

.stTextInput > div > div > input::placeholder {{
    color: {placeholder_color} !important;
    font-style: italic;
    font-family: 'Inter', sans-serif;
}}

/* Button styling */
.stButton > button {{
    width: 100%;
    border-radius: 8px;
    border: none;
    background: linear-gradient(135deg, #00a67d 0%, #00c49a 100%);
    color: white;
    padding: 0.75rem 1rem;
    font-size: 1rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 2px 6px rgba(0, 166, 125, 0.2);
    font-family: 'Inter', sans-serif;
}}

.stButton > button:hover {{
    transform: translateY(-1px);
    background: linear-gradient(135deg, #00c49a 0%, #00d4a6 100%);
    box-shadow: 0 4px 12px rgba(0, 166, 125, 0.3);
}}

/* File uploader styling */
.stFileUploader {{
    border: 2px dashed #00a67d;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    background: rgba(0, 166, 125, 0.02);
    transition: all 0.3s ease;
    margin: 1rem 0;
}}

.stFileUploader:hover {{
    background: rgba(0, 166, 125, 0.05);
    border-color: #00c49a;
    transform: translateY(-1px);
}}

/* Sidebar styling */
.css-1d391kg, [data-testid="stSidebar"] {{
    background: {sidebar_bg} !important;
    font-family: 'Inter', sans-serif;
}}

/* Sidebar text color */
[data-testid="stSidebar"] .element-container {{
    color: {text_color};
}}

.stSidebar .sidebar-content {{
    color: {text_color};
}}

/* Sidebar headings */
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3, 
[data-testid="stSidebar"] h4 {{
    font-family: 'DM Sans', 'Inter', sans-serif;
    font-weight: 600;
}}

/* Success/Warning/Error messages */
.stSuccess {{
    border-radius: 10px;
    padding: 1rem;
    border: none;
    background-color: rgba(0, 166, 125, 0.1);
    color: #00866a;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    font-family: 'Inter', sans-serif;
}}

.stWarning {{
    border-radius: 10px;
    padding: 1rem;
    border: none;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    font-family: 'Inter', sans-serif;
}}

.stError {{
    border-radius: 10px;
    padding: 1rem;
    border: none;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    font-family: 'Inter', sans-serif;
}}

/* Loading animation */
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

/* Typing indicator */
.typing-indicator {{
    display: flex;
    align-items: center;
    padding: 1rem;
    background: {user_msg_bg};
    border-radius: 15px;
    margin: 1rem 2rem 1rem 0;
    animation: fadeIn 0.5s ease-in;
    font-family: 'Inter', sans-serif;
}}

.typing-indicator::after {{
    content: "●●●";
    animation: typing 1.5s infinite;
    color: #00a67d;
    font-size: 1.5rem;
    margin-left: 0.5rem;
}}

@keyframes typing {{
    0%, 60%, 100% {{ opacity: 0; }}
    30% {{ opacity: 1; }}
}}

/* Cards for content sections */
.content-card {{
    background: {card_bg};
    color: {text_color};
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    border: 1px solid {border_color};
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}}

.content-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.06);
    border-color: #00a67d;
}}

/* Stats cards */
.stats-card {{
    background: linear-gradient(135deg, #00a67d 0%, #00c49a 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    margin: 0.5rem;
    box-shadow: 0 3px 10px rgba(0, 166, 125, 0.2);
}}

.stats-card h3 {{
    margin: 0;
    font-size: 1.8rem;
    font-family: 'DM Sans', 'Inter', sans-serif;
    font-weight: 700;
}}

.stats-card p {{
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
    font-family: 'Inter', sans-serif;
    font-weight: 400;
}}

/* Info message styling */
.stInfo {{
    background-color: rgba(0, 166, 125, 0.08);
    color: #1a5f53;
    border: 1px solid rgba(0, 166, 125, 0.2);
    border-radius: 10px;
    padding: 1rem;
    font-weight: 500;
    font-family: 'Inter', sans-serif;
}}

/* Select box styling */
.stSelectbox > div > div {{
    background-color: {input_bg};
    color: {text_color};
    border-radius: 12px;
    border: 2px solid {border_color};
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    transition: all 0.3s ease;
    font-family: 'Inter', sans-serif;
}}

.stSelectbox > div > div:hover {{
    border-color: #00a67d;
}}

/* Text area styling */
.stTextArea > div > div > textarea {{
    background-color: {input_bg};
    color: {input_text};
    border: 2px solid {border_color};
    border-radius: 12px;
    padding: 1rem;
    font-family: 'Inter', sans-serif;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    transition: all 0.3s ease;
    line-height: 1.5;
}}

.stTextArea > div > div > textarea:focus {{
    border-color: #00a67d;
    box-shadow: 0 0 0 3px rgba(0, 166, 125, 0.1);
    outline: none;
}}

.stTextArea > div > div > textarea::placeholder {{
    color: {placeholder_color};
    font-style: italic;
    font-family: 'Inter', sans-serif;
}}

/* Divider styling */
hr {{
    border-top: 1px solid {border_color};
    margin: 2rem 0;
}}

/* Footer styling */
.footer {{
    text-align: center;
    opacity: 0.7;
    padding: 1rem;
    color: {text_color};
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
}}

/* Theme toggle button container */
.theme-toggle {{
    display: flex;
    justify-content: center;
    margin: 1rem 0;
}}

.theme-toggle button {{
    background: #00a67d;
    border: none;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.3s ease;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
}}

.theme-toggle button:hover {{
    background: #00c49a;
    transform: translateY(-2px);
}}

/* Style for markdown content */
.markdown-text-container {{
    color: {text_color};
    font-family: 'Inter', sans-serif;
}}

/* Override streamlit's default text colors */
.stMarkdown, .stMarkdown * {{
    color: {text_color} !important;
    font-family: 'Inter', sans-serif;
}}

/* Headers styling */
h1, h2, h3, h4, h5, h6 {{
    font-family: 'DM Sans', 'Inter', sans-serif !important;
    font-weight: 600;
    color: {text_color} !important;
}}

/* Radio button styling */
.stRadio > div {{
    background-color: {card_bg};
    border-radius: 8px;
    padding: 0.5rem;
    border: 1px solid {border_color};
    font-family: 'Inter', sans-serif;
}}

.stRadio label {{
    color: {text_color} !important;
    font-family: 'Inter', sans-serif;
}}

/* Code blocks */
code {{
    font-family: 'JetBrains Mono', 'SF Mono', 'Menlo', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', monospace;
    font-size: 0.9em;
}}

/* Lists styling */
ul, ol {{
    font-family: 'Inter', sans-serif;
    line-height: 1.6;
}}

/* Additional overrides for light/dark mode */
.streamlit-expanderHeader, .streamlit-expanderContent {{
    background-color: {card_bg} !important;
    color: {text_color} !important;
}}

/* Override stApp container background */
.stApp {{
    background-color: {main_bg} !important;
}}
</style>
"""

# Apply the CSS
st.markdown(get_custom_css(st.session_state.theme), unsafe_allow_html=True)

# ------------------ TEXT EXTRACTORS ------------------

def extract_text_from_pdf(uploaded_file):
    text = ""
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)
    return df.to_string(index=False)

def extract_text_from_txt(uploaded_file):
    return uploaded_file.read().decode("utf-8")

def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Get visible text only
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        return "\n".join(paragraphs[:50])  # Limit to 50 paragraphs
    except Exception as e:
        return f"Error fetching {url}: {e}"

# ------------------ GEMINI Q&A ------------------

def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"

def ask_question_with_gemini(content_text, question):
    lang = detect_language(question)
    prompt = f"""
You are a helpful research assistant called EquityTool. Use the below content to answer the question.
Content:
\"\"\"
{content_text}
\"\"\"

Now answer this in the same language:

Question ({lang}): {question}
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# ------------------ STREAMLIT UI ------------------

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "content_loaded" not in st.session_state:
    st.session_state.content_loaded = False
if "total_content" not in st.session_state:
    st.session_state.total_content = ""
if "question" not in st.session_state:
    st.session_state.question = ""

# Add initial welcome message if the chat is empty
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "👋 Hello! I'm EquityTool, your research assistant powered by Google Gemini AI. Upload some content or add URLs in the sidebar, and I'll help you analyze and answer questions about it."
    })

# Custom header
st.markdown(f"""
<div class="custom-header">
    <h1>📊 EquityTool: Research Assistant</h1>
    <p>Upload documents • Analyze web content • Get insights in any language</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for content management
with st.sidebar:
    # Theme toggle at the top of sidebar
    st.markdown("### 🎨 Theme")
    theme_options = ["Light", "Dark"]
    selected_theme = st.radio(
        "Choose theme",
        theme_options,
        index=theme_options.index(st.session_state.theme),
        key="theme_selector",
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Add logout button if user is authenticated
    if "authenticated" in st.session_state and st.session_state["authenticated"]:
        if st.button("Logout"):
            logout()
    
    # Update theme if changed
    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 📁 Content Sources")
    
    # Resource type selection
    resource_type = st.selectbox(
        "Choose resource type:",
        ["📄 Upload Document", "🌐 Add Web Article", "📝 Enter Text Directly"],
        index=0
    )
    
    content_text = ""
    
    if resource_type == "📄 Upload Document":
        st.markdown("#### Upload Documents")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "csv", "txt"],
            help="Supported formats: PDF, CSV, TXT"
        )
        
        if uploaded_file and st.button("📊 Process Document", type="primary"):
            with st.spinner("Processing document..."):
                if uploaded_file.type == "application/pdf":
                    content_text = extract_text_from_pdf(uploaded_file)
                    st.session_state.content_source = f"📄 PDF: {uploaded_file.name}"
                elif uploaded_file.type == "text/csv":
                    content_text = extract_text_from_csv(uploaded_file)
                    st.session_state.content_source = f"📊 CSV: {uploaded_file.name}"
                elif uploaded_file.type == "text/plain":
                    content_text = extract_text_from_txt(uploaded_file)
                    st.session_state.content_source = f"📝 TXT: {uploaded_file.name}"
    
    elif resource_type == "🌐 Add Web Article":
        st.markdown("#### Add Web Articles (up to 3)")
        urls = []
        
        # Three URL inputs
        for i in range(1, 4):
            url = st.text_input(f"URL {i}:", placeholder=f"https://example{i}.com/article", key=f"url_{i}")
            if url.strip():
                urls.append(url.strip())
        
        if urls and st.button("🌐 Fetch All Articles", type="primary"):
            content_text = ""
            progress_bar = st.progress(0)
            
            for i, url in enumerate(urls):
                with st.spinner(f"Fetching article {i+1} of {len(urls)}..."):
                    article_content = extract_text_from_url(url)
                    content_text += f"\n\n--- Article {i+1} from {url} ---\n\n" + article_content
                    progress_bar.progress((i + 1) / len(urls))
            
            progress_bar.empty()
            st.session_state.content_source = f"🌐 Web Articles: {len(urls)} articles loaded"
    
    elif resource_type == "📝 Enter Text Directly":
        st.markdown("#### Direct Text Input")
        direct_text = st.text_area(
            "Paste your text here:",
            height=200,
            placeholder="Enter or paste your text content here..."
        )
        
        if direct_text and st.button("📝 Use Text", type="primary"):
            content_text = direct_text
            st.session_state.content_source = f"📝 Direct input ({len(direct_text)} chars)"
    
    # Process the content if any
    if content_text.strip():
        st.session_state.total_content = content_text
        st.session_state.content_loaded = True
        st.success(f"✅ Content loaded successfully!")
        
        # Add system message to chat
        source_info = getattr(st.session_state, 'content_source', 'Unknown source')
        st.session_state.messages.append({
            "role": "system",
            "content": f"Content loaded from: {source_info}. Ready for questions!"
        })
        st.rerun()
    
    # Show current content source
    if st.session_state.content_loaded and hasattr(st.session_state, 'content_source'):
        st.markdown("### 📌 Current Source")
        st.info(st.session_state.content_source)
        
        if st.button("🗑️ Clear Content"):
            st.session_state.content_loaded = False
            st.session_state.total_content = ""
            if hasattr(st.session_state, 'content_source'):
                delattr(st.session_state, 'content_source')
            st.session_state.messages.append({
                "role": "system",
                "content": "Content cleared. Please load new content to continue."
            })
            st.rerun()
    
    # Content stats
    if st.session_state.content_loaded:
        st.markdown("### 📊 Content Statistics")
        content_length = len(st.session_state.total_content)
        word_count = len(st.session_state.total_content.split())
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="stats-card">
                <h3>{content_length:,}</h3>
                <p>Characters</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stats-card">
                <h3>{word_count:,}</h3>
                <p>Words</p>
            </div>
            """, unsafe_allow_html=True)



# Main chat interface
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You:</strong> {message['content']}
        </div>
        """, unsafe_allow_html=True)
    elif message["role"] == "assistant":
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>EquityTool:</strong> {message['content']}
        </div>
        """, unsafe_allow_html=True)
    elif message["role"] == "system":
        st.markdown(f"""
        <div class="chat-message system-message">
            ℹ️ {message['content']}
        </div>
        """, unsafe_allow_html=True)

# Function to handle the message submission
def handle_submit():
    if st.session_state.question.strip():
        question = st.session_state.question
        st.session_state.question = ""  # Clear input BEFORE running the rest of the code
        
        if not st.session_state.content_loaded:
            st.session_state.messages.append({
                "role": "system",
                "content": "⚠️ Please load some content first using the sidebar!"
            })
            st.rerun()
            return
        
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })
        
        # Generate response
        answer = ask_question_with_gemini(st.session_state.total_content, question)
        
        # Add assistant response to chat
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })
        
        st.rerun()

# Chat input - Using on_change callback instead of checking in the main flow
col1, col2 = st.columns([4, 1])

with col1:
    st.text_input(
        "Ask your question...",
        key="question",
        placeholder="Ask a question about your content...",
        label_visibility="collapsed",
        on_change=handle_submit
    )

with col2:
    st.button("Send", type="primary", use_container_width=True, on_click=handle_submit)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
theme_emoji = "🌞" if st.session_state.theme == "Light" else "🌙"
st.markdown(f"""
<div class="footer">
    Made by 💕 | {theme_emoji} {st.session_state.theme} Theme
</div>
""", unsafe_allow_html=True)