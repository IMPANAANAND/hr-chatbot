import streamlit as st
import requests
import logging
import json

st.set_page_config(page_title="HR Resource Query Chatbot", layout="wide")
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8000/chat"

def initialize_session():
    """Initialize Streamlit session state."""
    logger.debug("Initializing session state")
    if "messages" not in st.session_state:
        st.session_state.messages = []
        logger.debug("Session state initialized with empty messages list")
    if "last_employees" not in st.session_state:
        st.session_state.last_employees = []

def display_employee_card(emp: dict):
    """Display employee info as a card."""
    try:
        logger.debug(f"Displaying employee card: {emp.get('id', 'Unknown')}")
        with st.container():
            st.markdown(
                f"""
                <div style="border: 1px solid #ccc; padding: 10px; margin: 10px;">
                    <h4>{emp.get('name', 'Unknown')} (ID: {emp.get('id', 'Unknown')})</h4>
                    <p><b>Skills:</b> {', '.join(emp.get('skills', []))}</p>
                    <p><b>Experience:</b> {emp.get('experience_years', 0)} years</p>
                    <p><b>Projects:</b> {', '.join(emp.get('projects', []))}</p>
                    <p><b>Availability:</b> {emp.get('availability', 'Unknown')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    except Exception as e:
        logger.error(f"Error rendering employee card: {str(e)}")
        st.error(f"Failed to render employee card: {str(e)}")

def main():
    """Main Streamlit app."""
    initialize_session()

    st.title("HR Resource Query Chatbot")
    st.write("Ask about employees by skills, experience, or projects (e.g., 'Find Python developers with 3+ years experience').")

    # Chat input
    with st.form(key="query_form"):
        query = st.text_input("Enter your query:", placeholder="e.g., Find developers who know AWS and Docker")
        submit_button = st.form_submit_button("Send")
        logger.debug(f"Received query: {query}")

        if submit_button and query:
            logger.debug(f"Appending user query to session state: {query}")
            st.session_state.messages.append({"role": "user", "content": query})
            try:
                # Call API
                logger.debug(f"Sending POST request to {API_URL} with query: {query}")
                response = requests.post(API_URL, json={"query": query})
                st.write("API Status Code:", response.status_code)
                st.write("API Raw Response:", response.text)
                response.raise_for_status()
                result = response.json()
                logger.debug(f"API response: {json.dumps(result, indent=2)}")

                # Display response
                logger.debug(f"Appending assistant response to session state: {result['response']}")
                st.session_state.messages.append({"role": "assistant", "content": result["response"]})

                # Store employees for display after rerun
                st.session_state.last_employees = result.get("employees", [])
            except Exception as e:
                logger.error(f"Error calling API: {str(e)}")
                st.error(f"Error: {str(e)}")
                st.session_state.last_employees = []

    # Always display latest employee cards after form
    if st.session_state.last_employees:
        for emp in st.session_state.last_employees:
            display_employee_card(emp)
    elif len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "assistant":
        st.info("No employees found for this query.")

    # Display chat history
    st.subheader("Chat History")
    for msg in st.session_state.messages:
        logger.debug(f"Rendering message: {msg}")
        if msg["role"] == "user":
            st.markdown(f"<b>You:</b> {msg['content']}", unsafe_allow_html=True)
        else:
            st.markdown(f"<b>Assistant:</b> {msg['content']}", unsafe_allow_html=True)

if __name__ == "__main__":
    main()