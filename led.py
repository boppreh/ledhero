import fcntl
import os
import time
import random
import threading
import sys
import tty
import termios

class Keyboard(object):
    KDSETLED = 0x4B32
    code_by_name = {'numlock': 2, 'capslock': 4, 'scrolllock': 1}
    name_by_key = {47: 'numlock', 42: 'capslock', 45: 'scrolllock'}

    def __init__(self):
        self.state = {'numlock': False, 'capslock': False, 'scrolllock': False}
        self.console_fd = os.open('/dev/console', os.O_NOCTTY)

    def get(self):
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        return ch

    def __enter__(self):
        self.fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(self.fd)
        return self

    def __exit__(self, type, value, tb):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

    def update(self):
        code = 0
        for name, value in self.state.items():
            if value:
                code |= Keyboard.code_by_name[name]
        fcntl.ioctl(self.console_fd, Keyboard.KDSETLED, code)

def listen_for_keys(k, callback):
    while True:
        key = ord(k.get())
        if key in k.name_by_key:
            callback(k.name_by_key[key])

if __name__ == '__main__':
    with Keyboard() as k:
        def callback(name):
            k.state[name] = False
        key_thread = threading.Thread(target=listen_for_keys, args=(k, callback))
        key_thread.start()

        while True:
            for name in k.state:
                k.state[name] = k.state[name] or random.random() < 0.1
            k.update()
            time.sleep(0.1)

