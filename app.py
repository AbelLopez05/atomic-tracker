"""
ATOMIC ENGINEERING TRACKER 2025
Dashboard Avanzado con Reportes Completos
Diseño inspirado en @my_habitts con mejoras para Ingeniería de Sistemas
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta
import json
import os
import calendar

# Imports locales
from database.db_manager import DatabaseManager
from utils.gamification import GamificationSystem, NIVELES, BADGES
from utils.validators import HabitValidator
from utils.metrics import MetricsCalculator
from utils.reports import ReportGenerator

# ===========================
# CONFIGURACIÓN DE LA PÁGINA
# ===========================

st.set_page_config(
    page_title="Sistema de Hábitos",
    page_icon="📙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar CSS personalizado
def load_css():
    css_file = "assets/style.css"
    if os.path.exists(css_file):
        with open(css_file, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ===========================
# INICIALIZACIÓN
# ===========================

@st.cache_resource
def init_database():
    return DatabaseManager()

@st.cache_data(ttl=3600)
def load_config():
    with open("config/habitos.json", "r", encoding="utf-8") as f:
        return json.load(f)

db = init_database()
config = load_config()
validator = HabitValidator(config)
gamification = GamificationSystem()
metrics_calc = MetricsCalculator()
reports = ReportGenerator()

# Estado de sesión
if 'fecha_actual' not in st.session_state:
    st.session_state.fecha_actual = date.today()

if 'habitos_completados' not in st.session_state:
    st.session_state.habitos_completados = db.obtener_habitos_dia(st.session_state.fecha_actual)

if 'vista_actual' not in st.session_state:
    st.session_state.vista_actual = 'dashboard'

# ===========================
# FUNCIONES AUXILIARES
# ===========================

def calcular_puntos_maximos():
    total = 0
    for bloque in config['bloques']:
        for habito in bloque['habitos']:
            if habito['puntos'] > 0:
                total += habito['puntos']
    return total

PUNTOS_MAXIMOS = calcular_puntos_maximos()

def refrescar_habitos():
    st.session_state.habitos_completados = db.obtener_habitos_dia(st.session_state.fecha_actual)

def toggle_habito(habito_id: str, bloque_id: str, puntos: int):
    fecha = st.session_state.fecha_actual
    habitos_actuales = st.session_state.habitos_completados
    
    if habito_id in habitos_actuales:
        puede_desmarcar, mensaje = validator.validar_desmarcar_habito(habito_id, habitos_actuales)
        if puede_desmarcar:
            if db.desmarcar_habito(fecha, habito_id, max_puntos=PUNTOS_MAXIMOS):
                if mensaje:
                    st.toast(mensaje, icon="⚠️")
                refrescar_habitos()
                st.rerun()
    else:
        puede_marcar, mensaje_error = validator.puede_marcar_habito(habito_id, habitos_actuales)
        if puede_marcar:
            if db.marcar_habito(fecha, habito_id, bloque_id, puntos, max_puntos=PUNTOS_MAXIMOS):
                st.toast(f"✓ ¡Hábito completado! +{puntos} pts", icon="✅")
                refrescar_habitos()
                st.rerun()
        else:
            st.error(mensaje_error)
            st.stop()

def obtener_color_progreso(porcentaje: float) -> str:
    if porcentaje >= 85:
        return "#00ff88"
    elif porcentaje >= 60:
        return "#FFB800"
    else:
        return "#FF3B3B"

# ===========================
# SIDEBAR - DASHBOARD LATERAL
# ===========================

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 style='font-size: 2rem; margin: 0;'>⚡</h1>
            <h3 style='margin: 0.5rem 0; color: #00ff88;'>ATOMIC TRACKER</h3>
            <p style='color: #8B93B0; font-size: 0.85rem;'>Dashboard 2025</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        
        st.markdown("---")
        
        # Métricas rápidas
        st.markdown("### ⚡ Métricas Rápidas")
        
        metricas_dia = db.obtener_metricas_dia(st.session_state.fecha_actual)
        historico = db.obtener_historico(dias=90)
        racha = metrics_calc.calcular_racha_perfecta(historico, 85)
        perfil = db.obtener_perfil()
        nivel_info = gamification.calcular_progreso_nivel(perfil.get('puntos_totales', 0))
        
        # Progreso del día
        porcentaje = metricas_dia['porcentaje']
        color = obtener_color_progreso(porcentaje)
        
        st.markdown(f"""
        <div style='background: #131829; padding: 1rem; border-radius: 12px; margin: 0.5rem 0; border-left: 4px solid {color};'>
            <p style='color: #8B93B0; font-size: 0.8rem; margin: 0;'>PROGRESO HOY</p>
            <h2 style='margin: 0.2rem 0; color: {color};'>{porcentaje:.1f}%</h2>
            <p style='color: #8B93B0; font-size: 0.75rem; margin: 0;'>{metricas_dia['puntos']}/{PUNTOS_MAXIMOS} pts</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Racha
        st.markdown(f"""
        <div style='background: #131829; padding: 1rem; border-radius: 12px; margin: 0.5rem 0; border-left: 4px solid #FF9800;'>
            <p style='color: #8B93B0; font-size: 0.8rem; margin: 0;'>🔥 RACHA</p>
            <h2 style='margin: 0.2rem 0; color: #FF9800;'>{racha}</h2>
            <p style='color: #8B93B0; font-size: 0.75rem; margin: 0;'>días consecutivos</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Nivel
        st.markdown(f"""
        <div style='background: #131829; padding: 1rem; border-radius: 12px; margin: 0.5rem 0; border-left: 4px solid #667eea;'>
            <p style='color: #8B93B0; font-size: 0.8rem; margin: 0;'>NIVEL</p>
            <h2 style='margin: 0.2rem 0; color: #667eea;'>{nivel_info['nivel']}</h2>
            <p style='color: #8B93B0; font-size: 0.75rem; margin: 0;'>{nivel_info['nombre_nivel']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.progress(nivel_info['porcentaje'] / 100)
        st.caption(f"🎯 {nivel_info['porcentaje']:.0f}% al siguiente nivel")
        
        st.markdown("---")
        
        # Análisis semanal rápido
        st.markdown("### 📅 Esta Semana")
        stats_semana = metrics_calc.calcular_porcentaje_semanal(historico, 85)
        
        st.metric(
            "Días >85%",
            f"{stats_semana['dias_meta_cumplida']}/7",
            delta=f"Meta: 6 días" if stats_semana['dias_meta_cumplida'] < 6 else "✓ Meta cumplida"
        )
        
        # Badges recientes
        st.markdown("---")
        st.markdown("### 🏆 Badges Desbloqueados")
        
        perfil_badges = {
            'dias_activos': perfil.get('dias_activos', 0),
            'racha_perfecta': racha,
            'racha_cero_porno': db.obtener_racha_habito('cero_porno')['actual'],
            'racha_peaje_ejercicio': db.obtener_racha_habito('peaje_ejercicio')['actual']
        }
        
        badges_desbloqueados = gamification.obtener_badges_desbloqueados(perfil_badges)
        
        if badges_desbloqueados:
            for badge in badges_desbloqueados[-3:]:  # Últimos 3
                st.markdown(f"""
                <div style='background: #131829; padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0; text-align: center;'>
                    <span style='font-size: 2rem;'>{badge['emoji']}</span><br>
                    <strong style='font-size: 0.9rem;'>{badge['nombre']}</strong>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("🎯 Completa más días para desbloquear badges")

# ===========================
# VISTA PRINCIPAL: DASHBOARD
# ===========================

# Helper para fecha en español
def fecha_en_espanol(fecha: date) -> str:
    dias = {
        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
        'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    dia_str = dias[fecha.strftime('%A')]
    mes_str = meses[fecha.month]
    return f"{dia_str}, {fecha.day} de {mes_str} {fecha.year}"

def render_dashboard():
    # Header con fecha
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        fecha_str = fecha_en_espanol(st.session_state.fecha_actual)
        st.markdown(f"""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 style='font-size: 2.5rem; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                ⚡ ATOMIC TRACKER
            </h1>
            <p style='color: #8B93B0; margin: 0.5rem 0; font-size: 1.1rem;'>
                📅 {fecha_str}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Alertas inteligentes
    render_alertas_sistema()
    
    # KPIs principales (4 columnas)
    render_kpis_principales()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Grid de hábitos
    render_grid_habitos()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráfico de tendencia
    render_grafico_tendencia_avanzado()

def render_alertas_sistema():
    ahora = datetime.now()
    hora_actual = ahora.hour
    habitos_completados = st.session_state.habitos_completados
    
    alerta_mostrada = False
    
    if 7 <= hora_actual < 9:
        if 'despertar_protocolo_frio' not in habitos_completados:
            st.warning("⏰ **ALERTA MATUTINA**: ¿Ya hiciste el protocolo anti-frío? ¡NO TOQUES EL CELULAR!")
            alerta_mostrada = True
    
    elif 11 <= hora_actual < 13:
        if 'bloque_enfoque' not in habitos_completados:
            st.warning("📚 **Hora de Enfoque**: Celular fuera → 1 hora de estudio técnico")
            alerta_mostrada = True
    
    elif 14 <= hora_actual < 18:
        if 'bloque_proyectos' not in habitos_completados:
            st.error("🚀 **TRABAJO PROFUNDO**: ¡NO Dota/Netflix! Proyectos primero.")
            alerta_mostrada = True
    
    elif 18 <= hora_actual < 21:
        if 'peaje_ejercicio' not in habitos_completados:
            st.error("💪 **¡PEAJE DEL DOTA!**: Sentadillas + Flexiones + Puente. Sin esto, NO hay juego.")
            alerta_mostrada = True
        elif 'dota2' not in habitos_completados and 'peaje_ejercicio' in habitos_completados:
            st.success("🎮 **Dota Desbloqueado**: Te lo ganaste. Disfruta sin culpa.")
            alerta_mostrada = True
    
    elif hora_actual >= 21:
        if 'protocolo_apagado' not in habitos_completados:
            st.warning("🌙 **Protocolo de Apagado**: PC off → Casaca lista → Celular lejos")
            alerta_mostrada = True
        if hora_actual >= 22 and 'dormir_temprano' not in habitos_completados:
            st.error("⏰ **CRÍTICO**: ¡Son las 10 PM! Tu hormona de crecimiento espera.")
            alerta_mostrada = True

def render_kpis_principales():
    metricas_dia = db.obtener_metricas_dia(st.session_state.fecha_actual)
    porcentaje_dia = metricas_dia['porcentaje']
    puntos_dia = metricas_dia['puntos']
    
    historico = db.obtener_historico(dias=90)
    racha_perfecta = metrics_calc.calcular_racha_perfecta(historico, 85)
    
    perfil = db.obtener_perfil()
    nivel_info = gamification.calcular_progreso_nivel(perfil.get('puntos_totales', 0))
    
    # Calcular hábitos completados hoy
    habitos_hoy = len(st.session_state.habitos_completados)
    total_habitos = sum(len(bloque['habitos']) for bloque in config['bloques'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        color = obtener_color_progreso(porcentaje_dia)
        delta_color = "normal" if porcentaje_dia >= 85 else "inverse"
        st.metric(
            label="📊 Progreso Hoy",
            value=f"{porcentaje_dia:.1f}%",
            delta=f"Meta: 85%",
            delta_color=delta_color
        )
    
    with col2:
        st.metric(
            label="🔥 Racha",
            value=f"{racha_perfecta} días",
            delta="Consecutivos"
        )
    
    with col3:
        st.metric(
            label="⭐ Puntos",
            value=f"{puntos_dia}",
            delta=f"/{PUNTOS_MAXIMOS}"
        )
    
    with col4:
        st.metric(
            label=f"{nivel_info['nombre_nivel']}",
            value=f"Nivel {nivel_info['nivel']}",
            delta=f"{nivel_info['porcentaje']:.0f}% sig."
        )
    
    # Barra de progreso animada
    color = obtener_color_progreso(porcentaje_dia)
    st.markdown(f"""
    <div class='progress-bar-container'>
        <div class='progress-bar-fill' style='width: {porcentaje_dia}%; background: linear-gradient(90deg, {color} 0%, {color}dd 100%);'>
            {porcentaje_dia:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Mensaje motivacional
    mensaje = gamification.generar_mensaje_motivacional(porcentaje_dia, racha_perfecta)
    
    if porcentaje_dia >= 85:
        st.success(f"💚 {mensaje}")
    elif porcentaje_dia >= 60:
        st.info(f"💙 {mensaje}")
    else:
        st.warning(f"🧡 {mensaje}")

def render_grid_habitos():
    st.markdown("## 📋 Tu Sistema de Hábitos")
    
    # Tabs para cada fase
    tabs = st.tabs([bloque['nombre'] for bloque in config['bloques']])
    
    for idx, bloque in enumerate(config['bloques']):
        with tabs[idx]:
            render_bloque_habitos_grid(bloque)

def render_bloque_habitos_grid(bloque: dict):
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #131829 0%, #1A1F3A 100%); 
                padding: 1.5rem; border-radius: 14px; border-left: 5px solid {bloque['color']};
                margin: 1rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.3);'>
        <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;'>
            <div>
                <h3 style='margin: 0; color: {bloque['color']}; font-size: 1.3rem;'>{bloque['nombre']}</h3>
                <p style='color: #8B93B0; margin: 0.3rem 0 0 0; font-size: 0.9rem;'>{bloque.get('subtitulo', '')}</p>
            </div>
            <div style='text-align: right; margin-top: 0.5rem;'>
                <p style='color: {bloque['color']}; margin: 0; font-size: 0.8rem;'>Identidad</p>
                <p style='color: white; margin: 0; font-weight: bold; font-size: 1rem;'>{bloque['identidad']}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    habitos_completados = st.session_state.habitos_completados
    habitos_bloqueados = validator.obtener_habitos_bloqueados(habitos_completados)
    
    # Grid de 2 columnas para hábitos
    cols = st.columns(2)
    
    for idx, habito in enumerate(bloque['habitos']):
        with cols[idx % 2]:
            render_habito_card(habito, bloque, habitos_completados, habitos_bloqueados)

def render_habito_card(habito: dict, bloque: dict, habitos_completados: list, habitos_bloqueados: list):
    habito_id = habito['id']
    esta_completado = habito_id in habitos_completados
    esta_bloqueado = habito_id in habitos_bloqueados and not esta_completado
    es_privado = habito.get('privado', False)
    es_critico = habito.get('critico', False)
    
    # Determinar estilo de tarjeta
    if esta_completado:
        bg_color = "rgba(0, 255, 136, 0.12)"
        border_color = "#00ff88"
        icon = "✓"
        icon_color = "#00ff88"
    elif esta_bloqueado:
        bg_color = "rgba(255, 184, 0, 0.1)"
        border_color = "#FFB800"
        icon = "🔒"
        icon_color = "#FFB800"
    else:
        bg_color = "#131829"
        border_color = "#1F2437"
        icon = "○"
        icon_color = "#8B93B0"
    
    nombre_display = habito['nombre'] if not es_privado else "🔒 Hábito Privado"
    descripcion = habito['descripcion'] if not es_privado else "Progreso privado"
    
    # Checkbox
    checkbox_key = f"habit_{bloque['id']}_{habito_id}"
    
    col1, col2 = st.columns([0.15, 0.85])
    
    with col1:
        if esta_bloqueado:
            st.checkbox("", value=False, disabled=True, key=checkbox_key, label_visibility="collapsed")
        else:
            nuevo_estado = st.checkbox("", value=esta_completado, key=checkbox_key, label_visibility="collapsed")
            if nuevo_estado != esta_completado:
                toggle_habito(habito_id, bloque['id'], habito['puntos'])
    
    with col2:
        critico_badge = "🔥" if es_critico else ""
        
        st.markdown(f"""
        <div class='habit-card {"habit-card-completed" if esta_completado else "habit-card-blocked" if esta_bloqueado else ""}' 
             style='background: {bg_color}; border-left: 4px solid {border_color};'>
            <div class='habit-card-content' style='display: flex; justify-content: space-between; align-items: center;'>
                <div style='flex: 1;'>
                    <strong style='color: {icon_color}; font-size: 1rem;'>{icon} {critico_badge} {nombre_display}</strong><br>
                    <small style='color: #8B93B0; line-height: 1.4; display: block; margin-top: 4px;'>{descripcion}</small>
                </div>
                <div class='habit-card-points' style='text-align: right; margin-left: 1rem;'>
                    <span style='background: {border_color}; color: #0A0E1A; padding: 0.2rem 0.6rem; 
                                 border-radius: 20px; font-weight: bold; font-size: 0.8rem; white-space: nowrap;'>
                        +{habito['puntos']} pts
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_grafico_tendencia_avanzado():
    st.markdown("## 📈 Análisis de Tendencia")
    
    historico = db.obtener_historico(dias=30)
    
    if not historico:
        st.info("📊 Completa más días para ver el análisis de tendencia")
        return
    
    df = pd.DataFrame(historico)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df = df.sort_values('fecha')
    
    # Crear gráfico con área sombreada
    fig = go.Figure()
    
    # Área de progreso
    fig.add_trace(go.Scatter(
        x=df['fecha'],
        y=df['porcentaje_cumplimiento'],
        mode='lines+markers',
        name='% Cumplimiento',
        line=dict(color='#00ff88', width=3, shape='spline'),
        marker=dict(size=10, color='#00ff88', symbol='circle',
                   line=dict(color='#0A0E1A', width=2)),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 136, 0.2)',
        hovertemplate='<b>%{x|%d %b}</b><br>Progreso: %{y:.1f}%<extra></extra>'
    ))
    
    # Línea de meta
    fig.add_hline(
        y=85,
        line_dash="dash",
        line_color="#FFB800",
        line_width=2,
        annotation_text="Meta: 85%",
        annotation_position="right",
        annotation=dict(font=dict(size=14, color="#FFB800"))
    )
    
    # Línea de excelencia
    fig.add_hline(
        y=100,
        line_dash="dot",
        line_color="#667eea",
        line_width=2,
        annotation_text="Perfección: 100%",
        annotation_position="right",
        annotation=dict(font=dict(size=12, color="#667eea"))
    )
    
    fig.update_layout(
        title={
            'text': "Progreso de los Últimos 30 Días",
            'font': {'size': 24, 'color': '#FFFFFF'}
        },
        xaxis_title="Fecha",
        yaxis_title="% Cumplimiento",
        template="plotly_dark",
        height=450,
        hovermode='x unified',
        showlegend=False,
        paper_bgcolor='#0A0E1A',
        plot_bgcolor='#131829',
        font=dict(family="Inter, sans-serif", color="#FFFFFF"),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    fig.update_xaxes(
        gridcolor='#1F2437',
        showgrid=True,
        zeroline=False
    )
    
    fig.update_yaxes(
        range=[0, 110],
        gridcolor='#1F2437',
        showgrid=True,
        zeroline=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Análisis de tendencia
    col1, col2, col3 = st.columns(3)
    
    tendencia = metrics_calc.analizar_tendencia(historico)
    stats = metrics_calc.calcular_estadisticas_generales(historico)
    
    with col1:
        st.metric("Tendencia", tendencia)
    
    with col2:
        st.metric("Promedio 30 días", f"{stats['promedio_cumplimiento']:.1f}%")
    
    with col3:
        st.metric("Mejor día", f"{stats['mejor_dia']:.1f}%")

# ===========================
# VISTA DE REPORTES
# ===========================

def render_reportes():
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='font-size: 2.5rem; margin: 0;'>📊 CENTRO DE REPORTES</h1>
        <p style='color: #8B93B0; margin: 0.5rem 0;'>Análisis completo de tu progreso</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs para diferentes períodos
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📅 Diario", "📆 Semanal", "📊 Mensual", 
        "📈 Trimestral", "📉 Semestral", "📕 Anual"
    ])
    
    with tab1:
        render_reporte_diario()
    
    with tab2:
        render_reporte_semanal()
    
    with tab3:
        render_reporte_mensual()
    
    with tab4:
        render_reporte_trimestral()
    
    with tab5:
        render_reporte_semestral()
    
    with tab6:
        render_reporte_anual()

def render_reporte_diario():
    st.markdown("### 📅 Reporte del Día")
    
    fecha_seleccionada = st.date_input(
        "Seleccionar fecha",
        value=date.today(),
        max_value=date.today(),
        key="fecha_reporte_diario"
    )
    
    reporte = reports.generar_reporte_diario(db, fecha_seleccionada)
    
    if reporte.get('habitos_completados', 0) == 0:
        st.info("No hay registros para esta fecha")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Día", reporte['dia_semana'])
    
    with col2:
        st.metric("Progreso", f"{reporte['porcentaje']:.1f}%")
    
    with col3:
        st.metric("Puntos", reporte['puntos'])
    
    with col4:
        st.metric("Hábitos", f"{reporte['habitos_completados']}/{reporte['habitos_totales']}")
    
    # Estado
    if reporte['meta_alcanzada']:
        st.success("✅ Meta del día alcanzada (+85%)")
    else:
        st.warning(f"⚠️ No se alcanzó la meta (85%). Falló por {85 - reporte['porcentaje']:.1f}%")
    
    # Lista de hábitos completados
    st.markdown("#### ✓ Hábitos Completados")
    if reporte['habitos_lista']:
        for habito_id in reporte['habitos_lista']:
            # Buscar nombre del hábito
            found = False
            for bloque in config['bloques']:
                for habito in bloque['habitos']:
                    if habito['id'] == habito_id:
                        st.markdown(f"- **{habito['nombre']}** ({habito['puntos']} pts)")
                        found = True
                        break
                if found: break

def render_reporte_semanal():
    st.markdown("### 📆 Reporte Semanal")
    
    reporte = reports.generar_reporte_semanal(db)
    
    if reporte.get('dias_registrados', 0) == 0:
        st.info("No hay datos para esta semana")
        return
        
    st.markdown(f"**Periodo:** {reporte['periodo']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Promedio Semanal", f"{reporte['promedio_porcentaje']}%")
    with col2:
        st.metric("Días Meta Cumplida", f"{reporte['dias_meta_cumplida']}/7")
    with col3:
        st.metric("Total Puntos", reporte['total_puntos'])
        
    if reporte['meta_semanal_cumplida']:
        st.success("🏆 ¡Semana Exitosa! (6+ días de meta cumplida)")
        
    # Mejor y peor día
    c1, c2 = st.columns(2)
    c1.info(f"🏅 Mejor día: {reporte['mejor_dia']['fecha']} ({reporte['mejor_dia']['porcentaje']}%)")
    c2.warning(f"📉 Peor día: {reporte['peor_dia']['fecha']} ({reporte['peor_dia']['porcentaje']}%)")

def render_reporte_mensual():
    st.markdown("### 📊 Reporte Mensual")
    reporte = reports.generar_reporte_mensual(db)
    
    if reporte.get('dias_registrados', 0) == 0:
        st.info("No hay datos para este mes")
        return
        
    st.markdown(f"**Mes:** {reporte['periodo']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Promedio Mensual", f"{reporte['promedio_porcentaje']}%")
    with col2:
        st.metric("Días Meta Cumplida", reporte['dias_meta_cumplida'])
    with col3:
        st.metric("Total Puntos", reporte['total_puntos'])
        
    st.markdown(f"**Tendencia:** {reporte['tendencia']}")
    
    # Gráfico diario del mes
    if reporte['datos_diarios']:
        df = pd.DataFrame(reporte['datos_diarios'])
        fig = px.bar(df, x='fecha', y='porcentaje_cumplimiento', 
                     title="Progreso Diario del Mes",
                     labels={'porcentaje_cumplimiento': '% Cumplimiento', 'fecha': 'Fecha'})
        fig.add_hline(y=85, line_dash="dash", line_color="green", annotation_text="Meta 85%")
        st.plotly_chart(fig, use_container_width=True)

def render_reporte_trimestral():
    st.markdown("### 📈 Reporte Trimestral")
    reporte = reports.generar_reporte_trimestral(db)
    
    if reporte.get('dias_registrados', 0) == 0:
        st.info("No hay datos para este trimestre")
        return
        
    st.markdown(f"**Periodo:** {reporte['periodo']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Promedio Trimestral", f"{reporte['promedio_porcentaje']}%")
    with col2:
        st.metric("Días Meta Cumplida", reporte['dias_meta_cumplida'])
        
    if reporte['promedio_por_mes']:
        st.bar_chart(reporte['promedio_por_mes'])

def render_reporte_semestral():
    st.markdown("### 📉 Reporte Semestral")
    reporte = reports.generar_reporte_semestral(db)
    
    if reporte.get('dias_registrados', 0) == 0:
        st.info("No hay datos para este semestre")
        return
        
    st.markdown(f"**Periodo:** {reporte['periodo']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Promedio Semestral", f"{reporte['promedio_porcentaje']}%")
    with col2:
        st.metric("Racha Máxima", f"{reporte['racha_maxima']} días")

def render_reporte_anual():
    st.markdown("### 📕 Reporte Anual")
    reporte = reports.generar_reporte_anual(db)
    
    if reporte.get('dias_registrados', 0) == 0:
        st.info("No hay datos para este año")
        return
        
    st.markdown(f"**Año:** {reporte['periodo']}")
    st.markdown(f"### {reporte['transformacion']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Promedio Anual", f"{reporte['promedio_porcentaje']}%")
    with col2:
        st.metric("Total Días Cumplidos", reporte['dias_meta_cumplida'])
    with col3:
        st.metric("Mejor Mes", str(reporte['mejor_mes']))
        
    if reporte['promedio_por_mes']:
        st.line_chart(reporte['promedio_por_mes'])

# ===========================
# FUNCIÓN PRINCIPAL
# ===========================

def main():
    """Función principal de la aplicación"""
    

    # Renderizar sidebar siempre
    render_sidebar()
    
    # Anchor para scroll
    st.markdown("<div id='top-marker'></div>", unsafe_allow_html=True)
    

    
    # Router simple eliminado - mostrar todo en una página
    render_dashboard()
    
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Renderizar reportes al final
    render_reportes()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p style='font-size: 1.2rem; color: #00ff88;'><strong>⚡ Atomic Engineering Tracker</strong></p>
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
    
    # SCRIPT DE SCROLL FINAL (Ejecutar al último)
    components_html = """
        <script>
            function forceScrollTop() {
                try {
                    var marker = window.parent.document.getElementById('top-marker');
                    if (marker) {
                        marker.scrollIntoView({behavior: 'instant', block: 'start'});
                    } else {
                        window.parent.scrollTo(0, 0);
                    }
                } catch (e) {
                    console.log("Scroll attempt failed");
                }
            }
            setTimeout(forceScrollTop, 100);
            setTimeout(forceScrollTop, 300);
            setTimeout(forceScrollTop, 500);
        </script>
    """
    st.components.v1.html(components_html, height=0)

# ===========================
# EJECUCIÓN
# ===========================

if __name__ == "__main__":
    main()