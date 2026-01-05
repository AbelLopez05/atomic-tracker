# ⚡ ATOMIC ENGINEERING TRACKER

Sistema de seguimiento de hábitos personales basado en la filosofía de **"Hábitos Atómicos"** de James Clear.

## 🎯 Filosofía

> "No te elevas al nivel de tus metas, desciendes al nivel de tus sistemas"

Este tracker implementa:
- **Progreso del 1%**: Mejora continua diaria
- **Identidad**: Cada hábito refuerza quién quieres ser
- **Gamificación**: Niveles, rachas y badges para mantener motivación
- **Sistemas sobre metas**: Enfoque en el proceso, no solo en resultados

## 🚀 Características

### Core Features
- ✅ Tracking diario de hábitos personalizados
- 📊 KPIs en tiempo real (% cumplimiento, rachas, puntos)
- 🎮 Sistema de gamificación (niveles, badges, logros)
- 🔒 Lógica de bloqueos (ej: Dota 2 solo después de ejercicio)
- 📈 Gráficos de tendencia mensual
- 🏆 Rachas de consistencia
- 📱 Diseño mobile-first (PWA-ready)

### Hábitos Implementados

### Hábitos Implementados (Tu Sistema Personalizado)

Este sistema está diseñado específicamente para tu rutina diaria y objetivos:

**🌅 FASE 1: Arranque del Sistema (07:00-09:00 AM)**
- 07:00 - Despertar + Protocolo Anti-Frío (¡NO TOCAR CELULAR!)
- 07:10 - Primera Victoria: Tender la Cama
- 07:15 - Aseo Personal + Postura (Gato-Vaca 1min)
- 07:45 - Desayuno Potente (Proteína para masa muscular)
- Lectura: 3 páginas Hábitos Atómicos (opcional)

**🌞 FASE 2: Bloque Productivo (09:00-13:00 PM)**
- 09:00 - Bloque Doméstico (Limpieza/Lavar/Cocina → NEAT)
- 11:00 - Bloque de Enfoque (1 hora estudio técnico → NO PC/PELIS)
- 13:00 - Almuerzo Completo (comer bastante)

**🚀 FASE 3: Trabajo Profundo (14:30-18:00 PM)**
- 14:30 - Proyectos de Ingeniería (Pomodoro 25/5 → NO Dota antes 6PM)
- Pausas Activas: Ángel de Pared cada hora

**🎮 FASE 4: Recompensa y Cierre (18:00-22:00 PM)**
- 18:00 - **PEAJE DEL DOTA**: Sentadillas + Flexiones + Puente (¡OBLIGATORIO!)
- Dota 2 (Ganado con ejercicio y trabajo previo)
- 20:00 - Cena Nutritiva
- 21:30 - Protocolo de Apagado (PC off + Casaca lista + Celular lejos)
- 22:00-22:30 - Dormir (Hormona de crecimiento)

**🔥 Hábitos Críticos (Todo el día)**
- Cero Porno (Racha de pureza)
- NO Tocar Celular al Despertar
- Postura Consciente (Hombros atrás todo el día)

## 🛠️ Stack Tecnológico

- **Frontend**: Streamlit 1.31.0
- **Backend**: Python 3.9+
- **Base de Datos**: SQLite (local, portátil)
- **Visualización**: Plotly
- **Deployment**: Streamlit Community Cloud (gratuito)

## 📦 Instalación Local

### Requisitos Previos
- Python 3.9 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/TU_USUARIO/atomic-tracker.git
cd atomic-tracker
```

2. **Crear entorno virtual (recomendado)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**
```bash
streamlit run app.py
```

5. **Abrir en el navegador**
La app se abrirá automáticamente en `http://localhost:8501`

## 🌐 Despliegue en Streamlit Cloud

### Paso 1: Preparar el Repositorio

1. Crear cuenta en [GitHub](https://github.com) (si no tienes)
2. Crear nuevo repositorio público llamado `atomic-tracker`
3. Subir el código:
```bash
git init
git add .
git commit -m "Initial commit: Atomic Tracker"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/atomic-tracker.git
git push -u origin main
```

### Paso 2: Desplegar en Streamlit Cloud

1. Ir a [share.streamlit.io](https://share.streamlit.io)
2. Iniciar sesión con GitHub
3. Clic en "New app"
4. Seleccionar:
   - Repository: `TU_USUARIO/atomic-tracker`
   - Branch: `main`
   - Main file path: `app.py`
5. Clic en "Deploy!"

### Paso 3: Acceder desde el Móvil

1. Copiar la URL generada (ej: `https://tu-app.streamlit.app`)
2. En tu celular, abrir el navegador y acceder a la URL
3. **Tip**: Agregar a pantalla de inicio para experiencia tipo app nativa

#### En Android:
- Chrome: Menú (⋮) → "Agregar a pantalla de inicio"

#### En iOS:
- Safari: Compartir → "Agregar a inicio"

## 📊 Uso del Sistema

### Flujo Diario Recomendado

1. **Mañana (7:00 AM)**
   - Abrir la app
   - Completar hábitos matinales
   - Verificar progreso del día

2. **Durante el día**
   - Marcar hábitos conforme los completas
   - Ver actualización de KPIs en tiempo real

3. **Noche (antes de dormir)**
   - Verificar % de cumplimiento
   - Si es >85%, ¡celebra la victoria!
   - Planificar mejoras para mañana

### Entendiendo las Métricas

- **Progreso Hoy**: % de puntos obtenidos vs máximo posible
  - 🏆 ≥100%: Día perfecto
  - ⚡ ≥85%: Meta cumplida
  - 👍 ≥60%: Buen avance
  - ⚠️ <60%: Requiere esfuerzo

- **Racha Actual**: Días consecutivos con >85%
  - Objetivo: Mantener la racha lo más larga posible
  - No te desanimes si se rompe, ¡comienza de nuevo!

- **Nivel**: Basado en puntos totales acumulados
  - 🌱 Novato (0 pts)
  - ⚡ Disciplina (100 pts)
  - 🔥 Ingeniero Atómico (500 pts)
  - 💎 Maestro de Hábitos (1500 pts)
  - 🏆 Leyenda (5000 pts)