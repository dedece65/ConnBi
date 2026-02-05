
import http.server
import socketserver
import urllib.parse
import pyodbc
import os
import webbrowser
from dotenv import load_dotenv

# Cargar variables
env_path = os.path.join(os.getcwd(), '.env')
load_dotenv(env_path, override=True)

PORT = 8000

# HTML básico con estilos inline para una apariencia decente
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consulta SQL Web</title>
    <style>
        body {{ font-family: sans-serif; background: #f4f4f9; padding: 20px; }}
        .container {{ max_width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        h2 {{ color: #333; }}
        textarea {{ width: 100%; height: 100px; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-family: monospace; }}
        button {{ background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin-top: 10px; font-size: 16px; }}
        button:hover {{ background: #218838; }}
        .result-box {{ margin-top: 20px; overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; color: #333; }}
        .error {{ color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 4px; }}
        .success {{ color: #155724; background: #d4edda; padding: 10px; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Ejecutor de Consultas SQL</h2>
        <form method="POST">
            <textarea name="query" placeholder="Escribe tu consulta SQL aquí...">{last_query}</textarea>
            <br>
            <button type="submit">Ejecutar Consulta</button>
        </form>

        <div class="result-box">
            {content}
        </div>
    </div>
</body>
</html>
"""

class QueryHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return # Silenciar logs de consola para limpieza

    def get_connection(self):
        # Lógica de conexión reutilizada
        server = os.getenv('DB_SERVER')
        username = os.getenv('DB_USER')
        password = os.getenv('DB_PASS')
        driver = os.getenv('DB_DRIVER')
        port = os.getenv('DB_PORT')

        if not all([server, username, password, driver, port]):
            raise ValueError("Faltan variables en .env")

        return pyodbc.connect(
            driver=f'{{{driver}}}',
            server=f'{server},{port}',
            database='2025FT',
            uid=username,
            pwd=password,
            Encrypt='no',
            TrustServerCertificate='yes'
        )

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(HTML_TEMPLATE.format(last_query="", content="").encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = urllib.parse.parse_qs(post_data)
        
        query = params.get('query', [''])[0].strip()
        result_html = ""
        
        if query:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute(query)

                try:
                    # Intento de fetch (SELECT)
                    columns = [column[0] for column in cursor.description]
                    rows = cursor.fetchall()
                    
                    # Construir tabla HTML
                    header = "".join(f"<th>{col}</th>" for col in columns)
                    body = ""
                    for row in rows:
                        cells = "".join(f"<td>{cell}</td>" for cell in row)
                        body += f"<tr>{cells}</tr>"
                    
                    result_html = f"""
                    <div class="success">✅ {len(rows)} filas devueltas.</div>
                    <table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>
                    """
                except pyodbc.ProgrammingError:
                    # No devuelve filas (INSERT/UPDATE)
                    conn.commit()
                    result_html = '<div class="success">✅ Operación ejecutada con éxito.</div>'
                
                conn.close()
            except Exception as e:
                result_html = f'<div class="error">❌ Error: {str(e)}</div>'
        else:
            result_html = '<div class="error">⚠️ La consulta estaba vacía.</div>'

        # Renderizar respuesta
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(HTML_TEMPLATE.format(last_query=query, content=result_html).encode('utf-8'))

if __name__ == "__main__":
    print(f"🚀 Iniciando servidor en http://localhost:{PORT}")
    print("Presiona Ctrl+C para detener.")
    
    # Intentar abrir el navegador automáticamente
    try:
        webbrowser.open(f"http://localhost:{PORT}")
    except:
        pass

    try:
        with socketserver.TCPServer(("", PORT), QueryHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido.")
    except Exception as e:
        print(f"\n❌ Error al iniciar servidor: {e}")
