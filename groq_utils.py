# groq_utils.py
import os
from utils import load_api_key
import groq  # Assuming the Groq API client library is named 'groq'
import streamlit as st

def initialize_groq():
    """Initializes the Groq API client."""
    api_key = st.secrets["api"]
    try:
        client = groq.Groq(api_key=api_key)  # Replace with the actual Groq API client initialization
        return client
    except Exception as e:
        raise ValueError(f"Error initializing Groq API: {e}")

def generate_response(model, prompt, history=None):
    """Generates a response from the Groq model."""
    try:
        system_prompt = """You are MediMate, a helpful and empathetic AI assistant providing preliminary health information. Act like a doctor speaking to a patient. Keep responses brief (max 3 sentences).

When a patient describes their symptoms, your goal is to:

1. Acknowledge their concern and offer reassurance.
2. Briefly assess their symptoms and suggest a possible cause, using empathetic language.
3. For potentially serious conditions (e.g., chest pain, difficulty breathing, severe abdominal pain, sudden vision changes), DO NOT recommend over-the-counter medications. Instead, strongly advise the patient to seek immediate medical attention.
4. Suggest simple home remedies or first aid measures (if appropriate and safe), explaining why they might help.
5. Indicate whether the patient should see a doctor ("See a doctor? Yes/No, with brief reason"), providing clear and understandable reasons.
6. If symptoms indicate an emergency, strongly recommend immediate medical assistance ("Seek immediate medical attention!") and explain why.

Format your response as a list of points:

* Assessment: [Brief assessment of symptoms and possible cause]
* Home Remedies:
    * [Home remedy 1] - [Brief explanation]
    * [Home remedy 2] - [Brief explanation]
    * [Home remedy 3] - [Brief explanation] (Provide up to 3 remedies)
* See a Doctor?: [Yes/No, with brief reason]

Remember to be cautious and avoid making definitive diagnoses. Always emphasize the importance of consulting with a qualified healthcare professional for accurate diagnosis and treatment.
"""

        messages = [{"role": "system", "content": system_prompt}]

        if history:
            messages.extend(history)  # Add conversation history

        messages.append({"role": "user", "content": prompt})  # Add the user's prompt

        chat_completion = model.chat.completions.create(
            messages=messages,
            model="mixtral-8x7b-32768",  # Replace with the desired Groq model
            temperature=0.7,  # Adjust temperature as needed
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Groq API error: {e}")
        return "Error generating response. Please check the Groq API and your connection."

def create_initial_prompt(user_input, age=None, gender=None, weight=None, height=None, medical_history=None, location=None, bmi=None, max_sentences=3):
    """
    Formats user data for the Groq model, including BMI.
    """
    bmi_string = f"{bmi:.2f}" if bmi is not None else "Not provided"  # Format BMI separately

    prompt = f"""I'm feeling unwell and experiencing: '{user_input}'.

Here are some details about me that might be helpful:
- Age: {age if age is not None else "Not provided"}
- Gender: {gender if gender else "Not provided"}
- Weight: {weight if weight is not None else "Not provided"}
- Height: {height if height is not None else "Not provided"}
- BMI: {bmi_string}  # Include the pre-formatted BMI string
- Medical History: {medical_history if medical_history else "Not provided"}
- Location: {location if location else "Not provided"}

Could you please provide a brief assessment and some recommendations based on this information?
"""

    return prompt

def ask_clarifying_question(model, current_prompt):
    """Asks a clarifying question to the user based on the current prompt."""
    clarification_prompt = f"""Based on our conversation so far: '{current_prompt}', to better understand your situation, could you tell me a little more about...? (Please suggest ONE specific clarifying question)."""
    response = generate_response(model, clarification_prompt)
    return response

def format_history(history):
    """
    Formats the conversation history into the format expected by the Groq API.

    Args:
        history: A list of dictionaries with 'role' and 'content' keys.

    Returns:
        A format suitable for the Groq API.
    """
    formatted_history = []
    for message in history:
        formatted_history.append({"role": message["role"], "content": message["content"]})
    return formatted_history
