import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

class ModeloIAVentasCostos:
    """
    Clase para predecir Ventas y Costos 3 años hacia adelante.
    - Si recibe solo 2 puntos, usa regresión lineal (proyección ANUAL).
    - Si recibe >=3 puntos, usa RandomForest (mejor para más historial).
    Acepta:
      - ventas (list-like) y costos (list-like) OR
      - df_unificado (pandas.DataFrame) del que intentará extraer columnas.
    """

    def __init__(self, ventas=None, costos=None, df_unificado=None):
        # Priorizar listas explícitas (más claro desde el endpoint)
        if ventas is not None and costos is not None:
            self.ventas = list(map(float, ventas))
            self.costos = list(map(float, costos))
        elif df_unificado is not None:
            self.ventas, self.costos = self._extraer_de_df(df_unificado)
        else:
            raise ValueError("Debe proporcionar 'ventas' y 'costos' o un 'df_unificado'.")

        if len(self.ventas) < 2 or len(self.costos) < 2:
            raise ValueError("Se requieren al menos 2 valores históricos (AÑO_ANTERIOR y AÑO_ACTUAL).")

    # --------------------
    # Extracción desde DataFrame (si se pasa df_unificado)
    # --------------------
    def _extraer_de_df(self, df):
        posibles_ventas = ["Ventas totales", "ventas", "ingresos", "total ventas", "ingresos totales"]
        posibles_costos = ["Costo de ventas", "costos", "costo ventas", "costo", "gastos"]

        def encontrar_col(df, lista):
            for col in df.columns:
                if any(col.strip().lower() == p.lower() for p in lista):
                    return col
            # fallback: contains
            for col in df.columns:
                if any(p.lower() in str(col).strip().lower() for p in lista):
                    return col
            return None

        col_v = encontrar_col(df, posibles_ventas)
        col_c = encontrar_col(df, posibles_costos)

        if col_v is None or col_c is None:
            raise ValueError("No se pudieron detectar columnas de ventas/costos en el DataFrame.")

        ventas = list(pd.to_numeric(df[col_v], errors='coerce').dropna().astype(float).tolist())
        costos = list(pd.to_numeric(df[col_c], errors='coerce').dropna().astype(float).tolist())

        return ventas, costos

    # --------------------
    # Proyección por regresión lineal (para 2 puntos)
    # --------------------
    def _proyectar_lineal(self, series, años_futuros=3):
        """
        series: lista de valores (longitud >= 2)
        Devuelve lista de preds para los próximos `años_futuros` (anuales).
        """
        # X: 0..n-1
        X = np.arange(len(series)).reshape(-1, 1)
        y = np.array(series).reshape(-1, 1)

        model = LinearRegression()
        model.fit(X, y)

        futuros = np.arange(len(series), len(series) + años_futuros).reshape(-1, 1)
        preds = model.predict(futuros).reshape(-1)
        return [float(p) for p in preds]

    # --------------------
    # Proyección con RandomForest (cuando hay suficiente historial)
    # --------------------
    def _proyectar_rf(self, series, años_futuros=3):
        X = np.arange(len(series)).reshape(-1, 1)
        y = np.array(series)

        model = RandomForestRegressor(n_estimators=200, random_state=42)
        model.fit(X, y)

        futuros = np.arange(len(series), len(series) + años_futuros).reshape(-1, 1)
        preds = model.predict(futuros)
        return [float(p) for p in preds]

    # --------------------
    # Public: predecir próximos N años (por defecto 3)
    # --------------------
    def predecir_proximos_anios(self, anios=3):
        """
        Retorna dict con:
          - 'metodo' : 'regresión lineal' o 'random_forest'
          - 'predicciones': {'ventas': [...], 'costos': [...]}
        Notas: Las predicciones son ANUALES (no mensuales).
        """
        resultado = {'metodo': None, 'predicciones': {}}

        # Decidir método según cantidad de puntos
        if len(self.ventas) <= 2 or len(self.costos) <= 2:
            # fallback lineal — este es el caso de tu plantilla: 2 años
            resultado['metodo'] = 'lineal'
            ventas_pred = self._proyectar_lineal(self.ventas, anios)
            costos_pred = self._proyectar_lineal(self.costos, anios)
        else:
            # hay más historial: usar RandomForest
            resultado['metodo'] = 'random_forest'
            ventas_pred = self._proyectar_rf(self.ventas, anios)
            costos_pred = self._proyectar_rf(self.costos, anios)

        resultado['predicciones']['ventas'] = ventas_pred
        resultado['predicciones']['costos'] = costos_pred

        # Añadir resumen simple (crecimiento anual promedio estimado)
        try:
            crecimiento_anual_promedio = ((ventas_pred[-1] / self.ventas[-1]) ** (1.0 / anios) - 1) * 100
        except Exception:
            crecimiento_anual_promedio = None

        resultado['resumen'] = {
            'crecimiento_anual_promedio_%': round(float(crecimiento_anual_promedio), 2) if crecimiento_anual_promedio is not None else None,
            'ultimo_valor_ventas': float(self.ventas[-1]),
            'ultimo_valor_costos': float(self.costos[-1])
        }

        return resultado
    def simular_crisis_financiera(self, porcentaje_caida=0.20, anios=3):
        """
        Simula una crisis financiera aplicando una caída porcentual en las ventas
        proyectadas por el modelo de Machine Learning.

        Parámetros:
            porcentaje_caida (float): Por defecto 0.20 (20% de caída en ventas)
            anios (int): Número de años a simular

        Retorna:
            dict con:
                - metodo_ml
                - escenario_base
                - escenario_crisis
                - evaluacion_supervivencia
        """

        # 1. Predicción base usando ML
        proyeccion_base = self.predecir_proximos_anios(anios)

        ventas_base = proyeccion_base["predicciones"]["ventas"]
        costos_base = proyeccion_base["predicciones"]["costos"]

        # 2. Aplicar shock de crisis: caída del X% en ventas
        ventas_crisis = [v * (1 - porcentaje_caida) for v in ventas_base]
        costos_crisis = costos_base[:]  # asumimos costos constantes (escenario conservador)

        # 3. Calcular utilidades en ambos escenarios
        utilidades_base = [v - c for v, c in zip(ventas_base, costos_base)]
        utilidades_crisis = [v - c for v, c in zip(ventas_crisis, costos_crisis)]

        # 4. Métricas financieras relevantes
        margen_promedio_crisis = np.mean([
            (u / v) if v > 0 else -1
            for u, v in zip(utilidades_crisis, ventas_crisis)
        ])

        # 5. Criterio de supervivencia (clasificación)
        # Regla académica:
        # - Si TODOS los años tienen pérdidas → NO sobrevive
        # - Si al menos un año tiene utilidad positiva → sobrevive
        sobrevive = any(u > 0 for u in utilidades_crisis)

        # 6. Clasificación explicable (importante académicamente)
        if sobrevive:
            clasificacion = "El negocio sobrevive a la crisis"
            nivel_riesgo = "Moderado" if margen_promedio_crisis < 0.10 else "Bajo"
        else:
            clasificacion = "El negocio NO sobrevive a la crisis"
            nivel_riesgo = "Alto"

        # 7. Resultado estructurado
        return {
            "metodo_ml": proyeccion_base["metodo"],
            "parametros_crisis": {
                "caida_ventas_%": round(porcentaje_caida * 100, 2),
                "anios_simulados": anios
            },
            "escenario_base": {
                "ventas": [round(v, 2) for v in ventas_base],
                "costos": [round(c, 2) for c in costos_base],
                "utilidades": [round(u, 2) for u in utilidades_base]
            },
            "escenario_crisis": {
                "ventas": [round(v, 2) for v in ventas_crisis],
                "costos": [round(c, 2) for c in costos_crisis],
                "utilidades": [round(u, 2) for u in utilidades_crisis]
            },
            "evaluacion_supervivencia": {
                "sobrevive": sobrevive,
                "clasificacion": clasificacion,
                "nivel_riesgo": nivel_riesgo,
                "margen_promedio_crisis_%": round(margen_promedio_crisis * 100, 2)
            }
        }