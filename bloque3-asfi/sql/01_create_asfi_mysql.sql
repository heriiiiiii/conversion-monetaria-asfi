CREATE DATABASE IF NOT EXISTS ASFI_Central;
USE ASFI_Central;

CREATE TABLE IF NOT EXISTS Bancos (
    BancoId INT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    AlgoritmoEncriptacion VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS Cuentas (
    CuentaId BIGINT NOT NULL,
    BancoId INT NOT NULL,
    SaldoUSD DECIMAL(18,4) NOT NULL,
    SaldoBs DECIMAL(18,4) NULL,
    FechaConversion DATETIME NULL,
    CodigoVerificacion CHAR(8) NULL,
    PRIMARY KEY (CuentaId, BancoId),
    CONSTRAINT fk_cuentas_bancos
        FOREIGN KEY (BancoId) REFERENCES Bancos(BancoId)
);