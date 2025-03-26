import os
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

def load_api_key():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("No Groq API key found. Make sure you have a .env file with GROQ_API_KEY set.")
    return api_key

def translate_text(text, target_language='en'):
    """
    Translates text to the specified target language using deep_translator.
    
    Args:
        text: The text to translate.
        target_language: The ISO 639-1 code of the target language (e.g., 'es' for Spanish, 'fr' for French).
    
    Returns:
        The translated text.
    """
    try:
        translator = GoogleTranslator(source='auto', target=target_language)
        translation = translator.translate(text)
        return translation
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails