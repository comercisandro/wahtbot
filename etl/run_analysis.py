import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
from etl.technical_analysis import TechnicalAnalysis
import boto3
import logging
from io import BytesIO
import sys

from etl.models import Models

models = Models()
# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Inicializa el cliente de S3
s3 = boto3.client('s3')
S3_BUCKET_NAME = 'your-bucket-name'

# Lista de símbolos a analizar
symbols = ['DIA', 'GGAL', 'MSFT', 'BMA', 'NVDA', 'QQQ', 'SPY', 'XLE', 'YPF', 'META', 'GOOGL', 'PAMP', 'SUPV', 'BYMA', 'AMZN', 'TGNO4', 'TRAN']

def upload_file_to_s3(data, s3_key, content_type='application/json'):
    """Sube datos a S3."""
    try:
        s3.put_object(Bucket=S3_BUCKET_NAME, Key=s3_key, Body=data, ContentType=content_type)
        logging.info(f"Archivo subido a S3 como {s3_key}")
    except Exception as e:
        logging.error(f"Error al subir archivo a S3: {str(e)}")

def download_file_from_s3(s3_key):
    """Descarga un archivo desde S3."""
    try:
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        return response['Body'].read()
    except s3.exceptions.NoSuchKey:
        logging.warning(f"No se encontró el archivo en S3: {s3_key}")
        return None
    except Exception as e:
        logging.error(f"Error al descargar archivo desde S3: {str(e)}")
        return None

def run_all():
    today_date = datetime.now().strftime('%Y-%m-%d')

    for symbol in symbols:
        try:
            # Ruta en S3 para el archivo JSON de predicción
            json_s3_key = f'forecast_results/{symbol}_forecast_results.json'
            json_data = download_file_from_s3(json_s3_key)

            if not json_data:
                # Obtener los datos históricos si no existe el archivo en S3
                indicadores = TechnicalAnalysis(symbol, year=2024)
                data = indicadores.data_year[['Close']].reset_index()
                data['Date'] = pd.to_datetime(data['Date'])
                data.rename(columns={'Date': 'date', 'Close': 'value'}, inplace=True)

                # Realizar la predicción
                response = models.perform_forecast(
                    strategy='cronos',
                    data_frame=data,
                    confidence_level=90,
                    horizon_days=15,
                    last_date=False,
                    save_plot=False
                )

                # Guardar los resultados en S3 como JSON
                json_data = json.dumps(response, indent=4)
                upload_file_to_s3(json_data.encode('utf-8'), json_s3_key)
                logging.info(f"Predicción guardada en S3 para '{symbol}'")

            else:
                # Si el archivo ya existe en S3, cargarlo
                response = json.loads(json_data)
                logging.info(f"Predicción cargada desde S3 para '{symbol}'")

            # Convertir el forecast en un DataFrame
            forecast_df = pd.DataFrame(response['forecast'])
            forecast_df['DATE_VALUE'] = pd.to_datetime(forecast_df['DATE_VALUE'])

            # Cargar el archivo histórico para el símbolo actual
            indicadores = TechnicalAnalysis(symbol, year=2024)
            data = indicadores.data_year[['Close']].reset_index()
            data['Date'] = pd.to_datetime(data['Date'])

            # Graficar los resultados históricos y las predicciones
            plt.figure(figsize=(14, 8))
            plt.plot(data['Date'].tail(30), data['Close'].tail(30), label='Precio de Cierre', color='blue', linestyle='-', linewidth=2)
            plt.plot(forecast_df['DATE_VALUE'], forecast_df['PREDICTED_VALUE'], label='Valor Predicho', color='orange', linestyle='--', linewidth=2)
            plt.fill_between(forecast_df['DATE_VALUE'], forecast_df['LOWER_BOUND'], forecast_df['UPPER_BOUND'], color='orange', alpha=0.3, label='Intervalo de Predicción')

            # Configuración de etiquetas y formato
            plt.xlabel('Fecha', fontsize=14, fontweight='bold')
            plt.ylabel('Precio (USD)', fontsize=14, fontweight='bold')
            plt.title(f"Precio de Cierre y Forecast para {symbol}", fontsize=16, fontweight='bold')
            plt.legend()

            # Formato de fechas en el eje x
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
            plt.gca().tick_params(axis='x', rotation=45)
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.tight_layout()

            # Guardar la gráfica en memoria en lugar de en disco
            img_data = BytesIO()
            plt.savefig(img_data, format='png', dpi=300, bbox_inches='tight')
            img_data.seek(0)

            # Subir la gráfica a S3
            plot_s3_key = f'forecast_plots/{symbol}_forecast_plot.png'
            upload_file_to_s3(img_data.getvalue(), plot_s3_key, content_type='image/png')
            plt.close()

            logging.info(f"Gráficos guardados en S3 para {symbol}")

        except FileNotFoundError as e:
            logging.error(f"Archivo no encontrado: {str(e)}")
        except json.JSONDecodeError as e:
            logging.error(f"Error al decodificar JSON para el símbolo {symbol}: {str(e)}")
        except pd.errors.EmptyDataError as e:
            logging.error(f"El archivo de datos para el símbolo {symbol} está vacío.")
        except Exception as e:
            logging.error(f"Error inesperado al procesar el símbolo {symbol}: {str(e)}")
