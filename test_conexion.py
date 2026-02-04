import pyodbc
import pandas as pd

import os
from dotenv import load_dotenv

load_dotenv()

def conectar_sage():
    try:
        # Estos datos te los dará el partner
        server = os.getenv('DB_SERVER')
        database = os.getenv('DB_DATABASE')
        username = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        driver = os.getenv('DB_DRIVER')
        port = os.getenv('DB_PORT')
        
        # Usamos kwargs para seguridad y manejo de caracteres especiales
        conn = pyodbc.connect(
            driver=f'{{{driver}}}',
            server=f'{server},{port}',
            database=database,
            uid=username,
            pwd=password,
            Encrypt='no',
            TrustServerCertificate='yes'
        )


        print("✅ Conexión exitosa a Sage 50")
        return conn
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# Prueba de lectura
conexion = conectar_sage()
if conexion:
    # Esta query es un ejemplo, cámbiala por la de tu bot
    query = "SELECT TOP 10 * FROM [Gestion!Factu]"
    df = pd.read_sql(query, conexion)
    print(df)
    conexion.close()