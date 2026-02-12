import os
import asyncio
import json
import machine
import network
import time

from server import app

DEFAULT_AP = "Newton"
DEFAULT_AP_PASSWORD = "admin"

led = machine.Pin("LED", machine.Pin.OUT)
wlan_sta = network.WLAN(network.STA_IF)
wlan_ap = network.WLAN(network.AP_IF)
config = {}

try:
    with open("config.json", "r") as f:
        config = json.load(f)
except Exception as e:
    print(f"Erreur lecture config: {e}")
    config = None



def is_bootsel_pressed():
    # 0xd0000008 est l'adresse du registre GPIO_HI_IN sur le RP2040
    # Le bit 1 de ce registre correspond à l'état du bouton BOOTSEL
    # Le bouton est "actif bas" (0 quand on appuie)
    return not (machine.mem32[0xd0000000 + 0x08] & (1 << 1))


async def connect_to_wifi():
    networks = config.get("networks", []) if config else []
    if not networks:
        return False

    wlan_sta.active(True)
    
    # On parcourt la liste des réseaux enregistrés
    for net in networks:
        ssid = net["ssid"]
        password = net["password"]
        
        print(f"Tentative de connexion à : {ssid}...")
        wlan_sta.connect(ssid, password)
        
        # On attend 7 secondes par tentative
        attempt = 0
        while attempt < 7:
            if wlan_sta.isconnected():
                print(f"Connecté avec succès à {ssid}!")
                print("IP:", wlan_sta.ifconfig()[0])
                # Flash rapide pour signaler le succès
                for _ in range(5):
                    led.toggle()
                    await asyncio.sleep(1)
                led.on()
                return True
            
            attempt += 1
            led.toggle()
            time.sleep(1)
            
        print(f"Échec pour {ssid}.")
        wlan_sta.disconnect() # On déconnecte avant de tester le suivant
        
    return False

def start_access_point():
    ap_config = config.get("ap", {}) if config else {}
    wlan_ap.config(essid=ap_config.get("ssid", DEFAULT_AP), password=ap_config.get("password", DEFAULT_AP_PASSWORD))
    wlan_ap.active(True)
    led.off()
    print("IP du Point d'Accès: 192.168.4.1")


async def wifi_monitor():
    while True:
        if not wlan_sta.isconnected() and not wlan_ap.active():
            print("Connexion perdue...")
            if not await connect_to_wifi():
                start_access_point()
        await asyncio.sleep(30)


async def reset_monitor():
    while True:
        if is_bootsel_pressed():
            try:
                os.remove("config.json")
                for _ in range(10):
                    led.toggle()
                    await asyncio.sleep(0.05)
            except:
                pass
            finally:
                start_access_point()
        await asyncio.sleep(10)


async def main():
    if not await connect_to_wifi():
        start_access_point()
    
    await asyncio.gather(
        # On rend le serveur accessible depuis l'AP ou via le réseau local
        # si on est parvenu à se connecter à un réseau WiFi
        app.run(host="0.0.0.0", port=80),
        wifi_monitor(),
        reset_monitor(),
    )


if __name__ == "__main__":
    asyncio.run(main())