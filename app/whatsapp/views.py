from flask import jsonify, request, Blueprint
from twilio.twiml.messaging_response import MessagingResponse

whatsapp_endpoint = Blueprint("whatsapp", __name__)

@whatsapp_endpoint.route("/whatsapp", methods=['POST'])
def handler_whatsapp():
    response = MessagingResponse()

    response.message("contacta2")

    return str(response)