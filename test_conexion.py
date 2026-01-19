import pyodbc
import pandas as pd

import os
from dotenv import load_dotenv

load_dotenv()

def conectar_sage():
    try:
        # Estos datos te los dará el partner
        server = os.getenv('SAGE_SERVER')
        database = os.getenv('SAGE_DATABASE')
        username = os.getenv('SAGE_USERNAME')
        password = os.getenv('SAGE_PASSWORD')
        
        # El driver que instalamos en el paso 1
        conn_str = (
            f'DRIVER={{{driver}}};'
            f'SERVER={server},{port};'
            f'DATABASE={database};'
            f'UID={user};'
            f'PWD={password};'
            f'Encrypt=no;'
            f'TrustServerCertificate=yes;'
        )

        conn = pyodbc.connect(conn_str)
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