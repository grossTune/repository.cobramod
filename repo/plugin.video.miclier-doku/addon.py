#!/usr/bin/python
# -*- coding: utf-8 -*-
import os,sys
import xbmc,xbmcgui,xbmcaddon,xbmcplugin

def fix_encoding(path):
	if sys.platform.startswith('win'):return unicode(path,'utf-8')
	else:return unicode(path,'utf-8').encode('ISO-8859-1')
	
addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path')

def set_content(content):
	xbmcplugin.setContent(int(sys.argv[1]),content)

def set_view_mode(view_mode):
    xbmc.executebuiltin('Container.SetViewMode(%s)' % (view_mode))

def set_end_of_directory(succeeded=True,updateListing=False,cacheToDisc=False):
	xbmcplugin.endOfDirectory(handle=int(sys.argv[1]),succeeded=True,updateListing=False,cacheToDisc=False)

def get_youtube_live_stream(channel_id):# is_folder_bool=False
	return'plugin://plugin.video.youtube/play/?channel_id=%s&live=1' % channel_id

def get_youtube_video(video_id):# is_folder_bool=False
	return'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % video_id

def get_youtube_playlist(playlist_id):# is_folder_bool=True
	return'plugin://plugin.video.youtube/playlist/%s/' % playlist_id

def get_youtube_channel(channel_id):# is_folder_bool=True
	return'plugin://plugin.video.youtube/channel/%s/' % channel_id

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path')
icon_path = os.path.join(addon_path,'resources','icon')
xbmcplugin.setContent(handle=int(sys.argv[1]), content='songs')
				
def add_item(name, url, iconimage='',
isFolder=True, IsPlayable=False):
    urlParams = {'name': name, 'url': url, 'iconimage': iconimage}
    liz = xbmcgui.ListItem(name, iconimage, iconimage)
    liz.setArt({'icon': iconimage, 'thumb' : iconimage})
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,isFolder=True)
    return ok

#-------------------#
#set_view_mode('50')
set_content('movies')
#-----------------------------------------------------------------------------------------------#

addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
icon1=xbmc.translatePath('special://home/addons/'+addonID+'/terrax.jpeg')
icon2=xbmc.translatePath('special://home/addons/'+addonID+'/terrax2.jpeg')
icon4=xbmc.translatePath('special://home/addons/'+addonID+'/zdfh.jpeg')
icon5=xbmc.translatePath('special://home/addons/'+addonID+'/n24d.jpg')
icon6=xbmc.translatePath('special://home/addons/'+addonID+'/arteh.png')
icon7=xbmc.translatePath('special://home/addons/'+addonID+'/arte.jpg')
icon8=xbmc.translatePath('special://home/addons/'+addonID+'/dokustreams.jpg')
icon9=xbmc.translatePath('special://home/addons/'+addonID+'/centauri.jpeg')
icon10=xbmc.translatePath('special://home/addons/'+addonID+'/mayday.jpg')
icon11=xbmc.translatePath('special://home/addons/'+addonID+'/crime.jpg')
icon12=xbmc.translatePath('special://home/addons/'+addonID+'/crime3.jpg')
icon13=xbmc.translatePath('special://home/addons/'+addonID+'/crime2.jpg')
icon14=xbmc.translatePath('special://home/addons/'+addonID+'/gang.jpg')
icon15=xbmc.translatePath('special://home/addons/'+addonID+'/universe.jpg')
icon16=xbmc.translatePath('special://home/addons/'+addonID+'/physik.jpg')
icon17=xbmc.translatePath('special://home/addons/'+addonID+'/history.jpg')
icon18=xbmc.translatePath('special://home/addons/'+addonID+'/wild5.jpg')
icon19=xbmc.translatePath('special://home/addons/'+addonID+'/anna.jpeg')
icon20=xbmc.translatePath('special://home/addons/'+addonID+'/wild12.jpg')
icon21=xbmc.translatePath('special://home/addons/'+addonID+'/reich.jpg')
icon22=xbmc.translatePath('special://home/addons/'+addonID+'/wwt.jpg')
icon23=xbmc.translatePath('special://home/addons/'+addonID+'/schlacht.jpg')
icon24=xbmc.translatePath('special://home/addons/'+addonID+'/war.jpg')
icon25=xbmc.translatePath('special://home/addons/'+addonID+'/tauchen.jpg')
icon26=xbmc.translatePath('special://home/addons/'+addonID+'/tauchen2.jpg')
icon27=xbmc.translatePath('special://home/addons/'+addonID+'/welt.jpg')



