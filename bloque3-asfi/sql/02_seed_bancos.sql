USE ASFI_Central;

INSERT INTO Bancos (BancoId, Nombre, AlgoritmoEncriptacion) VALUES
(1,  'Banco Unión S.A.',                             'Cesar'),
(2,  'Banco Mercantil Santa Cruz S.A.',             'Atbash'),
(3,  'Banco Nacional de Bolivia S.A. (BNB)',        'Vigenere'),
(4,  'Banco de Crédito de Bolivia S.A. (BCP)',      'Playfair'),
(5,  'Banco BISA S.A.',                             'Hill'),
(6,  'Banco Ganadero S.A.',                         'DES'),
(7,  'Banco Económico S.A.',                        '3DES'),
(8,  'Banco Prodem S.A.',                           'Blowfish'),
(9,  'Banco Solidario S.A.',                        'Twofish'),
(10, 'Banco Fortaleza S.A.',                        'AES'),
(11, 'Banco FIE S.A.',                              'RSA'),
(12, 'Banco PYME de la Comunidad S.A.',             'ElGamal'),
(13, 'Banco de Desarrollo Productivo S.A.M.',       'ECC'),
(14, 'Banco de la Nación Argentina',                'ChaCha20')
ON DUPLICATE KEY UPDATE
    Nombre = VALUES(Nombre),
    AlgoritmoEncriptacion = VALUES(AlgoritmoEncriptacion);
