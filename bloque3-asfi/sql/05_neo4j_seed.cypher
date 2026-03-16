// Grafo base para defensa de base no relacional orientada a grafos
MERGE (:Sistema {nombre: 'ASFI'});

UNWIND [
  {id:1,  nombre:'Banco Unión S.A.',                       algoritmo:'Cesar'},
  {id:2,  nombre:'Banco Mercantil Santa Cruz S.A.',       algoritmo:'Atbash'},
  {id:3,  nombre:'Banco Nacional de Bolivia S.A. (BNB)',  algoritmo:'Vigenere'},
  {id:4,  nombre:'Banco de Crédito de Bolivia S.A. (BCP)',algoritmo:'Playfair'},
  {id:5,  nombre:'Banco BISA S.A.',                       algoritmo:'Hill'},
  {id:6,  nombre:'Banco Ganadero S.A.',                   algoritmo:'DES'},
  {id:7,  nombre:'Banco Económico S.A.',                  algoritmo:'3DES'},
  {id:8,  nombre:'Banco Prodem S.A.',                     algoritmo:'Blowfish'},
  {id:9,  nombre:'Banco Solidario S.A.',                  algoritmo:'Twofish'},
  {id:10, nombre:'Banco Fortaleza S.A.',                  algoritmo:'AES'},
  {id:11, nombre:'Banco FIE S.A.',                        algoritmo:'RSA'},
  {id:12, nombre:'Banco PYME de la Comunidad S.A.',       algoritmo:'ElGamal'},
  {id:13, nombre:'Banco de Desarrollo Productivo S.A.M.', algoritmo:'ECC'},
  {id:14, nombre:'Banco de la Nación Argentina',          algoritmo:'ChaCha20'}
] AS banco
MERGE (b:Banco {bankId: banco.id})
SET b.nombre = banco.nombre,
    b.algoritmo = banco.algoritmo;

// Ejemplo de relación banco -> cuenta -> cliente
MERGE (cliente:Cliente {identificacion: '5977236805'})
MERGE (cuenta:Cuenta {cuentaId: 6490024209780150})
SET cuenta.saldoUsd = 3499999.0000,
    cuenta.saldoBs = 0.0
WITH cliente, cuenta
MATCH (b:Banco {bankId: 5})
MERGE (b)-[:POSEE]->(cuenta)
MERGE (cliente)-[:TITULAR_DE]->(cuenta);
