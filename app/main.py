import streamlit as st
import os
import sys
from agent.agent import FoodieSpotAgent
from datetime import datetime, timedelta

# Don't load environment variables from .env
# load_dotenv()

# Initialize Streamlit page
st.set_page_config(
    page_title="FoodieSpot Reservation Assistant",
    page_icon="🍽️",
    layout="wide"
)

def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent" not in st.session_state:
        # Hardcode API key and configuration
        openai_api_key = "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"
        openai_model = "gpt-4-turbo-preview"
        track_performance = True
            
        # Initialize the agent
        st.session_state.agent = FoodieSpotAgent(
            openai_api_key=openai_api_key,
            openai_model=openai_model,
            track_performance=track_performance
        )
    # Store user information
    if "user_info" not in st.session_state:
        st.session_state.user_info = {
            "name": None,
            "email": None,
            "phone": None,
            "last_restaurant": None,
            "last_party_size": None
        }
    # Store current date and time information
    if "date_info" not in st.session_state:
        today = datetime.now()
        st.session_state.date_info = {
            "today": today.strftime("%Y-%m-%d"),
            "tomorrow": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
            "this_weekend": {
                "saturday": (today + timedelta((5 - today.weekday()) % 7)).strftime("%Y-%m-%d"),
                "sunday": (today + timedelta((6 - today.weekday()) % 7)).strftime("%Y-%m-%d")
            },
            "next_weekend": {
                "saturday": (today + timedelta((5 - today.weekday()) % 7 + 7)).strftime("%Y-%m-%d"),
                "sunday": (today + timedelta((6 - today.weekday()) % 7 + 7)).strftime("%Y-%m-%d")
            },
            "current_time": today.strftime("%H:%M")
        }

def extract_user_info(message):
    """
    Extract user information from messages to maintain context
    """
    # Extract name from greeting patterns
    name_patterns = [
        r"(?i)hi\s+(?:i['']?m|my\s+name\s+is)\s+(\w+)",
        r"(?i)hello\s+(?:i['']?m|my\s+name\s+is)\s+(\w+)",
        r"(?i)(?:i['']?m|my\s+name\s+is)\s+(\w+)",
        r"(?i)(?:this\s+is|it['']?s)\s+(\w+)(?:\s+here)?",
        r"(?i)hi\s+(\w+)\s+here",
        r"(?i)hello\s+(\w+)\s+here"
    ]
    
    import re
    # Check for name patterns
    for pattern in name_patterns:
        match = re.search(pattern, message)
        if match:
            name = match.group(1).strip()
            if len(name) > 1:  # Filter out single letters
                st.session_state.user_info["name"] = name
                break
    
    # Extract phone number patterns
    phone_pattern = r'\b(?:\+\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)?\d{3}[\s-]?\d{4}\b'
    phone_match = re.search(phone_pattern, message)
    if phone_match:
        st.session_state.user_info["phone"] = phone_match.group(0)
    
    # Extract email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, message)
    if email_match:
        st.session_state.user_info["email"] = email_match.group(0)
    
    # Extract party size patterns
    party_patterns = [
        r"(?i)(?:table|reservation)\s+for\s+(\d+)",
        r"(?i)for\s+(\d+)\s+(?:people|persons|guests)",
        r"(?i)party\s+of\s+(\d+)",
        r"(?i)(\d+)\s+(?:people|persons|guests)"
    ]
    
    for pattern in party_patterns:
        match = re.search(pattern, message)
        if match:
            try:
                party_size = int(match.group(1))
                if 1 <= party_size <= 20:  # Reasonable party size range
                    st.session_state.user_info["last_party_size"] = party_size
                    break
            except (ValueError, TypeError):
                pass

def enrich_user_message(message):
    """
    Enrich user message with context information from session state
    """
    extract_user_info(message)
    
    # Check for date references
    date_enrichment = None
    time_enrichment = None
    
    # Process date references
    if "today" in message.lower():
        date_enrichment = st.session_state.date_info["today"]
    elif "tomorrow" in message.lower():
        date_enrichment = st.session_state.date_info["tomorrow"]
    elif "this weekend" in message.lower() or "this saturday" in message.lower():
        date_enrichment = st.session_state.date_info["this_weekend"]["saturday"]
    elif "this sunday" in message.lower():
        date_enrichment = st.session_state.date_info["this_weekend"]["sunday"]
    elif "next weekend" in message.lower() or "next saturday" in message.lower():
        date_enrichment = st.session_state.date_info["next_weekend"]["saturday"]
    elif "next sunday" in message.lower():
        date_enrichment = st.session_state.date_info["next_weekend"]["sunday"]
    
    # Add context information
    context = []
    
    # Add date information if found
    if date_enrichment:
        context.append(f"The date is: {date_enrichment}")
    
    # Add stored user information
    if st.session_state.user_info["name"]:
        context.append(f"This user's name is: {st.session_state.user_info['name']}")
    if st.session_state.user_info["email"]:
        context.append(f"User's email: {st.session_state.user_info['email']}")
    if st.session_state.user_info["phone"]:
        context.append(f"User's phone: {st.session_state.user_info['phone']}")
    if st.session_state.user_info["last_party_size"]:
        context.append(f"Requested party size: {st.session_state.user_info['last_party_size']}")
    
    # Add current time
    current_time = datetime.now().strftime("%H:%M")
    context.append(f"Current time is: {current_time}")
    
    # Return original message if no context to add
    if not context:
        return message
    
    # Return enriched message with context
    enriched_message = f"{message}\n\n[System Context Information: {'. '.join(context)}]"
    return enriched_message

def main():
    # Initialize session state
    initialize_session_state()
    
    # Page header
    st.title("🍽️ FoodieSpot Reservation Assistant")
    st.markdown("""
    Welcome to FoodieSpot's AI-powered reservation assistant! I can help you:
    - Find restaurants based on your preferences
    - Check availability
    - Make reservations
    
    Just tell me what you're looking for!
    """)
    
    # Chat interface
    chat_container = st.container()
    
    # Display chat messages
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What kind of restaurant are you looking for?"):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Enrich the user message with context information
        enriched_prompt = enrich_user_message(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.agent.process_message(enriched_prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Reset button
    if st.sidebar.button("Reset Conversation"):
        st.session_state.messages = []
        st.session_state.agent.reset_conversation()
        # Reset user information except for name
        name = st.session_state.user_info.get("name")
        st.session_state.user_info = {
            "name": name,  # Keep the name
            "email": None,
            "phone": None,
            "last_restaurant": None,
            "last_party_size": None
        }
        st.rerun()
    
    # Sidebar information
    st.sidebar.title("About")
    st.sidebar.info("""
    FoodieSpot Reservation Assistant helps you discover and book tables at our restaurants.
    
    Features:
    - Multiple cuisines
    - Various locations
    - Different ambiance options
    - Real-time availability
    """)

if __name__ == "__main__":
    main() 