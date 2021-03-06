# -*- coding:utf-8 -*-
#
# Copyright © 2020 cGIfl300
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the “Software”),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from configuration import *
import os
import codecs
from pathlib import Path
import configparser
from structures import Tdl
import datetime


class SR:
    """ Save and Restaure class
    Permits to save the download queue on the hard drive and to restaure it.
    Usage:
    SR.save(dllist)
    SR.restaure(dllist)
    """

    def __init__(self, local_queue):
        self.dllist = local_queue

    def bool2char(self, val):
        # boolean to 0 or 1
        if val:
            return "1"
        else:
            return "0"

    def char2bool(self, val):
        # 0 or 1 to boolean
        if str(val) == "1":
            return True
        else:
            return False

    def save(self):
        # Save queue
        fname = Path(f"{repertoire_script}data{os.sep}dl.ini")
        if not fname.is_file():
            # if no queue folder found, then we create it
            try:
                os.mkdir(f"{repertoire_script}data")
            except:
                pass

        # We always erase the old queue
        configfile = codecs.open(f"{repertoire_script}data{os.sep}dl.ini", "w", "utf-8")

        config = configparser.ConfigParser()

        for el in self.dllist:
            # Replacing unwanted characters in date by 0
            cle = str(el.date_cre).replace(" ", "0")
            cle = cle.replace(":", "0")
            cle = cle.replace("-", "0")
            cle = cle.replace(".", "0")

            # Create the root key
            config[f"record{cle}"] = {}

            # Create record's subkeys
            config[f"record{cle}"]["URL"] = el.URL
            config[f"record{cle}"]["date_cre"] = str(el.date_cre)
            config[f"record{cle}"]["date_exp"] = str(el.date_exp)
            config[f"record{cle}"]["is_active"] = self.bool2char(el.is_active)
            config[f"record{cle}"]["is_audio"] = self.bool2char(el.is_audio)
            config[f"record{cle}"]["is_playlist"] = self.bool2char(el.is_playlist)
            config[f"record{cle}"]["is_video"] = self.bool2char(el.is_video)

        config.write(configfile)
        configfile.close()

    def restaure(self):
        # Restaure the queue
        a_retourner = []
        try:
            config = configparser.ConfigParser()
            config.read(f"{repertoire_script}data{os.sep}dl.ini")
        except:
            return []

        for el in config.sections():
            section = el
            el_temp = Tdl()
            el_temp.URL = config[f"{el}"]["url"]
            el_temp.date_cre = datetime.datetime.strptime(config[f"{el}"]["date_cre"], "%Y-%m-%d %H:%M:%S.%f")
            el_temp.date_exp = datetime.datetime.strptime(config[f"{el}"]["date_exp"], "%Y-%m-%d %H:%M:%S.%f")
            el_temp.is_active = self.char2bool(config[f"{el}"]["is_active"])
            el_temp.is_audio = self.char2bool(config[f"{el}"]["is_audio"])
            el_temp.is_playlist = self.char2bool(config[f"{el}"]["is_playlist"])
            el_temp.is_video = self.char2bool(config[f"{el}"]["is_video"])
            a_retourner.append(el_temp)

        self.dllist = a_retourner
        return a_retourner

    def run(self):
        print("Running!")
