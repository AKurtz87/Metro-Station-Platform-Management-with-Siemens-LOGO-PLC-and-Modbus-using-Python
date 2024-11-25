import time
import random
import logging
import json
import zmq
from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor
from pymodbus.client import ModbusTcpClient

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Configurazione del PLC
PLC_CONFIG = {
    'ip': '192.168.1.3',
    'port': 510,
    'input_start': 0,
    'input_count': 4,
    'output_start': 8192,
    'output_count': 4
}

# Parametri treni
MIN_ARRIVAL_INTERVAL = 8
MAX_ARRIVAL_INTERVAL = 24
MIN_STOP_DURATION = 15
MAX_STOP_DURATION = 25
MIN_DEPARTURE_LIGHT_DURATION = 10
MAX_DEPARTURE_LIGHT_DURATION = 15

# Blocchi per binario
locks = [Lock() for _ in range(PLC_CONFIG['input_count'])]

# Dati condivisi per ZeroMQ
station_data = {
    "trains": [{"platform": i + 1, "status": "idle"} for i in range(PLC_CONFIG['input_count'])]
}

# Funzioni PLC
def set_output(client, output_start, output, state):
    try:
        coil_address = output_start + output
        client.write_coil(coil_address, state)
    except Exception as e:
        logger.error(f"Errore impostando l'uscita Q{output + 1}: {e}")

def read_inputs(client, start, count):
    try:
        result = client.read_discrete_inputs(start, count)
        return result.bits[:count] if not result.isError() else [False] * count
    except Exception as e:
        logger.error(f"Errore leggendo gli ingressi: {e}")
        return [False] * count

# Funzione per pubblicare aggiornamenti tramite ZeroMQ
def zmq_publisher():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://0.0.0.0:5556")
    logger.info("ZeroMQ publisher in ascolto su tcp://0.0.0.0:5556")
    while True:
        socket.send_json(station_data)
        time.sleep(1)  # Pubblica ogni secondo

# Gestione treni
def handle_train(client, platform):
    with locks[platform]:
        # Stato: Treno in arrivo
        station_data["trains"][platform]["status"] = "arriving"
        logger.info(f"Treno in arrivo al binario {platform + 1}.")

        # Simula l'arrivo del treno
        while True:
            set_output(client, PLC_CONFIG['output_start'], platform, True)
            time.sleep(0.5)
            set_output(client, PLC_CONFIG['output_start'], platform, False)
            time.sleep(0.5)
            if read_inputs(client, PLC_CONFIG['input_start'], PLC_CONFIG['input_count'])[platform]:
                break

        # Stato: Treno fermo
        station_data["trains"][platform]["status"] = "stopped"
        logger.info(f"Treno fermo al binario {platform + 1}.")
        time.sleep(random.randint(MIN_STOP_DURATION, MAX_STOP_DURATION))

        # Stato: Pronto a partire (luci lampeggianti)
        station_data["trains"][platform]["status"] = "ready_to_depart"
        logger.info(f"Treno pronto a partire dal binario {platform + 1} (luci lampeggianti).")
        while True:
            inputs = read_inputs(client, PLC_CONFIG['input_start'], PLC_CONFIG['input_count'])
            if not inputs[platform]:  # Il treno è pronto a partire
                break
            set_output(client, PLC_CONFIG['output_start'], platform, True)
            time.sleep(0.3)
            set_output(client, PLC_CONFIG['output_start'], platform, False)
            time.sleep(0.3)

        # Stato: Treno in partenza
        station_data["trains"][platform]["status"] = "departing"
        logger.info(f"Treno partito dal binario {platform + 1}.")
        set_output(client, PLC_CONFIG['output_start'], platform, True)
        time.sleep(random.randint(MIN_DEPARTURE_LIGHT_DURATION, MAX_DEPARTURE_LIGHT_DURATION))
        set_output(client, PLC_CONFIG['output_start'], platform, False)

        # Stato: Binario libero
        station_data["trains"][platform]["status"] = "idle"

def simulate_train_arrivals(client):
    with ThreadPoolExecutor(max_workers=4) as executor:
        while True:
            platform = random.randint(0, PLC_CONFIG['input_count'] - 1)
            if locks[platform].locked():
                time.sleep(2)
                continue
            executor.submit(handle_train, client, platform)
            time.sleep(random.randint(MIN_ARRIVAL_INTERVAL, MAX_ARRIVAL_INTERVAL))

# Main
def main():
    client = ModbusTcpClient(PLC_CONFIG['ip'], port=PLC_CONFIG['port'])
    if client.connect():
        logger.info(f"Connesso al PLC {PLC_CONFIG['ip']}:{PLC_CONFIG['port']}")
        try:
            # Avvia il publisher ZeroMQ in un thread separato
            Thread(target=zmq_publisher, daemon=True).start()
            # Simula gli arrivi dei treni
            simulate_train_arrivals(client)
        except KeyboardInterrupt:
            logger.info("Simulazione interrotta.")
        finally:
            client.close()
            logger.info("Connessione al PLC chiusa.")
    else:
        logger.error("Impossibile connettersi al PLC.")

if __name__ == "__main__":
    main()
