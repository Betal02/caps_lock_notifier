import os
import ctypes
from PIL import Image
import pystray
from pystray import MenuItem as item
import threading
import time
import keyboard
import configparser

status = True
config_file = r"C:\\Program Files\\CapsLockNotifier\\config.ini"
default_config = {
    'SETTINGS': {
        'popupMode': 'True'
    }
}

lock_close = Image.open(r"C:\\Program Files\\CapsLockNotifier\\img\\lock_close_blue.png")
lock_open = Image.open(r"C:\\Program Files\\CapsLockNotifier\\img\\lock_open_blue.png")


current_icon = None  # Variabile globale per l'icona corrente
popupMode = True  # Impostazione predefinita per il popup

def is_caps_lock_on():
    hllDll = ctypes.WinDLL("User32.dll")
    VK_CAPITAL = 0x14
    return hllDll.GetKeyState(VK_CAPITAL) & 0x0001

def close(icon):
    global status
    status = False
    icon.stop()

def disable_popup(icon):
    global popupMode
    popupMode = False
    update_config()

def enable_popup(icon):
    global popupMode
    popupMode = True
    update_config()

def setup(icon):
    icon.visible = True

def get_image():
    return lock_close if is_caps_lock_on() else lock_open

def show_popup(icon):
    if popupMode:
        if is_caps_lock_on():
            icon.notify("MAIUSCOLO ATTIVO")
        else:
            icon.notify("MAIUSCOLO NON ATTIVO")

def caps_lock_changed(event):
    global current_icon
    if event.event_type == keyboard.KEY_DOWN:
        show_popup(current_icon)
        if current_icon:
            current_icon.icon = get_image()

def run():
    global status, current_icon, popupMode
    
    icon = pystray.Icon('caps_lock_notify')
    icon.menu = pystray.Menu(
        item('Disattiva popup', disable_popup),
        item('Attiva popup', enable_popup),
        item('Chiudi', close)
    )
    icon.title = 'Caps Lock Notifier'
    icon.icon = get_image()
    
    current_icon = icon  # Imposta l'icona corrente

    keyboard.hook_key('caps lock', caps_lock_changed)
    icon.run(setup)

def update_config():
    config = configparser.ConfigParser()
    config.read(config_file)
    if not config.has_section('SETTINGS'):
        config['SETTINGS'] = {}
    config['SETTINGS']['popupMode'] = str(popupMode)
    
    with open(config_file, 'w') as configfile:
        config.write(configfile)

def read_config():
    if not os.path.exists(config_file):
        with open(config_file, 'w') as configfile:
            config = configparser.ConfigParser()
            config.read_dict(default_config)
            config.write(configfile)
    
    config = configparser.ConfigParser()
    config.read(config_file)
    global popupMode
    popupMode = config.getboolean('SETTINGS', 'popupMode', fallback=True)

if __name__ == '__main__':
    read_config()  # Legge le impostazioni dal file di configurazione all'avvio
    threading.Thread(target=run).start()

    try:
        while status:
            time.sleep(1)
    except KeyboardInterrupt:
        status = False
