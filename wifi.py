import asyncio
import network

from config import config


class Wifi:
    def __init__(self, led):
        self.led = led
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_ap = network.WLAN(network.AP_IF)

    async def connect(self):
        networks = config.networks
        if not networks:
            return False

        self.wlan_sta.active(True)
        
        # On parcourt la liste des réseaux enregistrés
        for net in networks:
            ssid = net["ssid"]
            password = net["password"]
            
            print(f"Tentative de connexion à : {ssid}...")
            self.wlan_sta.connect(ssid, password)
            
            # On attend 7 secondes par tentative
            attempt = 0
            while attempt < 7:
                if self.wlan_sta.isconnected():
                    print(f"Connecté avec succès à {ssid}!")
                    print("IP:", self.wlan_sta.ifconfig()[0])
                    # Flash rapide pour signaler le succès
                    for _ in range(5):
                        self.led.toggle()
                        await asyncio.sleep(1)
                    self.led.on()
                    return True
                
                attempt += 1
                self.led.toggle()
                time.sleep(1)
                
            print(f"Échec pour {ssid}.")
            self.wlan_sta.disconnect() # On déconnecte avant de tester le suivant
            
        return False

    def start_ap(self):
        ap_config = config.ap
        password = ap_config.get("password")
        if password:
            self.wlan_ap.config(essid=ap_config.get("ssid"), password=password)
        else:
            self.wlan_ap.config(essid=ap_config.get("ssid"), security=0)
        self.wlan_ap.active(True)
        self.led.off()
        print("IP du Point d'Accès: 192.168.4.1")

    async def monitor():
        while True:
            if not self.wlan_sta.isconnected() and not self.wlan_ap.active():
                print("Connexion perdue...")
                if not await self.connect():
                    self.start_ap()
            await asyncio.sleep(30)