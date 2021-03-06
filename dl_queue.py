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

from tkinter import *
import gettext
from configuration import *
from structures import *
import datetime
import subprocess
from time import strftime
from image_set import image_set
from class_dl import dl
import time
from threading import Thread
from setup_gui import Setup_GUI

from class_sr import SR

fr = gettext.translation("base", localedir=repertoire_script + "locales", languages=[langue_appli], fallback=False)
fr.install()
_ = fr.gettext
ngettext = fr.ngettext


class dl_queue(Toplevel):
    """ Interface graphique ...
    """

    def __init__(self, debug=False):
        Toplevel.__init__(self)
        self.debug = debug
        self.Tdl_list = []
        self.interval = check_interval * 1000

    def interface(self):
        """ Interface de la fenêtre
        """
        self.title(_("pYdl - Serveur"))
        self.geometry("400x600")
        self.iconphoto(False, PhotoImage(file=f"{repertoire_script}images{os.sep}icone.png"))

        self.panel_001 = Label(self, bg=couleur_fond)
        self.panel_002 = Canvas(self, background=couleur_fond)
        self.panel_003 = Canvas(self, background=couleur_fond)
        self.vsb = Scrollbar(self.panel_002, orient="vertical", command=self.panel_002.yview)
        self.panel_002.configure(yscrollcommand=self.vsb.set)
        self.frame = Frame(self.panel_002, background=couleur_fond)
        self.panel_002.create_window((1, 1), window=self.frame, anchor="nw", tags="self.frame")

        self.top_time = image_set(self.panel_001, f"images{os.sep}horloge")
        self.time_message = Label(
            self.panel_001,
            text=_("Téléchargement autorisé de\n{} h à {} h").format(h_dep, h_fin),
            bg=couleur_fond,
            fg=couleur_texte,
        )
        self.btn_clear = Button(
            self.panel_003,
            text=_("Vider"),
            command=self.apply_clear,
            bg=couleur_fond_saisie,
            fg=couleur_texte_saisie,
            activebackground=couleur_texte_saisie,
            activeforeground=couleur_fond_saisie,
        )

        """ Implantation des composants
        """

        self.panel_001.pack(expand=True, fill=BOTH)
        self.panel_002.pack(expand=True, fill=BOTH)
        self.panel_003.pack(expand=True, fill=BOTH)
        self.vsb.pack(side="right", fill="y")

        self.time_message.pack(expand=True, fill=BOTH)
        self.btn_clear.pack(expand=True, fill=BOTH)

        """ Binding
        """

        self.panel_002.bind("<Configure>", self.onFrameConfigure)
        self.top_time.btn.bind("<Button-1>", self.do_Setup)

    def apply_clear(self):
        del self.Tdl_list[:]
        sauvegarde = SR(local_queue=self.Tdl_list)
        sauvegarde.save()
        self.refresh_list()

    def do_Setup(self, event):
        app = Setup_GUI()
        app.run()

    def onFrameConfigure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.panel_002.config(scrollregion=self.panel_002.bbox("all"))

    def run(self):
        self.interface()
        self.after(self.interval, self.check_queue)

    def add_tdl(self, download):
        self.Tdl_list.append(download)
        sauvegarde = SR(local_queue=self.Tdl_list)
        self.Tdl_list = sauvegarde.save()
        self.refresh_list()

    def refresh_list(self):
        sauvegarde = SR(local_queue=self.Tdl_list)
        self.Tdl_list = sauvegarde.restaure()

        for enfant in self.frame.winfo_children():
            enfant.destroy()
        cursor = 0
        for download in self.Tdl_list:
            selection = dl(master=self.frame, tdl=download)
            selection.run()
            selection.grid(row=cursor, column=0)
            cursor += 1

        sauvegarde.save()

    def check_queue(self):
        heure = int(datetime.datetime.now().strftime("%H"))
        self.refresh_list()

        if (heure >= h_dep) and (heure <= h_fin):

            # Suppression des téléchargement obsolètes
            for download in self.Tdl_list:

                if (download.date_exp - datetime.datetime.now()).total_seconds() < 0:
                    # Download time expired or download done
                    self.Tdl_list.remove(download)

            # Lancement des téléchargements
            for download in self.Tdl_list:
                if (download.date_cre - datetime.datetime.now()).total_seconds() < 0:
                    download.is_active = True
                    sauvegarde = SR(local_queue=self.Tdl_list)
                    self.Tdl_list = sauvegarde.save()
                    # thread_001 = letsdl_fake(download)
                    thread_001 = letsdl(download)
                    thread_001.start()
                    self.refresh_list()
                    self.update()

                    # On supprime le téléchargement actif de la liste
                    for el in self.Tdl_list:
                        if el.is_active:
                            self.Tdl_list.remove(el)
                    sauvegarde = SR(local_queue=self.Tdl_list)
                    self.Tdl_list = sauvegarde.save()

                    # On attends la fin du téléchargement
                    thread_001.join()
                    break
        self.after(self.interval, self.check_queue)


class letsdl_fake(Thread):
    def __init__(self, download):
        Thread.__init__(self)
        self.download = download

    def run(self):
        time.sleep(1)
        print(f"{self.download.URL} est maintenant téléchargé")


class letsdl(Thread):
    def __init__(self, download):
        Thread.__init__(self)
        self.download = download

    def run(self):
        # Lancement de l'encodage
        # MP3 Version
        if self.download.is_audio:
            try:
                if self.download.is_playlist:
                    subprocess.call(
                        f"{path_youtubedl} -q -x --audio-format mp3 {self.download.URL} -o '{path_mp3}%(playlist_index)s - %(title)s.%(ext)s'",
                        shell=True,
                    )
                else:
                    subprocess.call(
                        f"{path_youtubedl} -q -x --audio-format mp3 {self.download.URL} -o '{path_mp3}%(title)s.%(ext)s'",
                        shell=True,
                    )
            except:
                pass
        # Video Version
        if self.download.is_video:
            try:
                if self.download.is_playlist:
                    subprocess.call(
                        f"{path_youtubedl} -q {self.download.URL} -o '{path_videos}%(playlist_index)s - %(title)s.%(ext)s'",
                        shell=True,
                    )
                else:
                    subprocess.call(f"{path_youtubedl} -q {self.download.URL} -o '{path_videos}%(title)s.%(ext)s'", shell=True)
            except:
                pass


if __name__ == "__main__":
    w = Tk()
    w.after(30000, w.destroy)
    w.wm_state("icon")
    App = dl_queue()
    App.run()
    w.mainloop()
