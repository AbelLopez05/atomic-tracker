"""
Sistema de Gamificación - Niveles, Badges y Logros
Basado en filosofía de Hábitos Atómicos
"""

from typing import Dict, List, Tuple

# Definición de niveles
NIVELES = {
    1: {"nombre": "🌱 Novato", "puntos_requeridos": 0, "descripcion": "Iniciando el cambio"},
    2: {"nombre": "⚡ Disciplinado", "puntos_requeridos": 100, "descripcion": "Formando el hábito"},
    3: {"nombre": "🔥 Ingeniero Atómico", "puntos_requeridos": 500, "descripcion": "1% mejor cada día"},
    4: {"nombre": "💎 Maestro de Hábitos", "puntos_requeridos": 1500, "descripcion": "La identidad se alinea"},
    5: {"nombre": "🏆 Leyenda", "puntos_requeridos": 5000, "descripcion": "Transformación completa"}
}

# Definición de badges/logros
BADGES = {
    "primera_victoria": {
        "emoji": "🎯",
        "nombre": "Primera Victoria",
        "descripcion": "Completaste tu primer día",
        "criterio": lambda perfil: perfil.get('dias_activos', 0) >= 1
    },
    "semana_perfecta": {
        "emoji": "⭐",
        "nombre": "Semana Perfecta",
        "descripcion": "7 días seguidos >85%",
        "criterio": lambda perfil: perfil.get('racha_perfecta', 0) >= 7
    },
    "mes_consistente": {
        "emoji": "🥈",
        "nombre": "Mes Consistente",
        "descripcion": "30 días activos",
        "criterio": lambda perfil: perfil.get('dias_activos', 0) >= 30
    },
    "guerrero_matutino": {
        "emoji": "🌅",
        "nombre": "Guerrero Matutino",
        "descripcion": "30 días sin tocar celular al despertar",
        "criterio": lambda perfil: perfil.get('racha_cero_celular', 0) >= 30
    },
    "ingeniero_atomico": {
        "emoji": "⚡",
        "nombre": "Ingeniero Atómico",
        "descripcion": "90 días de transformación",
        "criterio": lambda perfil: perfil.get('dias_activos', 0) >= 90
    },
    "pureza_mental": {
        "emoji": "🧠",
        "nombre": "Pureza Mental",
        "descripcion": "30 días racha Cero Porno",
        "criterio": lambda perfil: perfil.get('racha_cero_porno', 0) >= 30
    },
    "domador_del_dota": {
        "emoji": "🎮",
        "nombre": "Domador del Dota",
        "descripcion": "30 días haciendo ejercicio antes de jugar",
        "criterio": lambda perfil: perfil.get('racha_peaje_ejercicio', 0) >= 30
    },
    "crecimiento_muscular": {
        "emoji": "💪",
        "nombre": "Protocolo de Crecimiento",
        "descripcion": "30 días durmiendo antes de 22:30",
        "criterio": lambda perfil: perfil.get('racha_dormir_temprano', 0) >= 30
    },
    "ano_leyenda": {
        "emoji": "💎",
        "nombre": "Año Legendario",
        "descripcion": "365 días de disciplina",
        "criterio": lambda perfil: perfil.get('dias_activos', 0) >= 365
    }
}

