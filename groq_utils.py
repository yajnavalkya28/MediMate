# groq_utils.py
import os
import groq
import random
import re  # Import the regular expression module
import streamlit as st

def initialize_groq():
    """Initializes the Groq API client."""
    api_key = st.secrets["api"]
    try:
        client = groq.Groq(api_key=api_key)
        return client
    except Exception as e:
        raise ValueError(f"Error initializing Groq API: {e}")


def generate_response(model, prompt, history=None):
    """Generates a response from the Groq model."""
    try:
        # Define the structured system prompt
        structured_system_prompt = """You are MediMate, a helpful and empathetic AI assistant providing preliminary health information. Act like a doctor speaking to a patient. Keep responses VERY brief and to the point (max 2 sentences per bullet point).

ONLY provide information related to health and medical symptoms. If the user asks about recipes, travel, entertainment, or ANY other non-medical topic, you MUST respond ONLY with: "I am designed to provide health information only. I cannot assist with that request." There are NO EXCEPTIONS.

When a patient describes their symptoms, your goal is to:

1. Acknowledge their concern and offer reassurance.
2. Briefly assess their symptoms and suggest a possible cause, using empathetic language. Avoid definitive diagnoses.
3. Suggest simple, SAFE home remedies or first aid measures (if appropriate and safe), explaining WHY they might help and any precautions. Limit to well-established, generally safe remedies.
4. If appropriate, suggest over-the-counter (OTC) medications with clear dosage instructions, potential side effects, and a strong disclaimer.
5. Provide specific guidance on when the user should seek medical attention, including symptoms that warrant seeing a doctor or going to the emergency room.
6. Indicate whether the patient should see a doctor ("See a Doctor? Yes/No, with brief reason"), providing clear and understandable reasons. Be conservative - if there's any doubt, recommend seeing a doctor.

Here are some examples of how you can format your responses (choose one and vary it):

**Option 1:**

Okay, I understand you're feeling [symptoms]. It sounds like it could be [possible cause].

* Home Care: [Remedies and explanations - max 2 sentences]
* OTC Medications: [Medications, dosages, side effects, and disclaimer - max 2 sentences]
* When to See a Doctor: [Specific symptoms - max 2 sentences]
* See a Doctor?: [Yes/No, with reason - max 2 sentences]

**Option 2:**

Based on what you've described, it seems like you might have [possible cause]. Here are some things you can try:

* Home Remedies: [Remedies and explanations - max 2 sentences]
* Over-the-Counter Options: [Medications, dosages, side effects, and disclaimer - max 2 sentences]
* When to Seek Medical Help: [Specific symptoms - max 2 sentences]
* Should you see a doctor?: [Yes/No, with reason - max 2 sentences]

**Option 3:**

I'm sorry to hear you're feeling [symptoms]. It could be due to [possible cause].

* What you can do at home: [Remedies and explanations - max 2 sentences]
* OTC Medication Suggestions: [Medications, dosages, side effects, and disclaimer - max 2 sentences]
* When to get medical attention: [Specific symptoms - max 2 sentences]
* Doctor Visit?: [Yes/No, with reason - max 2 sentences]

Remember to always include the following disclaimer when recommending medications:

**Disclaimer:** This information is for informational purposes only and does not constitute medical advice. Always consult with a doctor or pharmacist before taking any medication, especially if you have any existing medical conditions or are taking other medications.
"""

        # Define the general chat system prompt
        general_chat_system_prompt = """You are MediMate, a helpful and empathetic AI assistant providing preliminary health information. Act like a doctor speaking to a patient. Keep responses VERY brief and to the point (max 2 sentences).

ONLY provide information related to health and medical symptoms. If the user asks about recipes, travel, entertainment, or ANY other non-medical topic, you MUST respond ONLY with: "I am designed to provide health information only. I cannot assist with that request." There are NO EXCEPTIONS.

In subsequent turns, avoid repeating information about the user's age, weight, or BMI unless it is directly relevant to the current question.

When a user reports a symptom, provide a brief and empathetic response. Then, ask a clarifying question to gather more information. For example:

* If the user says "I have a fever," you could respond with "I'm sorry to hear that you have a fever. Can you tell me how high your fever is and if you have any other symptoms, such as chills or body aches?"
* If the user says "I have a headache," you could respond with "I understand you have a headache. Where is the headache located and how severe is it on a scale of 1 to 10?"
* If the user says "I have a cough," you could respond with "I'm sorry to hear that you have a cough. Is it a dry cough or are you bringing up any mucus? How long have you had the cough?"

If the user provides an acknowledgment like "okay," "thanks," or "okay thanks," respond with a brief and encouraging message. For example:

* You could respond with "You're welcome! Please let me know if you have any other questions or concerns."
* You could respond with "I'm glad I could help. Please don't hesitate to reach out if you need anything else."
* You could respond with "Okay, I'm here if you need anything else. Take care!"

Remember to always prioritize safety and recommend seeking professional medical attention when necessary, but only if the symptoms are severe or persistent.
"""

        # Determine if it's the first turn
        is_first_turn = not history

        if is_first_turn:
            # Extract format options using regular expressions
            format_options = re.findall(r"\*\*Option \d+:\*\*(.*?)Remember to always include", structured_system_prompt, re.DOTALL)

            # Choose a random format option
            chosen_format = random.choice(format_options).strip()

            # Construct the dynamic system prompt
            dynamic_system_prompt = f"""You are MediMate, a helpful and empathetic AI assistant providing preliminary health information. Act like a doctor speaking to a patient. Keep responses VERY brief and to the point (max 2 sentences per bullet point).

ONLY provide information related to health and medical symptoms. If the user asks about recipes, travel, entertainment, or ANY other non-medical topic, you MUST respond ONLY with: "I am designed to provide health information only. I cannot assist with that request." There are NO EXCEPTIONS.

When a patient describes their symptoms, your goal is to:

1. Acknowledge their concern and offer reassurance.
2. Briefly assess their symptoms and suggest a possible cause, using empathetic language. Avoid definitive diagnoses.
3. Suggest simple, SAFE home remedies or first aid measures (if appropriate and safe), explaining WHY they might help and any precautions. Limit to well-established, generally safe remedies.
4. If appropriate, suggest over-the-counter (OTC) medications with clear dosage instructions, potential side effects, and a strong disclaimer.
5. Provide specific guidance on when the user should seek medical attention, including symptoms that warrant seeing a doctor or going to the emergency room.
6. Indicate whether the patient should see a doctor ("See a Doctor? Yes/No, with brief reason"), providing clear and understandable reasons. Be conservative - if there's any doubt, recommend seeing a doctor.

Here's the format you should use:

{chosen_format}

Remember to always include the following disclaimer when recommending medications:

**Disclaimer:** This information is for informational purposes only and does not constitute medical advice. Always consult with a doctor or pharmacist before taking any medication, especially if you have any existing medical conditions or are taking other medications.
"""
            system_prompt = dynamic_system_prompt
        else:
            # Use the general chat system prompt for subsequent turns
            system_prompt = general_chat_system_prompt

        messages = [{"role": "system", "content": system_prompt}]

        if history:
            messages.extend(format_history(history))  # Use format_history to ensure proper structure

        messages.append({"role": "user", "content": prompt})

        chat_completion = model.chat.completions.create(
            messages=messages,
            model="llama-3.2-1b-preview",  # Keep your chosen model
            temperature=0.4,  # Adjust temperature as needed (e.g., 0.3)
        )

        response_text = chat_completion.choices[0].message.content

        # Remove rigid post-processing, but keep the non-health topic check
        if any(keyword in response_text.lower() for keyword in ["recipe", "ingredients", "noodles", "cook", "food"]):
            return "I am designed to provide health information only. I cannot assist with that request."

        return response_text

    except Exception as e:
        print(f"Groq API error: {e}")
        return "Error generating response. Please check the Groq API and your connection."


