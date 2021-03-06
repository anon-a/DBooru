from threading import Thread
import importlib
import time
import socket
import main
import settings_file
import os


class BgTaskHost(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.port = 0
        
    def run(self):
        while True:
            try:
                self.background_host()
            except Exception:
                pass

    def background_host(self):
        import main
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('127.0.0.1', self.port))
        self.port = sock.getsockname()[1]
        while True:
            data, addr = sock.recvfrom(4)
            if data == b"UPDT":
                try:
                    main.update_db()
                except Exception:
                    sock.close()
                    del sock
                finally:
                    os.remove('update.lck')
        
class Settings_monitor(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.file = "settings_file.py"
        self.time = os.stat(self.file).st_mtime

    def run(self):
        while True:
            if self.time != os.stat(self.file).st_mtime:
                print("Settings changed, reloading")
                self.time = os.stat(self.file).st_mtime
                importlib.reload(settings_file)
            time.sleep(settings_file.polling_time)

class ThreadController(Thread):
    @staticmethod
    def log_debug(*args):
        j = ''
        for i in args:
            j += str(i)
        print("[DEBUG] " + str(j))

    def __init__(self):
        Thread.__init__(self)
        self.threads = []

    def run(self):
        self.watcher()

    def watcher(self):
        while True:
            time.sleep(1)
            p = 0
            for i in self.threads:
                if i.readiness == 1:
                    i.join()
                    self.threads.remove(i)
                    del i
                    p = p + 1
