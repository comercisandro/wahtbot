"""Flask app creation."""
import boto3
import zipfile
import os
import sys
from flask import Flask
from app.ping import ping
from app.whatsapp import whatsapp_endpoint
from app.portal_tracker import *

BUCKET_NAME = 'iwima-tracker-app'
INVENTARIO_KEY = 'inventario/data/inventario.csv'
DETALLES_KEY = 'detalles'
INVERSIONES_KEY = 'inversiones'
MODEL = 'env/cronos'
# Active endpoints noted as following:
# (url_prefix, blueprint_object)
ACTIVE_ENDPOINTS = (("/", ping), ("/", whatsapp_endpoint), ("/", tracker_endpoint), ("/", inventario_endpoint),
                    ("/", detalles_endpoint), ("/", agregar_egreso_endpoint), ("/", agregar_ingreso_endpoint),
                    ("/", listar_egresos_endpoint), ("/", listar_ingresos_endpoint), ("/", cargar_gastos_fijos_endpoint),
                    ("/", inversiones_endpoint), ("/", agregar_inversion_endpoint))


def download_and_extract_library_from_s3(bucket_name, zip_key, extract_to='/tmp'):
    """Download and extract the library from S3."""
    s3 = boto3.client('s3')
    zip_path = f"{extract_to}/cronos.zip"

    # Download the ZIP file from S3
    with open(zip_path, 'wb') as f:
        s3.download_fileobj(bucket_name, zip_key, f)

    # Extract the ZIP file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    # Add the extracted library path to sys.path
    library_path = os.path.join(extract_to, 'cronos')  # Replace with the actual folder name
    sys.path.append(library_path)


# Call the function to download and load the library at app initialization
download_and_extract_library_from_s3(BUCKET_NAME, MODEL)


def create_app():
    """Create Flask app."""
    app = Flask(__name__)

    # accepts both /endpoint and /endpoint/ as valid URLs
    app.url_map.strict_slashes = False

    # register each active blueprint
    for url, blueprint in ACTIVE_ENDPOINTS:
        app.register_blueprint(blueprint, url_prefix=url)

    return app
