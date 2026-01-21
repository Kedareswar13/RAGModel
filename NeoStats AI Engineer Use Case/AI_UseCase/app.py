import streamlit as st
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from models.llm import get_chatgroq_model
from db.database import init_db
from app.rag_pipeline import build_vectorstore_from_pdfs
from app.tools import rag_tool, booking_persistence_tool, email_tool
from app.admin_dashboard import render_admin_dashboard
from app.booking_flow import get_booking_state, summarize_booking, is_complete

def instructions_page():
    """Instructions and setup page"""
    st.title("The Chatbot Blueprint")
    st.markdown("Welcome! Follow these instructions to set up and use the chatbot.")
    
    st.markdown("""
    ## 🔧 Installation
                
    
    First, install the required dependencies: (Add Additional Libraries base don your needs)
    
    ```bash
    pip install -r requirements.txt
    ```
    
    ## API Key Setup
    
    You'll need API keys from your chosen provider. Get them from:
    
    ### OpenAI
    - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
    - Create a new API key
    - Set the variables in config
    
    ### Groq
    - Visit [Groq Console](https://console.groq.com/keys)
    - Create a new API key
    - Set the variables in config
    
    ### Google Gemini
    - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
    - Create a new API key
    - Set the variables in config
    
    ## 📝 Available Models
    
    ### OpenAI Models
    Check [OpenAI Models Documentation](https://platform.openai.com/docs/models) for the latest available models.
    Popular models include:
    - `gpt-4o` - Latest GPT-4 Omni model
    - `gpt-4o-mini` - Faster, cost-effective version
    - `gpt-3.5-turbo` - Fast and affordable
    
    ### Groq Models
    Check [Groq Models Documentation](https://console.groq.com/docs/models) for available models.
    Popular models include:
    - `llama-3.1-70b-versatile` - Large, powerful model
    - `llama-3.1-8b-instant` - Fast, smaller model
    - `mixtral-8x7b-32768` - Good balance of speed and capability
    
    ### Google Gemini Models
    Check [Gemini Models Documentation](https://ai.google.dev/gemini-api/docs/models/gemini) for available models.
    Popular models include:
    - `gemini-1.5-pro` - Most capable model
    - `gemini-1.5-flash` - Fast and efficient
    - `gemini-pro` - Standard model
    
    ## How to Use
    
    1. **Go to the Chat page** (use the navigation in the sidebar)
    2. **Start chatting** once everything is configured!
    
    ## Tips
    
    - **System Prompts**: Customize the AI's personality and behavior
    - **Model Selection**: Different models have different capabilities and costs
    - **API Keys**: Can be entered in the app or set as environment variables
    - **Chat History**: Persists during your session but resets when you refresh
    
    ## Troubleshooting
    
    - **API Key Issues**: Make sure your API key is valid and has sufficient credits
    - **Model Not Found**: Check the provider's documentation for correct model names
    - **Connection Errors**: Verify your internet connection and API service status
    
    ---
    
    Ready to start chatting? Navigate to the **Chat & Booking** page using the sidebar! 
    """)

def chat_and_booking_page():
    """Main chat, RAG, and booking interface page."""
    st.title("🤖 AI Booking Assistant")

    # Initialize DB (idempotent)
    init_db()

    # Short-term memory: last 25 messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None

    if "booking_mode" not in st.session_state:
        st.session_state.booking_mode = False

    booking_state = get_booking_state(st.session_state)

    try:
        llm = get_chatgroq_model()
    except Exception as e:
        llm = None
        st.warning(f"LLM not available: {e}")

    # PDF upload for RAG
    uploaded_pdfs = st.file_uploader(
        "Upload PDFs for RAG (optional)",
        type=["pdf"],
        accept_multiple_files=True,
    )
    if uploaded_pdfs:
        with st.spinner("Building knowledge base from PDFs..."):
            try:
                st.session_state.vectorstore = build_vectorstore_from_pdfs(uploaded_pdfs)
                st.success("Knowledge base updated from uploaded PDFs.")
            except Exception as e:
                st.error(f"Failed to build knowledge base: {e}")

    # Display chat history (limit to last 25 messages)
    for message in st.session_state.messages[-25:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Ask a question or say 'I want to book an appointment'...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Simple intent detection for booking
        is_booking_intent = any(
            kw in user_input.lower() for kw in ["book", "appointment", "reservation"]
        )
        if is_booking_intent:
            st.session_state.booking_mode = True

        with st.chat_message("assistant"):
            if is_booking_intent:
                st.markdown(
                    "I can help you with a booking. Please fill in the booking form below."
                )
            else:
                if llm is None:
                    answer = "LLM is not configured. Please set GROQ_API_KEY in environment or Streamlit secrets."
                else:
                    if st.session_state.vectorstore is not None:
                        answer = rag_tool(user_input, st.session_state.vectorstore, llm)
                    else:
                        response = llm.invoke(user_input)
                        answer = getattr(response, "content", str(response))

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

    # Booking form (slot filling via UI)
    if st.session_state.booking_mode:
        st.divider()
        st.subheader("Booking Details")

        col1, col2 = st.columns(2)
        with col1:
            booking_state.name = st.text_input("Name", value=booking_state.name)
            booking_state.email = st.text_input("Email", value=booking_state.email)
            booking_state.phone = st.text_input("Phone", value=booking_state.phone)
        with col2:
            booking_state.booking_type = st.text_input(
                "Booking type (e.g., doctor, salon)",
                value=booking_state.booking_type,
            )
            booking_state.date = st.text_input(
                "Preferred date (YYYY-MM-DD)", value=booking_state.date
            )
            booking_state.time = st.text_input(
                "Preferred time (HH:MM)", value=booking_state.time
            )

        if is_complete(booking_state):
            st.info(summarize_booking(booking_state))
            if st.button("✅ Confirm Booking"):
                payload = {
                    "name": booking_state.name,
                    "email": booking_state.email,
                    "phone": booking_state.phone,
                    "booking_type": booking_state.booking_type,
                    "date": booking_state.date,
                    "time": booking_state.time,
                }
                result = booking_persistence_tool(payload)
                if not result.get("success"):
                    st.error(f"Failed to save booking: {result.get('error')}")
                else:
                    booking_id = result.get("booking_id")
                    st.success(f"Booking saved with ID: {booking_id}")

                    # Send confirmation email
                    email_body = (
                        f"Hello {booking_state.name},\n\n"
                        f"Your booking (ID: {booking_id}) is confirmed.\n"
                        f"Type: {booking_state.booking_type}\n"
                        f"Date: {booking_state.date}\n"
                        f"Time: {booking_state.time}\n\n"
                        "Thank you."
                    )
                    email_result = email_tool(
                        to_email=booking_state.email,
                        subject="Booking Confirmation",
                        body=email_body,
                    )
                    if not email_result.get("success"):
                        st.warning(
                            "Email could not be sent, but booking was saved. "
                            f"Reason: {email_result.get('error')}"
                        )
                    else:
                        st.info("Confirmation email sent successfully.")

                    # Reset booking state and exit booking mode
                    st.session_state.booking_mode = False
                    st.session_state.booking_state = None


def main():
    st.set_page_config(
        page_title="AI Booking Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    with st.sidebar:
        st.title("Navigation")
        page = st.radio(
            "Go to:",
            ["Chat & Booking", "Admin Dashboard", "Instructions"],
            index=0,
        )

        if page == "Chat & Booking":
            st.divider()
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

    if page == "Instructions":
        instructions_page()
    elif page == "Admin Dashboard":
        render_admin_dashboard()
    else:
        chat_and_booking_page()

if __name__ == "__main__":
    main()