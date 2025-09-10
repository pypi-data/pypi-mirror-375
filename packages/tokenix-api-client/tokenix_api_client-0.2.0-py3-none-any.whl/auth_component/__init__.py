"""
Tokenix API Client - Cliente Python para la API de Tokenix

Este paquete proporciona un cliente completo para la API de Tokenix, incluyendo
autenticación HTTP y comunicación con todos los endpoints disponibles.
Maneja el flujo de dos tokens: token de autenticación y token de API.
"""

__version__ = "0.2.0"
__author__ = "Edwin Caicedo Venté"
__email__ = "ecaicedo@rapicredit.com"

from .simple_auth import SimpleTokenixAuth, create_auth_client
from .exceptions import (
    AuthError,
    HTTPAuthError,
    InvalidCredentialsError,
    ServiceUnavailableError
)

__all__ = [
    "SimpleTokenixAuth",
    "create_auth_client",
    "AuthError",
    "HTTPAuthError",
    "InvalidCredentialsError",
    "ServiceUnavailableError",
]