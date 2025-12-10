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
        
        print(f"📊 PDF Generator inicializado:")
        print(f"   - Claves en report_data: {list(self.report_data.keys())}")
        print(f"   - ¿Tiene 'resumen'?: {'resumen' in self.report_data}")
        
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
            
            # 2. INSIGHTS AUTOMÁTICOS (ahora al principio)
            if 'insights' in self.report_data:
                story.append(self._crear_seccion_insights(styles))
                story.append(Spacer(1, 15))
            
            # 3. ANÁLISIS HORIZONTAL
            story.append(self._crear_seccion_horizontal(styles))
            story.append(Spacer(1, 15))
            
            # 4. ANÁLISIS VERTICAL
            story.append(self._crear_seccion_vertical(styles))
            story.append(Spacer(1, 15))
            
            # 5. RAZONES FINANCIERAS
            story.append(self._crear_seccion_razones(styles))
            story.append(Spacer(1, 15))
            
            # 6. PUNTO DE EQUILIBRIO
            if self.report_data['resultados']['punto_equilibrio']:
                story.append(self._crear_seccion_equilibrio(styles))
                story.append(Spacer(1, 15))
            
            # 7. PREDICCIONES IA
            if 'resultados_ia' in self.report_data:
                story.append(self._crear_seccion_predicciones(styles))
                story.append(Spacer(1, 15))
            
            # 8. ANOMALÍAS FINANCIERAS
            if 'anomalias_financieras' in self.report_data:
                story.append(self._crear_seccion_anomalias(styles))
                story.append(Spacer(1, 15))
            
            # 9. INTERPRETACIÓN FINAL
            story.append(self._crear_seccion_interpretacion(styles))
            
            # Construir PDF
            doc.build(story)
            
            return output_filename
            
        except Exception as e:
            print(f"Error generando PDF: {e}")
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