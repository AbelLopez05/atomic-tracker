"""
Sistema de Validación y Lógica de Bloqueos
Implementa las reglas de dependencias entre hábitos
"""

from typing import List, Dict, Tuple


class HabitValidator:
    """Valida las reglas de bloqueo y dependencias entre hábitos"""
    
    def __init__(self, config_habitos: Dict):
        """
        Inicializa el validador con la configuración de hábitos
        
        Args:
            config_habitos: Diccionario con la estructura de bloques y hábitos
        """
        self.config = config_habitos
        self._construir_mapa_dependencias()
    
    def _construir_mapa_dependencias(self):
        """Construye un mapa de dependencias para acceso rápido"""
        self.dependencias = {}  # {habito_id: [habitos_requeridos]}
        self.bloqueantes = {}   # {habito_id: [habitos_que_bloquea]}
        
        for bloque in self.config['bloques']:
            for habito in bloque['habitos']:
                habito_id = habito['id']
                
                # Registrar dependencias (este hábito requiere otros)
                if 'requiere' in habito:
                    self.dependencias[habito_id] = habito['requiere']
                
                # Registrar bloqueos (este hábito bloquea otros)
                if 'bloquea' in habito:
                    self.bloqueantes[habito_id] = habito['bloquea']
    
    def puede_marcar_habito(self, habito_id: str, habitos_completados: List[str]) -> Tuple[bool, str]:
        """
        Verifica si un hábito puede ser marcado
        
        Args:
            habito_id: ID del hábito a verificar
            habitos_completados: Lista de IDs de hábitos ya completados hoy
        
        Returns:
            (puede_marcar, mensaje_error)
        """
        # Verificar si tiene dependencias
        if habito_id in self.dependencias:
            requeridos = self.dependencias[habito_id]
            faltantes = [req for req in requeridos if req not in habitos_completados]
            
            if faltantes:
                # Buscar nombres de los hábitos faltantes
                nombres_faltantes = []
                for req_id in faltantes:
                    nombre = self._buscar_nombre_habito(req_id)
                    nombres_faltantes.append(nombre)
                
                mensaje = f"⚠️ Primero debes completar: {', '.join(nombres_faltantes)}"
                return False, mensaje
        
        return True, ""
    
    def _buscar_nombre_habito(self, habito_id: str) -> str:
        """Busca el nombre de un hábito por su ID"""
        for bloque in self.config['bloques']:
            for habito in bloque['habitos']:
                if habito['id'] == habito_id:
                    return habito['nombre']
        return habito_id
    
    def obtener_habitos_bloqueados(self, habitos_completados: List[str]) -> List[str]:
        """
        Obtiene la lista de hábitos que están bloqueados actualmente
        
        Args:
            habitos_completados: Lista de hábitos ya completados
        
        Returns:
            Lista de IDs de hábitos bloqueados
        """
        bloqueados = []
        
        # Para cada hábito con dependencias
        for habito_id, requeridos in self.dependencias.items():
            # Si no están todos los requeridos, está bloqueado
            if not all(req in habitos_completados for req in requeridos):
                bloqueados.append(habito_id)
        
        return bloqueados
    
    def validar_desmarcar_habito(self, habito_id: str, habitos_completados: List[str]) -> Tuple[bool, str]:
        """
        Verifica si un hábito puede ser desmarcado sin afectar dependencias
        
        Args:
            habito_id: ID del hábito a desmarcar
            habitos_completados: Lista actual de hábitos completados
        
        Returns:
            (puede_desmarcar, mensaje_advertencia)
        """
        # Verificar si otros hábitos dependen de este
        if habito_id in self.bloqueantes:
            bloqueados = self.bloqueantes[habito_id]
            afectados = [h for h in bloqueados if h in habitos_completados]
            
            if afectados:
                nombres_afectados = [self._buscar_nombre_habito(h) for h in afectados]
                mensaje = f"⚠️ Esto desbloqueará: {', '.join(nombres_afectados)}"
                return True, mensaje  # Permite, pero advierte
        
        return True, ""