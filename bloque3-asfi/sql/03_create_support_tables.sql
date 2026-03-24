USE ASFI_Central;

CREATE TABLE IF NOT EXISTS BancoLlaves (
    BancoId INT PRIMARY KEY,
    Algoritmo VARCHAR(50) NOT NULL,
    LlaveReferencia VARCHAR(255) NOT NULL,
    TipoLlave VARCHAR(20) NOT NULL,
    UltimaSincronizacion DATETIME NOT NULL,
    FOREIGN KEY (BancoId) REFERENCES Bancos(BancoId)
);

CREATE TABLE IF NOT EXISTS AuditLog (
    AuditId BIGINT AUTO_INCREMENT PRIMARY KEY,
    Timestamp DATETIME NOT NULL,
    BancoId INT NOT NULL,
    CuentaId VARCHAR(255) NULL,
    Evento VARCHAR(50) NOT NULL,
    Detalle TEXT NULL,
    TipoCambio DECIMAL(18,4) NULL,
    ModoTipoCambio VARCHAR(20) NULL,
    FuenteTipoCambio VARCHAR(50) NULL,
    LoteId VARCHAR(100) NULL,
    INDEX idx_audit_banco_cuenta (BancoId, CuentaId),
    INDEX idx_audit_timestamp (Timestamp),
    FOREIGN KEY (BancoId) REFERENCES Bancos(BancoId)
);

CREATE TABLE IF NOT EXISTS TipoCambioLog (
    RateLogId BIGINT AUTO_INCREMENT PRIMARY KEY,
    Timestamp DATETIME NOT NULL,
    Modo VARCHAR(20) NOT NULL,
    TipoCambio DECIMAL(18,4) NOT NULL,
    BaseRate DECIMAL(18,4) NOT NULL,
    Drift DECIMAL(18,4) NOT NULL,
    Slot BIGINT NOT NULL,
    Source VARCHAR(50) NOT NULL,
    INDEX idx_rate_mode_time (Modo, Timestamp)
);

CREATE TABLE IF NOT EXISTS ProcesamientoErrores (
    ErrorId BIGINT AUTO_INCREMENT PRIMARY KEY,
    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    BancoId INT NOT NULL,
    CuentaId VARCHAR(255) NULL,
    Etapa VARCHAR(50) NOT NULL,
    Error TEXT NOT NULL,
    LoteId VARCHAR(100) NULL,
    INDEX idx_error_banco_cuenta (BancoId, CuentaId),
    FOREIGN KEY (BancoId) REFERENCES Bancos(BancoId)
);

CREATE TABLE IF NOT EXISTS BancoCallbacks (
    CallbackId BIGINT AUTO_INCREMENT PRIMARY KEY,
    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    BancoId INT NOT NULL,
    CuentaId VARCHAR(255) NOT NULL,
    SaldoBs DECIMAL(18,4) NOT NULL,
    CodigoVerificacion CHAR(8) NOT NULL,
    Accepted BOOLEAN NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    INDEX idx_callback_banco_cuenta (BancoId, CuentaId),
    FOREIGN KEY (BancoId) REFERENCES Bancos(BancoId)
);

CREATE TABLE IF NOT EXISTS ConsistencyChecks (
    CheckId BIGINT AUTO_INCREMENT PRIMARY KEY,
    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    BancoId INT NOT NULL,
    CuentaId VARCHAR(255) NOT NULL,
    IsConsistent BOOLEAN NOT NULL,
    Details TEXT NOT NULL,
    INDEX idx_consistency_banco_cuenta (BancoId, CuentaId),
    FOREIGN KEY (BancoId) REFERENCES Bancos(BancoId)
);