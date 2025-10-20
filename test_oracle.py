import os
from dotenv import load_dotenv
from modules.oracle import OracleConnector

# Cargar variables de entorno desde .env.example
load_dotenv('./batch_script/.env')

def test_oracle_connection():
    import os
    print('Directorio actual:', os.getcwd())
    print('¿Existe .env?', os.path.isfile('.env'))
    print('Probando conexión a Oracle...')
    print('ORACLE_USER:', os.getenv('ORACLE_USER'))
    print('ORACLE_PASSWORD:', os.getenv('ORACLE_PASSWORD'))
    print('ORACLE_DSN:', os.getenv('ORACLE_DSN'))
    oracle = OracleConnector()
    oracle.connect()
    if oracle.connection:
        print('Conexión exitosa a Oracle!')
        oracle.close()
    else:
        print('No se pudo conectar a Oracle. Revisa los parámetros y el mensaje de error anterior.')

if __name__ == "__main__":
    test_oracle_connection()
