import aiohttp
import logging
from typing import Optional, Dict

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UsersService:
    def __init__(self, base_url: str = "http://localhost:8001"):
        """
        Servicio para comunicarse con la API de usuarios
        
        Args:
            base_url: URL base del servicio de usuarios (ajustar según tu configuración)
        """
        self.base_url = base_url.rstrip('/')
    
    async def get_user_info(self, user_id: str) -> Optional[Dict]:
        """
        Obtiene información del usuario (foto y reputación)
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Dict con foto_url y reputacion, o None si hay error
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/users/{user_id}/reputacion"
                
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "foto_url": data.get("foto_url"),
                            "reputacion": data.get("reputacion", 0.0)
                        }
                    else:
                        logger.warning(f"Error al obtener info del usuario {user_id}: Status {response.status}")
                        return None
                        
        except aiohttp.ClientError as e:
            logger.error(f"Error de conexión al obtener info del usuario {user_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al obtener info del usuario {user_id}: {str(e)}")
            return None

# Instancia global del servicio
users_service = UsersService()