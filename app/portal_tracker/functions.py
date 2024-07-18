import pandas as pd
from io import StringIO
import boto3
from flask import jsonify, request, redirect, url_for
# Inicializa el cliente de S3
s3_client = boto3.client('s3')
BUCKET_NAME = 'iwima-tracker-app'
INVENTARIO_KEY = 'inventario/data/inventario.csv'
DETALLES_KEY = 'detalles'

def obtener_csv_de_s3(bucket, key, delimiter=';'):
    try:
        s3_object = s3_client.get_object(Bucket=bucket, Key=key)
        return pd.read_csv(StringIO(s3_object['Body'].read().decode('utf-8')), delimiter=delimiter)
    except s3_client.exceptions.NoSuchKey:
        raise FileNotFoundError(f"El archivo {key} no existe en el bucket {bucket}.")
    except Exception as e:
        raise Exception(f"Error al obtener el archivo CSV de S3: {e}")


def handle_post_agregar_egreso(item_id):
    fecha = request.form.get('fecha')
    tipo = request.form.get('tipo')
    detalle = request.form.get('detalle')
    monto = request.form.get('monto')

    try:
        df = obtener_csv_de_s3(BUCKET_NAME, f"{DETALLES_KEY}/{item_id}/egresos.csv", delimiter=',')
        new_entry = pd.DataFrame({'fecha': [fecha], 'tipo': [tipo], 'detalle': [detalle], 'monto': [monto]})
        df = pd.concat([df, new_entry], ignore_index=True)

        with StringIO() as output_csv:
            df.to_csv(output_csv, index=False)
            s3_client.put_object(Bucket=BUCKET_NAME, Key=f"{DETALLES_KEY}/{item_id}/egresos.csv",
                                 Body=output_csv.getvalue().encode('utf-8'))

        return redirect(url_for('detalles.ver_detalles', item_id=item_id))

    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Ocurrió un error inesperado al agregar egreso."}), 500
