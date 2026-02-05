
import pyodbc
import os
from dotenv import load_dotenv


# Forzamos la carga explícita y verbose
env_path = os.path.join(os.getcwd(), '.env')
print(f"📂 Buscando .env en: {env_path}")
loaded = load_dotenv(env_path, override=True)
print(f"📂 ¿Archivo .env cargado?: {'SÍ' if loaded else 'NO'}")


def listar_bases_datos():
    print("🔍 Intentando conectar al servidor para listar bases de datos...")

    # Recuperamos variables con Fallbacks (SAGE_..., DB_USER, etc.)
    server = os.getenv('DB_SERVER')
    username = os.getenv('DB_USER')
    password = os.getenv('DB_PASS')
    driver = os.getenv('DB_DRIVER')
    port = os.getenv('DB_PORT')

    missing = []
    if not server: missing.append("DB_SERVER")
    if not username: missing.append("DB_USER")
    if not password: missing.append("DB_PASS")

    if missing:
        print(f"❌ Error: Faltan las siguientes variables de entorno: {', '.join(missing)}")

    import socket
    
    # ---------------------------------------------------------
    # DIAGNÓSTICO DE RED PREVIO
    # ---------------------------------------------------------
    print("\n  Diagnóstico de Red:")
    
    # Limpiamos el servidor de la instancia para el check de socket (ej: 192.168.1.10\SAGE -> 192.168.1.10)
    host_ip = server.split('\\')[0]
    host_ip = host_ip.split(',')[0]
    
    print(f"   Intentando conectar vía TCP a {host_ip}:{port} ...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3) # 3 segundos de timeout para el socket
    try:
        result = sock.connect_ex((host_ip, int(port)))
        if result == 0:
            print(f"   ✅ PUERTO {port} ABIERTO. El servidor es alcanzable.")
        else:
            print(f"   ❌ PUERTO {port} CERRADO o BLOQUEADO (Código: {result}).")
    except Exception as e:
        print(f"   ❌ Error al intentar conectar socket: {e}")
    finally:
        sock.close()
    
    print("-" * 30)

    # Conectamos a 'master' para poder ver el listado global
    # Usamos kwargs para que pyodbc maneje el escapado de contraseñas con caracteres especiales
    try:
        conn = pyodbc.connect(
            driver=f'{{{driver}}}',
            server=f'{server},{port}',
            database='master',
            uid=username,
            pwd=password,
            Encrypt='no',
            TrustServerCertificate='yes'
        )
        cursor = conn.cursor()
        
        # Consulta para obtener todas las bases de datos de usuario (excluyendo las del sistema)
        query = "SELECT \
    RTRIM(LTRIM(NOMBRE2)) AS [Nombre Empresa], \
    RTRIM(LTRIM(CIF)) AS [NIF] \
FROM [COMU0001].dbo.OPCEMP"

        cursor.execute(query)
        
        dbs = cursor.fetchall()
        
        print(f"Consulta: {query}")
        print(f"\n✅ Conexión exitosa. Se han encontrado {len(dbs)} datos:")
        print("-" * 40)
        for row in dbs:
            print(f"📁 {row}")
        print("-" * 40)
        
        conn.close()
    except Exception as e:
        print(f"\n❌ Error al conectar: {e}")

if __name__ == "__main__":
    listar_bases_datos()
