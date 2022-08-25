import time
from struct import unpack

from datetime import date

today = date.today()
print(today)

import keyboard

print(time.time())

data = b"T\x08\xf9\x06\x90\x00a\x00\x00{\x00\x1c\x00"
print(data[11:14])
print(unpack("<H", data[11:14])[0])


while True:
    print("I'm looping forever!!")
    if keyboard.is_pressed("Esc"):
        break


t2 = time.time()

print(t2 - t)
