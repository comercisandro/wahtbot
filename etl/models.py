from typing import Any

import pandas as pd
from timeserieslib.forecast import Chronos
from timeserieslib.core import TimeSeries


class Models:
    def __init__(self):
        pass

    # Función de redondeo dentro de la clase Models
    def round_forecast(self, data_frame_forecast, decimal_places, date_column, forecast_column, lower_bound_column, upper_bound_column):
        formatted_forecast = []
        for entry in data_frame_forecast[[date_column, forecast_column, lower_bound_column, upper_bound_column]].to_dict(orient="records"):
            formatted_entry = {
                "DATE_VALUE": entry[date_column].strftime('%Y-%m-%d'),
                "PREDICTED_VALUE": round(entry[forecast_column], decimal_places),
                "LOWER_BOUND": round(entry[lower_bound_column], decimal_places),
                "UPPER_BOUND": round(entry[upper_bound_column], decimal_places)
            }
            formatted_forecast.append(formatted_entry)
        return formatted_forecast

    def perform_forecast(self, strategy='cronos', data_frame=None, confidence_level=90,
                         horizon_days=7, last_date=None,
                         save_plot=False):
        forecast_strategy = self._get_forecast_strategy(strategy)
        if forecast_strategy is None:
            raise ValueError("Estrategia no válida")

        return forecast_strategy.perform_forecast(data_frame, confidence_level, horizon_days, last_date, save_plot)

    def _get_forecast_strategy(self, strategy):
        if strategy == 'cronos':
            return CronosForecast(self)
        else:
            print(f"Estrategia no reconocida: {strategy}")
        return None


class CronosForecast:
    def __init__(self, model_helper, model_name='small', device='cpu'):
        self.model_helper = model_helper
        self.model = Chronos(model=model_name, device=device)

    def perform_forecast(self, data_frame, confidence_level=90,
                         horizon_days=7, last_date=False,
                         save_plot=False) -> dict[str, list[dict[str, Any]]]:
        ds = pd.to_datetime(data_frame["date"])
        y = data_frame['value'].tolist()

        # Determinar el número de decimales en la serie de entrada
        decimal_places = max(data_frame['value'].apply(lambda x: len(str(x).split('.')[1]) if '.' in str(x) else 0))

        ts = TimeSeries(ds=ds, y=y, series_id='test_id', frequency='D')

        forecast_ts = self.model.predict(
            ts,
            points=horizon_days,
            pi_level=confidence_level,
            max_min_scaler=True,
            num_samples=50,
            temperature=0.8,
            top_k=20,
            top_p=0.95
        )

        data_frame_forecast = forecast_ts.to_dataframe()

        # Formatear los resultados usando la función round_forecast del modelo helper (Models)
        formatted_forecast = self.model_helper.round_forecast(data_frame_forecast, decimal_places, 'ds', 'forecast', 'lower_bound', 'upper_bound')

        # Crear una respuesta JSON con los resultados formateados
        response = {"forecast": formatted_forecast}

        return response