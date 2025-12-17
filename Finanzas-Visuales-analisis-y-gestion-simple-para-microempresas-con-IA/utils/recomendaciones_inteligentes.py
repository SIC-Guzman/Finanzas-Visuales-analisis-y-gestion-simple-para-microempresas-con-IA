import math
from typing import Dict, List, Any

class GeneradorRecomendaciones:
    def __init__(self, resultados_analisis: Dict[str, Any]):
        """
        resultados_analisis debe contener:
        - resumen
        - resultados (horizontal, vertical, razones, punto_equilibrio)
        - resultados_ia
        - anomalias_financieras
        """
        self.resultados = resultados_analisis
        
    def generar_recomendaciones_accionables(self) -> List[Dict[str, str]]:
        """Genera recomendaciones específicas y accionables"""
        recomendaciones = []
        
        # 1. Recomendaciones basadas en ANOMALÍAS detectadas
        recomendaciones.extend(self._recomendaciones_por_anomalias())
        
        # 2. Recomendaciones basadas en RAZONES FINANCIERAS críticas
        recomendaciones.extend(self._recomendaciones_por_razones())
        
        # 3. Recomendaciones basadas en PUNTO DE EQUILIBRIO
        recomendaciones.extend(self._recomendaciones_por_equilibrio())
        
        # 4. Recomendaciones basadas en SIMULADOR DE CRISIS
        recomendaciones.extend(self._recomendaciones_por_crisis())
        
        # 5. Recomendaciones basadas en CRECIMIENTO
        recomendaciones.extend(self._recomendaciones_por_crecimiento())
        
        # Ordenar por prioridad (ROJO > AMARILLO > VERDE)
        return sorted(recomendaciones, key=lambda x: x.get('prioridad', 0), reverse=True)
    
    def _recomendaciones_por_anomalias(self) -> List[Dict[str, str]]:
        """Recomendaciones basadas en anomalías detectadas por IA"""
        recomendaciones = []
        anomalias = self.resultados.get('anomalias_financieras', {})
        
        if 'error' in anomalias or not anomalias.get('predicciones'):
            return recomendaciones
        
        for pred in anomalias.get('predicciones', []):
            riesgo = pred.get('riesgo', 'BAJO')
            prob = pred.get('prob', 0) * 100
            
            if riesgo == 'ALTO' and prob > 70:
                rec = {
                    'titulo': '⚠️ ANOMALÍA CRÍTICA DETECTADA',
                    'descripcion': f'Se detectó anomalía con {prob:.1f}% de probabilidad. Riesgo: ALTO',
                    'accion': 'Revisión inmediata de libros contables y conciliación bancaria urgente.',
                    'plazo': 'INMEDIATO (48 horas)',
                    'impacto': 'EVITAR FRAUDE O ERROR CONTABLE',
                    'prioridad': 100  # Máxima prioridad
                }
                recomendaciones.append(rec)
            
            elif riesgo == 'MEDIO':
                rec = {
                    'titulo': '⚠️ COMPORTAMIENTO ATÍPICO',
                    'descripcion': f'Variación anormal detectada ({prob:.1f}% probabilidad)',
                    'accion': 'Auditoría interna del trimestre afectado.',
                    'plazo': '1 SEMANA',
                    'impacto': 'PREVENIR PROBLEMAS FUTUROS',
                    'prioridad': 70
                }
                recomendaciones.append(rec)
        
        return recomendaciones
    
    def _recomendaciones_por_razones(self) -> List[Dict[str, str]]:
        """Recomendaciones basadas en razones financieras fuera de rango"""
        recomendaciones = []
        razones = self.resultados.get('resultados', {}).get('razones', {})
        
        # LIQUIDEZ CRÍTICA
        liquidez = razones.get('liquidez_corriente', 0)
        if liquidez < 1.0:
            deficit = max(0, (1.5 - liquidez) * 1000)  # Estimación en Q
            rec = {
                'titulo': '🚨 LIQUIDEZ EN RIESGO',
                'descripcion': f'Liquidez actual: {liquidez:.2f} (meta: >1.5)',
                'accion': f'Necesitas generar Q{deficit:,.0f} de efectivo adicional para cubrir deudas corto plazo.',
                'como': '1. Cobrar cuentas pendientes 2. Vender inventario obsoleto 3. Negociar plazo con proveedores',
                'plazo': '15 DÍAS',
                'prioridad': 90
            }
            recomendaciones.append(rec)
        
        # ENDEUDAMIENTO ALTO
        endeudamiento = razones.get('endeudamiento', 0)
        if endeudamiento > 60:
            rec = {
                'titulo': '💰 ENDEUDAMIENTO PELIGROSO',
                'descripcion': f'Endeudamiento: {endeudamiento:.1f}% (meta: <60%)',
                'accion': 'EVITAR TOMAR MÁS DEUDA ESTE TRIMESTRE.',
                'como': '1. Reestructurar deuda existente 2. Usar utilidades para pagar 3. Buscar inversionista en lugar de préstamo',
                'plazo': 'INMEDIATO',
                'impacto': 'Reducir riesgo de insolvencia',
                'prioridad': 85
            }
            recomendaciones.append(rec)
        
        # RENTABILIDAD BAJA
        roa = razones.get('roa', 0)
        if roa < 5:
            rec = {
                'titulo': '📉 RENTABILIDAD INSUFICIENTE',
                'descripcion': f'ROA: {roa:.1f}% (meta: >10%)',
                'accion': f'Necesitas aumentar utilidades en al menos {abs(roa-10):.1f}%',
                'como': '1. Revisar precios de venta 2. Reducir costos variables 3. Eliminar productos no rentables',
                'plazo': 'PRÓXIMO TRIMESTRE',
                'prioridad': 75
            }
            recomendaciones.append(rec)
        
        return recomendaciones
    
    def _recomendaciones_por_equilibrio(self) -> List[Dict[str, str]]:
        """Recomendaciones basadas en punto de equilibrio"""
        recomendaciones = []
        equilibrio = self.resultados.get('resultados', {}).get('punto_equilibrio', {})
        
        if not equilibrio:
            return recomendaciones
        
        margen_seg = equilibrio.get('margen_seguridad_porcentaje', 0)
        ventas_actuales = equilibrio.get('ventas_actuales', 0)
        punto_eq = equilibrio.get('punto_equilibrio_dolares', 0)
        
        # MARGEN DE SEGURIDAD BAJO
        if margen_seg < 15:
            deficit = punto_eq - ventas_actuales if ventas_actuales < punto_eq else 0
            
            if deficit > 0:
                rec = {
                    'titulo': '⚖️ PELIGRO: OPERANDO CON PÉRDIDAS',
                    'descripcion': f'Ventas actuales: Q{ventas_actuales:,.0f} < Punto equilibrio: Q{punto_eq:,.0f}',
                    'accion': f'URGENTE: Aumentar ventas en Q{deficit:,.0f} para cubrir costos fijos.',
                    'como': f'1. Incrementar precio un {(deficit/ventas_actuales*100):.1f}% 2. Vender {(deficit/equilibrio.get("precio_venta",1)):.0f} unidades más 3. Reducir costos fijos',
                    'plazo': '30 DÍAS',
                    'prioridad': 95
                }
            else:
                rec = {
                    'titulo': '⚠️ MARGEN DE SEGURIDAD AJUSTADO',
                    'descripcion': f'Margen de seguridad: {margen_seg:.1f}% (meta: >20%)',
                    'accion': f'Reducir costos fijos en al menos Q{ventas_actuales*0.05:,.0f} mensuales.',
                    'como': '1. Renegociar alquiler 2. Optimizar servicios 3. Reducir personal administrativo',
                    'plazo': '2 MESES',
                    'prioridad': 80
                }
            recomendaciones.append(rec)
        
        return recomendaciones
    
    def _recomendaciones_por_crisis(self) -> List[Dict[str, str]]:
        """Recomendaciones basadas en simulador de crisis"""
        recomendaciones = []
        resultados_ia = self.resultados.get('resultados_ia', {})
        resumen_ia = resultados_ia.get('resumen', {})
        
        if resumen_ia.get('sobrevive_crisis') == 'No sobrevive':
            rec = {
                'titulo': '🔥 CRISIS FINANCIERA INMINENTE',
                'descripcion': 'La empresa NO sobrevive a una caída del 20% en ventas',
                'accion': 'PLAN DE EMERGENCIA: Reducir costos fijos en al menos 30% de inmediato.',
                'como': '1. Suspender gastos no esenciales 2. Reducir inventario 3. Renegociar TODAS las deudas',
                'plazo': 'INMEDIATO',
                'impacto': 'SALVAR LA EMPRESA',
                'prioridad': 100
            }
            recomendaciones.append(rec)
        
        return recomendaciones
    
    def _recomendaciones_por_crecimiento(self) -> List[Dict[str, str]]:
        """Recomendaciones para mejorar crecimiento"""
        recomendaciones = []
        horizontal = self.resultados.get('resultados', {}).get('horizontal', {})
        
        # CRECIMIENTO DE VENTAS
        ventas = horizontal.get('Ventas totales', {})
        crecimiento = ventas.get('variacion_porcentual', 0) if ventas else 0
        
        if crecimiento < 5:
            rec = {
                'titulo': '📊 CRECIMIENTO ESTANCADO',
                'descripcion': f'Crecimiento ventas: {crecimiento:.1f}% (meta: >15%)',
                'accion': f'Implementar estrategia de marketing que aumente ventas en al menos 10% este trimestre.',
                'como': '1. Campaña en redes sociales 2. Programa de referidos 3. Ofertas por temporada',
                'plazo': '60 DÍAS',
                'prioridad': 65
            }
            recomendaciones.append(rec)
        
        # CONTROL DE COSTOS
        costo_ventas = horizontal.get('Costo de ventas', {})
        crecimiento_costos = costo_ventas.get('variacion_porcentual', 0) if costo_ventas else 0
        
        if crecimiento_costos > crecimiento and crecimiento_costos > 10:
            rec = {
                'titulo': '💸 COSTOS DESCONTROLADOS',
                'descripcion': f'Costos crecen {crecimiento_costos:.1f}% vs ventas {crecimiento:.1f}%',
                'accion': f'Reducir gastos operativos en al menos {crecimiento_costos-crecimiento:.1f}%',
                'como': '1. Buscar proveedores alternativos 2. Optimizar procesos 3. Reducir desperdicio',
                'plazo': '30 DÍAS',
                'prioridad': 75
            }
            recomendaciones.append(rec)
        
        return recomendaciones
    
    def resumen_recomendaciones(self) -> Dict[str, Any]:
        """Genera un resumen ejecutivo de recomendaciones"""
        todas_recomendaciones = self.generar_recomendaciones_accionables()
        
        # Contar por prioridad
        criticas = len([r for r in todas_recomendaciones if r.get('prioridad', 0) >= 80])
        urgentes = len([r for r in todas_recomendaciones if 60 <= r.get('prioridad', 0) < 80])
        sugerencias = len([r for r in todas_recomendaciones if r.get('prioridad', 0) < 60])
        
        # Principales acciones
        acciones_principales = []
        for rec in todas_recomendaciones[:3]:  # Top 3
            acciones_principales.append({
                'titulo': rec['titulo'],
                'accion_principal': rec['accion'],
                'plazo': rec.get('plazo', 'N/A')
            })
        
        return {
            'total_recomendaciones': len(todas_recomendaciones),
            'criticas': criticas,
            'urgentes': urgentes,
            'sugerencias': sugerencias,
            'recomendaciones': todas_recomendaciones,
            'acciones_principales': acciones_principales,
            'resumen': self._generar_resumen_texto(todas_recomendaciones)
        }
    
    def _generar_resumen_texto(self, recomendaciones: List[Dict]) -> str:
        """Genera texto de resumen ejecutivo"""
        if not recomendaciones:
            return "✅ La empresa presenta una situación financiera estable. Continúa con las prácticas actuales."
        
        criticas = [r for r in recomendaciones if r.get('prioridad', 0) >= 80]
        
        if criticas:
            return f"🚨 ALERTA: Se detectaron {len(criticas)} problemas CRÍTICOS que requieren atención inmediata. La empresa está en riesgo financiero."
        else:
            return f"⚠️ Se identificaron {len(recomendaciones)} áreas de mejora. Se recomienda implementar las acciones sugeridas para optimizar el desempeño financiero."