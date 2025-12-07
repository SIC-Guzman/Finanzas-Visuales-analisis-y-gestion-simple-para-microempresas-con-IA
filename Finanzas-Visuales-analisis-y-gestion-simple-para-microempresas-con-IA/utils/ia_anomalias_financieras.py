# modelo_anomalias.py
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression

class ModeloAnomaliasFinancieras:
    """
    Entrena IsolationForest sobre un vector de features construidos desde
    los totales calculados por _calcular_totales(). También genera predicciones
    futuras básicas (regresión lineal) y evalúa riesgo/anomalía sobre ellas.
    """

    def __init__(self, totales_dict, contamination=0.15):
        """
        totales_dict: dict retornado por analizador._calcular_totales()
        """
        self.totales = totales_dict
        self.contamination = contamination
        self.isof = None
        self.feature_df = None
        self._prepare_features()

    def _prepare_features(self):
        """Convierte totales en DataFrame + calcula ratios/crecimientos"""
        t = self.totales

        # Aseguramos valores numéricos (evitar ZeroDivision)
        def safe(x): 
            try: return float(x)
            except Exception: return np.nan

        data = {
            'total_ingresos_anterior': safe(t.get('total_ingresos_anterior')),
            'total_ingresos_actual' : safe(t.get('total_ingresos_actual')),
            'utilidad_neta_anterior' : safe(t.get('utilidad_neta_anterior')),
            'utilidad_neta_actual'  : safe(t.get('utilidad_neta_actual')),
            'total_activos_anterior' : safe(t.get('total_activos_anterior')),
            'total_activos_actual'  : safe(t.get('total_activos_actual')),
            'total_pasivos_anterior': safe(t.get('total_pasivos_anterior')),
            'total_pasivos_actual'  : safe(t.get('total_pasivos_actual')),
            'total_patrimonio_anterior': safe(t.get('total_patrimonio_anterior')),
            'total_patrimonio_actual'  : safe(t.get('total_patrimonio_actual')),
            'activo_corriente_anterior': safe(t.get('activo_corriente_anterior')),
            'activo_corriente_actual'  : safe(t.get('activo_corriente_actual')),
        }

        df = pd.DataFrame([data])

        # Ratios y crecimientos (usar eps para evitar div/0)
        eps = 1e-9
        df['crecimiento_ingresos'] = (df['total_ingresos_actual'] - df['total_ingresos_anterior']) / (df['total_ingresos_anterior'] + eps)
        df['crecimiento_utilidad'] = (df['utilidad_neta_actual'] - df['utilidad_neta_anterior']) / (df['utilidad_neta_anterior'] + eps)
        df['margen_neto_actual'] = df['utilidad_neta_actual'] / (df['total_ingresos_actual'] + eps)
        df['margen_neto_anterior'] = df['utilidad_neta_anterior'] / (df['total_ingresos_anterior'] + eps)
        df['apalancamiento_actual'] = df['total_pasivos_actual'] / (df['total_patrimonio_actual'] + eps)
        df['liquidez_actual'] = df['activo_corriente_actual'] / (df['total_pasivos_actual'] + eps)

        # Keep numeric columns only
        self.feature_df = df.replace([np.inf, -np.inf], np.nan).fillna(0)

    # -------------------------
    # Entrenar / detectar
    # -------------------------
    def entrenar_y_detectar(self):
        """
        Entrena IsolationForest con la fila actual (sí: isolation necesita más datos,
        pero en tu flujo anual usualmente solo hay una fila por empresa por análisis).
        Esto devuelve una puntuación y un estado.
        Nota: con 1 fila el modelo no es robusto; usamos el decision_function como score heurístico.
        """
        if self.feature_df is None:
            self._prepare_features()

        # Si hubiera más observaciones (por ejemplo, guardadas históricamente por empresa),
        # sería mejor entrenar sobre un conjunto mayor. Aquí entrenamos sobre la fila misma
        # con parámetros que marcan anomalía si la puntuación es baja.
        # Para estabilidad, ponemos n_estimators pequeño si hay muy pocos datos.
        n_est = 100
        self.isof = IsolationForest(n_estimators=n_est, contamination=self.contamination, random_state=42)
        try:
            self.isof.fit(self.feature_df)
            pred = self.isof.predict(self.feature_df)[0]   # 1 normal, -1 anomalía
            score = float(self.isof.decision_function(self.feature_df)[0])  # mayor = más "normal"
            estado = "ANÓMALO" if pred == -1 else "NORMAL"
        except Exception as e:
            # Fallback: si falla el fit (poco dato), devolvemos heurística basada en cambios
            score = float(self.feature_df['crecimiento_ingresos'].iloc[0])
            estado = "PENDIENTE_VALIDACION"

        return {
            "estado_actual": estado,
            "score_actual": score,
            "features": self.feature_df.to_dict(orient='records')[0]
        }

    # -------------------------
    # Predicción básica (regresión) y evaluación de riesgo
    # -------------------------
    def predecir_futuro_y_evaluar(self, años=3):
        """
        Predice total_ingresos, utilidad_neta y total_activos a partir de los dos puntos (anterior, actual)
        usando regresión lineal (como en tu ModeloIAVentasCostos) y luego evalúa riesgo/
        probabilidad de anomalía aplicando el IsolationForest (si entrenado).
        Retorna lista de dicts por año futuro: {'anio_offset':1, 'predicciones':{...}, 'prob_anomalia':0.12}
        """
        # preparar pares
        resultados = []
        pares = {
            "total_ingresos": [self.totales.get('total_ingresos_anterior'), self.totales.get('total_ingresos_actual')],
            "utilidad_neta": [self.totales.get('utilidad_neta_anterior'), self.totales.get('utilidad_neta_actual')],
            "total_activos": [self.totales.get('total_activos_anterior'), self.totales.get('total_activos_actual')]
        }

        # fit simple por campo
        for year_offset in range(1, años + 1):
            pred_dict = {}
            for campo, valores in pares.items():
                # si hay datos numéricos válidos
                try:
                    y = np.array([float(valores[0]), float(valores[1])])
                    X = np.array([[0], [1]])
                    lr = LinearRegression().fit(X, y)
                    pred = lr.predict(np.array([[1 + year_offset]])).tolist()[0]
                except Exception:
                    pred = None
                pred_dict[campo] = pred

            # crear fila con predicción y calcular features (ratios) como si fueran reales
            eps = 1e-9
            total_ing_pred = pred_dict['total_ingresos'] or 0.0
            util_pred = pred_dict['utilidad_neta'] or 0.0
            activos_pred = pred_dict['total_activos'] or 0.0
            # construir feature vector estilo self.feature_df
            feat = {
                'total_ingresos_anterior': float(self.totales.get('total_ingresos_actual') or 0.0),  # shift
                'total_ingresos_actual': float(total_ing_pred),
                'utilidad_neta_anterior': float(self.totales.get('utilidad_neta_actual') or 0.0),
                'utilidad_neta_actual': float(util_pred),
                'total_activos_anterior': float(self.totales.get('total_activos_actual') or 0.0),
                'total_activos_actual': float(activos_pred),
                'total_pasivos_anterior': float(self.totales.get('total_pasivos_actual') or 0.0),
                'total_pasivos_actual': float(self.totales.get('total_pasivos_actual') or 0.0),  # no predictamos pasivos
                'total_patrimonio_anterior': float(self.totales.get('total_patrimonio_actual') or 0.0),
                'total_patrimonio_actual': float(self.totales.get('total_patrimonio_actual') or 0.0),
                'activo_corriente_anterior': float(self.totales.get('activo_corriente_actual') or 0.0),
                'activo_corriente_actual': float(self.totales.get('activo_corriente_actual') or 0.0),
            }

            # calcular ratios
            crec_ing = (feat['total_ingresos_actual'] - feat['total_ingresos_anterior']) / (feat['total_ingresos_anterior'] + eps)
            margen = (feat['utilidad_neta_actual'] / (feat['total_ingresos_actual'] + eps)) if feat['total_ingresos_actual'] != 0 else 0.0
            apal = (feat['total_pasivos_actual'] / (feat['total_patrimonio_actual'] + eps)) if feat['total_patrimonio_actual'] != 0 else 0.0
            liquidez = (feat['activo_corriente_actual'] / (feat['total_pasivos_actual'] + eps)) if feat['total_pasivos_actual'] != 0 else 0.0

            feat_vec = pd.DataFrame([{
                'crecimiento_ingresos': crec_ing,
                'crecimiento_utilidad': 0.0,  # no calculado finamente aquí
                'margen_neto_actual': margen,
                'apalancamiento_actual': apal,
                'liquidez_actual': liquidez
            }]).fillna(0)

            # evaluar con IsolationForest si existe
            prob_anom = 0.0
            riesgo = "Bajo"
            if self.isof is not None:
                # decision_function: valores más bajos => más anomalía. Normalizamos a [0,1] heurístico
                df_score = float(self.isof.decision_function(feat_vec)[0])
                # Convertimos score a prob_anomalia (menor score => mayor prob)
                prob_anom = max(0.0, min(1.0, ( -df_score ) / (1.0 + abs(df_score))))
                if prob_anom > 0.7:
                    riesgo = "Alto"
                elif prob_anom > 0.3:
                    riesgo = "Medio"

            resultados.append({
                'anio_offset': year_offset,
                'predicciones': pred_dict,
                'prob_anomalia': round(float(prob_anom), 4),
                'riesgo': riesgo,
                'feature_vector': feat  # para debug/auditoría
            })

        return resultados
