# -*- coding: utf-8 -*-
#py3
from resources.lib import kodiutils
from resources.lib import kodilogging
import io
import os
import sys
import time
import zipfile
import urllib
import urllib.request
import logging
import xbmcaddon
import xbmcgui
import xbmc, base64



ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))


class Canceled(Exception):
    pass


class MyProgressDialog():
    def __init__(self, process):
        self.dp = xbmcgui.DialogProgress()
        self.dp.create("[B][COLORgoldenrod]Cobra Mod Installer[/COLOR][/B]", "[CR]".join((process, '', 'Bitte warten...')))

    def __call__(self, block_num, block_size, total_size):
        if self.dp.iscanceled():
            self.dp.close()
            raise Canceled
        percent = (block_num * block_size * 100) / total_size
        if percent < total_size:
            self.dp.update(int(percent))
        else:
            self.dp.close()

def exists(path):
    try:
        f = urllib.request.urlopen(path).getcode()
        return True
    except:
        return False



def read(response, progress_dialog):
    data = b""
    total_size = response.getheader('Content-Length').strip()
    total_size = int(total_size)
    bytes_so_far = 0
    chunk_size = 1024 * 1024
    reader = lambda: response.read(chunk_size)
    for index, chunk in enumerate(iter(reader, b"")):
        data += chunk
        progress_dialog(index, chunk_size, total_size)
    return data


def extract(zip_file, output_directory, progress_dialog):
    zin = zipfile.ZipFile(zip_file)
    files_number = len(zin.infolist())
    for index, item in enumerate(zin.infolist()):
        try:
            progress_dialog(index, 1, files_number)
        except Canceled:
            return False
        else:
            zin.extract(item, output_directory)
    return True


def get_build():
    addon_name = ADDON.getAddonInfo('name')
    bundleURL = "https://repostubebox.geative.de/Kodi/Build/cobra_windows.zip"
    bundleVersion = base64.b64decode("aHR0cHM6Ly9yZXBvc3R1YmVib3guZ2VhdGl2ZS5kZS9Lb2RpL0J1aWxkL3ZlcnNpb24=").decode("utf-8")
    if not exists(bundleURL):
        xbmcgui.Dialog().ok('Cobra Mod Build [B][COLORred]OFFLINE[/COLOR][/B]','Aktuell leider nicht verfügbar.Versuche es später nochmal...' )
        os._exit(0)

    version = "0"

    try:
        url = bundleURL
        response = urllib.request.urlopen(url)
        version = urllib.request.urlopen(str(bundleVersion)).read().decode("utf-8")
    except:
        xbmcgui.Dialog().ok('Cobra Mod Build [B][COLORred]OFFLINE[/COLOR][/B]','Aktuell leider nicht verfügbar.Versuche es später nochmal...' )
        os._exit(0)
    try:
        data = read(response, MyProgressDialog("wird heruntergeladen ..."))
    except Canceled:
        message = "Download abgebrochen );....."
    else:
        addon_folder = xbmc.translatePath(os.path.join('special://', 'home'))
        if extract(io.BytesIO(data), addon_folder, MyProgressDialog("Installation ...")):
            message = "Installation erfolgreich abgeschlossen....."
        else:
            message = "Die Installation wurde abgebrochen );....."

    d = open(os.path.join(xbmc.translatePath('special://home/addons'), 'version'), "w")
    d.write(str(version))
    d.close()
    dialog = xbmcgui.Dialog()
    dialog.ok(addon_name, "%s. Cobra Mod wird beendet, um den Vorgang abzuschliessen....." % message)
    os._exit(0)
