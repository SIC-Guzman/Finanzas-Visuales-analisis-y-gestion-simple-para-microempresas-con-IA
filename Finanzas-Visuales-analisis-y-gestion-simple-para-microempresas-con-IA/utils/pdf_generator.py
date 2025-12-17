import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from datetime import datetime
import json
from reportlab.platypus import KeepTogether
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepTogether

class PDFReportGenerator:
    
    def __init__(self, analizador, filename, empresa_data, resultados_completos=None):
        self.analizador = analizador
        self.filename = filename
        self.empresa_data = empresa_data
        
        # Asegurar que resultados_completos es un dict
        if resultados_completos and isinstance(resultados_completos, dict):
            self.report_data = resultados_completos
        else:
            # Generar desde el analizador
            self.report_data = analizador.generar_reporte_completo()
        
        # Asegurar que todas las claves necesarias existan
        self.report_data.setdefault('resumen', {})
        self.report_data.setdefault('resultados', {})
        self.report_data.setdefault('resultados_ia', {})
        self.report_data.setdefault('anomalias_financieras', {})
        self.report_data.setdefault('insights', {})
        self.report_data.setdefault('graficos', {})
        
        # Asegurar que existe la clave para simulador y semáforo
        self.report_data.setdefault('simulador_crisis', {})
        self.report_data.setdefault('semaforo_financiero', {})
        
        print(f"📊 PDF Generator inicializado:")
        
    def generar_reporte_pdf(self):
        """Genera el reporte PDF completo"""
        try:
            # Crear nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"reporte_financiero_{timestamp}.pdf"
            output_path = os.path.join('static', 'reports', output_filename)
            
            # Asegurar que existe la carpeta
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Crear documento
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Elementos del documento
            story = []
            styles = getSampleStyleSheet()
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#2C3E50'),
                alignment=1  # Centrado
            )
            title = Paragraph("REPORTE FINANCIERO", title_style)
            story.append(title)
            
            # Información del archivo
            info_style = ParagraphStyle(
                'InfoStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#7F8C8D')
            )
            
            info_text = f"""
            <b>Archivo analizado:</b> {self.filename}<br/>
            <b>Empresa:</b> {self.empresa_data.get('nombre', 'No especificada')}<br/>
            <b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
            """
            info = Paragraph(info_text, info_style)
            story.append(info)
            story.append(Spacer(1, 20))
            
            # ORDEN MEJORADO DE LAS SECCIONES:
            # 1. RESUMEN EJECUTIVO
            story.append(self._crear_seccion_resumen(styles))
            story.append(Spacer(1, 15))
            
            # 2. SEMÁFORO FINANCIERO (nueva sección)
            if 'semaforo_financiero' in self.report_data and self.report_data['semaforo_financiero']:
                story.append(self._crear_seccion_semaforo(styles))
                story.append(Spacer(1, 15))
            
            # 3. INSIGHTS AUTOMÁTICOS
            if 'insights' in self.report_data:
                story.append(self._crear_seccion_insights(styles))
                story.append(Spacer(1, 15))
            
            # 4. ANÁLISIS HORIZONTAL
            story.append(self._crear_seccion_horizontal(styles))
            story.append(Spacer(1, 15))
            
            # 5. ANÁLISIS VERTICAL
            story.append(self._crear_seccion_vertical(styles))
            story.append(Spacer(1, 15))
            
            # 6. RAZONES FINANCIERAS
            story.append(self._crear_seccion_razones(styles))
            story.append(Spacer(1, 15))
            
            # 7. PUNTO DE EQUILIBRIO
            if self.report_data['resultados']['punto_equilibrio']:
                story.append(self._crear_seccion_equilibrio(styles))
                story.append(Spacer(1, 15))
            
            # 8. PREDICCIONES IA
            if 'resultados_ia' in self.report_data:
                story.append(self._crear_seccion_predicciones(styles))
                story.append(Spacer(1, 15))
            
            # 9. SIMULADOR DE CRISIS (nueva sección)
            if 'resultados_ia' in self.report_data and 'resumen' in self.report_data['resultados_ia']:
                if 'sobrevive_crisis' in self.report_data['resultados_ia']['resumen']:
                    story.append(self._crear_seccion_simulador_crisis(styles))
                    story.append(Spacer(1, 15))
            
            # 10. ANOMALÍAS FINANCIERAS
            if 'anomalias_financieras' in self.report_data:
                story.append(self._crear_seccion_anomalias(styles))
                story.append(Spacer(1, 15))
            
            # 11. INTERPRETACIÓN FINAL
            story.append(self._crear_seccion_interpretacion(styles))
            
            # Construir PDF
            doc.build(story)
            
            return output_filename
            
        except Exception as e:
            print(f"Error generando PDF: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _crear_seccion_resumen(self, styles):
        """Crea la sección de resumen ejecutivo"""
        resumen = self.report_data['resumen']
        
        # Estilo para KPIs
        kpi_style = ParagraphStyle(
            'KPIStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2C3E50'),
            alignment=1
        )
        
        # Datos para la tabla de KPIs
        kpi_data = [
            ['INDICADOR', 'VALOR', 'ESTADO'],
            [
                'Crecimiento Ventas', 
                f"{resumen.get('crecimiento_ventas', 0):.1f}%",
                self._get_estado_crecimiento(resumen.get('crecimiento_ventas', 0))
            ],
            [
                'ROA', 
                f"{resumen.get('roa', 0):.1f}%", 
                self._get_estado_roa(resumen.get('roa', 0))
            ],
            [
                'Liquidez Corriente', 
                f"{resumen.get('liquidez', 0):.2f}", 
                self._get_estado_liquidez(resumen.get('liquidez', 0))
            ],
            [
                'Margen Seguridad', 
                f"{resumen.get('margen_seguridad', 0):.1f}%", 
                self._get_estado_margen(resumen.get('margen_seguridad', 0))
            ]
        ]
        
        # Crear tabla
        kpi_table = Table(kpi_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7'))
        ]))
        
        return kpi_table
    
    def _crear_seccion_horizontal(self, styles):
        """Crea la sección de análisis horizontal"""
        horizontal = self.report_data['resultados']['horizontal']
        
        # Encabezados
        data = [['CONCEPTO', 'AÑO ANTERIOR', 'AÑO ACTUAL', 'VARIACIÓN %']]
        
        # Datos
        for concepto, valores in horizontal.items():
            if concepto != 'utilidad_neta':
                variacion = valores.get('variacion_porcentual', 0)
                data.append([
                    concepto,
                    f"Q{valores.get('año_anterior', 0):,.2f}",
                    f"Q{valores.get('año_actual', 0):,.2f}",
                    f"{variacion:+.1f}%"
                ])
        
        table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7'))
        ]))
        
        return table
    
    def _crear_seccion_vertical(self, styles):
        """Crea la sección de análisis vertical"""
        vertical = self.report_data['resultados']['vertical']
        
        data = [['COMPONENTE', 'PORCENTAJE %']]
        
        # Estado de Resultados
        if vertical.get('estado_resultados'):
            data.append(['--- ESTADO DE RESULTADOS ---', ''])
            for concepto, porcentaje in vertical['estado_resultados'].items():
                data.append([concepto, f"{porcentaje:.1f}%"])
        
        # Balance General
        if vertical.get('balance_general'):
            data.append(['--- BALANCE GENERAL ---', ''])
            for concepto, porcentaje in vertical['balance_general'].items():
                data.append([concepto, f"{porcentaje:.1f}%"])
        
        table = Table(data, colWidths=[3.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.whitesmoke),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 2), (-1, -1), colors.HexColor('#ECF0F1')),
            ('FONTSIZE', (0, 2), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7'))
        ]))
        
        return table
    
    def _crear_seccion_razones(self, styles):
        """Crea la sección de razones financieras"""
        razones = self.report_data['resultados']['razones']
        
        data = [['RAZÓN', 'VALOR', 'META IDEAL', 'INTERPRETACIÓN']]
        
        if razones.get('liquidez_corriente'):
            data.append([
                'Liquidez Corriente',
                f"{razones['liquidez_corriente']:.2f}",
                '> 1.5',
                self._get_interpretacion_liquidez(razones['liquidez_corriente'])
            ])
        
        if razones.get('roa'):
            data.append([
                'ROA',
                f"{razones['roa']:.1f}%",
                '> 10%',
                self._get_interpretacion_roa(razones['roa'])
            ])
        
        if razones.get('roe'):
            data.append([
                'ROE',
                f"{razones['roe']:.1f}%",
                '> 15%',
                self._get_interpretacion_roe(razones['roe'])
            ])
        
        if razones.get('endeudamiento'):
            data.append([
                'Endeudamiento',
                f"{razones['endeudamiento']:.1f}%",
                '< 60%',
                self._get_interpretacion_endeudamiento(razones['endeudamiento'])
            ])
        
        table = Table(data, colWidths=[1.5*inch, 1*inch, 1*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FDEDEC')),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7'))
        ]))
        
        return table
    
    def _crear_seccion_equilibrio(self, styles):
        """Crea la sección de punto de equilibrio"""
        equilibrio = self.report_data['resultados']['punto_equilibrio']
        
        data = [
            ['CONCEPTO', 'VALOR'],
            ['Punto Equilibrio (Unidades)', f"{equilibrio['punto_equilibrio_unidades']:.0f}"],
            ['Punto Equilibrio (Q)', f"Q{equilibrio['punto_equilibrio_dolares']:,.2f}"],
            ['Margen de Contribución', f"Q{equilibrio['margen_contribucion']:,.2f}"],
            ['Margen de Seguridad', f"{equilibrio['margen_seguridad_porcentaje']:.1f}%"],
            ['Ventas Actuales', f"Q{equilibrio['ventas_actuales']:,.2f}"]
        ]
        
        table = Table(data, colWidths=[2.5*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F39C12')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FEF9E7')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7'))
        ]))
        
        return table
    
    def _crear_seccion_interpretacion(self, styles):
        """Crea la sección de interpretación"""
        resumen = self.report_data['resumen']
        
        interpretacion_style = ParagraphStyle(
            'InterpretacionStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2C3E50'),
            backColor=colors.HexColor('#ECF0F1'),
            borderPadding=10,
            spaceAfter=12
        )
        
        texto = f"""
        <b>Interpretación General:</b><br/>
        • <b>Crecimiento:</b> {self._get_interpretacion_completa_crecimiento(resumen.get('crecimiento_ventas', 0))}<br/>
        • <b>Rentabilidad:</b> {self._get_interpretacion_completa_rentabilidad(resumen.get('roa', 0))}<br/>
        • <b>Liquidez:</b> {self._get_interpretacion_completa_liquidez(resumen.get('liquidez', 0))}<br/>
        • <b>Estabilidad:</b> {self._get_interpretacion_completa_margen(resumen.get('margen_seguridad', 0))}<br/>
        <br/>
        <i>Este reporte fue generado automáticamente por el Sistema de Análisis Financiero.</i>
        """
        
        return Paragraph(texto, interpretacion_style)

    def _crear_seccion_predicciones(self, styles):
        """Crea la sección de predicciones IA - DEVUELVE UN SOLO ELEMENTO"""
        resultados_ia = self.report_data.get('resultados_ia', {})
        
        if 'error' in resultados_ia:
            return Paragraph(f"<b>Predicciones IA:</b> {resultados_ia['error']}", styles['Normal'])
        
        if 'predicciones' not in resultados_ia:
            return Paragraph("<b>Predicciones IA:</b> No disponibles", styles['Normal'])
        
        # Título de la sección
        titulo_style = ParagraphStyle(
            'TituloPredicciones',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#8E44AD')
        )
        titulo = Paragraph("📊 PREDICCIONES IA - PROYECCIÓN 3 AÑOS", titulo_style)
        
        # Crear tabla simple
        predicciones = resultados_ia['predicciones']
        ventas = predicciones.get('ventas', [])
        costos = predicciones.get('costos', [])
        
        data = [['AÑO', 'VENTAS (Q)', 'COSTOS (Q)', 'CRECIMIENTO %']]
        
        for i in range(min(len(ventas), 3)):
            venta = ventas[i] if i < len(ventas) else 0
            costo = costos[i] if i < len(costos) else 0
            
            # Calcular crecimiento vs año anterior
            crecimiento = 0
            if i > 0 and ventas[i-1] > 0:
                crecimiento = ((venta - ventas[i-1]) / ventas[i-1]) * 100
            
            data.append([
                f"Año {i+1}",
                f"Q{venta:,.2f}",
                f"Q{costo:,.2f}",
                f"{crecimiento:+.1f}%" if i > 0 else "N/A"
            ])
        
        table = Table(data, colWidths=[1*inch, 1.5*inch, 1.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8E44AD')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F4ECF7')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D7BDE2')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')])
        ]))
        
        # Crear un contenedor con título y tabla
        from reportlab.platypus import KeepTogether
        return KeepTogether([titulo, Spacer(1, 6), table])

    def _crear_seccion_anomalias(self, styles):
        """Crea la sección de anomalías financieras - DEVUELVE UN SOLO ELEMENTO"""
        anomalias = self.report_data.get('anomalias_financieras', {})
        
        if 'error' in anomalias:
            return Paragraph(f"<b>Anomalías:</b> {anomalias['error']}", styles['Normal'])
        
        predicciones = anomalias.get('predicciones', [])
        
        if not predicciones:
            return Paragraph("<b>Anomalías:</b> Sin predicciones disponibles", styles['Normal'])
        
        # Título de la sección
        titulo_style = ParagraphStyle(
            'TituloAnomalias',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#E74C3C')
        )
        titulo = Paragraph("⚠️ DETECCIÓN DE ANOMALÍAS FINANCIERAS", titulo_style)
        
        # Crear tabla simple
        data = [['PERIODO', 'PROBABILIDAD', 'NIVEL DE RIESGO']]  # ← CORREGIDO "RIESGO"
        
        for pred in predicciones[:3]:
            probabilidad = pred.get('prob', 0) * 100
            riesgo = pred.get('riesgo', 'BAJO').upper()
            
            # Color según riesgo
            color_riesgo = colors.HexColor('#27AE60')  # Verde para BAJO
            if riesgo == 'MEDIO':
                color_riesgo = colors.HexColor('#F39C12')  # Naranja
            elif riesgo == 'ALTO':
                color_riesgo = colors.HexColor('#E74C3C')  # Rojo
            
            data.append([
                pred.get('anios', 'N/A'),
                f"{probabilidad:.1f}%",
                riesgo
            ])
        
        table = Table(data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FDEDEC')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#F5B7B1')),
            ('TEXTCOLOR', (2, 1), (2, -1), colors.HexColor('#2C3E50')),
            ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold')
        ]))
        
        # Información adicional sobre las anomalías
        info_text = """
        <b>Interpretación de riesgos:</b><br/>
        • <font color="#27AE60"><b>BAJO</b></font>: Operación normal, sin anomalías significativas<br/>
        • <font color="#F39C12"><b>MEDIO</b></font>: Posibles desviaciones que requieren monitoreo<br/>
        • <font color="#E74C3C"><b>ALTO</b></font>: Anomalías detectadas, revisión inmediata recomendada<br/>
        """
        info_paragraph = Paragraph(info_text, styles['Normal'])
        
        from reportlab.platypus import KeepTogether
        return KeepTogether([titulo, Spacer(1, 6), table, Spacer(1, 12), info_paragraph])

    def _crear_seccion_insights(self, styles):
        """Crea la sección de insights automáticos - DEVUELVE UN SOLO ELEMENTO"""
        insights_data = self.report_data.get('insights', {})
        
        if not insights_data:
            return Paragraph("<b>Insights IA:</b> No generados", styles['Normal'])
        
        # Título de la sección
        titulo_style = ParagraphStyle(
            'TituloInsights',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#2E86C1')
        )
        titulo = Paragraph("💡 INSIGHTS AUTOMÁTICOS DETECTADOS", titulo_style)
        
        # Crear un solo párrafo con toda la información
        resumen = insights_data.get('resumen', 'Sin resumen')
        insights_list = insights_data.get('insights', [])
        
        # Estilo para el contenido
        contenido_style = ParagraphStyle(
            'InsightsContent',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2C3E50'),
            backColor=colors.HexColor('#EAF2F8'),
            borderPadding=12,
            spaceAfter=6
        )
        
        # Construir contenido
        contenido_text = f"<b>📋 Resumen ejecutivo:</b><br/>{resumen}<br/><br/>"
        
        if insights_list:
            contenido_text += "<b>🔍 Insights detectados:</b><br/>"
            for i, insight in enumerate(insights_list[:5]):  # Máximo 5 insights
                titulo_insight = insight.get('titulo', f'Insight {i+1}')
                descripcion = insight.get('descripcion', 'Sin descripción')
                
                # Icono según el número
                icono = '✓' if i % 2 == 0 else '➤'
                contenido_text += f"{icono} <b>{titulo_insight}:</b> {descripcion}<br/>"
        
        # Recomendaciones si existen
        recomendaciones = insights_data.get('recomendaciones', [])
        if recomendaciones:
            contenido_text += "<br/><b>🎯 Recomendaciones:</b><br/>"
            for rec in recomendaciones[:3]:  # Máximo 3 recomendaciones
                contenido_text += f"• {rec}<br/>"
        
        contenido = Paragraph(contenido_text, contenido_style)
        
        from reportlab.platypus import KeepTogether
        return KeepTogether([titulo, Spacer(1, 6), contenido])

    # Métodos auxiliares para interpretaciones
    def _get_estado_crecimiento(self, valor):
        if valor > 15: return "EXCELENTE"
        elif valor > 0: return "BUENO" 
        else: return "MEJORABLE"
    
    def _get_estado_roa(self, valor):
        if valor > 15: return "ALTO"
        elif valor > 8: return "ADECUADO"
        else: return "BAJO"
    
    def _get_estado_liquidez(self, valor):
        if valor > 2.0: return "ÓPTIMA"
        elif valor > 1.0: return "ADECUADA"
        else: return "RIESGO"
    
    def _get_estado_margen(self, valor):
        if valor > 20: return "SEGURO"
        elif valor > 10: return "ESTABLE"
        else: return "AJUSTADO"
    
    def _get_interpretacion_liquidez(self, valor):
        if valor > 2.0: return "Excelente capacidad de pago"
        elif valor > 1.5: return "Buena liquidez"
        elif valor > 1.0: return "Liquidez adecuada"
        else: return "Riesgo de liquidez"
    
    def _get_interpretacion_roa(self, valor):
        if valor > 15: return "Alta rentabilidad activos"
        elif valor > 10: return "Buena rentabilidad"
        elif valor > 5: return "Rentabilidad aceptable"
        else: return "Baja rentabilidad"
    
    def _get_interpretacion_roe(self, valor):
        if valor > 20: return "Excelente retorno patrimonio"
        elif valor > 15: return "Buen retorno"
        elif valor > 10: return "Retorno aceptable"
        else: return "Bajo retorno"
    
    def _get_interpretacion_endeudamiento(self, valor):
        if valor < 40: return "Bajo endeudamiento"
        elif valor < 60: return "Endeudamiento moderado"
        elif valor < 80: return "Alto endeudamiento"
        else: return "Endeudamiento crítico"
    
    def _get_interpretacion_completa_crecimiento(self, valor):
        if valor > 15: return "Crecimiento sólido y superior al 15% anual"
        elif valor > 0: return "Crecimiento positivo con oportunidades de mejora"
        else: return "Tendencia decreciente que requiere atención"
    
    def _get_interpretacion_completa_rentabilidad(self, valor):
        if valor > 15: return "Alta rentabilidad con excelente uso de activos"
        elif valor > 8: return "Rentabilidad adecuada para el sector"
        else: return "Oportunidad para optimizar la rentabilidad"
    
    def _get_interpretacion_completa_liquidez(self, valor):
        if valor > 2.0: return "Posición de liquidez muy sólida"
        elif valor > 1.5: return "Buena capacidad de pago a corto plazo"
        elif valor > 1.0: return "Liquidez adecuada para operaciones"
        else: return "Se recomienda fortalecer la posición de liquidez"
    
    def _get_interpretacion_completa_margen(self, valor):
        if valor > 20: return "Amplio margen de seguridad operativa"
        elif valor > 10: return "Margen de seguridad estable y adecuado"
        else: return "Margen ajustado, recomienda precaución operativa"


        # Añadir import de Spacer si no está


        return None
    
    def _crear_seccion_semaforo(self, styles):
        """Crea la sección del semáforo financiero - DEVUELVE UN SOLO ELEMENTO"""
        semaforo_data = self.report_data.get('semaforo_financiero', {})
        
        if not semaforo_data:
            return Paragraph("<b>Semáforo Financiero:</b> No disponible", styles['Normal'])
        
        # Título de la sección
        titulo_style = ParagraphStyle(
            'TituloSemaforo',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#2C3E50')
        )
        
        # Determinar color del título basado en el estado general
        estado_general = semaforo_data.get('estado_general', 'AMARILLO')
        if estado_general == 'VERDE':
            color_titulo = colors.HexColor('#27AE60')
        elif estado_general == 'ROJO':
            color_titulo = colors.HexColor('#E74C3C')
        else:
            color_titulo = colors.HexColor('#F39C12')
        
        titulo_style.textColor = color_titulo
        titulo = Paragraph(f"🚦 SEMÁFORO FINANCIERO - ESTADO: {estado_general}", titulo_style)
        
        # Mensaje general
        mensaje = semaforo_data.get('mensaje', 'Sin evaluación disponible')
        mensaje_style = ParagraphStyle(
            'MensajeSemaforo',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2C3E50'),
            backColor=colors.HexColor('#F8F9F9'),
            borderPadding=10,
            spaceAfter=12
        )
        mensaje_parrafo = Paragraph(f"<b>Evaluación:</b> {mensaje}", mensaje_style)
        
        # Tabla de áreas evaluadas
        areas = semaforo_data.get('areas', {})
        
        if areas:
            data = [['ÁREA', 'ESTADO', 'SCORE', 'INTERPRETACIÓN']]
            
            # Liquidez
            liq = areas.get('liquidez', {})
            if liq:
                data.append([
                    'Liquidez',
                    liq.get('estado', 'N/A'),
                    f"{liq.get('score', 0):.1f}",
                    self._get_interpretacion_semaforo_liquidez(liq.get('estado', ''))
                ])
            
            # Rentabilidad
            rent = areas.get('rentabilidad', {})
            if rent:
                data.append([
                    'Rentabilidad',
                    rent.get('estado', 'N/A'),
                    f"{rent.get('score', 0):.1f}",
                    self._get_interpretacion_semaforo_rentabilidad(rent.get('estado', ''))
                ])
            
            # Endeudamiento
            endeud = areas.get('endeudamiento', {})
            if endeud:
                data.append([
                    'Endeudamiento',
                    endeud.get('estado', 'N/A'),
                    f"{endeud.get('score', 0):.1f}",
                    self._get_interpretacion_semaforo_endeudamiento(endeud.get('estado', ''))
                ])
            
            # Riesgo IA
            riesgo = areas.get('riesgo_ia', {})
            if riesgo:
                data.append([
                    'Riesgo Anomalías',
                    riesgo.get('estado', 'N/A'),
                    f"{riesgo.get('score', 0):.1f}",
                    self._get_interpretacion_semaforo_riesgo(riesgo.get('estado', ''))
                ])
            
            table = Table(data, colWidths=[1.5*inch, 1*inch, 0.8*inch, 2.2*inch])
            
            # Estilos de la tabla con colores según estado
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7'))
            ])
            
            # Aplicar colores según estado en la columna 1 (índice 1)
            for i in range(1, len(data)):
                estado = data[i][1]
                if estado == 'VERDE':
                    table_style.add('BACKGROUND', (1, i), (1, i), colors.HexColor('#27AE60'))
                    table_style.add('TEXTCOLOR', (1, i), (1, i), colors.white)
                elif estado == 'ROJO':
                    table_style.add('BACKGROUND', (1, i), (1, i), colors.HexColor('#E74C3C'))
                    table_style.add('TEXTCOLOR', (1, i), (1, i), colors.white)
                elif estado == 'AMARILLO':
                    table_style.add('BACKGROUND', (1, i), (1, i), colors.HexColor('#F39C12'))
                    table_style.add('TEXTCOLOR', (1, i), (1, i), colors.white)
                
                # Alternar colores de fondo para filas
                if i % 2 == 0:
                    table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F8F9F9'))
                else:
                    table_style.add('BACKGROUND', (0, i), (-1, i), colors.white)
            
            table.setStyle(table_style)
            
            # Leyenda de colores
            leyenda_style = ParagraphStyle(
                'LeyendaSemaforo',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#7F8C8D'),
                spaceAfter=6
            )
            
            leyenda_text = """
            <b>Leyenda:</b> 
            <font color="#27AE60"><b>VERDE</b></font> = Óptimo | 
            <font color="#F39C12"><b>AMARILLO</b></font> = Precaución | 
            <font color="#E74C3C"><b>ROJO</b></font> = Necesita atención
            """
            leyenda = Paragraph(leyenda_text, leyenda_style)
            
            return KeepTogether([titulo, Spacer(1, 6), mensaje_parrafo, Spacer(1, 12), table, Spacer(1, 8), leyenda])
        
        return KeepTogether([titulo, Spacer(1, 6), mensaje_parrafo])
    
    def _crear_seccion_simulador_crisis(self, styles):
        """Crea la sección del simulador de crisis financiera - DEVUELVE UN SOLO ELEMENTO"""
        resultados_ia = self.report_data.get('resultados_ia', {})
        resumen_ia = resultados_ia.get('resumen', {})
        
        if 'sobrevive_crisis' not in resumen_ia:
            return Paragraph("<b>Simulador de Crisis:</b> No disponible", styles['Normal'])
        
        # Título de la sección
        titulo_style = ParagraphStyle(
            'TituloSimulador',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#E74C3C')
        )
        
        # Determinar icono y color basado en si sobrevive
        sobrevive = resumen_ia.get('sobrevive_crisis', 'No evaluado')
        if sobrevive == "Sobrevive":
            icono = "✅"
            color_titulo = colors.HexColor('#27AE60')
            titulo_text = "🛡️ SIMULADOR DE CRISIS - RESULTADO: SOBREVIVE"
        elif sobrevive == "No sobrevive":
            icono = "❌"
            color_titulo = colors.HexColor('#E74C3C')
            titulo_text = "⚠️ SIMULADOR DE CRISIS - RESULTADO: NO SOBREVIVE"
        else:
            icono = "❓"
            color_titulo = colors.HexColor('#F39C12')
            titulo_text = "❔ SIMULADOR DE CRISIS - RESULTADO: NO EVALUADO"
        
        titulo_style.textColor = color_titulo
        titulo = Paragraph(titulo_text, titulo_style)
        
        # Descripción del escenario
        desc_style = ParagraphStyle(
            'DescSimulador',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2C3E50'),
            backColor=colors.HexColor('#FDEDEC'),
            borderPadding=10,
            spaceAfter=10
        )
        
        desc_text = f"""
        <b>Escenario simulado:</b> Crisis financiera con caída del 20% en ventas<br/>
        <b>Resultado:</b> {sobrevive}<br/>
        <b>Metodología:</b> Análisis de capacidad de supervivencia ante caídas bruscas en ingresos
        """
        desc_parrafo = Paragraph(desc_text, desc_style)
        
        # Tabla con datos del simulador
        predicciones = resultados_ia.get('predicciones', {})
        ventas_crisis = predicciones.get('ventas_crisis', [])
        utilidades_crisis = resumen_ia.get('utilidades_crisis', [])
        
        if ventas_crisis and len(ventas_crisis) >= 3:
            data = [['AÑO', 'VENTAS NORMALES (Q)', 'VENTAS CRISIS (Q)', 'DIFERENCIA %', 'UTILIDAD CRISIS (Q)']]
            
            # Obtener ventas normales de las predicciones regulares
            ventas_normales = predicciones.get('ventas', [])
            
            for i in range(min(3, len(ventas_crisis))):
                venta_normal = ventas_normales[i] if i < len(ventas_normales) else ventas_crisis[i] / 0.8
                venta_crisis = ventas_crisis[i]
                diferencia_pct = ((venta_crisis - venta_normal) / venta_normal * 100) if venta_normal > 0 else -20
                utilidad = utilidades_crisis[i] if i < len(utilidades_crisis) else 0
                
                data.append([
                    f"Año {i+1}",
                    f"Q{venta_normal:,.2f}",
                    f"Q{venta_crisis:,.2f}",
                    f"{diferencia_pct:+.1f}%",
                    f"Q{utilidad:,.2f}"
                ])
            
            table = Table(data, colWidths=[0.8*inch, 1.5*inch, 1.5*inch, 1*inch, 1.5*inch])
            
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FDEDEC')),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#F5B7B1'))
            ])
            
            # Resaltar diferencias negativas
            for i in range(1, len(data)):
                if i % 2 == 0:
                    table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FBEEE6'))
                
                # Resaltar columna de diferencia si es muy negativa
                if i < len(data):
                    diferencia_cell = data[i][3]
                    if "20.0%" in diferencia_cell or "-20.0%" in diferencia_cell:
                        table_style.add('TEXTCOLOR', (3, i), (3, i), colors.HexColor('#E74C3C'))
                        table_style.add('FONTNAME', (3, i), (3, i), 'Helvetica-Bold')
            
            table.setStyle(table_style)
            
            # Recomendaciones basadas en el resultado
            recom_style = ParagraphStyle(
                'RecomSimulador',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#2C3E50'),
                spaceAfter=6
            )
            
            if sobrevive == "Sobrevive":
                recom_text = """
                <b>✅ Recomendaciones:</b><br/>
                • La empresa muestra <b>resiliencia financiera</b> ante crisis<br/>
                • Mantener reservas de liquidez para mayor seguridad<br/>
                • Continuar con estrategias de diversificación de ingresos
                """
            elif sobrevive == "No sobrevive":
                recom_text = """
                <b>⚠️ Acciones urgentes recomendadas:</b><br/>
                • <b>Reducir costos fijos</b> de manera inmediata<br/>
                • Buscar <b>nuevas fuentes de ingresos</b><br/>
                • Crear un <b>fondo de emergencia</b> para cubrir 6 meses de gastos<br/>
                • Revisar estructura de deuda y negociar términos
                """
            else:
                recom_text = """
                <b>📊 Consideraciones:</b><br/>
                • Se recomienda realizar análisis más detallado de escenarios<br/>
                • Evaluar diferentes niveles de impacto en ventas<br/>
                • Desarrollar plan de contingencia para diversos escenarios
                """
            
            recom_parrafo = Paragraph(recom_text, recom_style)
            
            return KeepTogether([titulo, Spacer(1, 6), desc_parrafo, Spacer(1, 12), table, Spacer(1, 12), recom_parrafo])
        
        # Si no hay datos detallados, mostrar solo el resultado
        simple_style = ParagraphStyle(
            'SimpleSimulador',
            parent=styles['Normal'],
            fontSize=11,
            textColor=color_titulo,
            alignment=1,
            backColor=colors.HexColor('#FEF9E7'),
            borderPadding=15,
            spaceAfter=12
        )
        
        simple_text = f"""
        <b>{icono} RESULTADO DEL SIMULADOR DE CRISIS</b><br/>
        <font size="12"><b>{sobrevive}</b></font><br/>
        <i>Escenario: Caída del 20% en ventas</i>
        """
        
        return KeepTogether([titulo, Spacer(1, 6), Paragraph(simple_text, simple_style)])
    
    # Añadir métodos auxiliares para el semáforo
    def _get_interpretacion_semaforo_liquidez(self, estado):
        interpretaciones = {
            'VERDE': 'Liquidez óptima, capacidad sólida de pago',
            'AMARILLO': 'Liquidez adecuada, monitorear flujo de caja',
            'ROJO': 'Riesgo de liquidez, revisar obligaciones a corto plazo'
        }
        return interpretaciones.get(estado, 'Sin evaluación')
    
    def _get_interpretacion_semaforo_rentabilidad(self, estado):
        interpretaciones = {
            'VERDE': 'Alta rentabilidad, uso eficiente de recursos',
            'AMARILLO': 'Rentabilidad aceptable, oportunidades de mejora',
            'ROJO': 'Baja rentabilidad, revisar márgenes y costos'
        }
        return interpretaciones.get(estado, 'Sin evaluación')
    
    def _get_interpretacion_semaforo_endeudamiento(self, estado):
        interpretaciones = {
            'VERDE': 'Bajo endeudamiento, estructura financiera sólida',
            'AMARILLO': 'Endeudamiento moderado, mantener bajo control',
            'ROJO': 'Alto endeudamiento, riesgo financiero elevado'
        }
        return interpretaciones.get(estado, 'Sin evaluación')
    
    def _get_interpretacion_semaforo_riesgo(self, estado):
        interpretaciones = {
            'VERDE': 'Bajo riesgo de anomalías, operación estable',
            'AMARILLO': 'Riesgo moderado, monitorear tendencias',
            'ROJO': 'Alto riesgo de anomalías, revisión inmediata'
        }
        return interpretaciones.get(estado, 'Sin evaluación')
    
    # También necesitas modificar el método _crear_seccion_predicciones para incluir datos del simulador
    def _crear_seccion_predicciones(self, styles):
        """Crea la sección de predicciones IA - Versión mejorada con simulador"""
        resultados_ia = self.report_data.get('resultados_ia', {})
        
        if 'error' in resultados_ia:
            return Paragraph(f"<b>Predicciones IA:</b> {resultados_ia['error']}", styles['Normal'])
        
        if 'predicciones' not in resultados_ia:
            return Paragraph("<b>Predicciones IA:</b> No disponibles", styles['Normal'])
        
        # Título de la sección
        titulo_style = ParagraphStyle(
            'TituloPredicciones',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#8E44AD')
        )
        titulo = Paragraph("📊 PREDICCIONES IA - PROYECCIÓN 3 AÑOS", titulo_style)
        
        # Crear tabla simple
        predicciones = resultados_ia['predicciones']
        ventas = predicciones.get('ventas', [])
        costos = predicciones.get('costos', [])
        
        data = [['AÑO', 'VENTAS (Q)', 'COSTOS (Q)', 'CRECIMIENTO %']]
        
        for i in range(min(len(ventas), 3)):
            venta = ventas[i] if i < len(ventas) else 0
            costo = costos[i] if i < len(costos) else 0
            
            # Calcular crecimiento vs año anterior
            crecimiento = 0
            if i > 0 and ventas[i-1] > 0:
                crecimiento = ((venta - ventas[i-1]) / ventas[i-1]) * 100
            
            data.append([
                f"Año {i+1}",
                f"Q{venta:,.2f}",
                f"Q{costo:,.2f}",
                f"{crecimiento:+.1f}%" if i > 0 else "N/A"
            ])
        
        table = Table(data, colWidths=[1*inch, 1.5*inch, 1.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8E44AD')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F4ECF7')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D7BDE2')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')])
        ]))
        
        # Nota sobre el simulador (si existe)
        nota_text = ""
        resumen_ia = resultados_ia.get('resumen', {})
        if 'sobrevive_crisis' in resumen_ia:
            nota_text = f"<i>Nota: Se incluye simulación de crisis (-20% ventas) en sección independiente</i>"
            nota = Paragraph(nota_text, styles['Normal'])
            return KeepTogether([titulo, Spacer(1, 6), table, Spacer(1, 6), nota])
        
        return KeepTogether([titulo, Spacer(1, 6), table])
    
    # Modificar la sección de interpretación para incluir semáforo
    def _crear_seccion_interpretacion(self, styles):
        """Crea la sección de interpretación final con semáforo"""
        resumen = self.report_data['resumen']
        semaforo = self.report_data.get('semaforo_financiero', {})
        
        interpretacion_style = ParagraphStyle(
            'InterpretacionStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2C3E50'),
            backColor=colors.HexColor('#ECF0F1'),
            borderPadding=10,
            spaceAfter=12
        )
        
        # Incluir información del semáforo si existe
        semaforo_text = ""
        if semaforo:
            estado_general = semaforo.get('estado_general', 'NO DISPONIBLE')
            mensaje = semaforo.get('mensaje', '')
            semaforo_text = f"• <b>Semaforo Financiero:</b> Estado {estado_general} - {mensaje}<br/>"
        
        texto = f"""
        <b>Interpretación General:</b><br/>
        {semaforo_text}
        • <b>Crecimiento:</b> {self._get_interpretacion_completa_crecimiento(resumen.get('crecimiento_ventas', 0))}<br/>
        • <b>Rentabilidad:</b> {self._get_interpretacion_completa_rentabilidad(resumen.get('roa', 0))}<br/>
        • <b>Liquidez:</b> {self._get_interpretacion_completa_liquidez(resumen.get('liquidez', 0))}<br/>
        • <b>Estabilidad:</b> {self._get_interpretacion_completa_margen(resumen.get('margen_seguridad', 0))}<br/>
        <br/>
        <i>Este reporte fue generado automáticamente por el Sistema de Análisis Financiero.</i>
        """
        
        return Paragraph(texto, interpretacion_style)