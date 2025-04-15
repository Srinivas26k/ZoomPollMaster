import pyautogui
import time

print("Move your mouse to find coordinates.")
print("Press Ctrl+C to stop.")

try:
    while True:
        x, y = pyautogui.position()
        rgb = pyautogui.screenshot().getpixel((x, y))
        position_str = f'X: {x} Y: {y} RGB: {rgb}'
        print(position_str, end='')
        print('\b' * len(position_str), end='', flush=True)
        time.sleep(0.1)
except KeyboardInterrupt:
    print('\n\nDone! Coordinates captured.')