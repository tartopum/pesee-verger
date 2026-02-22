from machine import I2C, Pin
import time

from config import config


# https://wiki.dfrobot.com/SKU_DFR1184_Gravity_2-Channel_15Bit_0-10V_ADC_Module
# https://github.com/DFRobot/DFRobot_ADS1115_0_10V/blob/master/python/raspberrypi/DFRobot_ADS1115_0_10V.py
i2c = I2C(0, sda=Pin(config.pressure_sensor["pin_sda"]), scl=Pin(config.pressure_sensor["pin_scl"]), freq=100000)

def read_pressure_voltage():
    REG_SELECT_CHANNEL = 0x20
    REG_READ_VOLTAGE = 0x31

    try:
        # 1. Sélectionner le canal (0x01 ou 0x02)
        i2c.writeto_mem(
            config.pressure_sensor["addr"],
            REG_SELECT_CHANNEL,
            bytes([config.pressure_sensor["channel"]])
        )
        time.sleep(0.05) # Petit délai pour laisser le temps au MCU de traiter
        
        # 2. Lire 3 octets depuis le registre 0x31
        # Le module renvoie la tension sous forme d'entier (0.01 mV par unité)
        data = i2c.readfrom_mem(
            config.pressure_sensor["addr"],
            REG_READ_VOLTAGE,
            3
        )
        
        # 3. Combiner les octets (Poids fort -> Poids faible)
        raw_val = (data[0] << 16) | (data[1] << 8) | data[2]
        
        # 4. Conversion en mV (le module renvoie des centièmes de mV)
        voltage_mv = raw_val / 100.0
        return voltage_mv
    except Exception as e:
        print("Erreur de lecture :", e)
        return None