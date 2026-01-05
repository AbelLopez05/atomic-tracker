"""
Sistema de Reportes Avanzados
Genera análisis diario, semanal, mensual, trimestral, semestral y anual
"""

import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, List, Tuple
import calendar


class ReportGenerator:
    """Generador de reportes avanzados para análisis temporal"""
    
    DIAS_ES = {
        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
        'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    
    MESES_ES = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    @staticmethod
    def generar_reporte_diario(db, fecha: date) -> Dict:
        """
        Genera reporte completo del día
        
        Returns:
            Dict con métricas, hábitos completados, y análisis
        """
        metricas = db.obtener_metricas_dia(fecha)
        habitos_completados = db.obtener_habitos_dia(fecha)
        
        # Calcular estadísticas
        total_habitos_posibles = 16  # Actualizar según tu config
        habitos_completados_count = len(habitos_completados)
        
        return {
            'fecha': fecha.isoformat(),
            'dia_semana': self.DIAS_ES[fecha.strftime('%A')],
            'puntos': metricas['puntos'],
            'porcentaje': metricas['porcentaje'],
            'habitos_completados': habitos_completados_count,
            'habitos_totales': total_habitos_posibles,
            'tasa_cumplimiento': (habitos_completados_count / total_habitos_posibles * 100) if total_habitos_posibles > 0 else 0,
            'habitos_lista': habitos_completados,
            'meta_alcanzada': metricas['porcentaje'] >= 85
        }
    
    @staticmethod
    def generar_reporte_semanal(db, fecha_fin: date = None) -> Dict:
        """
        Genera reporte de la semana actual o especificada
        
        Args:
            fecha_fin: Último día de la semana (default: hoy)
        
        Returns:
            Dict con estadísticas semanales
        """
        if fecha_fin is None:
            fecha_fin = date.today()
        
        # Calcular inicio de semana (lunes)
        dias_desde_lunes = fecha_fin.weekday()
        fecha_inicio = fecha_fin - timedelta(days=dias_desde_lunes)
        
        # Obtener datos de la semana
        historico = db.obtener_historico(dias=90)
        df = pd.DataFrame(historico)
        
        if df.empty:
            return ReportGenerator._reporte_vacio('semanal')
        
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Filtrar semana actual
        mask = (df['fecha'] >= pd.Timestamp(fecha_inicio)) & (df['fecha'] <= pd.Timestamp(fecha_fin))
        semana_data = df[mask]
        
        if semana_data.empty:
            return ReportGenerator._reporte_vacio('semanal')
        
        # Calcular métricas
        dias_meta = (semana_data['porcentaje_cumplimiento'] >= 85).sum()
        promedio = semana_data['porcentaje_cumplimiento'].mean()
        mejor_dia = semana_data.loc[semana_data['porcentaje_cumplimiento'].idxmax()]
        peor_dia = semana_data.loc[semana_data['porcentaje_cumplimiento'].idxmin()]
        
        return {
            'periodo': f"Semana {fecha_inicio.day}/{fecha_inicio.month} - {fecha_fin.day}/{fecha_fin.month}/{fecha_fin.year}",
            'dias_registrados': len(semana_data),
            'dias_meta_cumplida': int(dias_meta),
            'promedio_porcentaje': round(promedio, 1),
            'total_puntos': int(semana_data['puntos_totales'].sum()),
            'mejor_dia': {
                'fecha': f"{self.DIAS_ES[mejor_dia['fecha'].strftime('%A')]} {mejor_dia['fecha'].day}/{mejor_dia['fecha'].month}",
                'porcentaje': round(mejor_dia['porcentaje_cumplimiento'], 1)
            },
            'peor_dia': {
                'fecha': f"{self.DIAS_ES[peor_dia['fecha'].strftime('%A')]} {peor_dia['fecha'].day}/{peor_dia['fecha'].month}",
                'porcentaje': round(peor_dia['porcentaje_cumplimiento'], 1)
            },
            'meta_semanal_cumplida': int(dias_meta) >= 6,
            'datos_diarios': semana_data.to_dict('records')
        }
    
    @staticmethod
    def generar_reporte_mensual(db, año: int = None, mes: int = None) -> Dict:
        """
        Genera reporte del mes actual o especificado
        
        Args:
            año: Año del reporte (default: actual)
            mes: Mes del reporte (default: actual)
        
        Returns:
            Dict con estadísticas mensuales
        """
        if año is None or mes is None:
            hoy = date.today()
            año = hoy.year
            mes = hoy.month
        
        # Obtener primer y último día del mes
        primer_dia = date(año, mes, 1)
        ultimo_dia = date(año, mes, calendar.monthrange(año, mes)[1])
        
        # Obtener datos
        historico = db.obtener_historico(dias=90)
        df = pd.DataFrame(historico)
        
        if df.empty:
            return ReportGenerator._reporte_vacio('mensual')
        
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Filtrar mes
        mask = (df['fecha'] >= pd.Timestamp(primer_dia)) & (df['fecha'] <= pd.Timestamp(ultimo_dia))
        mes_data = df[mask]
        
        if mes_data.empty:
            return ReportGenerator._reporte_vacio('mensual')
        
        # Calcular métricas
        dias_meta = (mes_data['porcentaje_cumplimiento'] >= 85).sum()
        promedio = mes_data['porcentaje_cumplimiento'].mean()
        
        # Análisis por semana
        mes_data['semana'] = mes_data['fecha'].dt.isocalendar().week
        por_semana = mes_data.groupby('semana')['porcentaje_cumplimiento'].mean()
        
        return {
        return {
            'periodo': f"{self.MESES_ES[mes]} {año}",
            'mes': mes,
            'año': año,
            'dias_registrados': len(mes_data),
            'dias_meta_cumplida': int(dias_meta),
            'promedio_porcentaje': round(promedio, 1),
            'total_puntos': int(mes_data['puntos_totales'].sum()),
            'porcentaje_dias_perfectos': round((dias_meta / len(mes_data) * 100), 1) if len(mes_data) > 0 else 0,
            'tendencia': ReportGenerator._calcular_tendencia(mes_data),
            'mejor_semana': int(por_semana.idxmax()) if not por_semana.empty else None,
            'promedio_por_semana': por_semana.to_dict() if not por_semana.empty else {},
            'datos_diarios': mes_data.to_dict('records')
        }
    
    @staticmethod
    def generar_reporte_trimestral(db, año: int = None, trimestre: int = None) -> Dict:
        """
        Genera reporte trimestral (Q1, Q2, Q3, Q4)
        
        Args:
            año: Año del reporte
            trimestre: 1, 2, 3 o 4
        
        Returns:
            Dict con estadísticas trimestrales
        """
        if año is None or trimestre is None:
            hoy = date.today()
            año = hoy.year
            trimestre = (hoy.month - 1) // 3 + 1
        
        # Calcular meses del trimestre
        mes_inicio = (trimestre - 1) * 3 + 1
        mes_fin = mes_inicio + 2
        
        primer_dia = date(año, mes_inicio, 1)
        ultimo_dia = date(año, mes_fin, calendar.monthrange(año, mes_fin)[1])
        
        # Obtener datos
        historico = db.obtener_historico(dias=180)
        df = pd.DataFrame(historico)
        
        if df.empty:
            return ReportGenerator._reporte_vacio('trimestral')
        
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Filtrar trimestre
        mask = (df['fecha'] >= pd.Timestamp(primer_dia)) & (df['fecha'] <= pd.Timestamp(ultimo_dia))
        trim_data = df[mask]
        
        if trim_data.empty:
            return ReportGenerator._reporte_vacio('trimestral')
        
        # Análisis por mes
        trim_data['mes'] = trim_data['fecha'].dt.month
        por_mes = trim_data.groupby('mes').agg({
            'porcentaje_cumplimiento': 'mean',
            'puntos_totales': 'sum'
        })
        
        dias_meta = (trim_data['porcentaje_cumplimiento'] >= 85).sum()
        
        return {
            'periodo': f"Q{trimestre} {año}",
            'trimestre': trimestre,
            'año': año,
            'meses': [self.MESES_ES[m] for m in range(mes_inicio, mes_fin + 1)],
            'dias_registrados': len(trim_data),
            'dias_meta_cumplida': int(dias_meta),
            'promedio_porcentaje': round(trim_data['porcentaje_cumplimiento'].mean(), 1),
            'total_puntos': int(trim_data['puntos_totales'].sum()),
            'mejor_mes': self.MESES_ES[int(por_mes['porcentaje_cumplimiento'].idxmax())] if not por_mes.empty else None,
            'promedio_por_mes': {self.MESES_ES[mes]: round(datos['porcentaje_cumplimiento'], 1) 
                                  for mes, datos in por_mes.iterrows()},
            'crecimiento': ReportGenerator._calcular_crecimiento_trimestral(trim_data)
        }
    
    @staticmethod
    def generar_reporte_semestral(db, año: int = None, semestre: int = None) -> Dict:
        """
        Genera reporte semestral (S1: Ene-Jun, S2: Jul-Dic)
        """
        if año is None or semestre is None:
            hoy = date.today()
            año = hoy.year
            semestre = 1 if hoy.month <= 6 else 2
        
        mes_inicio = 1 if semestre == 1 else 7
        mes_fin = 6 if semestre == 1 else 12
        
        primer_dia = date(año, mes_inicio, 1)
        ultimo_dia = date(año, mes_fin, calendar.monthrange(año, mes_fin)[1])
        
        historico = db.obtener_historico(dias=365)
        df = pd.DataFrame(historico)
        
        if df.empty:
            return ReportGenerator._reporte_vacio('semestral')
        
        df['fecha'] = pd.to_datetime(df['fecha'])
        mask = (df['fecha'] >= pd.Timestamp(primer_dia)) & (df['fecha'] <= pd.Timestamp(ultimo_dia))
        sem_data = df[mask]
        
        if sem_data.empty:
            return ReportGenerator._reporte_vacio('semestral')
        
        dias_meta = (sem_data['porcentaje_cumplimiento'] >= 85).sum()
        
        return {
            'periodo': f"Semestre {semestre} - {año}",
            'semestre': semestre,
            'año': año,
            'dias_registrados': len(sem_data),
            'dias_meta_cumplida': int(dias_meta),
            'promedio_porcentaje': round(sem_data['porcentaje_cumplimiento'].mean(), 1),
            'total_puntos': int(sem_data['puntos_totales'].sum()),
            'racha_maxima': ReportGenerator._calcular_racha_maxima(sem_data),
            'consistencia': round((dias_meta / len(sem_data) * 100), 1) if len(sem_data) > 0 else 0
        }
    
    @staticmethod
    def generar_reporte_anual(db, año: int = None) -> Dict:
        """
        Genera reporte anual completo
        """
        if año is None:
            año = date.today().year
        
        primer_dia = date(año, 1, 1)
        ultimo_dia = date(año, 12, 31)
        
        historico = db.obtener_historico(dias=400)
        df = pd.DataFrame(historico)
        
        if df.empty:
            return ReportGenerator._reporte_vacio('anual')
        
        df['fecha'] = pd.to_datetime(df['fecha'])
        mask = (df['fecha'] >= pd.Timestamp(primer_dia)) & (df['fecha'] <= pd.Timestamp(ultimo_dia))
        año_data = df[mask]
        
        if año_data.empty:
            return ReportGenerator._reporte_vacio('anual')
        
        # Análisis por mes
        año_data['mes'] = año_data['fecha'].dt.month
        por_mes = año_data.groupby('mes').agg({
            'porcentaje_cumplimiento': 'mean',
            'puntos_totales': 'sum'
        })
        
        dias_meta = (año_data['porcentaje_cumplimiento'] >= 85).sum()
        
        return {
            'periodo': f"Año {año}",
            'año': año,
            'dias_registrados': len(año_data),
            'dias_meta_cumplida': int(dias_meta),
            'promedio_porcentaje': round(año_data['porcentaje_cumplimiento'].mean(), 1),
            'total_puntos': int(año_data['puntos_totales'].sum()),
            'mejor_mes': self.MESES_ES[int(por_mes['porcentaje_cumplimiento'].idxmax())] if not por_mes.empty else None,
            'peor_mes': self.MESES_ES[int(por_mes['porcentaje_cumplimiento'].idxmin())] if not por_mes.empty else None,
            'racha_maxima_año': ReportGenerator._calcular_racha_maxima(año_data),
            'promedio_por_mes': {self.MESES_ES[mes]: round(datos['porcentaje_cumplimiento'], 1) 
                                  for mes, datos in por_mes.iterrows()},
            'transformacion': ReportGenerator._analizar_transformacion_anual(año_data)
        }
    
    # Métodos auxiliares
    
    @staticmethod
    def _reporte_vacio(tipo: str) -> Dict:
        """Retorna estructura de reporte vacío"""
        return {
            'periodo': f'{tipo.capitalize()} sin datos',
            'dias_registrados': 0,
            'mensaje': 'Completa más días para ver estadísticas'
        }
    
    @staticmethod
    def _calcular_tendencia(df: pd.DataFrame) -> str:
        """Calcula si la tendencia es ascendente, descendente o estable"""
        if len(df) < 7:
            return "Insuficiente datos"
        
        # Comparar primera y segunda mitad
        mitad = len(df) // 2
        primera_mitad = df.iloc[:mitad]['porcentaje_cumplimiento'].mean()
        segunda_mitad = df.iloc[mitad:]['porcentaje_cumplimiento'].mean()
        
        diferencia = segunda_mitad - primera_mitad
        
        if diferencia > 5:
            return "📈 Ascendente"
        elif diferencia < -5:
            return "📉 Descendente"
        else:
            return "➡️ Estable"
    
    @staticmethod
    def _calcular_racha_maxima(df: pd.DataFrame) -> int:
        """Calcula la racha máxima de días >85%"""
        if df.empty:
            return 0
        
        racha_actual = 0
        racha_maxima = 0
        
        df_sorted = df.sort_values('fecha')
        fecha_anterior = None
        
        for _, row in df_sorted.iterrows():
            fecha_actual = row['fecha'].date()
            
            if fecha_anterior is None or (fecha_actual - fecha_anterior).days == 1:
                if row['porcentaje_cumplimiento'] >= 85:
                    racha_actual += 1
                    racha_maxima = max(racha_maxima, racha_actual)
                else:
                    racha_actual = 0
            else:
                racha_actual = 1 if row['porcentaje_cumplimiento'] >= 85 else 0
            
            fecha_anterior = fecha_actual
        
        return racha_maxima
    
    @staticmethod
    def _calcular_crecimiento_trimestral(df: pd.DataFrame) -> Dict:
        """Analiza el crecimiento durante el trimestre"""
        if len(df) < 3:
            return {'mensaje': 'Insuficiente datos'}
        
        # Dividir en

        df_sorted = df.sort_values('fecha')
        df_sorted['mes'] = df_sorted['fecha'].dt.month
        crecimiento = {}
        meses = df_sorted['mes'].unique()
        
        for i in range(len(meses) - 1):
            mes_actual = df_sorted[df_sorted['mes'] == meses[i]]['porcentaje_cumplimiento'].mean()
            mes_siguiente = df_sorted[df_sorted['mes'] == meses[i+1]]['porcentaje_cumplimiento'].mean()
            diferencia = mes_siguiente - mes_actual
            crecimiento[f"Mes {i+1} a Mes {i+2}"] = f"{diferencia:+.1f}%"
        
        return crecimiento
    
    @staticmethod
    def _analizar_transformacion_anual(df: pd.DataFrame) -> str:
        """Analiza la transformación durante el año"""
        if len(df) < 30:
            return "Año en progreso"
        
        primer_mes = df[df['fecha'].dt.month == df['fecha'].dt.month.min()]['porcentaje_cumplimiento'].mean()
        ultimo_mes = df[df['fecha'].dt.month == df['fecha'].dt.month.max()]['porcentaje_cumplimiento'].mean()
        
        mejora = ultimo_mes - primer_mes
        
        if mejora > 20:
            return f"🚀 Transformación Extraordinaria (+{mejora:.1f}%)"
        elif mejora > 10:
            return f"⭐ Gran Mejora (+{mejora:.1f}%)"
        elif mejora > 0:
            return f"📈 Progreso Positivo (+{mejora:.1f}%)"
        else:
            return f"⚠️ Requiere ajustes ({mejora:.1f}%)"