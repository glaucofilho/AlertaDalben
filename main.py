import requests
import time
import os

API_URL = "https://www.supermercadosdalben.com.br/api/public/evento-experiencia/categoria?categoria_id=-1"
HEADERS = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'origin': 'https://experienciasdalben.com.br',
    'referer': 'https://experienciasdalben.com.br/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0'
}
ID_FILE = "last_event_id.txt"

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
                    print(f"\n🆕 Novo evento em Valinhos detectado:")
                    print(f"📌 Nome: {event['nome']}")
                    print(f"📍 Local: {event['local']}")
                    print(f"🆔 ID: {current_id}")
                    save_last_seen_id(current_id)
                    last_seen_id = current_id
                    break  # Para de verificar após encontrar o mais novo evento válido
                else:
                    print("Nenhum novo evento relevante.")
                    break
        else:
            print("Nenhum evento encontrado.")
        
        time.sleep(60)  # Espera 1 minuto

if __name__ == "__main__":
    main()
