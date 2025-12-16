from utils.ia_anomalias_financieras import ModeloAnomaliasFinancieras
from utils.analizador_financiero1 import AnalizadorFinanciero
import pandas as pd

try:
    # Inicializar analizador
    analizador = AnalizadorFinanciero("C:/Users/jgcal/OneDrive/Documentos/PythonProjects/Proyecto_IA/Finanzas-Visuales-analisis-y-gestion-simple-para-microempresas-con-IA/Plantillas/Plantilla_Financiera_Avanzada.xlsx")

    # Calcular totales
    totales = analizador._calcular_totales()

    # Validación mínima
    if totales.get("total_ingresos_actual") is None:
        raise Exception("Faltan datos para análisis de anomalías.")

    # ✅ CONSTRUCTOR CORRECTO (SIN keyword 'totales')
    model_anom = ModeloAnomaliasFinancieras(
        totales,          
        contamination=0.12
    )

    # Entrenar y detectar
    det = model_anom.entrenar_y_detectar()

    # ✅ NOMBRE CORRECTO DEL PARÁMETRO
    pred = model_anom.predecir_futuro_y_evaluar(anios=3)

    
    #costos_actuales = totales.get("total_costos_actual", 0)

    print("\n================= ANÁLISIS DE ANOMALÍAS =================\n")

    # ===== RESULTADO ACTUAL =====
    print(">>> ESTADO FINANCIERO ACTUAL\n")
    print(f"Estado Final: {det.get('estado_final')}")
    print(f"Estado IA: {det.get('estado_ia')}")
    print(f"Score IA: {det.get('score_ia')}")
    print(f"Nivel reglas: {det.get('reglas', {}).get('nivel_riesgo_reglas')}")
    print("\nAlertas:")
    for a in det.get("reglas", {}).get("alertas", []):
        print(" -", a)

    print("\nFeatures usadas por la IA:")
    for k, v in det.get("features", {}).items():
        print(f"  {k}: {v}")

    # ===== PREDICCIONES =====
    print("\n\n>>> PREDICCIONES FUTURAS\n")

    for p in pred:
        print(f"AÑO +{p['anios_offset']}")
        print("Predicciones:")
        for k, v in p["predicciones"].items():
            print(f"  {k}: {v}")
        print(f"Probabilidad de anomalía: {p['prob_anomalia']}")
        print(f"Riesgo: {p['riesgo']}")
        print("-" * 50)

except Exception as e:
    print("\n❌ ERROR EN ANOMALÍAS FINANCIERAS:")
    print(str(e))
