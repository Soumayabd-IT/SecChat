# project.py

import streamlit as st
from modules.data_store import generate_data_store
from modules.chatbot import answer_question


def main():
    """Main function to run the Streamlit chatbot application"""
    st.set_page_config(page_title="Cyber Chatbot", page_icon="🤖", layout="wide")
    st.title("🧠 Chatbot Cybersecurity – Knowledge Base & Q&A")

    # Section 1: Generate/Update Knowledge Base
    st.header("📚 Generate Chroma Database")
    if st.button("Generate / Update Database"):
        with st.spinner("Processing..."):
            generate_data_store()
            st.success("✅ Database updated successfully!")

    st.divider()

    # Section 2: Ask Questions
    st.header("💬 Ask a Question")
    query = st.text_input("Your question:")

    if query:
        # Validate input before processing
        if not validate_input(query):
            st.error("❌ Please enter a valid question.")
            return

        # Check if topic is cybersecurity-related
        if not detect_cyber_topic(query):
            st.warning("⚠️ This question seems outside the cybersecurity domain. Results may be less accurate.")

        # Get answer from RAG system
        with st.spinner("Searching in knowledge base..."):
            response, sources = answer_question(query)

        # Format and display response
        formatted_response = format_response(response)

        st.subheader("🟢 Response")
        st.write(formatted_response)

        st.subheader("📁 Sources")
        if sources:
            for i, source in enumerate(sources, 1):
                st.write(f"{i}. {source}")
        else:
            st.write("No sources available.")


def validate_input(text):
    """
    Validates that user input is not empty and contains meaningful content.

    Args:
        text: User input string

    Returns:
        bool: True if input is valid, False otherwise

    Examples:
        >>> validate_input("What is malware?")
        True
        >>> validate_input("")
        False
        >>> validate_input("   ")
        False
    """
    if text is None:
        return False
    if not isinstance(text, str):
        return False
    if not text.strip():
        return False
    return True


def detect_cyber_topic(message):
    """
    Detects if the message is related to cybersecurity topics.

    Args:
        message (str): User's message

    Returns:
        bool: True if message contains cybersecurity keywords, False otherwise

    Examples:
        >>> detect_cyber_topic("What is malware?")
        True
        >>> detect_cyber_topic("What's the weather?")
        False
    """
    if not message or not isinstance(message, str):
        return False

    # Comprehensive list of cybersecurity-related keywords
    cyber_keywords = [
        # English keywords
        'cyber', 'security', 'hack', 'malware', 'virus', 'phishing',
        'ransomware', 'firewall', 'encryption', 'vulnerability',
        'attack', 'threat', 'breach', 'password', 'authentication',
        'sql injection', 'xss', 'ddos', 'trojan', 'worm',
        'exploit', 'penetration', 'intrusion', 'antivirus',
        'spyware', 'botnet', 'zero-day', 'backdoor', 'rootkit',

        # French keywords
        'sécurité', 'attaque', 'menace', 'vulnérabilité',
        'piratage', 'chiffrement', 'pare-feu', 'rançongiciel'
    ]

    message_lower = message.lower()
    return any(keyword in message_lower for keyword in cyber_keywords)


def format_response(response):
    """
    Formats and cleans the chatbot response.

    Args:
        response (str): Raw response from the chatbot

    Returns:
        str: Formatted response or error message

    Examples:
        >>> format_response("  test  ")
        'test'
        >>> format_response("")
        'I couldn't generate a response. Please try again.'
    """
    if response is None:
        return "I couldn't generate a response. Please try again."

    if not isinstance(response, str):
        return "I couldn't generate a response. Please try again."

    # Remove extra whitespace
    formatted = response.strip()

    # Check if response is empty after stripping
    if not formatted:
        return "I couldn't generate a response. Please try again."

    # Preserve error messages (they start with ❌)
    if formatted.startswith("❌"):
        return formatted

    return formatted


if __name__ == "__main__":
    main()