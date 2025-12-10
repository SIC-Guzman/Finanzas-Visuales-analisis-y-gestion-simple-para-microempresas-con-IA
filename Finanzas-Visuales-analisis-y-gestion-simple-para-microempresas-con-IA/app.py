# ==================== 1. IMPORTS Y CONFIGURACIÓN ====================
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
import os
from pathlib import Path
import pandas as pd
from werkzeug.utils import secure_filename
from utils.ia_ventas_costos import ModeloIAVentasCostos
from utils.ia_anomalias_financieras import ModeloAnomaliasFinancieras
from utils.analizador_financiero1 import AnalizadorFinanciero
from flask import send_file
from utils.pdf_generator import PDFReportGenerator 
from utils.generador_insights import GeneradorInsights
from types import SimpleNamespace

# ==================== 2. CONFIGURACIÓN DE FLASK ====================
app = Flask(__name__)
app.secret_key = 'analizador_financiero_2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

Path('static/reports').mkdir(parents=True, exist_ok=True)
# Asegurar que existe la carpeta uploads
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Extensiones permitidas
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== 3. RUTAS PRINCIPALES ====================

@app.route('/')
def home():
    """Página de inicio"""
    return render_template('home.html')

@app.route('/upload')
def upload_page():
    """Página de subida de archivos"""
    return render_template('upload.html')

