from flask import jsonify, request, Blueprint, render_template
import pandas as pd

tracker_endpoint = Blueprint("tracker", __name__)
inventario_endpoint = Blueprint("inventario", __name__)

@tracker_endpoint.route("/", methods=['GET'])
def handler_tracker():
    return render_template('portal.html')


# Ruta para mostrar el inventario
@inventario_endpoint.route("/inventario", methods=['GET'])
def inventario():
    df = pd.read_csv("data/inventario.csv", delimiter=';')
    data = df.to_dict(orient='records')
    return render_template('inventario.html', data=data)

# Ruta para descargar el inventario como archivo Excel
# @app.route("/download", methods=['GET'])
# def download():
#     return send_file("inventario.xlsx", as_attachment=True)