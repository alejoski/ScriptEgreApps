import requests
import os

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
SCOPE = os.getenv("SCOPE")
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"


def obtener_token():
    data = {
        "client_id": CLIENT_ID,
        "scope": SCOPE,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    response = requests.post(TOKEN_URL, data=data)
    response.raise_for_status()
    return response.json()["access_token"]



####################################################################
# Envio de correo de notificacion al egresado
# Parametros:
#   - remitente: correo del remitente
#   - destinatario: correo del destinatario
#   - asunto: asunto del correo
#   - cuerpo: cuerpo del correo
#####################################################################
def enviar_correo_graph(remitente, destinatario, asunto, cuerpo):
    token = obtener_token()
    url = f"https://graph.microsoft.com/v1.0/users/{remitente}/sendMail"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    
    cuerpo = """
        <h3>Notificación de Actualización de cuenta Uniandes</h3>
        <br>
        <p>Estimado(a) Egresado(a),</p>
        <p>Le informamos que sus datos han sido actualizados exitosamente en nuestro sistema.</p>

    <p>Atentamente,</p>
    <p>El equipo de soporte</p>
    """
    
    mensaje = {
        "message": {
            "subject": asunto,
            "body": {
                "contentType": "HTML",
                "content": cuerpo
            },
            "toRecipients": [
                {"emailAddress": {"address": destinatario}}
            ]
        }
    }
    response = requests.post(url, headers=headers, json=mensaje)
    response.raise_for_status()
    return response.status_code == 202

# Ejemplo de uso:
# enviar_correo_graph("remitente@tu_dominio.com", "destinatario@dominio.com", "Asunto", "Cuerpo del mensaje")
