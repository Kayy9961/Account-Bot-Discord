import websocket
import json
import threading
import time
import requests
import re

TOKEN = 'TU TOKEN DE DISCORD'
GATEWAY_URL = "wss://gateway.discord.gg/?v=9&encoding=json"
BASE_API_URL = "https://discord.com/api/v9"

def on_message(ws, message):
    data = json.loads(message)

    if data['t'] == 'READY':
        global user_id
        user_id = data['d']['user']['id']
        print(f"Conectado como: {data['d']['user']['username']}")

    if data['op'] == 10:  
        heartbeat_interval = data['d']['heartbeat_interval'] / 1000
        threading.Thread(target=heartbeat, args=(ws, heartbeat_interval)).start()
        payload = {
            'op': 2,
            'd': {
                'token': TOKEN,
                'properties': {
                    '$os': 'linux',
                    '$browser': 'chrome',
                    '$device': 'pc'
                }
            }
        }
        ws.send(json.dumps(payload))

    if data['t'] == 'MESSAGE_CREATE' and 'd' in data:
        handle_command(data['d'])

def heartbeat(ws, interval):
    while True:
        time.sleep(interval)
        heartbeat_payload = {
            'op': 1,
            'd': None
        }
        ws.send(json.dumps(heartbeat_payload))

def on_error(ws, error):
    print(f"Error: {error}")
def on_close(ws):
    print("Conexión cerrada")
def on_open(ws):
    print("Conexión establecida")
def start_connection():
    ws = websocket.WebSocketApp(GATEWAY_URL,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

def handle_command(message):
    content = message['content']
    channel_id = message['channel_id']
    
    match = re.match(r'\.eliminar\s*(\d+)?', content)
    if match and message['author']['id'] == user_id:
        print(f"Comando .eliminar recibido en el canal {channel_id}")
        num_messages = int(match.group(1)) if match.group(1) else None
        delete_user_messages(channel_id, num_messages)

def delete_user_messages(channel_id, num_messages=None):
    headers = {
        'Authorization': f'{TOKEN}',  
        'Content-Type': 'application/json'
    }
    url = f"{BASE_API_URL}/channels/{channel_id}/messages"
    params = {
        'limit': 100  
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        messages = response.json()
        delete_count = 0  
        
        user_messages = [msg for msg in messages if msg['author']['id'] == user_id]
        
        if num_messages is not None:
            user_messages = user_messages[:num_messages]
        for message in user_messages:
            delete_url = f"{BASE_API_URL}/channels/{channel_id}/messages/{message['id']}"
            delete_response = requests.delete(delete_url, headers=headers)
            
            if delete_response.status_code == 204:
                print(f"Mensaje {message['id']} eliminado.")
                delete_count += 1
                time.sleep(3) 
                
                if delete_count % 20 == 0:
                    print("Esperando 5 segundos después de eliminar 20 mensajes.")
                    time.sleep(5) 
            else:
                print(f"Error eliminando el mensaje {message['id']}: {delete_response.status_code}")
    else:
        print(f"Error obteniendo mensajes: {response.status_code}")

if __name__ == "__main__":
    start_connection()

#Fin