def create_initial_prompt(user_input, age=None, gender=None, weight=None, height=None, medical_history=None, location=None, bmi=None, max_sentences=3):
    """Formats user data for the Groq model, including BMI."""

    # No Input Validation
    bmi_string = f"{bmi:.2f}" if bmi is not None else "Not provided"

    prompt = f"""I'm feeling unwell and experiencing: '{user_input}'.

Here are some details about me that might be helpful:
- Age: {age if age is not None else "Not provided"}
- Gender: {gender if gender else "Not provided"}
- Weight: {weight if weight is not None else "Not provided"}
- Height: {height if height is not None else "Not provided"}
- BMI: {bmi_string}
- Medical History: {medical_history if medical_history is not None else "Not provided"}
- Location: {location if location is not None else "Not provided"}

Could you please provide a brief assessment and some recommendations based on this information?
"""

    return prompt


def ask_clarifying_question(model, current_prompt):
    """Asks a clarifying question to the user based on the current prompt."""
    clarification_prompt = f"""Based on our conversation so far: '{current_prompt}', to better understand your symptoms, could you please provide more details about the location and intensity of your discomfort?"""  # More specific question

    try:
        response = generate_response(model, clarification_prompt)
        return response
    except Exception as e:
        print(f"Error asking clarifying question: {e}")
        return "Could you please provide more information about your symptoms?"


def format_history(history):
    """Formats the conversation history into the format expected by the Groq API."""
    formatted_history = []
    for message in history:
        formatted_history.append({"role": message["role"], "content": message["content"]})
    return formatted_history
