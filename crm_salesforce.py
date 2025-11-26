import requests
import os

# Configuración de credenciales Salesforce
SF_CLIENT_ID = os.getenv("SF_CLIENT_ID")
SF_CLIENT_SECRET = os.getenv("SF_CLIENT_SECRET")
SF_USERNAME = os.getenv("SF_USERNAME")
SF_PASSWORD = os.getenv("SF_PASSWORD")
SF_TOKEN_URL = os.getenv("SF_TOKEN_URL")
SF_API_URL = os.getenv("SF_API_URL")

def obtener_token_salesforce():
    data = {
        'grant_type': 'password',
        'client_id': SF_CLIENT_ID,
        'client_secret': SF_CLIENT_SECRET,
        'username': SF_USERNAME,
        'password': SF_PASSWORD
    }
    response = requests.post(SF_TOKEN_URL, data=data)
    response.raise_for_status()
    return response.json()['access_token']

def crear_multipurpose(numero_documento):
    token = obtener_token_salesforce()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    body = {
        'numeroDocumento': str(numero_documento)
    }
    response = requests.post(SF_API_URL, headers=headers, json=body)
    response.raise_for_status()
    return response.json()  # O response.text si la respuesta no es JSON

# Ejemplo de uso:
resultado = crear_multipurpose("1001342560")
print(resultado)
