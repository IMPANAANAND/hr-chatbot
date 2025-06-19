import streamlit as st
import requests
import json
import logging

st.set_page_config(page_title="HR Resource Query Chatbot", layout="wide")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8000/chat"

def initialize_session():
    """Initialize Streamlit session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

def display_employee_card(emp: dict):
    """Display employee info as a card."""
    with st.container():
        st.markdown(
            f"""
            <div style="border: 1px solid #ccc; padding: 10px; margin: 10px;">
                <h4>{emp['name']} (ID: {emp['id']})</h4>
                <p><b>Skills:</b> {', '.join(emp['skills'])}</p>
                <p><b>Experience:</b> {emp['experience_years']} years</p>
                <p><b>Projects:</b> {', '.join(emp['projects'])}</p>
                <p><b>Availability:</b> {emp['availability']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

def main():
    """Main Streamlit app."""
    initialize_session()

    st.title("HR Resource Query Chatbot")
    st.write("Ask about employees by skills, experience, or projects (e.g., 'Find Python developers with 3+ years experience').")

    # Chat input
    with st.container():
        query = st.text_input("Enter your query:", placeholder="e.g., Find developers who know AWS and Docker")
        if st.button("Send"):
            if query:
                st.session_state.messages.append({"role": "user", "content": query})
                try:
                    # Call API
                    response = requests.post(API_URL, json={"query": query})
                    response.raise_for_status()
                    result = response.json()

                    # Display response
                    st.session_state.messages.append({"role": "assistant", "content": result["response"]})
                    
                    # Display employee cards
                    for emp in result["employees"]:
                        display_employee_card(emp)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    logger.error(f"Error calling API: {e}")

    # Display chat history
    with st.container():
        st.subheader("Chat History")
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"<b>You:</b> {msg['content']}", unsafe_allow_html=True)
            else:
                st.markdown(f"<b>Assistant:</b> {msg['content']}", unsafe_allow_html=True)

if __name__ == "__main__":
    main()