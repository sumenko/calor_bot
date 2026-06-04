import sys
import time

sym = '■'
label = 'Inbound'
label = '∙'
duration = 100 # sec
bar_len = 20

for elapsed in range(duration):
    filled = int(elapsed / duration * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)
    speed = elapsed
    sys.stdout.write(f'\r{label} [{bar}]  {speed:>7.2f} Мбит/с')
    sys.stdout.flush()
    time.sleep(0.1)