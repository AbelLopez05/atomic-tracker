"""
ATOMIC ENGINEERING TRACKER
Sistema de seguimiento de hábitos personales basado en "Hábitos Atómicos"
Desarrollado para transformación personal y mejora continua del 1%

Author: Ingeniero de Sistemas
Stack: Python + Streamlit + SQLite
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta
import json
import os

# Imports locales
from database.db_manager import DatabaseManager
from utils.gamification import GamificationSystem, NIVELES
from utils.validators import HabitValidator
from utils.metrics import MetricsCalculator

# ===========================
# CONFIGURACIÓN DE LA PÁGINA
# ===========================

st.set_page_config(
    page_title="⚡ Atomic Tracker",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cargar CSS personalizado
def load_css():
    """Carga estilos CSS personalizados"""
    css_file = "assets/style.css"
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# CSS adicional para mobile optimization
st.markdown("""
<style>
    /* Ocultar menú de Streamlit y footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Reducir padding en mobile */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Mejorar legibilidad de métricas */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }
    
    /* Espaciado de checkboxes */
    .stCheckbox {
        margin: 0.5rem 0;
    }
    
    /* Botones más grandes para mobile */
    .stButton > button {
        width: 100%;
        padding: 0.75rem;
        font-size: 1.1rem;
        border-radius: 8px;
    }
    
    /* Divisores visuales */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# ===========================
# INICIALIZACIÓN
# ===========================

@st.cache_resource
def init_database():
    """Inicializa la conexión a la base de datos (singleton)"""
    return DatabaseManager()

