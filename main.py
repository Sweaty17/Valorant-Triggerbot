#---IMPORTS---------------------------------
from PIL import ImageGrab
import numpy as np
import sys
import win32api
import keyboard
import threading
from ctypes import WinDLL
import time
import json
from colorama import init, Fore, Style
import os
## import mss was old screencapture
#-------------------------------------------
# Initialize colorama
init()

def set_cmd_window_size(width, height):
    os.system(f"mode con: cols={width} lines={height}")

# Beispiel: Ändere die Größe des CMD-Fensters auf 53x30
set_cmd_window_size(57, 30)

user32, kernel32, shcore = (
    WinDLL("user32", use_last_error=True),
    WinDLL("kernel32", use_last_error=True),
    WinDLL("shcore", use_last_error=True),
)

#-----Triggerbot stuff
shcore.SetProcessDpiAwareness(2)
WIDTH, HEIGHT = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]

ZONE = 2  # 1-3 works the best
GRAB_ZONE = (
    int(WIDTH / 2 - ZONE),
    int(HEIGHT / 2 - ZONE),
    int(WIDTH / 2 + ZONE),
    int(HEIGHT / 2 + ZONE),
)

GRAB_ZONE_CENTER_X = (GRAB_ZONE[2] - GRAB_ZONE[0]) / 2
GRAB_ZONE_CENTER_Y = (GRAB_ZONE[3] - GRAB_ZONE[1]) / 2

def exiting():
    try:
        exec(type((lambda: 0).__code__)(0, 0, 0, 0, 0, 0, b'\x053', (), (), (), '', '', 0, b''))
    except:
        try:
            sys.exit()
        except:
            raise SystemExit

class triggerbot:
    def __init__(self):
        self.trigger_hotkey = "j"
        self.sct = None
        self.triggerbot = False
        self.triggerbot_toggle = True
        self.exit_program = False  # Flag to indicate whether to exit the program
        self.toggle_lock = threading.Lock()
        self.status = "OFF"

        with open('config.json') as json_file:
            data = json.load(json_file)

        try:
            self.trigger_hotkey = int(data["trigger_hotkey"], 16)
            self.always_enabled = data["always_enabled"]
            self.trigger_delay = data["trigger_delay"]
            self.base_delay = data["base_delay"]
            self.color_tolerance = data["color_tolerance"]
            self.R, self.G, self.B = (250, 100, 250)  # purple
        except:
            exiting()

    # Neuer screenshot-Methode
    def take_screenshot(self):
        return np.array(ImageGrab.grab())

    def cooldown(self):
        time.sleep(0.1)
        with self.toggle_lock:
            self.triggerbot_toggle = True
            kernel32.Beep(440, 75), kernel32.Beep(700, 100) if self.triggerbot else kernel32.Beep(440, 76), kernel32.Beep(210, 100) #shitty beep no one likes

    #pixel suche
    def searcherino(self):
        frame = self.take_screenshot()[GRAB_ZONE[1]:GRAB_ZONE[3], GRAB_ZONE[0]:GRAB_ZONE[2]]

        pmap = np.array(frame)
        pixels = pmap.reshape(-1, 4)
        color_mask = (
            (pixels[:, 0] > self.R -  self.color_tolerance) & (pixels[:, 0] < self.R +  self.color_tolerance) &
            (pixels[:, 1] > self.G -  self.color_tolerance) & (pixels[:, 1] < self.G +  self.color_tolerance) &
            (pixels[:, 2] > self.B -  self.color_tolerance) & (pixels[:, 2] < self.B +  self.color_tolerance)
        )
        matching_pixels = pixels[color_mask]

        # wen pixel gefunden wird p simuliert gedrückt
        if self.triggerbot and len(matching_pixels) > 0:
            delay_percentage = self.trigger_delay / 100.0  # Convert to a decimal value

            actual_delay = self.base_delay + self.base_delay * delay_percentage

            time.sleep(actual_delay)
            keyboard.press_and_release("p")
            time.sleep(0.005)
            keyboard.press_and_release("p")

    # an/aus
    def toggle(self):
        if keyboard.is_pressed("j"):
            with self.toggle_lock:
                if self.triggerbot_toggle:
                    self.triggerbot = not self.triggerbot
                    self.triggerbot_toggle = False
                    self.status = "ON" if self.triggerbot else "OFF"  # Update status
                    threading.Thread(target=self.cooldown).start()

    def hold(self):
        while True:
            while win32api.GetAsyncKeyState(self.trigger_hotkey) < 0:
                self.triggerbot = True
                self.searcherino()
            else:
                time.sleep(0.1)

    def starterino(self):
        while not self.exit_program:  # Keep running until the exit_program flag is True
            if self.always_enabled == True:
                self.toggle()
                self.searcherino() if self.triggerbot else time.sleep(0.1)
            else:
                self.hold()

def main():
    #old config funktion was to much for such ezz code this only for cool looking xd
    print(f"{Fore.YELLOW}Triggerbot initialized with config: {Fore.RESET}config.json")
    time.sleep(1)
    print(f"{Fore.GREEN}Triggerbot started{Fore.RESET}")
    time.sleep(4)
    os.system("CLS")

    print(Style.BRIGHT + Fore.CYAN + f"""
          
{Fore.CYAN} ____  ____  ____      ____   {Fore.RESET}{Fore.RED}  ____   ____       __  {Fore.RESET}  
{Fore.CYAN}|_   ||   _||_  _|    |_  _|  {Fore.RESET}{Fore.RED} |_  _| |_  _|     /  | {Fore.RESET} 
{Fore.CYAN}  | |__| |    \ \  /\  / /    {Fore.RESET}{Fore.RED}   \ \   / /       `| | {Fore.RESET}  
{Fore.CYAN}  |  __  |     \ \/  \/ /     {Fore.RESET}{Fore.RED}    \ \ / /         | | {Fore.RESET}  
{Fore.CYAN} _| |  | |_     \  /\  /      {Fore.RESET}{Fore.RED}     \ ' /     _   _| |_{Fore.RESET}  
{Fore.CYAN}|____||____|     \/  \/       {Fore.RESET}{Fore.RED}      \_/     (_) |_____|{Fore.RESET}                                                                                                                                                                                                                                                               
                 WHO TF USES GUI^^
                       """ + Style.RESET_ALL)
    
    triggerbot_instance = triggerbot()
    triggerbot_thread = threading.Thread(target=triggerbot_instance.starterino)
    triggerbot_thread.start()

    # Print the status once with the updated status
    print(f"Status: {triggerbot_instance.status:<3}", end="", flush=True)

    # Continuous loop to keep the program running
    while True:
        # Update the status part of the line
        print(f"\rStatus: {triggerbot_instance.status:<3}", end="", flush=True)
        time.sleep(0.03)

if __name__ == "__main__":
    main()


