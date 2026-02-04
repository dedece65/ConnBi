
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
    
    
    # Debug: Imprimir claves disponibles (sin valores sensibles/completos) para depurar
    print("\n🔎 Claves encontradas en el entorno (filtradas):")
    for k in os.environ:
        if any(x in k.upper() for x in ['DB_', 'SAGE', 'USER', 'PASS', 'SERVER']):
            # Mostramos el nombre y si tiene valor (oculto)
            val_masked = '*' * 5 if os.environ[k] else '[VACÍO]'
            print(f"   - {k}: {val_masked}")
    print("-" * 30)

    # Recuperamos variables con Fallbacks (SAGE_..., DB_USER, etc.)
    server = os.getenv('DB_SERVER') or os.getenv('SAGE_SERVER')
    
    username = os.getenv('DB_USERNAME') or os.getenv('DB_USER') or os.getenv('SAGE_USERNAME') or os.getenv('SAGE_USER')
    
    password = os.getenv('DB_PASSWORD') or os.getenv('DB_PASS') or os.getenv('SAGE_PASSWORD')
    
    driver = os.getenv('DB_DRIVER') or os.getenv('SAGE_DRIVER') or 'ODBC Driver 17 for SQL Server'
    port = os.getenv('DB_PORT') or os.getenv('SAGE_PORT') or '1433'

    missing = []
    if not server: missing.append("DB_SERVER (o SAGE_SERVER)")
    if not username: missing.append("DB_USERNAME (o DB_USER, SAGE_USERNAME)")
    if not password: missing.append("DB_PASSWORD (o SAGE_PASSWORD)")

    if missing:
        print(f"❌ Error: Faltan las siguientes variables de entorno: {', '.join(missing)}")
        
        # Diagnóstico inteligente: ¿Usas nombres antiguos?
        check_sage = os.getenv('SAGE_SERVER')
        if check_sage:
            print("\n⚠️  ¡AVISO! He detectado variables que empiezan por 'SAGE_' (ej. SAGE_SERVER).")
            print("   El script actual espera 'DB_' (DB_SERVER, DB_USERNAME...).")
            print("   -> Por favor, renombra las variables en tu archivo .env o actualiza el script.")
        else:
            print("\nRevisa tu archivo .env y asegúrate de que tienes:")
            print("DB_SERVER=...\nDB_USERNAME=...\nDB_PASSWORD=...")
        return

    import socket
    
    # ---------------------------------------------------------
    # DIAGNÓSTICO DE RED PREVIO
    # ---------------------------------------------------------
    print("\n🩺 Diagnóstico de Red:")
    
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
            print("      Posibles causas:")
            print("      1. Firewall de Windows bloqueando el puerto 1433.")
            print("      2. SQL Server no está configurado para permitir conexiones remotas (TCP/IP).")
            print("      3. La dirección IP del servidor es incorrecta.")
            print("      4. Si usas instancia con nombre (ej: SERVIDOR\\SAGE), comprueba si el puerto es dinámico.")
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
        query = "SELECT name FROM sys.databases WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb') ORDER BY name"
        cursor.execute(query)
        
        dbs = cursor.fetchall()
        
        print(f"\n✅ Conexión exitosa. Se han encontrado {len(dbs)} bases de datos:")
        print("-" * 40)
        for row in dbs:
            print(f"📁 {row.name}")
        print("-" * 40)
        print("Busca nombres como 'COMUNES', 'Ejer2024', o el nombre de tu empresa.")
        
        conn.close()
    except Exception as e:
        print(f"\n❌ Error al conectar: {e}")
        print("Verifica que DB_SERVER, DB_USERNAME y DB_PASSWORD sean correctos en tu .env")

if __name__ == "__main__":
    listar_bases_datos()
