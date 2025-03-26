import os
from utils import load_api_key
import groq
import streamlit as st
def initialize_groq():
    """
    Initializes the Groq API client.
    
    Returns:
        Groq client instance
    """
    api_key = st.secrets["api"]
    try:
        client = groq.Groq(api_key=api_key)
        return client
    except Exception as e:
        raise ValueError(f"Error initializing Groq API: {e}")

def list_available_groq_models(client):
    """
    List available Groq models.
    
    Args:
        client: Initialized Groq client
    
    Returns:
        List of available model IDs
    """
    try:
        models = client.models.list()
        available_models = [model.id for model in models.data]
        print("Available Groq Models:")
        for model in available_models:
            print(f"- {model}")
        return available_models
    except Exception as e:
        print(f"Error listing models: {e}")
        return []

def generate_response(model, prompt, history=None):
    """
    Generates a response from the Groq model.
    
    Args:
        model: Initialized Groq client
        prompt: User's input prompt
        history: Conversation history (optional)
    
    Returns:
        Generated response
    """
    try:
        # Get available models
        available_models = list_available_groq_models(model)
        
        if not available_models:
            return "No Groq models are currently available. Please check your API settings."
        
        # Use the first available model
        selected_model = available_models[0]
        
        system_prompt = """You are MediMate, a helpful and empathetic AI assistant providing preliminary health information. Act like a doctor speaking to a patient. Keep responses brief (max 3 sentences)."""
        
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})
        
        chat_completion = model.chat.completions.create(
            messages=messages,
            model=selected_model,
            temperature=0.7,
        )
        
        return chat_completion.choices[0].message.content
    
    except Exception as e:
        print(f"Groq API error: {e}")
        return f"Error generating response: {str(e)}"

def create_initial_prompt(user_input, age=None, gender=None, weight=None, height=None, medical_history=None, location=None, bmi=None, max_sentences=3):
    """
    Formats user data for the Groq model, including BMI.
    
    Args:
        user_input: User's health description
        age, gender, weight, height, etc.: User's health details
    
    Returns:
        Formatted prompt for the model
    """
    bmi_string = f"{bmi:.2f}" if bmi is not None else "Not provided"
    prompt = f"""I'm feeling unwell and experiencing: '{user_input}'.Here are some details about me that might be helpful:- Age: {age if age is not None else "Not provided"}- Gender: {gender if gender else "Not provided"}- Weight: {weight if weight is not None else "Not provided"}- Height: {height if height is not None else "Not provided"}- BMI: {bmi_string}- Medical History: {medical_history if medical_history else "Not provided"}- Location: {location if location else "Not provided"}Could you please provide a brief assessment and some recommendations based on this information?"""
    return prompt

def ask_clarifying_question(model, current_prompt):
    """
    Asks a clarifying question to the user based on the current prompt.
    
    Args:
        model: Initialized Groq client
        current_prompt: Current conversation context
    
    Returns:
        A clarifying question
    """
    clarification_prompt = f"""Based on our conversation so far: '{current_prompt}', to better understand your situation, could you tell me a little more about...? (Please suggest ONE specific clarifying question)."""
    response = generate_response(model, clarification_prompt)
    return response

def format_history(history):
    """
    Formats the conversation history into the format expected by the Groq API.
    
    Args:
        history: A list of dictionaries with 'role' and 'content' keys
    
    Returns:
        Formatted conversation history
    """
    formatted_history = []
    for message in history:
        formatted_history.append({"role": message["role"], "content": message["content"]})
    return formatted_history
