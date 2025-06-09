import requests
import time
import os
import smtplib
from email.message import EmailMessage
from twilio.rest import Client
from os import getenv
from dotenv import load_dotenv

load_dotenv()
# --- Configurações ---
API_URL = "https://www.supermercadosdalben.com.br/api/public/evento-experiencia/categoria?categoria_id=-1"
ID_FILE = "last_event_id.txt"

# Gmail
EMAIL_ADDRESS = "glaucosixx@gmail.com"
EMAIL_PASSWORD = getenv("senha_gmail")
EMAIL_DESTINO = "paullagsf@gmail.com,glaucolmf@hotmail.com,glaucowow@hotmail.com.br"

# Twilio
TWILIO_SID = "AC701d4bff81da8244199367fc6454f28f"
TWILIO_AUTH_TOKEN = getenv("twilio_token")
TWILIO_PHONE_NUMBER = "+13393296702"  # Número Twilio
WHATSAPP_TO = "whatsapp:+5535991482323"  # Ex: whatsapp:+5511999999999
SMS_TO = "+5535991482323"  # Ex: +5511999999999

HEADERS = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'origin': 'https://experienciasdalben.com.br',
    'referer': 'https://experienciasdalben.com.br/',
    'user-agent': 'Mozilla/5.0'
}


def load_last_seen_id():
    if os.path.exists(ID_FILE):
        with open(ID_FILE, "r") as f:
            return int(f.read().strip())
    return -1

def save_last_seen_id(event_id):
    with open(ID_FILE, "w") as f:
        f.write(str(event_id))

def fetch_events():
    try:
        response = requests.get(API_URL, headers=HEADERS)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        print(f"Erro ao buscar eventos: {e}")
        return []

def send_email(subject, content):
    for email in EMAIL_DESTINO.split(","):
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email
        msg.set_content(content)

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)
                print("✅ E-mail enviado.")
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")

def send_whatsapp_sms(message):
    # for number in WHATSAPP_TO.split(","):
    #     try:
    #         client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    #         # WhatsApp
    #         client.messages.create(
    #             body=message,
    #             from_="whatsapp:" + TWILIO_PHONE_NUMBER,
    #             to=number
    #         )
    #         print("✅ WhatsApp enviado.")


    #     except Exception as e:
    #         print(f"Erro ao enviar WhatsApp: {e}")

    for number in SMS_TO.split(","):
        try:
            client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

            # SMS
            client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=number
            )
            print("✅ SMS enviado.")

        except Exception as e:
            print(f"Erro ao enviar SMS: {e}")

            

def main():
    last_seen_id = load_last_seen_id()
    print(f"Iniciando monitoramento. Último ID conhecido: {last_seen_id}")

    while True:
        events = fetch_events()
        if events:
            for event in events:
                current_id = event.get("id")
                local = event.get("local", "").lower()
                if current_id > last_seen_id and "valinhos" in local:
                    nome = event["nome"]
                    local = event["local"]
                    mensagem = f"🆕 Novo evento em Valinhos!\n\n📌 Nome: {nome}\n📍 Local: {local}\n🆔 ID: {current_id}"

                    print(mensagem)
                    # send_email("Novo Evento em Valinhos!", mensagem)
                    send_whatsapp_sms(mensagem)

                    save_last_seen_id(current_id)
                    last_seen_id = current_id
                    break
        else:
            print("Nenhum evento encontrado.")

        time.sleep(60)

if __name__ == "__main__":
    main()
