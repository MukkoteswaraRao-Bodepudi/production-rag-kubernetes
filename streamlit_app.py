"""
Production Streamlit frontend for the Kubernetes RAG system.
Optimized for smooth animations and compatible with Light/Dark Mode.

Run:
uv run streamlit run streamlit_app.py

Optional environment variable:
RAG_API_URL=http://127.0.0.1:8000
"""

from __future__ import annotations

import os
import time
import requests
from datetime import datetime
from typing import Any, Dict, Tuple

import streamlit as st

# ============================================================
# CONFIGURATION
# ============================================================

API_BASE_URL = os.getenv("RAG_API_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT = int(os.getenv("RAG_API_TIMEOUT", "180"))
HEALTH_TIMEOUT = 5

st.set_page_config(
    page_title="Kubernetes Knowledge Base",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# ULTRA-SMOOTH CSS (Light & Dark Mode Compatible)
# ============================================================

def inject_custom_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
            scroll-behavior: smooth;
        }
        
        /* Smooth Fade-In Animation for all elements */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Hide default Streamlit headers for a native app feel */
        #MainMenu, header, [data-testid="stToolbar"] {
            visibility: hidden !important;
            height: 0 !important;
        }
        
        /* Sidebar Glassmorphism */
        section[data-testid="stSidebar"] {
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-right: 1px solid rgba(168, 85, 247, 0.1);
        }
        
        /* Glowing Brand Logo */
        .brand-row {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 25px;
            animation: fadeIn 0.6s ease-out;
        }
        .brand-mark {
            width: 45px;
            height: 45px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
            color: #fff;
            font-size: 24px;
            box-shadow: 0 0 20px rgba(168, 85, 247, 0.4);
            transition: transform 0.3s ease;
        }
        .brand-mark:hover {
            transform: scale(1.05) rotate(5deg);
        }
        .brand-title {
            font-size: 18px;
            font-weight: 700;
            background: linear-gradient(to right, #6366f1, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .brand-subtitle { color: #888; font-size: 12px; }
        
        /* Status Pill */
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 14px;
            border: 1px solid rgba(168, 85, 247, 0.2);
            border-radius: 999px;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .status-dot { width: 8px; height: 8px; border-radius: 50%; }
        .online { color: #34d399; }
        .online .status-dot { background: #34d399; box-shadow: 0 0 10px #34d399; }
        .offline { color: #f87171; }
        .offline .status-dot { background: #f87171; box-shadow: 0 0 10px #f87171; }
        
        /* Hero Section (Empty State) */
        .hero-mark {
            width: 80px;
            height: 80px;
            margin: 0 auto 20px;
            border-radius: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #6366f1, #ec4899);
            color: #fff;
            font-size: 40px;
            box-shadow: 0 15px 35px rgba(99, 102, 241, 0.3);
            animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .hero-title {
            text-align: center;
            font-size: clamp(32px, 5vw, 48px);
            font-weight: 800;
            background: linear-gradient(to right, #6366f1, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            animation: fadeIn 1s ease-out;
        }
        
        /* Chat Bubble Styling */
        [data-testid="stChatMessage"] {
            border: 1px solid rgba(168, 85, 247, 0.1);
            border-radius: 16px !important;
            padding: 1.5rem !important;
            margin-bottom: 1.5rem;
            animation: fadeIn 0.5s ease-out forwards;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }
        [data-testid="chat-message-user"] {
            border-color: rgba(99, 102, 241, 0.3);
        }
        
        /* Button Hover Effects */
        .stButton > button {
            transition: all 0.2s ease !important;
            border-radius: 8px !important;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(168, 85, 247, 0.2) !important;
            border-color: #a855f7 !important;
            color: #a855f7 !important;
        }
        
        /* Input Area Glowing Focus (Fixed for Light & Dark Mode) */
        [data-testid="stChatInput"] {
            background: transparent !important;
        }
        [data-testid="stChatInput"] > div {
            border-radius: 16px !important;
            border: 1px solid rgba(168, 85, 247, 0.4) !important;
            transition: all 0.3s ease;
        }
        [data-testid="stChatInput"] > div:focus-within {
            border-color: #a855f7 !important;
            box-shadow: 0 0 20px rgba(168, 85, 247, 0.15) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# STATE MANAGEMENT
# ============================================================

def init_state() -> None:
    defaults = {
        "messages": [],
        "backend_online": None,
        "last_health_check": 0.0,
        "mode": "Detailed",
        "show_diagnostics": True,
        "pending_query": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def clear_conversation() -> None:
    st.session_state.messages = []
    st.session_state.pending_query = None
    st.rerun()

def queue_query(query: str) -> None:
    if query and query.strip():
        st.session_state.pending_query = query.strip()
        st.rerun()

# ============================================================
# API HELPERS
# ============================================================

def check_backend() -> bool:
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=HEALTH_TIMEOUT)
        return response.ok
    except requests.RequestException:
        return False

def call_backend(question: str, mode: str, endpoint: str = "query") -> Tuple[Dict[str, Any], bool]:
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/{endpoint}",
            json={"question": question, "mode": mode},
            timeout=REQUEST_TIMEOUT,
        )
        if not response.ok:
            try:
                body = response.json()
                detail = body.get("detail") or body.get("error") or response.text[:500]
            except ValueError:
                detail = response.text[:500]
            return {"error": f"Backend Error ({response.status_code}): {detail}"}, False
            
        return response.json(), True

    except requests.exceptions.ConnectionError:
        return {"error": f"Cannot connect to backend at {API_BASE_URL}"}, False
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The backend might be overloaded."}, False
    except Exception as exc:
        return {"error": f"Unexpected error: {str(exc)}"}, False

# ============================================================
# UI MODULES
# ============================================================

def render_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="brand-row">
                <div class="brand-mark">🌌</div>
                <div>
                    <div class="brand-title">RAG Studio</div>
                    <div class="brand-subtitle">K8s Knowledge Workspace</div>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )

        now = time.time()
        if st.session_state.backend_online is None or (now - st.session_state.last_health_check) > 15:
            st.session_state.backend_online = check_backend()
            st.session_state.last_health_check = now

        status_class = "online" if st.session_state.backend_online else "offline"
        status_label = "System Online" if st.session_state.backend_online else "System Offline"
        
        st.markdown(
            f"""
            <div class="status-pill {status_class}">
                <span class="status-dot"></span>
                {status_label}
            </div>
            """, 
            unsafe_allow_html=True
        )

        st.divider()
        
        if st.button("✨ New Session", use_container_width=True):
            clear_conversation()

        st.session_state.mode = st.radio(
            "Intelligence Level", 
            ["Detailed", "Simple"], 
            horizontal=True
        )
        
        st.session_state.show_diagnostics = st.toggle(
            "Show Analytics & Sources", 
            value=st.session_state.show_diagnostics
        )

        st.divider()
        st.caption("⚙️ **Engine Config**")
        st.caption(f"**API Endpoint:** `{API_BASE_URL}`")
        st.caption("**Model Routing:** Hybrid RAG")

        if st.button("↻ Ping Server", use_container_width=True):
            st.session_state.backend_online = check_backend()
            st.session_state.last_health_check = time.time()
            st.rerun()

def render_empty_state():
    st.markdown('<div style="height: 8vh;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-mark">✦</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Kubernetes Nexus</div>', unsafe_allow_html=True)
    
    st.markdown(
        """<div style="text-align: center; color: #888; font-size: 18px; margin-bottom: 50px;">
        Query your documentation with grounded, context-aware AI.
        </div>""", 
        unsafe_allow_html=True
    )
    
    suggestions = [
        "Deployments vs ReplicaSets: Explain the difference",
        "How do Services route traffic to Pods?",
        "What is the default Replica count for Deployments?",
        "Explain maxUnavailable and maxSurge rules"
    ]
    
    cols = st.columns(2)
    for idx, suggestion in enumerate(suggestions):
        with cols[idx % 2]:
            if st.button(suggestion, use_container_width=True):
                queue_query(suggestion)

def render_message_metadata(message: Dict[str, Any]):
    if not st.session_state.show_diagnostics or message.get("is_error"):
        return

    metadata = message.get("metadata", {})
    sources = message.get("diagnostics", {}).get("sources", [])
    latency_ms = metadata.get("latency_ms")
    
    stats_str = ""
    if latency_ms:
        stats_str += f"⚡ **{latency_ms}ms latency** "
    if sources:
        stats_str += f" | 📚 **{len(sources)} grounded sources** "
        
    if stats_str:
        st.caption(stats_str)
    
    if sources:
        with st.expander("🔍 Inspect Source References"):
            for idx, source in enumerate(sources, 1):
                doc_name = source.get("document", "Unknown document")
                page_num = source.get("page", "N/A")
                st.markdown(f"**{idx}. {doc_name}** `(Page: {page_num})`")

def render_chat_history():
    for index, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            if message["role"] == "assistant":
                render_message_metadata(message)
                
                col1, col2, col3, _ = st.columns([1, 1, 1, 8])
                with col1:
                    if st.button("👍", key=f"up_{index}"):
                        st.toast("System updated with your preference.")
                with col2:
                    if st.button("👎", key=f"down_{index}"):
                        st.toast("Feedback logged for review.")
                with col3:
                    if st.button("📋", key=f"copy_{index}"):
                        st.session_state[f"show_raw_{index}"] = not st.session_state.get(f"show_raw_{index}", False)
                        st.rerun()
                
                if st.session_state.get(f"show_raw_{index}", False):
                    st.code(message["content"], language="markdown")

def process_pending_query():
    query = st.session_state.pending_query
    
    with st.chat_message("user"):
        st.markdown(query)
        
    with st.chat_message("assistant"):
        with st.spinner("Synthesizing answer from Kubernetes vectors..."):
            result, ok = call_backend(query, st.session_state.mode)
            
        if ok:
            answer = result.get("answer", "No response synthesized.")
            st.markdown(answer)
            
            msg_payload = {
                "role": "assistant",
                "content": answer,
                "time": datetime.now().strftime("%I:%M %p"),
                "diagnostics": {"sources": result.get("sources", [])},
                "metadata": result.get("metadata", {}),
                "is_error": False,
            }
            
            st.session_state.messages.append({
                "role": "user", 
                "content": query, 
                "time": datetime.now().strftime("%I:%M %p")
            })
            st.session_state.messages.append(msg_payload)
            render_message_metadata(msg_payload)
            
        else:
            error_msg = result.get("error", "System fault detected.")
            formatted_error = f"🚨 **Connection Fault:**\n\n`{error_msg}`"
            st.error(formatted_error)
            
            st.session_state.messages.append({
                "role": "user", 
                "content": query,
                "time": datetime.now().strftime("%I:%M %p")
            })
            st.session_state.messages.append({
                "role": "assistant",
                "content": formatted_error,
                "is_error": True,
            })
            
    st.session_state.pending_query = None
    st.rerun()

# ============================================================
# MAIN APPLICATION LOOP
# ============================================================

def main():
    inject_custom_css()
    init_state()
    render_sidebar()

    if not st.session_state.messages and not st.session_state.pending_query:
        render_empty_state()
    else:
        render_chat_history()

    if st.session_state.pending_query:
        process_pending_query()

    if not st.session_state.pending_query:
        if query := st.chat_input("Enter your Kubernetes query..."):
            queue_query(query)

if __name__ == "__main__":
    main()