add_item('WELT Dokus & Reportagen',get_youtube_playlist('PLslDofkqdKI9Lt5PKR2BE3y4LULTMfT3A'),icon27)
add_item('Terra X',get_youtube_playlist('PLikmWKyGm7w4PQMbunBvj0PiafEgRzKLJ'),icon1)
add_item('Terra X II',get_youtube_playlist('PLg-rKdrKbDtlX-Alj0pyJ8BV2UUcU0yEZ'),icon2)
add_item('ZDF-History',get_youtube_playlist('PLtgw6t2VdpFa-EQZiCCu0eQtKPokLCavG'),icon4)
add_item('N24 Doku',get_youtube_playlist('PLLKmPm7DWMTk7DecizEnA14FR6Ukk1RtP'),icon5)
add_item('ARTE- History ',get_youtube_playlist('PL-t786AQxGO_7Rt3_4O01qKZXm6D-G-Od'),icon6)
add_item('ARTE- Dokus und Reportagen ',get_youtube_playlist('PLlQWnS27jXh846YQxXL9VeyoU47xCAmpY'),icon7)
add_item('Dokustreams',get_youtube_playlist('PLikmWKyGm7w68KLLD6Vx3brMDnEqwiUHK'),icon8)
add_item('Alpha Centauri',get_youtube_playlist('PLikmWKyGm7w4foHDk9XjMc7udzX-lS9ir'),icon9)
add_item('MAYDAY -Alarm Im Cockpit',get_youtube_playlist('PL087XIfT5XzzjCYvxVENPCJpLTzdUa8xg'),icon10)
add_item('Crime Dokus',get_youtube_playlist('PL8vy1Dmnedmpjwe51g22ts-GjhKYeqnL1'),icon11)
add_item('Dokus Kriminalfälle',get_youtube_playlist('PLD9tXDfn3aaOiQsMHzpPQK3fVBtYqo5Hl'),icon12)
add_item('Mord Dokus',get_youtube_playlist('PL71TJK-M7RX27K06Bj2-bEDNUiPRU_dPG'),icon13)
add_item('Ganster Dokus',get_youtube_playlist('PLk9HPyqc6AILC4JrdbTCWRp5jNJqLx4kg'),icon14)
add_item('Universum Dokumentationen',get_youtube_playlist('PLybSgyzzjOmk0GXvMkEW0PPiVPUvs3Rgg'),icon15)
add_item('DOKU // Physik // Science // Technik // Raumfahrt',get_youtube_playlist('PLEs1C_0f4i7-Y9fQbGjHqxhm6oRMerEEx'),icon16)
add_item('Geschichte, chronologisch',get_youtube_playlist('PLCmAcRSgj3IQy579zESYlbuEUn0UILucl'),icon17)
add_item('Natur- und Tierdokumentationen',get_youtube_playlist('PL4d-w5KrJjTZZxEb0XKIKLLkZbdWK5iJn'),icon18)
add_item('Tier Dokus Anna, Paula und die wilden Tiere ',get_youtube_playlist('PLydq0NtegKH-KFQMy20gfaS4Wee80zCkv'),icon19)
add_item('Tierdokumentationen ',get_youtube_playlist('PLOtxwk6mlZ-vOwYSa_EZgtF_6Xs9QrNXm'),icon20)
add_item('Doku-Das Dritte Reich',get_youtube_playlist('PLWCh1VrmvgDmxqpmRyslpSzE1XucQ63lO'),icon21)
add_item('Doku-2.Weltkrieg 1',get_youtube_playlist('PLPdh1srUHkHMBSQSyoCxRX_Tft7UPtZKI'),icon22)
add_item('Doku-2.Weltkrieg 2',get_youtube_playlist('PLB5Igv7tds-k1Z55IIM94K9eUoIsPlgBF'),icon22)
add_item('Doku-2.Weltkrieg 3',get_youtube_playlist('PLas7oA026StNicIR-pGRDTbLC9w-i9KMh'),icon22)
add_item('Legendäre Schlachten',get_youtube_playlist('PLexOauvOy9YExEsobKvMOXRN8Q1MmymjT'),icon23)
add_item('Kriegsfilme  ',get_youtube_playlist('PLsGK3aH9-P9koGCe60moCG4P3Y3SXEwAM'),icon24)
add_item('Tauchen',get_youtube_playlist('PL34ba0YZpTzq9ybHk8OOH1RMxnsxm8Lvq'),icon25)
add_item('Unterwasser Doku 1.',get_youtube_playlist('PLsGK3aH9-P9kICi2pgw6ygjBgBCZioT83'),icon26)
add_item('Unterwasser Doku 2.',get_youtube_playlist('PLi1BIRwUIrR0HX0zhHiHIErpDRLWAtkpC'),icon26)


	
#-----------------------------------------------------------------------------------------------#

set_end_of_directory()