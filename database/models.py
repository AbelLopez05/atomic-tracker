"""
Modelos de Base de Datos para Atomic Tracker
Define la estructura de las tablas SQLite
"""

CREATE_TABLES = """
-- Tabla principal de registros diarios
CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha DATE NOT NULL UNIQUE,
    puntos_totales INTEGER DEFAULT 0,
    porcentaje_cumplimiento REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de hábitos completados por día
CREATE TABLE IF NOT EXISTS habitos_completados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha DATE NOT NULL,
    habito_id TEXT NOT NULL,
    bloque_id TEXT NOT NULL,
    puntos INTEGER DEFAULT 0,
    hora_completado TIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fecha) REFERENCES registros(fecha),
    UNIQUE(fecha, habito_id)
);

-- Tabla de rachas
CREATE TABLE IF NOT EXISTS rachas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habito_id TEXT UNIQUE NOT NULL,
    racha_actual INTEGER DEFAULT 0,
    racha_maxima INTEGER DEFAULT 0,
    ultima_fecha DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de nivel y gamificación
CREATE TABLE IF NOT EXISTS perfil (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    nivel INTEGER DEFAULT 1,
    puntos_totales INTEGER DEFAULT 0,
    dias_activos INTEGER DEFAULT 0,
    identidad_actual TEXT DEFAULT 'Novato',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar perfil inicial si no existe
INSERT OR IGNORE INTO perfil (id, nivel, puntos_totales) VALUES (1, 1, 0);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_registros_fecha ON registros(fecha);
CREATE INDEX IF NOT EXISTS idx_habitos_fecha ON habitos_completados(fecha);
CREATE INDEX IF NOT EXISTS idx_rachas_habito ON rachas(habito_id);
"""