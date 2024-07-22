"""Flask app creation."""
from flask import Flask
from app.ping import ping
from app.whatsapp import whatsapp_endpoint
from app.portal_tracker import *

# Active endpoints noted as following:
# (url_prefix, blueprint_object)
ACTIVE_ENDPOINTS = (("/", ping), ("/", whatsapp_endpoint), ("/", tracker_endpoint), ("/", inventario_endpoint),
                    ("/", detalles_endpoint), ("/", agregar_egreso_endpoint), ("/", agregar_ingreso_endpoint),
                    ("/", listar_egresos_endpoint), ("/", listar_ingresos_endpoint), ("/", cargar_gastos_fijos_endpoint))


def create_app():
    """Create Flask app."""
    app = Flask(__name__)

    # accepts both /endpoint and /endpoint/ as valid URLs
    app.url_map.strict_slashes = False

    # register each active blueprint
    for url, blueprint in ACTIVE_ENDPOINTS:
        app.register_blueprint(blueprint, url_prefix=url)

    return app