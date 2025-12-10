# utils/generador_insights.py
import numpy as np

class GeneradorInsights:
    """
    Generador automático de insights financieros basado en:
    - Totales
    - Razones Financieras
    - Análisis Horizontal y Vertical
    - Predicciones IA
    - Anomalías IA
    """

    def __init__(self, totales=None, razones=None, horizontal=None, vertical=None,
                 predicciones=None, anomalias=None):
        # Validar y convertir tipos
        self.totales = totales if isinstance(totales, dict) else {}
        self.razones = razones if isinstance(razones, dict) else {}
        self.horizontal = horizontal if isinstance(horizontal, dict) else {}
        self.vertical = vertical if isinstance(vertical, dict) else {}
        self.predicciones = predicciones if isinstance(predicciones, list) else []
        self.anomalias = anomalias if isinstance(anomalias, dict) else {}
        
        # Debug
        print(f"🔍 GeneradorInsights inicializado:")
        print(f"   - totales tipo: {type(self.totales)}")
        print(f"   - razones tipo: {type(self.razones)}")
        print(f"   - horizontal tipo: {type(self.horizontal)}")
        print(f"   - vertical tipo: {type(self.vertical)}")
        print(f"   - predicciones tipo: {type(self.predicciones)}")
        print(f"   - anomalias tipo: {type(self.anomalias)}")
    # ============================================================
    # 🔥 FUNCIÓN PRINCIPAL
    # ============================================================
    def generar_insights(self):

        # Generar lista de insights individuales
        insights_list = []
        insights_list.extend(self._insights_totales())
        insights_list.extend(self._insights_razones())
        insights_list.extend(self._insights_horizontal())
        insights_list.extend(self._insights_vertical())
        insights_list.extend(self._insights_predicciones())
        insights_list.extend(self._insights_anomalias())

        # Limpiar vacíos
        insights_list = [i for i in insights_list if i]

        # ============================
        # 📌 RESUMEN AUTOMÁTICO
        # ============================
        resumen = self._generar_resumen(insights_list)

        # ============================
        # 📌 RECOMENDACIONES AUTOMÁTICAS
        # ============================
        recomendaciones = self._generar_recomendaciones(insights_list)

        # ============================
        # 📌 ESTRUCTURA FINAL (IMPORTANTE)
        # ============================
        return {
            "resumen": resumen,
            "insights": insights_list,
            "recomendaciones": recomendaciones
        }

    # ============================================================
    # 🧠 RESUMEN AUTOMÁTICO
    # ============================================================
    def _generar_resumen(self, insights):
        if not insights:
            return "No se detectaron hallazgos significativos en los datos analizados."

        # Tomamos solo los títulos más relevantes
        titulos = [i["titulo"] for i in insights[:4]]

        return "Se identificaron los siguientes puntos clave: " + "; ".join(titulos) + "."

    # ============================================================
    # 🛠️ RECOMENDACIONES AUTOMÁTICAS
    # ============================================================
    def _generar_recomendaciones(self, insights):
        recomendaciones = []

        for i in insights:
            titulo = i["titulo"].lower()

            if "costos" in titulo:
                recomendaciones.append("Optimizar los costos operativos y revisar gastos innecesarios.")
            if "ingresos" in titulo or "ventas" in titulo:
                recomendaciones.append("Evaluar estrategias para aumentar ingresos y mejorar flujo de caja.")
            if "riesgo" in titulo or "anomalías" in titulo:
                recomendaciones.append("Revisar movimientos irregulares y validar integridad de los datos.")
            if "liquidez" in titulo:
                recomendaciones.append("Ajustar pasivos a corto plazo o aumentar activos líquidos.")

        # Quitar duplicados
        return list(dict.fromkeys(recomendaciones))

    # ============================================================
    # 1️⃣ INSIGHTS SOBRE TOTALES
    # ============================================================
    def _insights_totales(self):
        data = []

        ingresos = self.totales.get("total_ingresos_actual", 0)
        costos = self.totales.get("total_costos_actual", 0)
        utilidad = ingresos - costos

        if ingresos == 0:
            data.append(self._msg("Ingresos nulos",
                "No se registraron ingresos. Revisa estructura del archivo o fuentes de datos."))
            return data

        margen = (utilidad / ingresos) * 100 if ingresos else 0

        if margen < 10:
            data.append(self._msg(
                "Margen de utilidad muy bajo",
                f"El margen actual es de solo {margen:.2f}%. Esto indica riesgo financiero."
            ))
        elif margen > 30:
            data.append(self._msg(
                "Margen sólido",
                f"El margen actual es saludable: {margen:.2f}%."
            ))

        if costos > ingresos:
            data.append(self._msg(
                "Costos exceden ingresos",
                "Los costos superan los ingresos, generando pérdidas operativas."
            ))

        return data

    # ============================================================
    # 2️⃣ INSIGHTS SOBRE RAZONES FINANCIERAS
    # ============================================================
    def _insights_razones(self):
        data = []
        r = self.razones

        liquidez = r.get("liquidez_corriente")
        deuda = r.get("razon_deuda")
        rentabilidad = r.get("margen_neto")

        if liquidez is not None:
            if liquidez < 1:
                data.append(self._msg(
                    "Liquidez insuficiente",
                    f"La liquidez corriente es {liquidez:.2f}."
                ))

        if deuda is not None and deuda > 0.7:
            data.append(self._msg(
                "Nivel de endeudamiento riesgoso",
                f"La razón de deuda es {deuda:.2f}."
            ))

        if rentabilidad is not None and rentabilidad < 5:
            data.append(self._msg(
                "Rentabilidad muy baja",
                f"Rentabilidad neta de {rentabilidad:.2f}%."
            ))

        return data

    # ============================================================
    # 3️⃣ INSIGHTS HORIZONTAL
    # ============================================================
    def _insights_horizontal(self):
        data = []
        inc_ing = self.horizontal.get("incremento_ingresos")
        inc_cost = self.horizontal.get("incremento_costos")

        if inc_ing is not None and inc_ing < 0:
            data.append(self._msg("Caída en ingresos",
                                  f"Ingresos disminuyeron {inc_ing:.2f}%."))
        return data

    # ============================================================
    # 4️⃣ INSIGHTS VERTICAL
    # ============================================================
    def _insights_vertical(self):
        data = []
        gastos = self.vertical.get("gastos_sobre_ingresos")

        if gastos and gastos > 70:
            data.append(self._msg(
                "Gastos demasiado altos",
                f"Gastos equivalen al {gastos:.2f}% de los ingresos."
            ))

        return data

    # ============================================================
    # 5️⃣ INSIGHTS PREDICCIONES IA
    # ============================================================
    def _insights_predicciones(self):
        data = []
        for p in self.predicciones:
            riesgo = p.get("riesgo")
            prob = p.get("prob_anomalia")
            anio = p.get("anios_offset")

            if riesgo == "alto":
                data.append(self._msg(
                    f"Riesgo futuro alto (+{anio})",
                    f"Probabilidad de anomalía: {prob:.2%}"
                ))
        return data

    # ============================================================
    # 6️⃣ INSIGHTS ANOMALÍAS IA
    # ============================================================
    def _insights_anomalias(self):
        data = []

        estado = self.anomalias.get("estado_ia")
        score = self.anomalias.get("score_ia")

        if estado == "anómalo":
            data.append(self._msg(
                "Se detectaron anomalías financieras",
                f"Score anómalo: {score}"
            ))

        return data

    # ============================================================
    # 📌 UTILIDAD
    # ============================================================
    def _msg(self, titulo, descripcion):
        return {"titulo": titulo, "descripcion": descripcion}
