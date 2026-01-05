"""
Gestor de Base de Datos SQLite
Maneja todas las operaciones CRUD del sistema
"""

import sqlite3
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple, Optional
from database.models import CREATE_TABLES


class DatabaseManager:
    def __init__(self, db_path: str = "database/tracker.db"):
        """Inicializa la conexión a la base de datos"""
        self.db_path = db_path
        # Crear carpeta si no existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Crea una conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acceder por nombre de columna
        return conn
    
    def _init_database(self):
        """Inicializa las tablas de la base de datos"""
        conn = self._get_connection()
        try:
            conn.executescript(CREATE_TABLES)
            conn.commit()
        finally:
            conn.close()
    
    # ========================
    # OPERACIONES DE REGISTRO
    # ========================
    
    def crear_registro_dia(self, fecha: date) -> bool:
        """Crea un registro para el día si no existe"""
        conn = self._get_connection()
        try:
            conn.execute(
                "INSERT OR IGNORE INTO registros (fecha) VALUES (?)",
                (fecha.isoformat(),)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creando registro: {e}")
            return False
        finally:
            conn.close()
    
    def marcar_habito(self, fecha: date, habito_id: str, bloque_id: str, puntos: int) -> bool:
        """Marca un hábito como completado"""
        conn = self._get_connection()
        try:
            # Asegurar que existe el registro del día
            self.crear_registro_dia(fecha)
            
            # Insertar o actualizar el hábito completado
            conn.execute("""
                INSERT OR REPLACE INTO habitos_completados 
                (fecha, habito_id, bloque_id, puntos, hora_completado)
                VALUES (?, ?, ?, ?, ?)
            """, (fecha.isoformat(), habito_id, bloque_id, puntos, datetime.now().time().isoformat()))
            
            # Actualizar racha
            self._actualizar_racha(conn, habito_id, fecha)
            
            # Recalcular métricas del día
            self._recalcular_metricas_dia(conn, fecha)
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error marcando hábito: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def desmarcar_habito(self, fecha: date, habito_id: str) -> bool:
        """Desmarca un hábito"""
        conn = self._get_connection()
        try:
            conn.execute("""
                DELETE FROM habitos_completados 
                WHERE fecha = ? AND habito_id = ?
            """, (fecha.isoformat(), habito_id))
            
            # Recalcular métricas
            self._recalcular_metricas_dia(conn, fecha)
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error desmarcando hábito: {e}")
            return False
        finally:
            conn.close()
    
    def obtener_habitos_dia(self, fecha: date) -> List[str]:
        """Obtiene los IDs de hábitos completados en una fecha"""
        conn = self._get_connection()
        try:
            cursor = conn.execute("""
                SELECT habito_id FROM habitos_completados 
                WHERE fecha = ?
            """, (fecha.isoformat(),))
            return [row['habito_id'] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    # ========================
    # MÉTRICAS Y ESTADÍSTICAS
    # ========================
    
    def _recalcular_metricas_dia(self, conn: sqlite3.Connection, fecha: date):
        """Recalcula puntos y porcentaje del día"""
        cursor = conn.execute("""
            SELECT COALESCE(SUM(puntos), 0) as total_puntos
            FROM habitos_completados
            WHERE fecha = ?
        """, (fecha.isoformat(),))
        
        total_puntos = cursor.fetchone()['total_puntos']
        
        # Puntos máximos posibles (calculado desde config más adelante)
        # Por ahora usamos un valor fijo
        puntos_maximos = 175  # Suma de todos los puntos posibles
        porcentaje = (total_puntos / puntos_maximos * 100) if puntos_maximos > 0 else 0
        
        conn.execute("""
            UPDATE registros 
            SET puntos_totales = ?, porcentaje_cumplimiento = ?
            WHERE fecha = ?
        """, (total_puntos, porcentaje, fecha.isoformat()))
    
    def obtener_metricas_dia(self, fecha: date) -> Dict:
        """Obtiene las métricas del día actual"""
        conn = self._get_connection()
        try:
            self.crear_registro_dia(fecha)
            
            cursor = conn.execute("""
                SELECT puntos_totales, porcentaje_cumplimiento
                FROM registros
                WHERE fecha = ?
            """, (fecha.isoformat(),))
            
            row = cursor.fetchone()
            return {
                'puntos': row['puntos_totales'] if row else 0,
                'porcentaje': row['porcentaje_cumplimiento'] if row else 0.0
            }
        finally:
            conn.close()
    
    def obtener_racha_habito(self, habito_id: str) -> Dict:
        """Obtiene información de racha de un hábito"""
        conn = self._get_connection()
        try:
            cursor = conn.execute("""
                SELECT racha_actual, racha_maxima, ultima_fecha
                FROM rachas
                WHERE habito_id = ?
            """, (habito_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'actual': row['racha_actual'],
                    'maxima': row['racha_maxima'],
                    'ultima_fecha': row['ultima_fecha']
                }
            return {'actual': 0, 'maxima': 0, 'ultima_fecha': None}
        finally:
            conn.close()
    
    def _actualizar_racha(self, conn: sqlite3.Connection, habito_id: str, fecha: date):
        """Actualiza la racha de un hábito"""
        cursor = conn.execute("""
            SELECT racha_actual, racha_maxima, ultima_fecha
            FROM rachas
            WHERE habito_id = ?
        """, (habito_id,))
        
        row = cursor.fetchone()
        
        if row is None:
            # Primera vez que se completa este hábito
            conn.execute("""
                INSERT INTO rachas (habito_id, racha_actual, racha_maxima, ultima_fecha)
                VALUES (?, 1, 1, ?)
            """, (habito_id, fecha.isoformat()))
        else:
            ultima_fecha = datetime.fromisoformat(row['ultima_fecha']).date() if row['ultima_fecha'] else None
            racha_actual = row['racha_actual']
            racha_maxima = row['racha_maxima']
            
            # Verificar si es día consecutivo
            if ultima_fecha and (fecha - ultima_fecha).days == 1:
                racha_actual += 1
            elif ultima_fecha != fecha:
                racha_actual = 1
            
            # Actualizar racha máxima si corresponde
            racha_maxima = max(racha_maxima, racha_actual)
            
            conn.execute("""
                UPDATE rachas
                SET racha_actual = ?, racha_maxima = ?, ultima_fecha = ?
                WHERE habito_id = ?
            """, (racha_actual, racha_maxima, fecha.isoformat(), habito_id))
    
    def obtener_historico(self, dias: int = 30) -> List[Dict]:
        """Obtiene el histórico de los últimos N días"""
        conn = self._get_connection()
        try:
            fecha_inicio = (date.today() - timedelta(days=dias)).isoformat()
            cursor = conn.execute("""
                SELECT fecha, puntos_totales, porcentaje_cumplimiento
                FROM registros
                WHERE fecha >= ?
                ORDER BY fecha ASC
            """, (fecha_inicio,))
            
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def obtener_perfil(self) -> Dict:
        """Obtiene el perfil del usuario"""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT * FROM perfil WHERE id = 1")
            row = cursor.fetchone()
            return dict(row) if row else {}
        finally:
            conn.close()
    
    def actualizar_perfil(self, puntos_dia: int):
        """Actualiza el perfil del usuario con los puntos del día"""
        conn = self._get_connection()
        try:
            conn.execute("""
                UPDATE perfil
                SET puntos_totales = puntos_totales + ?,
                    dias_activos = dias_activos + 1
                WHERE id = 1
            """, (puntos_dia,))
            conn.commit()
        finally:
            conn.close()