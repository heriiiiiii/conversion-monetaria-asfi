#!/usr/bin/env python3
"""
Script genérico de prueba de conexión y consultas a Bases de Datos.
Soporta: PostgreSQL, MariaDB/MySQL y MongoDB.

Permite configurar el motor, credenciales y consulta directamente en las 
variables al inicio del script o mediante argumentos de línea de comandos.

Dependencias requeridas (instalar con pip):
    pip install psycopg2-binary pymysql pymongo
"""

import argparse
import sys

# =============================================================================
# VARIABLES DE CONFIGURACIÓN POR DEFECTO
# (Puedes modificar estos valores directamente para definir el comportamiento por defecto)
# =============================================================================
DEFAULT_ENGINE = "postgres"  # Opciones: "postgres", "mariadb", "mysql", "mongodb"
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 5433          # Postgres es 5432 ó 5433 en tu docker. MariaDB: 3308. Mongo: 27017
DEFAULT_USER = "admin"
DEFAULT_PASSWORD = "admin123"
DEFAULT_DB = "banco_fie"

# Consultas por defecto según el motor si no se especifica otra
DEFAULT_SQL_QUERY = "SELECT * FROM cuentas LIMIT 5;"
DEFAULT_MONGO_QUERY = "{}" # Para mongo, representará un filtro find() vacío
# =============================================================================


def connect_postgres(host, port, user, password, dbname, query):
    try:
        import psycopg2
    except ImportError:
        print("❌ Error: psycopg2-binary no está instalado. Ejecuta: pip install psycopg2-binary")
        sys.exit(1)

    print(f"🔌 Conectando a PostgreSQL ({host}:{port} - DB: {dbname})...")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname
        )
        cursor = conn.cursor()
        
        # Si la consulta es solo listar tablas:
        if query.strip().upper() == "LIST TABLES":
            query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"

        print(f"▶ Ejecutando consulta: {query}")
        cursor.execute(query)
        
        rows = cursor.fetchall()
        print(f"\n✅ Resultados ({len(rows)} filas):")
        
        # Imprimir nombres de columnas si existen
        if cursor.description:
            col_names = [desc[0] for desc in cursor.description]
            print(" | ".join(col_names))
            print("-" * 50)
            
        for row in rows:
            print(row)
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")


def connect_mysql_mariadb(host, port, user, password, dbname, query, engine_name="MariaDB/MySQL"):
    try:
        import pymysql
    except ImportError:
        print("❌ Error: pymysql no está instalado. Ejecuta: pip install pymysql")
        sys.exit(1)

    print(f"🔌 Conectando a {engine_name} ({host}:{port} - DB: {dbname})...")
    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=dbname,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cursor:
            if query.strip().upper() == "LIST TABLES":
                query = "SHOW TABLES;"

            print(f"▶ Ejecutando consulta: {query}")
            cursor.execute(query)
            rows = cursor.fetchall()
            
            print(f"\n✅ Resultados ({len(rows)} filas):")
            if rows:
                print(" | ".join(rows[0].keys()))
                print("-" * 50)
                for row in rows:
                    print(" | ".join(str(val) for val in row.values()))
            else:
                print("(Sin resultados)")
                
        conn.close()
    except Exception as e:
        print(f"❌ Error conectando a {engine_name}: {e}")


def connect_mongodb(host, port, user, password, dbname, query):
    try:
        import pymongo
    except ImportError:
        print("❌ Error: pymongo no está instalado. Ejecuta: pip install pymongo")
        sys.exit(1)

    print(f"🔌 Conectando a MongoDB ({host}:{port} - DB: {dbname})...")
    try:
        # Construir URI de conexión
        uri = f"mongodb://{user}:{password}@{host}:{port}/?authSource=admin"
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Verificar conexión
        client.admin.command('ping')
        
        db = client[dbname]
        
        if query.strip().upper() == "LIST COLLECTIONS":
            collections = db.list_collection_names()
            print(f"\n✅ Colecciones en '{dbname}':")
            for col in collections:
                print(f" - {col}")
        else:
            # Asumimos que la consulta la hacemos sobre la colección 'cuentas' por defecto
            import ast
            print(f"▶ Ejecutando find() en colección 'cuentas' con filtro: {query}")
            
            try:
                filtro = ast.literal_eval(query) if query.strip() and query != "{}" else {}
            except Exception:
                print("⚠️ No se pudo parsear el query como diccionario, usando filtro vacío {}")
                filtro = {}
                
            docs = list(db.cuentas.find(filtro).limit(5))
            print(f"\n✅ Resultados ({len(docs)} documentos mostrados):")
            for doc in docs:
                print(doc)
                
        client.close()
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")


def main():
    parser = argparse.ArgumentParser(description="Cliente unificado de base de datos")
    parser.add_argument("--engine", default=DEFAULT_ENGINE, choices=["postgres", "mariadb", "mysql", "mongodb"])
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--db", default=DEFAULT_DB)
    parser.add_argument("--query", default=None, help="Query SQL (Ej: 'SELECT * FROM cuentas') o 'LIST TABLES'")
    
    args = parser.parse_args()
    
    # Resolver query
    if args.query is None:
        query = DEFAULT_MONGO_QUERY if args.engine == "mongodb" else DEFAULT_SQL_QUERY
    else:
        query = args.query

    print("=" * 60)
    print(f"🛠️  INICIANDO CLIENTE DB - Motor: {args.engine.upper()}")
    print("=" * 60)

    if args.engine == "postgres":
        connect_postgres(args.host, args.port, args.user, args.password, args.db, query)
    elif args.engine in ("mariadb", "mysql"):
        connect_mysql_mariadb(args.host, args.port, args.user, args.password, args.db, query, engine_name=args.engine)
    elif args.engine == "mongodb":
        connect_mongodb(args.host, args.port, args.user, args.password, args.db, query)

if __name__ == "__main__":
    main()
