import streamlit as st
from services.llm_service import ask_llm, get_suggested_questions

def get_text(message, key):
    return st.text_area(message, value="", key=key)

def ai_assistant_page():
    # Page title and introduction
    st.title("🤖 CertiGuide")
    st.markdown("""
        Welcome to **CertiGuide**, your intelligent assistant for navigating employee certifications and project data within our system. 
        Whether you're tracking certification statuses, exploring project details, or managing employee records, CertiGuide is here to assist you.
    """)

    # Sidebar settings
    st.sidebar.header("Assistant Settings")
    show_suggestions = st.sidebar.checkbox("Show Suggested Questions", value=True)

    if show_suggestions:
        st.sidebar.markdown("### Suggested Questions")
        questions = get_suggested_questions()

        # Display suggested questions as clickable buttons
        for question in questions:
            if st.sidebar.button(question):
                # Set the user input text and trigger answer fetching
                st.session_state.user_input_text = question
                st.session_state.submit_question = True
                st.rerun()  # Trigger a rerun to process the question

    # Input area for user's question
    st.subheader("Ask the AI a Question")
    st.markdown("""
        **Instructions:**  
        Type your question in the input box below. You can ask about:
        - Employee certification statuses
        - Project details
        - Certification expiration dates
        - And other data related to our system.

        If you're unsure what to ask, use the suggested questions from the sidebar.
    """)

    # Initialize session state for user input and submission flag
    if 'user_input_text' not in st.session_state:
        st.session_state.user_input_text = ""
    if 'submit_question' not in st.session_state:
        st.session_state.submit_question = False

    user_input = get_text("Type your question here:", key="user_input_text")

    # Process the question if 'submit_question' is True
    if st.session_state.submit_question:
        if user_input.strip():
            answer = ask_llm(user_input)
        else:
            st.warning("Please enter a question before clicking 'Get Answer'.")
        st.session_state.submit_question = False  # Reset the flag after processing

    # Button to submit the question to the AI
    if st.button("Get Answer"):
        if user_input.strip():
            answer = ask_llm(user_input)
        else:
            st.warning("Please enter a question before clicking 'Get Answer'.")

    # Footer or additional info
    st.markdown("""
        ---
        **Need help?**  
        Use the suggested questions in the sidebar or contact support for more assistance with formulating your queries.
    """)

# Run the AI Assistant page
ai_assistant_page()
