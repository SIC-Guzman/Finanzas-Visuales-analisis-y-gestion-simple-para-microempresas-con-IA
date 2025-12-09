# Deteccion y Prediccion de Anomalias Financieras
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression

class ModeloAnomaliasFinancieras:
    """
    Modelo hibrido: combina reglas financieras + IsolationForest.
    """

    def __init__(self, totales_dict, contamination=0.15):
        self.totales = totales_dict
        self.contamination = contamination
        self.isof = None
        self.feature_df = None
        self._prepare_features()

    # ===============================================================
    #   GENERACION DE FEATURES NUMÉRICOS
    # ===============================================================
    def _prepare_features(self):
        """Convierte totales en DataFrame + ratios."""
        t = self.totales

        def safe(x):
            try: return float(x)
            except: return 0.0

        df = pd.DataFrame([{
            'ingresos_ant': safe(t.get('total_ingresos_anterior')),
            'ingresos_act': safe(t.get('total_ingresos_actual')),
            'utilidad_ant': safe(t.get('utilidad_neta_anterior')),
            'utilidad_act': safe(t.get('utilidad_neta_actual')),
            'activos_ant': safe(t.get('total_activos_anterior')),
            'activos_act': safe(t.get('total_activos_actual')),
            'pasivos_act': safe(t.get('total_pasivos_actual')),
            'patrimonio_act': safe(t.get('total_patrimonio_actual')),
            'activo_corriente': safe(t.get('activo_corriente_actual')),
        }])

        eps = 1e-9
        df["crec_ing"] = (df.ingresos_act - df.ingresos_ant) / (df.ingresos_ant + eps)
        df["crec_util"] = (df.utilidad_act - df.utilidad_ant) / (df.utilidad_ant + eps)
        df["margen_neto"] = df.utilidad_act / (df.ingresos_act + eps)
        df["apalancamiento"] = df.pasivos_act / (df.patrimonio_act + eps)
        df["liquidez"] = df.activo_corriente / (df.pasivos_act + eps)

        self.feature_df = df.fillna(0).replace([np.inf, -np.inf], 0)

    # ===============================================================
    #   MOTOR DE REGLAS FINANCIERAS
    # ===============================================================
    def evaluar_reglas_financieras(self):
        """
        Evalua indicadores clave y genera alertas explicables.
        """
        df = self.feature_df.iloc[0]
        alertas = []
        riesgo_total = 0  # 0 bajo, 1 medio, 2 alto

        # --- 1. Ingresos negativos ---
        if df.ingresos_act < 0:
            alertas.append("Ingresos actuales negativos: comportamiento no razonable.")
            riesgo_total += 2

        # --- 2. Utilidad negativa mas del -30% de ingresos ---
        if df.utilidad_act < -0.3 * df.ingresos_act:
            alertas.append("Perdidas severas: utilidad < -30% de los ingresos.")
            riesgo_total += 2

        # --- 3. Apalancamiento muy alto ---
        if df.apalancamiento > 3:
            alertas.append("Apalancamiento alto (>3): muchos pasivos frente a patrimonio.")
            riesgo_total += 2

        # --- 4. Liquidez muy baja ---
        if df.liquidez < 0.7:
            alertas.append("Liquidez limitada (<0.7): podría haber riesgo de pago.")
            riesgo_total += 1

        # --- 5. Caida fuerte de ingresos (>30%) ---
        if df.crec_ing < -0.3:
            alertas.append("Caída importante de ingresos (>30%).")
            riesgo_total += 1

        # --- 6. Margen neto muy bajo ---
        if df.margen_neto < 0.02:  # <2%
            alertas.append("Margen neto bajo (<2%): rentabilidad limitada.")
            riesgo_total += 1

        # Definición del riesgo semántico
        if riesgo_total >= 3:
            nivel = "ALTO"
        elif riesgo_total == 2:
            nivel = "MEDIO"
        else:
            nivel = "BAJO"

        return {
            "nivel_riesgo_reglas": nivel,
            "alertas": alertas
        }

    # ===============================================================
    #   IA: ISOLATION FOREST
    # ===============================================================
    def entrenar_y_detectar(self):
        """
        Entrena IsolationForest y combina con reglas financieras.
        """
        # Entrenamos el IsolationForest con la unica fila disponible
        
        self.isof = IsolationForest(
            contamination=self.contamination,
            n_estimators=100,
            random_state=42
        ).fit(self.feature_df)

        pred = self.isof.predict(self.feature_df)[0]       # 1 normal, -1 anomalía
        score = float(self.isof.decision_function(self.feature_df)[0])

        estado_ia = "ANÓMALO" if pred == -1 else "NORMAL"

        # Reglas financieras
        reglas = self.evaluar_reglas_financieras()

        # Fusión de resultados
        if reglas["nivel_riesgo_reglas"] == "ALTO" or estado_ia == "ANÓMALO":
            estado_final = "RIESGO ALTO"
        elif reglas["nivel_riesgo_reglas"] == "MEDIO":
            estado_final = "RIESGO MEDIO"
        else:
            estado_final = "RIESGO BAJO"

        return {
            "estado_final": estado_final,
            "estado_ia": estado_ia,
            "score_ia": score,
            "reglas": reglas,
            "features": self.feature_df.to_dict(orient="records")[0]
        }

    # ===============================================================
    #   PREDICCION FUTURA 
    # ===============================================================
    def predecir_futuro_y_evaluar(self, anios=3):
        """
        Se utiliza IA pura para proyectar ingresos, utilidad y activos.
        """
        resultados = []
        pares = {
            "total_ingresos": [
                self.totales.get('total_ingresos_anterior'),
                self.totales.get('total_ingresos_actual')
            ],
            "utilidad_neta": [
                self.totales.get('utilidad_neta_anterior'),
                self.totales.get('utilidad_neta_actual')
            ],
            "total_activos": [
                self.totales.get('total_activos_anterior'),
                self.totales.get('total_activos_actual')
            ]
        }

        for year_offset in range(1, anios + 1):
            pred_dict = {}
            for campo, valores in pares.items():
                try:
                    y = np.array([float(valores[0]), float(valores[1])])
                    X = np.array([[0], [1]])
                    lr = LinearRegression().fit(X, y)
                    pred = float(lr.predict([[1 + year_offset]])[0])
                except:
                    pred = None

                pred_dict[campo] = pred

            # Evaluar IA 
            prob_anom = 0.0
            riesgo = "Bajo"
            if self.isof is not None:
                feat_vec = pd.DataFrame([self.feature_df.mean()])  # dummy future
                score = float(self.isof.decision_function(feat_vec)[0])

                prob_anom = max(0.0, min(1.0, (-score) / (1 + abs(score))))
                if prob_anom > 0.7:
                    riesgo = "Alto"
                elif prob_anom > 0.3:
                    riesgo = "Medio"

            resultados.append({
                "anios_offset": year_offset,
                "predicciones": pred_dict,
                "prob_anomalia": round(prob_anom, 3),
                "riesgo": riesgo
            })

        return resultados
