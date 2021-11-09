# -*- coding: utf-8 -*-
# Module: default
# Author: Roman V. M. | mari 
# Created on: 28.11.2014 | 26.12.2020
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
from urllib.parse import urlencode
from urllib.parse import parse_qsl
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests
import json
import time
import os.path
version = '2.4';

_url = sys.argv[0]
_handle = int(sys.argv[1])

json_x = None
addon    = xbmcaddon.Addon()
addonDir = xbmc.translatePath(addon.getAddonInfo('path'))

def check_version():
    r = None
    try:
        r = requests.get('https://wagasworld.com/version.json').json()
    except:
        dialog = xbmcgui.Dialog()
        dialog.ok("Fehler", "Wagasworld ist gerade nicht zu erreichen. Bitte später wieder probieren.")
        return False
    if(r['version'] != version):
        dialog = xbmcgui.Dialog()
        dialog.ok("Update", "Es gibt ein neues Addon-Update, bitte updaten.")   
        return False
    return True
    
def renew_playlist():
    xbmcplugin.setPluginCategory(_handle, 'Wagasworld')
    global addon
    if os.path.isfile(addonDir + '/' + 'playlist.json'):
        os.remove(addonDir + '/' + 'playlist.json')
    addon.setSetting('cookie', "")
    dialog = xbmcgui.Dialog()
    dialog.ok("Erfolg", "Playlist wird erneuert")
    return

def update_json(new):
    global addon
    global json_x
    if new == False:
        if os.path.isfile(addonDir + '/' + 'playlist.json'):
            if(time.time() - os.path.getmtime(addonDir + '/' + 'playlist.json') > 14400):
                return update_json(True)
            else:
                with open(addonDir + '/' + 'playlist.json') as f:
                    json_x = json.loads(f.read())
                return True
        else:
            return update_json(True)
    else:                     
        cookie = addon.getSetting('cookie')
        if(cookie != "" and len(cookie) > 1):   
            arr = cookie.split('|')
            headers = {'Cookie': arr[0]}
            r = requests.get('https://wagasworld.com/k_playlist.php', headers=headers)
            f = open(addonDir + '/' + 'playlist.json', "w")
            f.write(r.text)
            f.close()
            json_x = json.loads(r.text)
            return True 
        else:
            return check_credentials()
    return False
    
    
def check_credentials():
    global addon
    cookie_str = None
    cookie = addon.getSetting('cookie')
    if(cookie != "" and len(cookie) > 1):
    # hier nur cookie nutzen für die requests, sonst login versuchen
        arr = cookie.split('|')
        if(len(arr)) == 1:
            arr.append(0)
        if(time.time() - int(float(arr[1])) > 14400):  # cookie nur alle 4std prüfen
            headers = {'Cookie': arr[0]}
            r = requests.get('https://wagasworld.com/k_check_cookie.php', headers=headers)
            json_data = json.loads(r.text)
            if(json_data['status'] == "OK"):
                addon.setSetting('cookie', arr[0] + '|' + str(time.time()))
                return True
            else:
                addon.setSetting('cookie', "")
                return check_credentials()
        else:
            return True
    else:
        username = addon.getSetting('username')
        password = addon.getSetting('password') 
        if(username == "" or password == "" or len(username) < 1 or len(password) < 1):
            dialog = xbmcgui.Dialog()
            dialog.ok("Fehler", "Es wurden keine Benutzerdaten angegeben")
            return False       
        a_session = requests.Session()   
        ro = a_session.post('https://wagasworld.com/k_l0gin.php', data = {'username':username, 'password': password})
        session_cookies = a_session.cookies
        json_data = json.loads(ro.text)
        cookies_dictionary = session_cookies.get_dict()
        if(json_data['status'] == "OK"):
            cookie_str =  "; ".join([str(x)+"="+str(y) for x,y in cookies_dictionary.items()])
        else:
            dialog = xbmcgui.Dialog()
            dialog.ok("Fehler", "Die angegebenen Benutzerdaten sind falsch")
            return False
        if(cookie_str):
            addon.setSetting('cookie', cookie_str + '|' + str(time.time()))
        return True
    return False
    
        
def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def get_categories():
    return list(map(lambda x: x['category_name'], list(json_x)))


def get_videos(category):
    global json_x
    for data in json_x:
        if data['category_name'] == category:
            return dict(data)
    return None


def list_categories():
    xbmcplugin.setPluginCategory(_handle, 'Wagasworld')
    xbmcplugin.setContent(_handle, 'videos')
    categories = get_categories()
    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category)
        info = ''
        for data in json_x:
            if data['category_name'] == category:
                if 'info' in data:
                    info = data['info']           
                if 'image' in data:
                    list_item.setArt({'thumb': data['image'], 'icon': data['image'], 'fanart': data['image']})     
                    break                  
        list_item.setInfo('video', {'title': category, 'mediatype': 'video', 'plot' : info})
        url = get_url(action='listing', category=category)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)



def list_videos(category):
    xbmcplugin.setPluginCategory(_handle, category)
    xbmcplugin.setContent(_handle, 'videos')
    videos = get_videos(category)
    for k, video in videos.items():
        if((type(video)) == dict):
            info = ''
            if 'info' in video:
                info = video['info']                               
            list_item = xbmcgui.ListItem(label=video['name'])
            list_item.setInfo('video', {'title': video['name'], 'plot': info, 'mediatype': 'video'})
            list_item.setArt({'thumb': video['image'], 'icon': video['image'], 'fanart': video['image']})
            list_item.setProperty('IsPlayable', 'true')
            url = get_url(action='play', video=video['link'])
            is_folder = False
            xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    global addon
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """
    cookie = addon.getSetting('cookie')
    arr = cookie.split('|')
    headers = {'Cookie': arr[0]}
    r = requests.get(path, headers=headers)    
    data = json.loads(r.text)
    if 'not_logged' in data['link'] and addon.getSetting('cookie') != "":
        addon.setSetting('cookie', "")  
        ret = check_credentials()
        if(ret == False):
            return
        return play_video(path)
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=data['link'])
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)

def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            list_videos(params['category'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
        elif params['action'] == 'renew_playlist':
            # Play a video from a provided URL.
            renew_playlist()
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        if(check_version() == True):
            list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    if(check_credentials() == True):
        update_json(False)
        router(sys.argv[2][1:])