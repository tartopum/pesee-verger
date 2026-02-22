import asyncio
import machine
import time

from config import config
from server import app
from wifi import Wifi

led = machine.Pin("LED", machine.Pin.OUT)
config.load()
wifi = Wifi(led)


def is_bootsel_pressed():
    # 0xd0000008 est l'adresse du registre GPIO_HI_IN sur le RP2040
    # Le bit 1 de ce registre correspond à l'état du bouton BOOTSEL
    # Le bouton est "actif bas" (0 quand on appuie)
    return not (machine.mem32[0xd0000000 + 0x08] & (1 << 1))

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
    if not await wifi.connect():
        wifi.start_ap()
    
    await asyncio.gather(
        # On rend le serveur accessible depuis l'AP ou via le réseau local
        # si on est parvenu à se connecter à un réseau WiFi
        app.run(host="0.0.0.0", port=80),
        wifi.monitor(),
        reset_monitor(),
    )


if __name__ == "__main__":
    asyncio.run(main())