class GamificationSystem:
    """Sistema de gamificación y progresión del usuario"""
    
    @staticmethod
    def calcular_nivel(puntos_totales: int) -> Tuple[int, Dict]:
        """
        Calcula el nivel actual basado en puntos totales
        Retorna: (nivel_actual, info_nivel)
        """
        nivel_actual = 1
        for nivel, info in sorted(NIVELES.items(), reverse=True):
            if puntos_totales >= info['puntos_requeridos']:
                nivel_actual = nivel
                break
        
        return nivel_actual, NIVELES[nivel_actual]
    
    @staticmethod
    def calcular_progreso_nivel(puntos_totales: int) -> Dict:
        """
        Calcula el progreso hacia el siguiente nivel
        Retorna: {nivel_actual, puntos_actuales, puntos_siguiente_nivel, porcentaje}
        """
        nivel_actual, info_actual = GamificationSystem.calcular_nivel(puntos_totales)
        
        # Si es nivel máximo
        if nivel_actual == max(NIVELES.keys()):
            return {
                'nivel': nivel_actual,
                'puntos_actuales': puntos_totales,
                'puntos_siguiente_nivel': puntos_totales,
                'porcentaje': 100,
                'es_nivel_maximo': True
            }
        
        # Calcular progreso al siguiente nivel
        puntos_nivel_actual = NIVELES[nivel_actual]['puntos_requeridos']
        puntos_siguiente_nivel = NIVELES[nivel_actual + 1]['puntos_requeridos']
        
        puntos_en_nivel = puntos_totales - puntos_nivel_actual
        puntos_necesarios = puntos_siguiente_nivel - puntos_nivel_actual
        porcentaje = (puntos_en_nivel / puntos_necesarios * 100) if puntos_necesarios > 0 else 0
        
        return {
            'nivel': nivel_actual,
            'nombre_nivel': info_actual['nombre'],
            'puntos_actuales': puntos_totales,
            'puntos_siguiente_nivel': puntos_siguiente_nivel,
            'porcentaje': porcentaje,
            'es_nivel_maximo': False
        }
    
    @staticmethod
    def obtener_badges_desbloqueados(perfil: Dict) -> List[Dict]:
        """
        Verifica qué badges ha desbloqueado el usuario
        Retorna: lista de badges desbloqueados
        """
        badges_desbloqueados = []
        
        for badge_id, badge_info in BADGES.items():
            if badge_info['criterio'](perfil):
                badges_desbloqueados.append({
                    'id': badge_id,
                    'emoji': badge_info['emoji'],
                    'nombre': badge_info['nombre'],
                    'descripcion': badge_info['descripcion']
                })
        
        return badges_desbloqueados
    
    @staticmethod
    def obtener_proximo_badge(perfil: Dict) -> Dict:
        """
        Encuentra el próximo badge alcanzable
        Retorna: info del próximo badge o None
        """
        badges_pendientes = []
        
        for badge_id, badge_info in BADGES.items():
            if not badge_info['criterio'](perfil):
                badges_pendientes.append({
                    'id': badge_id,
                    'emoji': badge_info['emoji'],
                    'nombre': badge_info['nombre'],
                    'descripcion': badge_info['descripcion']
                })
        
        # Retornar el primero (más cercano)
        return badges_pendientes[0] if badges_pendientes else None
    
    @staticmethod
    def generar_mensaje_motivacional(porcentaje_dia: float, racha: int) -> str:
        """
        Genera mensajes motivacionales basados en el progreso
        """
        if porcentaje_dia >= 100:
            mensajes = [
                "🏆 ¡DÍA PERFECTO! Tu sistema está funcionando.",
                "💎 Así se forja un Ingeniero Atómico.",
                "🔥 Tu yo del futuro te agradece este esfuerzo."
            ]
        elif porcentaje_dia >= 85:
            mensajes = [
                "⚡ ¡Meta cumplida! El frío no te venció.",
                "🎯 La consistencia es tu nueva identidad.",
                "💪 Ganaste el día. Ahora disfruta tu Dota sin culpa."
            ]
        elif porcentaje_dia >= 60:
            mensajes = [
                "👍 Vas bien, pero puedes dar más.",
                "📈 Aún estás a tiempo de llegar al 85%.",
                "🌱 Cada hábito cuenta. ¿Qué te falta marcar?"
            ]
        elif porcentaje_dia >= 30:
            mensajes = [
                "⚠️ Alerta temprana. ¿El frío te ganó?",
                "💡 Recuerda: El sistema funciona si tú lo haces funcionar.",
                "🔔 No dejes que un mal día se convierta en semana."
            ]
        else:
            mensajes = [
                "🆘 Día difícil detectado. Mañana resetea con el protocolo anti-frío.",
                "💭 Los malos días enseñan. ¿Qué falló en tu sistema?",
                "🌅 El sol saldrá mañana. Prepara tu casaca y vuelve a empezar."
            ]
        
        # Agregar mención de racha si es significativa
        if racha >= 30:
            return mensajes[0] + f" | 🔥 ¡{racha} días imparable!"
        elif racha >= 7:
            return mensajes[0] + f" | ⭐ {racha} días consecutivos. Vas en serio."
        
        return mensajes[0]
    
    @staticmethod
    def analizar_mejor_momento_dia(habitos_completados: List[Dict]) -> str:
        """
        Analiza en qué momento del día el usuario es más productivo
        """
        if not habitos_completados:
            return "Sin datos suficientes"
        
        # Analizar bloques más completados
        bloques_count = {}
        for habito in habitos_completados:
            bloque = habito.get('bloque_id', 'unknown')
            bloques_count[bloque] = bloques_count.get(bloque, 0) + 1
        
        mejor_bloque = max(bloques_count, key=bloques_count.get) if bloques_count else "unknown"
        
        bloques_nombres = {
            'manana': '🌅 Mañana',
            'salud': '💪 Salud',
            'mente': '🧠 Mente',
            'ocio': '🎮 Ocio'
        }
        
        return bloques_nombres.get(mejor_bloque, "Indefinido")