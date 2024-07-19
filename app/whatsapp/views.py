from flask import jsonify, request, Blueprint
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd


whatsapp_endpoint = Blueprint("whatsapp", __name__)

@whatsapp_endpoint.route("/whatsapp", methods=['POST'])
def handler_whatsapp():
    from_number = request.values.get('From')
    incoming_msg = request.values.get('Body', '').strip()
    resp = MessagingResponse()
    msg = resp.message()

    if from_number not in user_states:
        user_states[from_number] = {
            'step': 'inicio',
            'tipo': None,
            'ciudad': None,
            'precio_max': None,
            'habitaciones': None,
            'banos': None
        }

    state = user_states[from_number]

    if state['step'] == 'inicio':
        msg.body("¿Qué tipo de inmueble estás buscando? (Casa, Apartamento, Oficina)")
        state['step'] = 'tipo'
    elif state['step'] == 'tipo':
        state['tipo'] = incoming_msg
        msg.body("¿En qué ciudad estás buscando? (Ciudad A, Ciudad B)")
        state['step'] = 'ciudad'
    elif state['step'] == 'ciudad':
        state['ciudad'] = incoming_msg
        msg.body("¿Cuál es tu presupuesto máximo?")
        state['step'] = 'precio'
    elif state['step'] == 'precio':
        state['precio_max'] = int(incoming_msg)
        msg.body("¿Cuántas habitaciones necesitas?")
        state['step'] = 'habitaciones'
    elif state['step'] == 'habitaciones':
        state['habitaciones'] = int(incoming_msg)
        msg.body("¿Cuántos baños necesitas?")
        state['step'] = 'banos'
    elif state['step'] == 'banos':
        state['banos'] = int(incoming_msg)

        # Filtrar inmuebles
        inmuebles = filtrar_inmuebles(
            tipo=state['tipo'],
            ciudad=state['ciudad'],
            precio_max=state['precio_max'],
            habitaciones=state['habitaciones'],
            banos=state['banos']
        )

        if not inmuebles.empty:
            respuesta = "Inmuebles disponibles:\n"
            for index, row in inmuebles.iterrows():
                respuesta += f"{row['id']}: {row['tipo']} en {row['ciudad']} por ${row['precio']} con {row['habitaciones']} habitaciones y {row['banos']} baños.\n"
        else:
            respuesta = "No se encontraron inmuebles con los criterios especificados."

        msg.body(respuesta)
        state['step'] = 'inicio'  # Resetear la conversación
    else:
        msg.body("No entendí tu mensaje. Por favor, responde con la opción correspondiente.")

    return str(resp)


# Leer el archivo CSV
df = pd.read_csv('data/inmuebles.csv')

# Diccionario para almacenar el estado de cada usuario
user_states = {}

# Función para filtrar datos
def filtrar_inmuebles(tipo=None, ciudad=None, precio_max=None, habitaciones=None, banos=None):
    inmuebles_filtrados = df
    if tipo:
        inmuebles_filtrados = inmuebles_filtrados[inmuebles_filtrados['tipo'] == tipo]
    if ciudad:
        inmuebles_filtrados = inmuebles_filtrados[inmuebles_filtrados['ciudad'] == ciudad]
    if precio_max:
        inmuebles_filtrados = inmuebles_filtrados[inmuebles_filtrados['precio'] <= precio_max]
    if habitaciones:
        inmuebles_filtrados = inmuebles_filtrados[inmuebles_filtrados['habitaciones'] <= habitaciones]
    if banos:
        inmuebles_filtrados = inmuebles_filtrados[inmuebles_filtrados['banos'] <= banos]
    return inmuebles_filtrados
