from flask import jsonify, request, Blueprint, render_template
import boto3
from app.portal_tracker.functions import obtener_csv_de_s3, handle_post_agregar_egreso


# Inicializa el cliente de S3
s3_client = boto3.client('s3')
BUCKET_NAME = 'iwima-tracker-app'
INVENTARIO_KEY = 'inventario/data/inventario.csv'
DETALLES_KEY = 'detalles'


# Definición de blueprints
tracker_endpoint = Blueprint("tracker", __name__)
inventario_endpoint = Blueprint("inventario", __name__)
detalles_endpoint = Blueprint("detalles", __name__)
agregar_egreso_endpoint = Blueprint("agregar_egreso", __name__)


@tracker_endpoint.route("/", methods=['GET'])
def handler_tracker():
    return render_template('portal.html')

@inventario_endpoint.route("/inventario", methods=['GET'])
def inventario():
    try:
        df = obtener_csv_de_s3(BUCKET_NAME, INVENTARIO_KEY)
        data = df.to_dict(orient='records')
        return render_template('inventario.html', data=data)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Ocurrió un error inesperado."}), 500

@detalles_endpoint.route('/detalles/<item_id>', methods=['GET'])
def ver_detalles(item_id):
    try:
        df = obtener_csv_de_s3(BUCKET_NAME, f"{DETALLES_KEY}/{item_id}/egresos.csv", delimiter=',')
        detalles = df.to_dict(orient='records') if not df.empty else []
        return render_template('detalles.html', detalles=detalles, item_id=item_id)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Ocurrió un error inesperado."}), 500

@agregar_egreso_endpoint.route('/agregar_egreso/<item_id>', methods=['GET', 'POST'])
def agregar_egreso(item_id):
    if request.method == 'GET':
        return render_template('agregar_egreso.html', item_id=item_id)

    if request.method == 'POST':
        return handle_post_agregar_egreso(item_id)

    return jsonify({"error": "Método HTTP no soportado."}), 405
