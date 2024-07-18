from flask import jsonify, request, Blueprint, render_template, redirect, url_for
import pandas as pd
import boto3
from io import StringIO
import csv

# Especifica el nombre del bucket y el nombre del archivo
bucket_name = 'iwima-tracker-app'
inventario_key = 'inventario/data/inventario.csv'
detalles_key = 'detalles'

# Inicializa la sesión de boto3 y el cliente de S3
s3_client = boto3.client('s3')

tracker_endpoint = Blueprint("tracker", __name__)
inventario_endpoint = Blueprint("inventario", __name__)
detalles_endpoint = Blueprint("detalles", __name__)
agregar_egreso_endpoint = Blueprint("agregar_egreso", __name__)


@tracker_endpoint.route("/", methods=['GET'])
def handler_tracker():
    return render_template('portal.html')


# Ruta para mostrar el inventario
@inventario_endpoint.route("/inventario", methods=['GET'])
def inventario():

    try:
        # Imprime el nombre del bucket y la clave del archivo para depuración
        print(f"Bucket: {bucket_name}, Key: {inventario_key}")

        # Descarga el archivo desde S3
        s3_object = s3_client.get_object(Bucket=bucket_name, Key=inventario_key)

        # Lee el archivo CSV en un DataFrame de pandas
        df = pd.read_csv(StringIO(s3_object['Body'].read().decode('utf-8')), delimiter=';')

        # Convierte el DataFrame a un diccionario
        data = df.to_dict(orient='records')

        # Renderiza la plantilla con los datos del inventario
        return render_template('inventario.html', data=data)

    except s3_client.exceptions.NoSuchKey:
        print("Error: El archivo especificado no existe en el bucket.")
        return jsonify({"error": "El archivo especificado no existe en el bucket."}), 404

    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"error": "Ocurrió un error inesperado."}), 500


@detalles_endpoint.route('/detalles/<item_id>', methods=['GET'])
def ver_detalles(item_id):
    try:
        print(f"Intentando obtener detalles para el elemento {item_id}")
        s3_object = s3_client.get_object(Bucket=bucket_name, Key=f"{detalles_key}/{item_id}/egresos.csv")
        df = pd.read_csv(StringIO(s3_object['Body'].read().decode('utf-8')), delimiter=',')

        detalles = df.to_dict(orient='records') if not df.empty else []

        return render_template('detalles.html', detalles=detalles, item_id=item_id)

    except s3_client.exceptions.NoSuchKey:
        print(f"Error: El archivo de detalles especificado no existe en el bucket para el item_id {item_id}.")
        return jsonify({"error": f"El archivo de detalles especificado no existe en el bucket para el item_id {item_id}."}), 404

    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"error": "Ocurrió un error inesperado."}), 500


@agregar_egreso_endpoint.route('/agregar_egreso/<item_id>', methods=['GET', 'POST'])
def agregar_egreso(item_id):
    if request.method == 'GET':
        print(f"Renderizando formulario para agregar egreso al elemento {item_id}")
        return render_template('agregar_egreso.html', item_id=item_id)

    elif request.method == 'POST':
        print(f"Agregando nuevo egreso al elemento {item_id}")
        fecha = request.form.get('fecha')
        tipo = request.form.get('tipo')
        detalle = request.form.get('detalle')
        monto = request.form.get('monto')

        try:
            # Obtener el archivo CSV actual de detalles desde S3
            print(f"Obteniendo archivo CSV actual de egresos para el elemento {item_id}")
            s3_object = s3_client.get_object(Bucket=bucket_name, Key=f"{detalles_key}/{item_id}/egresos.csv")
            current_csv_content = s3_object['Body'].read().decode('utf-8')

            # Cargar el archivo CSV en un DataFrame de pandas
            print("Cargando el archivo CSV en un DataFrame de pandas")
            df = pd.read_csv(StringIO(current_csv_content), delimiter=',')

            # Crear un nuevo DataFrame para el nuevo registro
            print("Creando un nuevo DataFrame para el nuevo registro")
            new_entry = pd.DataFrame({'fecha': [fecha], 'tipo': [tipo], 'detalle': [detalle], 'monto': [monto]})

            # Concatenar el nuevo registro con el DataFrame existente
            print("Concatenando el nuevo registro con el DataFrame existente")
            df = pd.concat([df, new_entry], ignore_index=True)

            # Guardar el DataFrame actualizado en S3
            print("Guardando el DataFrame actualizado en S3")
            with StringIO() as output_csv:
                df.to_csv(output_csv, index=False)
                s3_client.put_object(Bucket=bucket_name, Key=f"{detalles_key}/{item_id}/egresos.csv",
                                     Body=output_csv.getvalue().encode('utf-8'))

            # Redirigir de vuelta a la página de detalles del elemento
            print(f"Redirigiendo de vuelta a la página de detalles del elemento {item_id}")
            return redirect(url_for('detalles.ver_detalles', item_id=item_id))

        except s3_client.exceptions.NoSuchKey:
            print(f"Error: No se encontró el archivo de detalles para el item_id {item_id}.")
            return jsonify({"error": "No se encontró el archivo de detalles."}), 404

        except Exception as e:
            print(f"Error inesperado al agregar egreso: {e}")
            return jsonify({"error": "Ocurrió un error inesperado al agregar egreso."}), 500

    else:
        print("Método HTTP no soportado")
        return jsonify({"error": "Método HTTP no soportado."}), 405
