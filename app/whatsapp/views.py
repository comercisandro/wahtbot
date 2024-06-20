from flask import jsonify, request, Blueprint
from twilio.twiml.messaging_response import MessagingResponse
from app.whatsapp.models import create_pipeline, translate

whatsapp_endpoint = Blueprint("whatsapp", __name__)

# Variable de estado para el contexto de la conversación
user_context = {}
result = None

@whatsapp_endpoint.route("/whatsapp", methods=['POST'])
def handler_whatsapp():
    incoming_msg = request.values.get('Body', '').lower()
    response = MessagingResponse()

    if 'hola' in incoming_msg:
        user_context['menu'] = True
        user_context['state'] = 'main_menu'
        welcome_message = (
            "¡Hola! Bienvenido a nuestro asistente virtual para WhatsApp. Por favor, elige una de las siguientes opciones:\n"
            "1. text-generation\n"
            "2. text-classification\n"
            "3. sentiment-analysis"
        )
        response.message(welcome_message)
    elif user_context.get('state') == 'main_menu' and incoming_msg == '1':
        response.message("Por favor, ingresa el texto para generar:")
        user_context['state'] = 'awaiting_text'
    elif user_context.get('state') == 'awaiting_text':
        text_to_generate = incoming_msg
        pipeline = create_pipeline('text-generation')
        result = pipeline(text_to_generate)
        user_context['generated_text'] = result[0]['generated_text']
        response.message(f"Generación de texto:\n{user_context['generated_text']}")
        response.message("¿Quieres traducir este texto al español? Responde con '1' para sí o cualquier otra cosa para no.")
        user_context['state'] = 'awaiting_translation'
    elif user_context.get('state') == 'awaiting_translation':
        if incoming_msg == '1':
            translator = translate()
            translated_text = translator(user_context['generated_text'])
            response.message(f"Texto traducido:\n{translated_text[0]['translation_text']}")
        else:
            response.message("¡Entendido! Aquí está tu respuesta original:")
            response.message(user_context['generated_text'])
        user_context['state'] = 'main_menu'
        del user_context['generated_text']
    else:
        if user_context.get('state') == 'main_menu':
            response.message("Por favor, elige una opción válida del menú.")
        else:
            response.message("¡Hola! ¿Cómo puedo ayudarte hoy?")

    return str(response)