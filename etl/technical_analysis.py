#V1
import yfinance as yf
import pandas as pd
import mplfinance as mpf
import numpy as np
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import talib as ta
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

pd.options.mode.chained_assignment = None


class TechnicalAnalysis:
    def __init__(self, symbol, year):
        self.symbol = symbol
        self.ticket = yf.Ticker("MSFT")
        # Obtener información general sobre la empresa
        self.info = self.ticket.info

        # Obtener la lista de accionistas principales
        self.holders = self.ticket.major_holders

        self.data = yf.download(self.symbol, interval='1d')
        self.year = year
        self.data = self.data.rename(columns={'Adj Close': 'adj_close'})
        self.data_year = self._get_year_data()


    def plot_fibonacci_retracements(self):

        if self.year:
            data = self._get_year_data()
        else:
            data = self.data.copy()

        # Calcular los niveles de Fibonacci retracements
        low = data['Low'].min()
        high = data['High'].max()
        diff = high - low
        levels = [0.236, 0.382, 0.5, 0.618, 0.786]
        retracements = []
        for level in levels:
            retracements.append(high - level * diff)

        # Crear una figura y un eje
        fig, ax = plt.subplots(figsize=(12,6)) # Added figsize to control the initial size

        # Graficar las velas
        mpf.plot(data, type='candle', ax=ax)

        # Graficar los niveles de Fibonacci retracements como líneas horizontales verdes
        for level, retracement in zip(levels, retracements):
            ax.axhline(y=retracement, color='g', linestyle='--', linewidth=2)
            ax.text(data.index[0], retracement, f'{level*100}%')

        # Configurar el título y las etiquetas de los ejes
        ax.set_title(f"Gráfico de velas y Fibonacci retracements para {self.symbol}")
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Precio')

        # Formatear las fechas en el eje x
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        # Agregar una leyenda
        ax.legend()

        # Mostrar la figura
        plt.show()



    def plot_bbands(self, plot, save_path=None):
        # Filtrar por año si se proporciona
        if self.year:
            data = self._get_year_data()
        else:
            data = self.data.copy()

        data.loc[:, 'upper'], data.loc[:, 'middle'], data.loc[:, 'lower'] = ta.BBANDS(data['adj_close'], timeperiod=20)
        self.data['upper'] = data['upper']
        self.data['middle'] = data['middle']
        self.data['lower'] = data['lower']
        if plot:
          fig, ax = plt.subplots(figsize=(12, 8))

          ax.plot(data.index, data['adj_close'], label='Precio de cierre')
          ax.plot(data.index, data['upper'], label='Banda superior')
          ax.plot(data.index, data['middle'], label='Banda media')
          ax.plot(data.index, data['lower'], label='Banda inferior')
          ax.fill_between(data.index, data['upper'], data['lower'], alpha=0.1)
          ax.legend(loc='best')
          ax.set_xlabel('Fecha')
          ax.set_ylabel('Precio')
          ax.set_title(f'Bandas de Bollinger para {self.symbol} {year if year else "Total"}')

          if save_path:
            plt.savefig(save_path)  # Guardar el gráfico
        else:
            plt.show()


    def plot_macd(self, plot, save_path=None):
      # Filtrar por año si se proporciona
      if self.year:
          data = self._get_year_data()
      else:
          data = self.data.copy()

      # Calcular MACD
      data['macd'], data['macd_signal'], data['macd_hist'] = ta.MACD(data['adj_close'], fastperiod=12, slowperiod=26, signalperiod=9)
      self.data['macd'] = data['macd']
      self.data['macd_signal'] = data['macd_signal']
      self.data['macd_hist'] = data['macd_hist']

      if plot:
          fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

          # Estilo del gráfico de retornos
          ax1.plot(data.index, data['adj_close'], color='deepskyblue', linestyle='-', linewidth=2, label='Precio de Cierre')
          ax1.set_xlabel('Fecha', fontsize=14, fontweight='bold')
          ax1.set_ylabel('Precio de Cierre', fontsize=14, fontweight='bold')
          ax1.set_title(f'Retornos de {self.symbol} {self.year if self.year else "Total"}', fontsize=16, fontweight='bold')
          ax1.grid(True, linestyle='--', alpha=0.6)
          ax1.set_facecolor('#f0f0f0')
          ax1.tick_params(axis='both', which='major', labelsize=12)
          ax1.legend(loc='upper left', fontsize=12)

          # Estilo del gráfico de MACD
          ax2.plot(data.index, data['macd'], color='blue', linestyle='-', linewidth=2, label='MACD')
          ax2.plot(data.index, data['macd_signal'], color='orange', linestyle='-', linewidth=2, label='MACD Signal')
          ax2.bar(data.index, data['macd_hist'], color=['red' if x < 0 else 'green' for x in data['macd_hist']], alpha=0.6, label='MACD Histogram')
          ax2.axhline(y=0, color='black', linestyle='--', linewidth=1.5)
          ax2.set_xlabel('Fecha', fontsize=14, fontweight='bold')
          ax2.set_ylabel('MACD', fontsize=14, fontweight='bold')
          ax2.set_title(f'Indicador MACD de {self.symbol} {self.year if self.year else "Total"}', fontsize=16, fontweight='bold')
          ax2.grid(True, linestyle='--', alpha=0.6)
          ax2.set_facecolor('#f0f0f0')
          ax2.tick_params(axis='both', which='major', labelsize=12)
          ax2.legend(loc='best', fontsize=12)

          # Mejorar el formato de las fechas
          ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
          fig.autofmt_xdate()

          # Ajustar la disposición
          plt.tight_layout()

          # Ajustar DPI para alta resolución
          if save_path:
              plt.savefig(save_path, dpi=300, bbox_inches='tight')  # Guardar el gráfico con alta resolución y ajuste de bordes
          else:
              plt.show()

    def plot_candlestick(self, save_path=None):
      # Filtrar por año si se proporciona
      if self.year:
          data = self._get_year_data()
      else:
          data = self.data.copy()

      # Configura el título del gráfico
      title = f'{self.symbol} {self.year if self.year else "Total"}'

      # Verifica si la columna 'Volume' está presente
      if 'Volume' not in data.columns:
          print("La columna 'Volume' no está presente en los datos.")
          return

      # Definir un estilo personalizado
      my_style = mpf.make_mpf_style(base_mpf_style='yahoo', rc={
          'figure.facecolor': 'white',
          'axes.facecolor': 'white',
          'axes.edgecolor': 'black',
          'axes.labelcolor': 'black',
          'xtick.color': 'black',
          'ytick.color': 'black'
      })

      # Configuración de los gráficos
      if save_path:
          # Guardar el gráfico en el archivo especificado
          mpf.plot(data, type='candle', volume=True, style=my_style, title=title, savefig=save_path, figsize=(14, 8), tight_layout=True)
      else:
          # Mostrar el gráfico
          mpf.plot(data, type='candle', volume=True, style=my_style, title=title, figsize=(14, 8), tight_layout=True)

      # Ajustar el tamaño del gráfico y su disposición
      plt.tight_layout()


    def _get_year_data(self):
        if self.year:
          return self.data.loc[str(self.year):]
        else:
            return self.data.copy()
        # return self.data[self.data.index.year == self.year]

    def plot_returns_rsi(self, plot, save_path=None):
        # Filtrar por año si se proporciona
        if self.year:
            spy_indicators = self._get_year_data()
        else:
            spy_indicators = self.data.copy()

        # Calcular RSI
        delta = spy_indicators['adj_close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        spy_indicators['rsi'] = 100 - (100 / (1 + rs))
        self.data['rsi'] = spy_indicators['rsi']

        if plot:
            fig, ax2 = plt.subplots(figsize=(14, 10), sharex=True)

            # Estilo del gráfico de RSI
            ax2.plot(spy_indicators.index, spy_indicators['rsi'], color='darkviolet', linestyle='-', linewidth=2, label='RSI')
            ax2.axhline(y=70, color='red', linestyle='--', linewidth=1.5, label='Sobrecompra (70)')
            ax2.axhline(y=30, color='green', linestyle='--', linewidth=1.5, label='Sobreventa (30)')
            ax2.set_xlabel('Fecha', fontsize=14, fontweight='bold')
            ax2.set_ylabel('RSI', fontsize=14, fontweight='bold')
            ax2.set_title(f'Índice de Fuerza Relativa (RSI) de {self.symbol}', fontsize=16, fontweight='bold')
            ax2.grid(True, linestyle='--', alpha=0.6)
            ax2.set_facecolor('white')
            ax2.tick_params(axis='both', which='major', labelsize=12)
            ax2.legend(loc='best', fontsize=12)

            # Mejorar el formato de las fechas
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            fig.autofmt_xdate()

            # Ajustar la disposición
            plt.tight_layout()

            # Ajustar DPI para alta resolución
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')  # Guardar el gráfico con alta resolución y ajuste de bordes
            else:
                plt.show()
