# ==================== 1. IMPORTS Y CONFIGURACIÓN ====================
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
import os
from pathlib import Path
from werkzeug.utils import secure_filename
from utils.analizador_financiero1 import AnalizadorFinanciero
from flask import send_file
from utils.pdf_generator import PDFReportGenerator 

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
    """Procesa el análisis completo después de confirmar datos"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        analizador = AnalizadorFinanciero(filepath)
        resultados = analizador.generar_reporte_completo()
        
        if resultados:
            return render_template('results.html', 
                                resultados=resultados,
                                filename=filename,
                                empresa=resultados.get('datos_entrada', {}).get('empresa', {}))
        else:
            flash('Error generando análisis completo', 'error')
            return redirect(url_for('upload_page'))
    except Exception as e:
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