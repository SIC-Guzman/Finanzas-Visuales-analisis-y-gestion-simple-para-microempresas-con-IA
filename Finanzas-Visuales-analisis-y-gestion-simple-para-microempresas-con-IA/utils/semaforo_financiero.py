class SemaforoFinanciero:
    def __init__(self, razones: dict, resultados_ia: dict, anomalias: dict):
        self.razones = razones or {}
        self.resultados_ia = resultados_ia or {}
        self.anomalias = anomalias or {}

    # ------------------------------
    # UTILIDAD BASE
    # ------------------------------
    def _estado_por_score(self, score: float):
        if score >= 70:
            return "VERDE"
        elif score >= 40:
            return "AMARILLO"
        else:
            return "ROJO"

    # ------------------------------
    # INDICADORES
    # ------------------------------
    def evaluar_liquidez(self):
        liquidez = self.razones.get("liquidez_corriente", 0)
        score = min(max(liquidez * 50, 0), 100)
        return score, self._estado_por_score(score)

    def evaluar_rentabilidad(self):
        margen = self.razones.get("margen_neto", 0)
        score = min(max(margen * 100, 0), 100)
        return score, self._estado_por_score(score)

    def evaluar_endeudamiento(self):
        deuda = self.razones.get("endeudamiento", 1)
        score = max(0, 100 - deuda * 100)
        return score, self._estado_por_score(score)

    def evaluar_riesgo_ia(self):
        riesgo = "BAJO"
        if self.anomalias:
            pred = self.anomalias.get("predicciones", [])
            if pred:
                riesgo = pred[0].get("riesgo", "BAJO")

        score = {"BAJO": 80, "MEDIO": 55, "ALTO": 25}.get(riesgo, 50)
        return score, self._estado_por_score(score)


    def generar_semaforo(self):
        liq_score, liq_estado = self.evaluar_liquidez()
        rent_score, rent_estado = self.evaluar_rentabilidad()
        end_score, end_estado = self.evaluar_endeudamiento()
        riesgo_score, riesgo_estado = self.evaluar_riesgo_ia()

        scores = [liq_score, rent_score, end_score, riesgo_score]
        promedio = sum(scores) / len(scores)

        estado_general = self._estado_por_score(promedio)

        mensaje = {
            "VERDE": "El negocio está sano y estable",
            "AMARILLO": "El negocio es viable, pero requiere atención",
            "ROJO": "El negocio está en riesgo financiero"
        }[estado_general]

        return {
            "estado_general": estado_general,
            "mensaje": mensaje,
            "areas": {
                "liquidez": {"estado": liq_estado, "score": round(liq_score, 1)},
                "rentabilidad": {"estado": rent_estado, "score": round(rent_score, 1)},
                "endeudamiento": {"estado": end_estado, "score": round(end_score, 1)},
                "riesgo_ia": {"estado": riesgo_estado, "score": round(riesgo_score, 1)}
            }
        }