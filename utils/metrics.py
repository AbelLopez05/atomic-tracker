"""
Sistema de Métricas y Análisis
Calcula KPIs y estadísticas del progreso
"""

from datetime import date, timedelta
from typing import Dict, List
import statistics


class MetricsCalculator:
    """Calcula métricas y estadísticas de progreso"""
    
    @staticmethod
    def calcular_porcentaje_semanal(historico: List[Dict], meta: float = 85.0) -> Dict:
        """
        Calcula el porcentaje de días que cumplen la meta semanal
        
        Args:
            historico: Lista de registros diarios
            meta: Meta de porcentaje diario (default 85%)
        
        Returns:
            Dict con estadísticas semanales
        """
        if not historico:
            return {
                'dias_meta_cumplida': 0,
                'total_dias': 0,
                'porcentaje_exito': 0.0,
                'dias_faltantes': 7
            }
        
        # Filtrar últimos 7 días
        hoy = date.today()
        fecha_inicio = hoy - timedelta(days=6)  # Últimos 7 días incluyendo hoy
        
        registros_semana = [
            r for r in historico
            if date.fromisoformat(r['fecha']) >= fecha_inicio
        ]
        
        dias_meta = sum(1 for r in registros_semana if r['porcentaje_cumplimiento'] >= meta)
        total_dias = len(registros_semana)
        porcentaje = (dias_meta / 7 * 100) if total_dias > 0 else 0
        
        return {
            'dias_meta_cumplida': dias_meta,
            'total_dias': total_dias,
            'porcentaje_exito': porcentaje,
            'dias_faltantes': 7 - dias_meta,
            'cumple_meta_semanal': dias_meta >= 6  # 6 de 7 días
        }
    
    @staticmethod
    def calcular_racha_perfecta(historico: List[Dict], meta: float = 85.0) -> int:
        """
        Calcula la racha actual de días consecutivos cumpliendo la meta
        
        Args:
            historico: Lista de registros ordenados por fecha DESC
            meta: Meta de porcentaje diario
        
        Returns:
            Número de días en racha
        """
        if not historico:
            return 0
        
        racha = 0
        hoy = date.today()
        
        # Ordenar por fecha descendente
        registros_ordenados = sorted(
            historico,
            key=lambda x: x['fecha'],
            reverse=True
        )
        
        # Contar días consecutivos desde hoy hacia atrás
        fecha_esperada = hoy
        for registro in registros_ordenados:
            fecha_registro = date.fromisoformat(registro['fecha'])
            
            # Si hay gap en las fechas, terminar racha
            if fecha_registro != fecha_esperada:
                break
            
            # Si cumple la meta, aumentar racha
            if registro['porcentaje_cumplimiento'] >= meta:
                racha += 1
                fecha_esperada = fecha_registro - timedelta(days=1)
            else:
                break
        
        return racha
    
    @staticmethod
    def analizar_tendencia(historico: List[Dict], ventana: int = 7) -> str:
        """
        Analiza la tendencia de progreso (subiendo/bajando/estable)
        
        Args:
            historico: Lista de registros
            ventana: Tamaño de ventana para comparar
        
        Returns:
            "subiendo", "bajando" o "estable"
        """
        if len(historico) < ventana * 2:
            return "insuficiente_datos"
        
        # Ordenar por fecha
        registros_ordenados = sorted(historico, key=lambda x: x['fecha'])
        
        # Comparar promedio de primera mitad vs segunda mitad
        mitad = len(registros_ordenados) // 2
        primera_mitad = registros_ordenados[:mitad]
        segunda_mitad = registros_ordenados[mitad:]
        
        promedio_primera = statistics.mean(r['porcentaje_cumplimiento'] for r in primera_mitad)
        promedio_segunda = statistics.mean(r['porcentaje_cumplimiento'] for r in segunda_mitad)
        
        diferencia = promedio_segunda - promedio_primera
        
        if diferencia > 5:
            return "📈 Subiendo"
        elif diferencia < -5:
            return "📉 Bajando"
        else:
            return "➡️ Estable"
    
    @staticmethod
    def calcular_estadisticas_generales(historico: List[Dict]) -> Dict:
        """
        Calcula estadísticas generales del historial
        
        Returns:
            Dict con múltiples métricas
        """
        if not historico:
            return {
                'promedio_cumplimiento': 0.0,
                'mejor_dia': 0.0,
                'peor_dia': 0.0,
                'desviacion_estandar': 0.0,
                'total_dias': 0
            }
        
        porcentajes = [r['porcentaje_cumplimiento'] for r in historico]
        
        return {
            'promedio_cumplimiento': statistics.mean(porcentajes),
            'mejor_dia': max(porcentajes),
            'peor_dia': min(porcentajes),
            'desviacion_estandar': statistics.stdev(porcentajes) if len(porcentajes) > 1 else 0,
            'total_dias': len(historico),
            'mediana': statistics.median(porcentajes)
        }
    
    @staticmethod
    def predecir_cumplimiento_semanal(historico: List[Dict], meta: float = 85.0) -> Dict:
        """
        Predice si se cumplirá la meta semanal basado en el progreso actual
        
        Returns:
            Dict con predicción y mensaje
        """
        stats_semana = MetricsCalculator.calcular_porcentaje_semanal(historico, meta)
        
        dias_cumplidos = stats_semana['dias_meta_cumplida']
        dias_restantes = 7 - stats_semana['total_dias']
        
        # Para cumplir meta semanal necesitas 6 de 7 días
        dias_necesarios = 6 - dias_cumplidos
        
        if dias_cumplidos >= 6:
            return {
                'cumplira': True,
                'mensaje': "✅ ¡Meta semanal asegurada!",
                'confianza': "alta"
            }
        elif dias_necesarios <= dias_restantes:
            return {
                'cumplira': True,
                'mensaje': f"⚡ Vas bien. Necesitas {dias_necesarios} día(s) más.",
                'confianza': "media"
            }
        else:
            return {
                'cumplira': False,
                'mensaje': "⚠️ Difícil cumplir meta. ¡Da el máximo!",
                'confianza': "baja"
            }