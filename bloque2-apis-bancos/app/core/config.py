from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ============================================
    # CONFIGURACIÓN DEL BANCO / SERVICIO
    # ============================================
    BANCO_ID: int
    BANCO_NOMBRE: str
    API_PORT: int = 8001
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ============================================
    # SEGURIDAD BÁSICA BLOQUE 2
    # ============================================
    API_KEY_ASFI: str = "asfi_default_key_2024"
    API_KEY_BANCO: Optional[str] = None

    NONCE_EXPIRATION_SECONDS: int = 300
    MAX_NONCE_HISTORY: int = 10000

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 1000
    RATE_LIMIT_BURST: int = 50

    IP_WHITELIST_ENABLED: bool = False
    IP_WHITELIST: str = ""

    USE_HTTPS: bool = False
    SSL_CERT_PATH: Optional[str] = None
    SSL_KEY_PATH: Optional[str] = None

    # ============================================
    # CONFIGURACIÓN DE BASE DE DATOS
    # ============================================
    DB_ENGINE: str
    DB_HOST: str = "localhost"
    DB_PORT: Optional[int] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_TABLE: str = "cuentas"

    # MongoDB
    MONGODB_URI: Optional[str] = None
    MONGODB_DATABASE: Optional[str] = None
    MONGODB_COLLECTION: str = "cuentas"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_KEY_PREFIX: str = "cuenta:"

    # ============================================
    # CONFIGURACIÓN DE DATOS / ESQUEMA REAL BLOQUE 1
    # ============================================
    ENCRYPTION_ALGORITHM: str
    ENCRYPTION_KEY: Optional[str] = None
    ENCRYPTION_THRESHOLD_USD: float = 100000.0

    FIELD_ID: str = "id"
    FIELD_CI: str = "ci"
    FIELD_NOMBRES: str = "nombres"
    FIELD_APELLIDOS: str = "apellidos"
    FIELD_NRO_CUENTA: str = "nro_cuenta"
    FIELD_BANCO_ID: str = "id_banco"
    FIELD_SALDO_USD: str = "saldo"
    FIELD_SALDO_BS: str = "saldo_bs"
    FIELD_CI_CIFRADO: str = "ci_cifrado"
    FIELD_SALDO_CIFRADO: str = "saldo_cifrado"
    FIELD_CODE_VERIF: str = "code_verif"

    # ============================================
    # PAGINACIÓN
    # ============================================
    DEFAULT_LIMIT: int = 100
    MAX_LIMIT: int = 1000

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()