@app.route('/analyze', methods=['POST'])
def analyze_file():

    """Procesa el archivo subido y redirige a validación"""
    if 'file' not in request.files:
        flash('❌ No se seleccionó ningún archivo', 'error')
        return redirect(url_for('upload_page'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('❌ No se seleccionó ningún archivo', 'error')
        return redirect(url_for('upload_page'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            analizador = AnalizadorFinanciero(filepath)
            
            if analizador.datos is None:
                flash('❌ Error al cargar el archivo. Verifica el formato.', 'error')
                return redirect(url_for('upload_page'))
            
            # Redirigir a validación de datos
            return redirect(url_for('validate_data', filename=filename))
                
        except Exception as e:
            flash(f'❌ Error procesando el archivo: {str(e)}', 'error')
            return redirect(url_for('upload_page'))
    else:
        flash('❌ Formato no permitido. Use Excel (.xlsx, .xls) o CSV (.csv)', 'error')
        return redirect(url_for('upload_page'))

@app.route('/validate/<filename>')
def validate_data(filename):
    """Valida datos y redirige a confirmación"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        analizador = AnalizadorFinanciero(filepath)
        
        if analizador.datos is None:
            flash('❌ Error al cargar el archivo. Verifica el formato.', 'error')
            return redirect(url_for('upload_page'))
        
        # Redirigir a confirmación completa de datos
        return redirect(url_for('confirm_data', filename=filename))
        
    except Exception as e:
        flash(f'Error validando datos: {str(e)}', 'error')
        return redirect(url_for('upload_page'))

@app.route('/confirm-data/<filename>')
def confirm_data(filename):
    """Muestra página de confirmación de datos cargados"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        analizador = AnalizadorFinanciero(filepath)
        
        if analizador.datos is None:
            flash('❌ Error al cargar el archivo para confirmación', 'error')
            return redirect(url_for('upload_page'))
        
        # Obtener datos limpios para visualización
        datos_visualizacion = analizador.obtener_datos_para_visualizacion()
        
        print("📊 Datos para visualización:")
        print(f"   - Empresa: {len(datos_visualizacion.get('empresa', []))} items")
        print(f"   - Estado Resultados: {len(datos_visualizacion.get('estado_resultados', []))} filas")
        print(f"   - Balance General: {len(datos_visualizacion.get('balance_general', []))} filas")
        print(f"   - Equilibrio: {len(datos_visualizacion.get('equilibrio', []))} items")
        
        # Pasar los datos limpios a la plantilla
        return render_template('confirm_data.html', 
                             filename=filename,
                             datos=analizador.datos,
                             datos_visualizacion=datos_visualizacion)
        
    except Exception as e:
        flash(f'Error en confirmación de datos: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('upload_page'))


@app.route('/process-analysis/<filename>', methods=['POST'])
def process_analysis(filename):
    """Procesa el análisis completo después de confirmar datos y agrega predicciones de IA"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        # --- Inicializar analizador financiero ---
        analizador = AnalizadorFinanciero(filepath)
        resultados = analizador.generar_reporte_completo()

        # --- Debug: mostrar lo que trae resultados ---
        print("🔎 DEBUG: Tipo de 'resultados':", type(resultados))
        try:
            print("🔎 DEBUG: Claves en resultados:", list(resultados.keys()) if isinstance(resultados, dict) else "no es dict")
        except Exception:
            print("🔎 DEBUG: no se pudo listar claves de resultados")

        # --- Asegurar que 'resultados' es un dict ---
        if not isinstance(resultados, dict):
            resultados = {}

        # --- Inicializar campos obligatorios para el template ---
        resultados.setdefault('resumen', {})      # si falta, crear vacío
        resultados.setdefault('resultados', {})   # sub-diccionario principal
        resultados.setdefault('graficos', {})     # datos para charts

        # --- Predicción IA de ventas y costos ---
        # --- Predicción IA de ventas y costos ---
        try:
            print("🔄 Intentando obtener ventas y costos para IA...")
            ventas, costos = analizador.obtener_ventas_y_costos()
            print(f"✅ Ventas obtenidas: {ventas}")
            print(f"✅ Costos obtenidos: {costos}")
            
            if ventas and costos and len(ventas) > 0 and len(costos) > 0:
                modelo_ia = ModeloIAVentasCostos(ventas=ventas, costos=costos)
                resultados_ia = modelo_ia.predecir_proximos_anios(anios=3)
                resultados['resultados_ia'] = resultados_ia
                print(f"✅ Predicciones IA generadas: {resultados_ia}")
            else:
                resultados['resultados_ia'] = {
                    'error': 'Datos insuficientes para predicciones IA',
                    'ventas_recibidas': ventas,
                    'costos_recibidos': costos
                }
                print("⚠️ Datos insuficientes para IA")
                
        except Exception as e:
            resultados['resultados_ia'] = {
                'error': f"No se pudieron generar predicciones de IA: {str(e)}",
                'detalle': 'Revisar método obtener_ventas_y_costos()'
            }
            print(f"❌ Error en IA ventas/costos: {e}")
            import traceback
            traceback.print_exc()

        # --- Anomalías financieras ---
        # --- Anomalías financieras ---
        try:
            print("🔄 Intentando detectar anomalías...")
            totales = analizador._calcular_totales()
            print(f"✅ Totales calculados: {totales}")
            
            if totales and totales.get("total_ingresos_actual") is not None:
                model_anom = ModeloAnomaliasFinancieras(totales, contamination=0.12)
                det = model_anom.entrenar_y_detectar()
                pred = model_anom.predecir_futuro_y_evaluar(anios=3)

                detalles = [{
                    "anios": "Actual",
                    "ventas": totales.get("total_ingresos_actual", 0),
                    "tipo": det.get("estado_final", "DESCONOCIDO"),
                    "estado_ia": det.get("estado_ia", "DESCONOCIDO"),
                    "score_ia": det.get("score_ia", 0)
                }]

                predicciones = []
                for p in pred:
                    predicciones.append({
                        "anios": f"Año +{p.get('anios_offset', 0)}",
                        "predicciones": p.get("predicciones", {}),
                        "prob": p.get("prob_anomalia", 0),
                        "riesgo": p.get("riesgo", "BAJO")
                    })

                resultados["anomalias_financieras"] = {
                    "detalles": detalles,
                    "predicciones": predicciones,
                    "raw": {"det": det, "pred": pred}
                }
                print(f"✅ Anomalías generadas: {len(predicciones)} predicciones")
            else:
                resultados["anomalias_financieras"] = {
                    "error": "Faltan datos para análisis de anomalías",
                    "totales_obtenidos": totales
                }
                print("⚠️ Totales insuficientes para anomalías")

        except Exception as e:
            resultados["anomalias_financieras"] = {
                "error": f"Error en Anomalias Financieras: {str(e)}"
            }
            print(f"❌ Error en anomalias: {e}")
            import traceback
            traceback.print_exc()

        # --- Generador de insights ---
        try:
            print("🔄 Iniciando generador de insights...")
            
            # 1. Obtener datos correctamente
            totales = analizador._calcular_totales() if hasattr(analizador, '_calcular_totales') else {}
            
            # 2. Obtener los resultados financieros (ya calculados)
            resultados_financieros = resultados.get('resultados', {})
            
            print(f"🔍 DEBUG - Estructura de resultados_financieros:")
            print(f"   - Claves: {list(resultados_financieros.keys())}")
            
            # 3. Asegurar que resultados_ia sea una lista
            resultados_ia = resultados.get('resultados_ia', [])
            if isinstance(resultados_ia, dict) and 'error' in resultados_ia:
                resultados_ia = []  # Si hay error, usar lista vacía
            
            # 4. VERIFICAR DATOS ANTES DE CREAR GENERADOR
            print(f"🔍 DEBUG - Datos para GeneradorInsights:")
            print(f"   - totales: {type(totales)}, keys: {list(totales.keys())[:3] if totales else 'vacío'}")
            print(f"   - razones: {type(resultados_financieros.get('razones', {}))}")
            print(f"   - horizontal: {type(resultados_financieros.get('horizontal', {}))}")
            print(f"   - vertical: {type(resultados_financieros.get('vertical', {}))}")
            print(f"   - predicciones: {type(resultados_ia)}")
            print(f"   - anomalias: {type(resultados.get('anomalias_financieras', {}))}")
            
            # 4. Crear generador con datos validados
            gen = GeneradorInsights(
                totales=totales,
                razones=resultados_financieros.get('razones', {}),
                horizontal=resultados_financieros.get('horizontal', {}),
                vertical=resultados_financieros.get('vertical', {}),
                predicciones=resultados_ia,
                anomalias=resultados.get('anomalias_financieras', {})
            )
            
            # 5. Generar insights
            insights_obj = gen.generar_insights()
            
            print(f"✅ Insights generados - Tipo: {type(insights_obj)}")
            print(f"✅ Insights generados - Contenido: {insights_obj}")
            
            # 6. Asegurar estructura correcta
            if isinstance(insights_obj, dict):
                resultados['insights'] = insights_obj
                print(f"✅ Insights agregados a resultados como dict")
                print(f"   - Claves: {list(insights_obj.keys())}")
                if 'insights' in insights_obj:
                    print(f"   - Número de insights: {len(insights_obj.get('insights', []))}")
            else:
                print(f"⚠️ Insights no eran dict, se convierten")
                resultados['insights'] = {
                    "resumen": "Insights generados correctamente",
                    "insights": insights_obj if isinstance(insights_obj, list) else [],
                    "recomendaciones": []
                }
            
        except Exception as e:
            print(f"❌ ERROR en generador de insights: {e}")
            import traceback
            traceback.print_exc()
            
            # Estructura mínima para evitar errores en la plantilla
            resultados['insights'] = {
                "resumen": "Error al generar insights automáticos",
                "insights": [],
                "recomendaciones": []
            }
            print(f"🔧 Se estableció estructura mínima de insights")


         # Asegurar que todas las claves necesarias existan
        resultados.setdefault('resumen', {})
        resultados.setdefault('insights', {})
        resultados.setdefault('resultados', {})
        resultados.setdefault('graficos', {})
        resultados.setdefault('datos_entrada', {})

        # Convertir None a dict vacío si es necesario
        if resultados['resumen'] is None:
            resultados['resumen'] = {}
        if resultados['insights'] is None:
            resultados['insights'] = {}

        print("✅ DEBUG - Estructura final:")
        print(f"   - resumen keys: {list(resultados.get('resumen', {}).keys())}")
        print(f"   - resumen contenido: {resultados.get('resumen', {})}")
        print(f"   - insights keys: {list(resultados.get('insights', {}).keys())}")
        
        # Debug adicional - ¡SIN intentar acceder con punto!
        print("🔍 DEBUG - Verificando estructura...")
        print(f"   - Acceso seguro con get: {resultados.get('resumen')}")
        print(f"   - Tipo de resultados: {type(resultados)}")
        print(f"   - ¿Es dict?: {isinstance(resultados, dict)}")

        # --- Renderizar plantilla ---
        print("🔎 DEBUG: Antes de renderizar, claves en resultados:", list(resultados.keys()))
        # Verificación EXTRA de seguridad
        print("🛡️ VERIFICACIÓN EXTRA:")
        print(f"   - ¿resultados tiene 'resumen'?: {'resumen' in resultados}")
        print(f"   - ¿resultados.resumen existe? (NO usar): Vamos a intentar...")

        # NO HAGAS esto en producción, solo para debug:
        try:
            # Esto fallará si resultados no es DotDict
            temp = resultados.resumen
            print(f"   - ¡SORPRESA! resultados.resumen funciona: {temp}")
        except AttributeError:
            print(f"   - Bien, resultados.resumen NO funciona (como esperábamos)")
            
        print(f"   - Acceso correcto: resultados['resumen']: {resultados['resumen']}")
        # JUSTO ANTES del return, reemplaza resultados con un dict nuevo
        resultados_final = dict(resultados)  # Crea una copia limpia

        print("🆕 Dict final creado:")
        print(f"   - Tipo: {type(resultados_final)}")
        print(f"   - Claves: {list(resultados_final.keys())}")

        try:
    # Intentar renderizar normalmente
            return render_template(
                'results.html',
                resultados=resultados_final,
                filename=filename,
                empresa=resultados_final.get('datos_entrada', {}).get('empresa', {})
            )
        except Exception as e:
            # Capturar CUALQUIER error durante el renderizado
            print(f"🚨 ERROR CRÍTICO EN RENDER_TEMPLATE: {str(e)}")
            print(f"🚨 Traceback completo:")
            import traceback
            traceback.print_exc()
            
            # Renderizar una página de error específica
            flash(f'Error al mostrar resultados: {str(e)}', 'error')
            return render_template('error_render.html', 
                                error=str(e),
                                datos_estructura=resultados_final.keys())

    except Exception as e:
        print("❌ ERROR en process_analysis:", e)
        flash(f'Error en análisis: {str(e)}', 'error')
        return redirect(url_for('upload_page'))

@app.route('/analysis')
def analysis_demo():
    """Página de ejemplo con análisis de demostración"""
    return render_template('analysis.html')

@app.route('/generar_pdf', methods=['POST'])
def generar_pdf():
    """Genera PDF usando el archivo original pero con datos ya validados"""
    try:
        print("🔍 DEBUG: Iniciando generación de PDF...")
        
        if not request.is_json:
            return "Se esperaba JSON", 400
            
        data = request.get_json()
        print("🔍 DEBUG: Datos recibidos para PDF")
        
        # Obtener el filename para cargar el archivo original
        filename = data.get('filename')
        if not filename:
            return "No se especificó archivo", 400
        
        # Ruta del archivo original
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            return "Archivo no encontrado", 404
        
        # Crear analizador con el archivo original
        from utils.analizador_financiero1 import AnalizadorFinanciero
        analizador = AnalizadorFinanciero(file_path)
        
        # Generar el reporte completo (igual que en results)
        resultados = analizador.generar_reporte_completo()
        
        # Usar PDFReportGenerator con los resultados
        from utils.pdf_generator import PDFReportGenerator
        pdf_generator = PDFReportGenerator(analizador, filename, resultados.get('datos_entrada', {}).get('empresa', {}))
        pdf_filename = pdf_generator.generar_reporte_pdf()
        
        if pdf_filename:
            pdf_path = os.path.join('static', 'reports', pdf_filename)
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=f"reporte_financiero_{filename.replace('.xlsx', '')}.pdf",
                mimetype='application/pdf'
            )
        else:
            return "Error generando el PDF", 500
            
    except Exception as e:
        print(f"❌ Error en generar_pdf: {e}")
        import traceback
        traceback.print_exc()
        return f"Error al generar PDF: {str(e)}", 500

@app.route('/eliminar_pdf/<filename>', methods=['DELETE'])
def eliminar_pdf(filename):
    """Elimina un PDF generado (opcional, para limpieza)"""
    try:
        pdf_path = os.path.join('static', 'reports', filename)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            return "PDF eliminado", 200
        else:
            return "PDF no encontrado", 404
    except Exception as e:
        return f"Error eliminando PDF: {str(e)}", 500

@app.route('/descargar_plantilla/<tipo>')
def descargar_plantilla(tipo):
    """Descarga las plantillas - usa archivos originales"""
    try:
        if tipo == 'excel_simple':
            return send_file(
                'plantillas/Indicadores_Financieros_Basicos_Calculados.xlsx',
                as_attachment=True,
                download_name='Plantilla_Financiera_Simple.xlsx'
            )
        elif tipo == 'excel_avanzado':
            return send_file(
                'plantillas/Indicadores_Financieros_Basicos_Calculados_v3.xlsx',
                as_attachment=True,
                download_name='Plantilla_Financiera_Avanzada.xlsx'
            )
        elif tipo == 'csv':
            # Solo el CSV se genera dinámicamente
            from utils.generar_plantillas import generar_csv
            csv_buffer = generar_csv()
            return send_file(
                csv_buffer,
                as_attachment=True,
                download_name='Plantilla_Financiera.csv',
                mimetype='text/csv'
            )
        else:
            flash('Tipo de plantilla no válido', 'error')
            return redirect(url_for('home'))
            
    except Exception as e:
        print(f"❌ Error en descargar_plantilla: {e}")
        flash(f'Error descargando plantilla: {str(e)}', 'error')
        return redirect(url_for('home'))
    

# ==================== 4. MANEJO DE ERRORES ====================

@app.errorhandler(404)
def not_found(error):
    """Maneja errores 404 - Página no encontrada"""
    return render_template('error.html', error=error), 404

@app.errorhandler(500)
def internal_error(error):
    """Maneja errores 500 - Error interno del servidor"""
    return render_template('error.html', error=error), 500

@app.route('/debug-estructura/<filename>')
def debug_estructura(filename):
    """Debug de estructura de datos para confirmación"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        analizador = AnalizadorFinanciero(filepath)
        datos_visualizacion = analizador.obtener_datos_para_visualizacion()
        
        print("\n" + "="*50)
        print("🔍 DEBUG ESTRUCTURA DE DATOS")
        print("="*50)
        
        print("\n📊 EMPRESA (estructura):")
        for i, item in enumerate(datos_visualizacion.get('empresa', [])):
            print(f"  [{i}] Tipo: {type(item)} - Keys: {list(item.keys()) if isinstance(item, dict) else 'No es dict'}")
            print(f"      Contenido: {item}")
        
        print("\n📊 EQUILIBRIO (estructura):")
        for i, item in enumerate(datos_visualizacion.get('equilibrio', [])):
            print(f"  [{i}] Tipo: {type(item)} - Keys: {list(item.keys()) if isinstance(item, dict) else 'No es dict'}")
            print(f"      Contenido: {item}")
        
        print("\n📊 ESTADO RESULTADOS (primer item):")
        if datos_visualizacion.get('estado_resultados'):
            first_item = datos_visualizacion['estado_resultados'][0]
            print(f"  Tipo: {type(first_item)} - Keys: {list(first_item.keys())}")
        
        return jsonify({
            'empresa_estructura': [
                {'tipo': str(type(item)), 'keys': list(item.keys()) if isinstance(item, dict) else None}
                for item in datos_visualizacion.get('empresa', [])
            ],
            'equilibrio_estructura': [
                {'tipo': str(type(item)), 'keys': list(item.keys()) if isinstance(item, dict) else None}
                for item in datos_visualizacion.get('equilibrio', [])
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})
# ==================== 5. EJECUCIÓN PRINCIPAL ====================

if __name__ == '__main__':
    print("🚀 Analizador Financiero iniciando...")
    print("📊 Accede en: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)