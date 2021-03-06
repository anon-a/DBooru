import gc
import os
import socket
import sys
import time
import logging
from threading import Thread

import requests

import settings_file

from . import input_parser as ip
from . import threads as TC

global is_error_code
is_error_code = False


class Loader(Thread):
    def __init__(self, url, fileid, fileform=''):
        Thread.__init__(self)
        self.readiness = 0
        self.url = url
        self.id = fileid
        self.format = fileform
        self.raw_data = b''
        self.proxy = settings_file.enable_proxy
        self.ip = settings_file.proxy_ip
        self.port = settings_file.proxy_port
        self.tmp = None
        if settings_file.suppress_errors is True:
            logging.raiseExceptions = False

    def run(self):
        print(f"Receiving {self.id}") if self.format == '' else ''
        try:
            self.get_raw_image()
        except:
            self.readiness = 1
            return
        print(f"Wiritng {self.id}") if self.format == '' else ''
        self.writer()
        self.readiness = 1
        del self.raw_data
        return

    def get_raw_image(self):
        with requests.Session() as s:
            s.headers = {
                'User-Agent': 'DBooru/2.0 (Image Loader module) (github.com/mcilya/DBooru)'}
            if self.proxy is False:
                self.tmp = s.get(
                    "{}".format(self.url), verify=settings_file.ssl_verify)
            else:
                self.tmp = s.get(
                    "{}".format(self.url),
                    proxies=dict(https='{}://{}:{}'.format(settings_file.proxy_type, self.ip, self.port), 
                    http='{}://{}:{}'.format(settings_file.proxy_type, self.ip, self.port)), verify=settings_file.ssl_verify)
            if self.tmp.status_code >= 400:
                global is_error_code
                is_error_code = True
                return
            else:
                self.raw_data = self.tmp.content

    def writer(self):
        try:
            open(settings_file.images_path + self.id + (('.' + self.format) if self.format != '' else ''), 'rb').close()
        except FileNotFoundError:
            with open(settings_file.images_path + self.id + (('.' + self.format) if self.format != '' else ''), 'wb') as file:
                file.write(self.raw_data)
                file.flush()


def run(module, file, check_files=True, check_local=True, endwith="\r"):
    tc = TC.ThreadController()
    tc.start()
    if settings_file.suppress_errors is True:
        logging.raiseExceptions = False
    try:
        os.mkdir(settings_file.images_path)
    except FileExistsError:
        pass
    parsed = ip.name_tag_parser(file)
    chk = len(parsed)
    print("Loading Images" + " " * 32, flush=True, end=endwith)
    c = 0
    if "PyPy" in sys.version:
        slp = 0.1
    else:
        slp = 0.2
    if check_files is True:
        for i in range(chk):
            print(
                "Loading image {} of {} ({}% done) (Running threads {})".format(
                    i, chk, format(((i/chk)*100), '.4g'), len(tc.threads)) + " " * 32,
                flush=True, end=endwith)
            try:
                open(settings_file.images_path +
                     str(parsed[i][7] + parsed[i][0]) + '.' + parsed[i][1], 'rb').close()
            except FileNotFoundError:
                if is_error_code == True:
                    break
                t = Loader(parsed[i][2],
                           str(parsed[i][7] + parsed[i][0]),
                           parsed[i][1])
                t.start()
                tc.threads.append(t)
                time.sleep(slp)
                if len(tc.threads) < settings_file.thread_cap:
                    pass
                else:
                    time.sleep(settings_file.sleep_time)
    else:
        for i in range(chk):
            print(f"Loading image {i} of {chk} ({format(((i/chk)*100), '.4g')}% done) (Running threads {len(tc.threads)})" + " " * 32, flush=True, end=endwith)
            if is_error_code == True:
                break
            t = Loader(parsed[i][2],
                       str(parsed[i][7] + parsed[i][0]),
                       parsed[i][1])
            t.start()
            tc.threads.append(t)
            time.sleep(module.slp)
            if len(tc.threads) < settings_file.thread_cap:
                pass
            else:
                time.sleep(settings_file.sleep_time)
    while len(tc.threads) > 0:
        gc.collect()
        print("Waiting {} thread(s) to end routine".format(
            len(tc.threads)) + " " * 32, flush=True, end=endwith)
        if c >= settings_file.time_wait and len(tc.threads) < 5:
            tc.threads = []
        elif len(tc.threads) < 5:
            print("Left to download {}".format(str([x.id for x in [x for x in tc.threads]]))+ " "*32, end=endwith)
            time.sleep(1)
            c += 1
    del tc