@st.cache_data(ttl=3600)
def load_config():
    """Carga la configuración de hábitos desde JSON"""
    with open("config/habitos.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Instanciar objetos globales
db = init_database()
config = load_config()
validator = HabitValidator(config)
gamification = GamificationSystem()
metrics_calc = MetricsCalculator()

# ===========================
# ESTADO DE LA SESIÓN
# ===========================

if 'fecha_actual' not in st.session_state:
    st.session_state.fecha_actual = date.today()

if 'habitos_completados' not in st.session_state:
    st.session_state.habitos_completados = db.obtener_habitos_dia(st.session_state.fecha_actual)

if 'mostrar_estadisticas' not in st.session_state:
    st.session_state.mostrar_estadisticas = False

# ===========================
# FUNCIONES AUXILIARES
# ===========================

def calcular_puntos_maximos():
    """Calcula el total de puntos posibles en un día"""
    total = 0
    for bloque in config['bloques']:
        for habito in bloque['habitos']:
            # No contar Dota 2 porque da 0 puntos
            if habito['puntos'] > 0:
                total += habito['puntos']
    return total

PUNTOS_MAXIMOS = calcular_puntos_maximos()

def refrescar_habitos():
    """Recarga los hábitos completados del día desde la BD"""
    st.session_state.habitos_completados = db.obtener_habitos_dia(st.session_state.fecha_actual)

def toggle_habito(habito_id: str, bloque_id: str, puntos: int):
    """
    Marca o desmarca un hábito
    
    Args:
        habito_id: ID del hábito
        bloque_id: ID del bloque al que pertenece
        puntos: Puntos que otorga el hábito
    """
    fecha = st.session_state.fecha_actual
    habitos_actuales = st.session_state.habitos_completados
    
    if habito_id in habitos_actuales:
        # Desmarcar
        puede_desmarcar, mensaje = validator.validar_desmarcar_habito(habito_id, habitos_actuales)
        if puede_desmarcar:
            if db.desmarcar_habito(fecha, habito_id):
                if mensaje:
                    st.warning(mensaje)
                refrescar_habitos()
                st.rerun()
    else:
        # Marcar
        puede_marcar, mensaje_error = validator.puede_marcar_habito(habito_id, habitos_actuales)
        if puede_marcar:
            if db.marcar_habito(fecha, habito_id, bloque_id, puntos):
                refrescar_habitos()
                st.rerun()
        else:
            st.error(mensaje_error)
            st.stop()

def obtener_emoji_progreso(porcentaje: float) -> str:
    """Retorna emoji según el porcentaje de progreso"""
    if porcentaje >= 100:
        return "🏆"
    elif porcentaje >= 85:
        return "⚡"
    elif porcentaje >= 60:
        return "👍"
    elif porcentaje >= 30:
        return "⚠️"
    else:
        return "🆘"

def obtener_color_progreso(porcentaje: float) -> str:
    """Retorna color hex según el porcentaje"""
    if porcentaje >= 85:
        return "#00ff41"  # Verde
    elif porcentaje >= 60:
        return "#ff9800"  # Naranja
    else:
        return "#f44336"  # Rojo

# ===========================
# COMPONENTES UI
# ===========================

def render_header():
    """Renderiza el encabezado de la aplicación"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center;'>
            <h1 style='margin: 0; font-size: 2.5rem;'>⚡ ATOMIC ENGINEERING TRACKER</h1>
            <p style='color: #888; margin-top: 0.5rem;'>1% mejor cada día</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Fecha actual
    st.markdown(f"""
    <div style='text-align: center; margin: 1rem 0;'>
        <h3 style='color: #00ff41;'>📅 {st.session_state.fecha_actual.strftime('%A, %d de %B %Y')}</h3>
    </div>
    """, unsafe_allow_html=True)

def render_kpis_principales():
    """Renderiza los KPIs principales en la parte superior"""
    # Obtener métricas del día
    metricas_dia = db.obtener_metricas_dia(st.session_state.fecha_actual)
    porcentaje_dia = metricas_dia['porcentaje']
    puntos_dia = metricas_dia['puntos']
    
    # Obtener histórico para calcular racha
    historico = db.obtener_historico(dias=90)
    racha_perfecta = metrics_calc.calcular_racha_perfecta(historico, config['configuracion']['meta_diaria'])
    
    # Obtener perfil para nivel
    perfil = db.obtener_perfil()
    nivel_info = gamification.calcular_progreso_nivel(perfil.get('puntos_totales', 0))
    
    # Layout de KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        emoji = obtener_emoji_progreso(porcentaje_dia)
        st.metric(
            label=f"{emoji} Progreso Hoy",
            value=f"{porcentaje_dia:.1f}%",
            delta=f"Meta: {config['configuracion']['meta_diaria']}%"
        )
    
    with col2:
        st.metric(
            label="🔥 Racha Actual",
            value=f"{racha_perfecta} días",
            delta="Días consecutivos >85%"
        )
    
    with col3:
        st.metric(
            label="⭐ Puntos Hoy",
            value=f"{puntos_dia}/{PUNTOS_MAXIMOS}",
            delta=f"{PUNTOS_MAXIMOS - puntos_dia} restantes"
        )
    
    with col4:
        st.metric(
            label=f"{nivel_info['nombre_nivel']}",
            value=f"Nivel {nivel_info['nivel']}",
            delta=f"{nivel_info['porcentaje']:.0f}% al siguiente"
        )
    
    # Barra de progreso visual
    st.markdown("### 📊 Progreso del Día")
    color = obtener_color_progreso(porcentaje_dia)
    
    st.markdown(f"""
    <div style='background: #1e1e1e; border-radius: 15px; overflow: hidden; height: 40px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);'>
        <div style='
            width: {porcentaje_dia}%;
            height: 100%;
            background: linear-gradient(90deg, {color} 0%, {color}dd 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 1.2rem;
            transition: width 0.5s ease;
        '>
            {porcentaje_dia:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Mensaje motivacional
    mensaje = gamification.generar_mensaje_motivacional(porcentaje_dia, racha_perfecta)
    st.info(mensaje)

def render_alertas_sistema():
    """Muestra alertas inteligentes basadas en la hora y hábitos"""
    ahora = datetime.now()
    hora_actual = ahora.hour
    habitos_completados = st.session_state.habitos_completados
    
    # Alerta matutina (7-9 AM)
    if 7 <= hora_actual < 9:
        if 'despertar_protocolo_frio' not in habitos_completados:
            st.warning("⏰ **ALERTA MATUTINA**: ¿Ya hiciste el protocolo anti-frío? ¡Es tu ancla!")
        elif 'tender_cama' not in habitos_completados:
            st.info("🛏️ **Primera Victoria pendiente**: Tiende la cama. Es tu ritual.")
    
    # Alerta de enfoque (11 AM - 1 PM)
    elif 11 <= hora_actual < 13:
        if 'bloque_enfoque' not in habitos_completados:
            st.warning("📚 **Hora de Enfoque**: Celular fuera. 1 hora de estudio técnico.")
    
    # Alerta de trabajo profundo (2:30 PM - 6 PM)
    elif 14 <= hora_actual < 18:
        if 'bloque_proyectos' not in habitos_completados:
            st.error("🚀 **TRABAJO PROFUNDO**: ¡NO Dota/Netflix! Proyectos de ingeniería primero.")
    
    # Alerta del peaje (6 PM - 9 PM)
    elif 18 <= hora_actual < 21:
        if 'peaje_ejercicio' not in habitos_completados:
            st.error("💪 **¡PEAJE DEL DOTA!**: Sentadillas + Flexiones + Puente. Sin esto, NO hay juego.")
        elif 'peaje_ejercicio' in habitos_completados and 'dota2' not in habitos_completados:
            st.success("🎮 **Dota desbloqueado**: Te lo ganaste. Disfruta sin culpa.")
    
    # Alerta de apagado (9:30 PM en adelante)
    elif hora_actual >= 21:
        if 'protocolo_apagado' not in habitos_completados:
            st.warning("🌙 **Protocolo de Apagado**: Apaga PC. Prepara casaca. Celular lejos.")
        if hora_actual >= 22:
            st.error("⏰ **ALERTA CRÍTICA**: Ya son las 10 PM. Tu hormona de crecimiento espera. ¡A dormir!")

def render_bloque_habitos(bloque: dict):
    """
    Renderiza un bloque de hábitos con sus checkboxes
    
    Args:
        bloque: Diccionario con info del bloque
    """
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid {bloque['color']};
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    '>
        <h3 style='margin: 0; color: {bloque['color']};'>{bloque['nombre']}</h3>
        <p style='color: #888; margin: 0.3rem 0 0 0; font-size: 0.9rem;'>{bloque.get('subtitulo', '')}</p>
        <p style='color: #aaa; margin: 0.5rem 0 0 0;'>Identidad: <strong style='color: {bloque['color']};'>{bloque['identidad']}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    habitos_completados = st.session_state.habitos_completados
    habitos_bloqueados = validator.obtener_habitos_bloqueados(habitos_completados)
    
    for habito in bloque['habitos']:
        habito_id = habito['id']
        esta_completado = habito_id in habitos_completados
        esta_bloqueado = habito_id in habitos_bloqueados and not esta_completado
        es_privado = habito.get('privado', False)
        es_critico = habito.get('critico', False)
        
        # Crear columnas para checkbox y detalles
        col1, col2 = st.columns([0.08, 0.92])
        
        with col1:
            # Checkbox con key único
            checkbox_key = f"habit_{bloque['id']}_{habito_id}"
            
            if esta_bloqueado:
                st.checkbox(
                    label="🔒",
                    value=False,
                    disabled=True,
                    key=checkbox_key,
                    help="Completa los hábitos requeridos primero"
                )
            else:
                nuevo_estado = st.checkbox(
                    label="✓" if esta_completado else "○",
                    value=esta_completado,
                    key=checkbox_key,
                    label_visibility="collapsed"
                )
                
                # Detectar cambio de estado
                if nuevo_estado != esta_completado:
                    toggle_habito(habito_id, bloque['id'], habito['puntos'])
        
        with col2:
            # Mostrar nombre (ofuscado si es privado)
            nombre_display = habito['nombre'] if not es_privado else "🔒 Hábito Privado"
            
            # Indicador de criticidad
            icono_critico = "🔥" if es_critico else ""
            
            # Estilo según estado
            if esta_completado:
                st.markdown(f"""
                <div style='
                    background: rgba(0, 255, 65, 0.15);
                    padding: 0.9rem;
                    border-radius: 10px;
                    border-left: 4px solid #00ff41;
                    margin-bottom: 0.5rem;
                '>
                    <strong style='color: #00ff41; font-size: 1.05rem;'>✓ {icono_critico} {nombre_display}</strong><br>
                    <small style='color: #aaa; line-height: 1.5;'>{habito['descripcion'] if not es_privado else 'Progreso privado'}</small><br>
                    <small style='color: #00ff41; font-weight: bold;'>+{habito['puntos']} pts</small>
                </div>
                """, unsafe_allow_html=True)
            elif esta_bloqueado:
                st.markdown(f"""
                <div style='
                    background: rgba(255, 152, 0, 0.1);
                    padding: 0.9rem;
                    border-radius: 10px;
                    border-left: 4px solid #ff9800;
                    opacity: 0.7;
                    margin-bottom: 0.5rem;
                '>
                    <strong style='color: #ff9800; font-size: 1.05rem;'>🔒 {icono_critico} {nombre_display}</strong><br>
                    <small style='color: #888;'>Bloqueado - Completa los requisitos primero</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='
                    background: #1a1a1a;
                    padding: 0.9rem;
                    border-radius: 10px;
                    border-left: 4px solid #555;
                    transition: all 0.3s ease;
                    margin-bottom: 0.5rem;
                '>
                    <strong style='font-size: 1.05rem;'>{icono_critico} {nombre_display}</strong><br>
                    <small style='color: #888; line-height: 1.5;'>{habito['descripcion'] if not es_privado else 'Progreso privado'}</small><br>
                    <small style='color: #666;'>+{habito['puntos']} pts</small>
                </div>
                """, unsafe_allow_html=True)

def render_grafico_tendencia():
    """Renderiza gráfico de tendencia mensual"""
    historico = db.obtener_historico(dias=30)
    
    if not historico:
        st.info("📊 Completa al menos un día para ver el gráfico de tendencia")
        return
    
    # Preparar datos
    df = pd.DataFrame(historico)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df = df.sort_values('fecha')
    
    # Crear gráfico con Plotly
    fig = go.Figure()
    
    # Línea de progreso
    fig.add_trace(go.Scatter(
        x=df['fecha'],
        y=df['porcentaje_cumplimiento'],
        mode='lines+markers',
        name='% Cumplimiento',
        line=dict(color='#00ff41', width=3),
        marker=dict(size=8, color='#00ff41'),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 65, 0.1)'
    ))
    
    # Línea de meta
    fig.add_hline(
        y=config['configuracion']['meta_diaria'],
        line_dash="dash",
        line_color="orange",
        annotation_text=f"Meta: {config['configuracion']['meta_diaria']}%",
        annotation_position="right"
    )
    
    # Personalización
    fig.update_layout(
        title="📈 Tendencia de los Últimos 30 Días",
        xaxis_title="Fecha",
        yaxis_title="% Cumplimiento",
        template="plotly_dark",
        height=400,
        hovermode='x unified',
        showlegend=True,
        paper_bgcolor='#0e1117',
        plot_bgcolor='#1e1e1e'
    )
    
    fig.update_yaxes(range=[0, 110])
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Análisis de tendencia
    tendencia = metrics_calc.analizar_tendencia(historico)
    
    if tendencia == "📈 Subiendo":
        st.success(f"**{tendencia}** - ¡Excelente! Tu consistencia está mejorando.")
    elif tendencia == "📉 Bajando":
        st.warning(f"**{tendencia}** - Momento de ajustar. ¿Qué hábito necesita más atención?")
    else:
        st.info(f"**{tendencia}** - Mantén el ritmo.")

def render_estadisticas_avanzadas():
    """Renderiza panel de estadísticas avanzadas"""
    if not st.session_state.mostrar_estadisticas:
        if st.button("📊 Ver Estadísticas Avanzadas", use_container_width=True):
            st.session_state.mostrar_estadisticas = True
            st.rerun()
        return
    
    if st.button("✖️ Ocultar Estadísticas", use_container_width=True):
        st.session_state.mostrar_estadisticas = False
        st.rerun()
        return
    
    st.markdown("---")
    st.markdown("## 📊 Estadísticas Avanzadas")
    
    historico = db.obtener_historico(dias=90)
    
    if not historico:
        st.info("Completa más días para ver estadísticas")
        return
    
    # Estadísticas generales
    stats = metrics_calc.calcular_estadisticas_generales(historico)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Promedio General", f"{stats['promedio_cumplimiento']:.1f}%")
        st.metric("🏆 Mejor Día", f"{stats['mejor_dia']:.1f}%")
    
    with col2:
        st.metric("📉 Peor Día", f"{stats['peor_dia']:.1f}%")
        st.metric("📏 Desviación Estándar", f"{stats['desviacion_estandar']:.1f}%")
    
    with col3:
        st.metric("🗓️ Total Días Activos", stats['total_dias'])
        st.metric("📌 Mediana", f"{stats['mediana']:.1f}%")
    
    # Análisis semanal
    st.markdown("### 📅 Análisis Semanal")
    stats_semana = metrics_calc.calcular_porcentaje_semanal(historico)
    prediccion = metrics_calc.predecir_cumplimiento_semanal(historico)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Días >85% esta semana",
            f"{stats_semana['dias_meta_cumplida']}/7",
            delta="Meta: 6/7 días"
        )
    
    with col2:
        if prediccion['cumplira']:
            st.success(prediccion['mensaje'])
        else:
            st.warning(prediccion['mensaje'])
    
    # Racha por hábito crítico (Cero Porno)
    st.markdown("### 🏆 Rachas de Hábitos Críticos")
    
    for bloque in config['bloques']:
        for habito in bloque['habitos']:
            if habito.get('critico', False):
                racha_info = db.obtener_racha_habito(habito['id'])
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    nombre_display = "🔒 Hábito Privado" if habito.get('privado') else habito['nombre']
                    st.markdown(f"**{nombre_display}**")
                with col2:
                    st.metric("Racha", f"{racha_info['actual']} días")
    
    # Nivel y Progresión
    st.markdown("### ⭐ Progresión de Nivel")
    perfil = db.obtener_perfil()
    nivel_info = gamification.calcular_progreso_nivel(perfil.get('puntos_totales', 0))
    
    st.markdown(f"**Nivel Actual:** {nivel_info['nombre_nivel']}")
    st.progress(nivel_info['porcentaje'] / 100)
    st.caption(f"Faltan {nivel_info['puntos_siguiente_nivel'] - nivel_info['puntos_actuales']} puntos para el siguiente nivel")



# ===========================
# FUNCIÓN PRINCIPAL
# ===========================

def main():
    """Función principal de la aplicación"""
    
    # Header
    render_header()
    
    # Alertas inteligentes por hora
    render_alertas_sistema()
    
    st.markdown("---")
    
    # KPIs principales
    render_kpis_principales()
    
    st.markdown("---")
    
    # Sección de hábitos
    st.markdown("## 📋 Tu Sistema de Hábitos")
    st.caption("⚡ Marca cada hábito inmediatamente después de completarlo. Los bloqueados 🔒 requieren cumplir requisitos primero.")
    
    # Renderizar cada bloque de hábitos
    for bloque in config['bloques']:
        render_bloque_habitos(bloque)
        st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gráfico de tendencia
    render_grafico_tendencia()
    
    # Estadísticas avanzadas (colapsable)
    render_estadisticas_avanzadas()
    
    # Footer motivacional
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p style='font-size: 1.2rem; color: #00ff41;'><strong>⚡ Atomic Engineering Tracker</strong></p>
        <p style='font-size: 0.95rem; margin: 1rem 0;'>
            "No te elevas al nivel de tus metas, desciendes al nivel de tus sistemas"<br>
            <em>— James Clear</em>
        </p>
        <p style='font-size: 0.85rem; color: #888;'>
            🌅 El frío no decide por ti. Tu sistema sí.<br>
            💪 Cada hábito es un voto a favor de tu nueva identidad.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ===========================
# EJECUCIÓN
# ===========================

if __name__ == "__main__":
    main()