# medimate_app.py
import streamlit as st
import os

os.environ['PYTHONIOENCODING'] = 'utf-8'  # Set encoding

from groq_utils import initialize_groq, generate_response, create_initial_prompt, ask_clarifying_question, format_history  # Changed import
from utils import translate_text

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

# Inject CSS for input fields
st.markdown(
    """
    <style>
    input[type="text"], input[type="number"] {
        font-family: 'Nirmala UI', 'Lohit Telugu', 'Devanagari', sans-serif !important;
        font-size: 16px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Groq model (do this only once)
try:
    model = initialize_groq()  # Changed initialization function
except ValueError as e:
    st.error(str(e))
    st.stop()

def calculate_bmi(weight_kg, height_cm):
    """Calculates BMI given weight in kg and height in cm."""
    height_m = height_cm / 100
    try:
        bmi = weight_kg / (height_m ** 2)
        return bmi
    except ZeroDivisionError:
        return None

def main():
    st.title("MediMate - Your AI Health Assistant")

    # Language selection
    languages = {
        'en': 'English',
        'te': 'తెలుగు',  # Telugu
        'hi': 'हिन्दी'  # Hindi
    }
    selected_language = st.selectbox("Select Language", options=list(languages.keys()), format_func=lambda x: languages[x])

    # User information input
    age = st.number_input("Age", min_value=1, max_value=120, value=30, step=1, format="%d")  # Number input for age
    gender = st.selectbox("Gender", options=["Male", "Female", "Other"])
    weight = st.number_input("Weight (kg)", min_value=1, max_value=300, value=70, step=1, format="%d")  # Number input for weight
    height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170, step=1, format="%d") # Number input for height
    medical_history = st.text_input("Relevant Medical History (optional)")
    location = st.text_input("Location (optional)")

    # Calculate BMI
    bmi = calculate_bmi(weight, height)
    if bmi is not None:
        st.write(f"Your BMI is: {bmi:.2f}")  # Display BMI with 2 decimal places
    else:
        st.write("Could not calculate BMI. Please check weight and height.")

    # Initialize session state for conversation history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)  # Allow HTML

    # Get user input
    if prompt := st.chat_input("Describe your health problem..."):
        # Translate user input
        translated_prompt = translate_text(prompt, selected_language)
        print(f"Translated prompt: {translated_prompt}")  # Debugging

        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": prompt})  # Store original prompt
        with st.chat_message("user"):
            st.markdown(prompt, unsafe_allow_html=True)  # Allow HTML

        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            # First turn: Create initial prompt
            if len(st.session_state.messages) == 1:
                initial_prompt = create_initial_prompt(translated_prompt, age=age, gender=gender, weight=weight, height=height, medical_history=medical_history, location=location, bmi=bmi)  # Pass BMI
                response = generate_response(model, initial_prompt, history=[])  # Pass an empty history
                full_response = response
            else:
                # Subsequent turns: Use the conversation history
                history = format_history(st.session_state.messages[:-1]) # Exclude the last message (current user prompt)
                translated_prompt = translate_text(prompt, selected_language)
                response = generate_response(model, translated_prompt, history=history)
                full_response = response

            # Translate assistant's response back to the selected language
            translated_response = translate_text(full_response, selected_language)
            print(f"Translated response: {translated_response}")  # Debugging
            message_placeholder.markdown(translated_response, unsafe_allow_html=True)  # Allow HTML

        # Add assistant message to session state
        st.session_state.messages.append({"role": "assistant", "content": full_response})  # Store original response

if __name__ == "__main__":
    main()
