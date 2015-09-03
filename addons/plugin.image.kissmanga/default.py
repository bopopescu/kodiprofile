### ############################################################################################################
###	#	
### # Project: 			#		KissManga.com - by The Highway 2013.
### # Author: 			#		The Highway
### # Version:			#		v0.3.5
### # Description: 	#		http://www.KissManga.com
###	#	
### ############################################################################################################
### ############################################################################################################
##### Imports #####
import xbmc,xbmcplugin,xbmcgui,xbmcaddon,xbmcvfs
#import requests ### (Removed in v0.2.1b to fix scripterror on load on Mac OS.) ### 
try: import requests ### <import addon="script.module.requests" version="1.1.0"/> ### 
except: t=''				 ### See https://github.com/kennethreitz/requests ### 


import urllib,urllib2,re,os,sys,htmllib,string,StringIO,logging,random,array,time,datetime
import urlresolver
import copy
###
#import cookielib
#import base64
#import threading
###
#import unicodedata ### I don't want to use unless I absolutely have to. ### 
#import zipfile ### Removed because it caused videos to not play. ### 
import HTMLParser, htmlentitydefs
try: 		import StorageServer
except: import storageserverdummy as StorageServer
try: 		from t0mm0.common.addon 				import Addon
except: from t0mm0_common_addon 				import Addon
try: 		from t0mm0.common.net 					import Net
except: from t0mm0_common_net 					import Net
try: 		from sqlite3 										import dbapi2 as sqlite; print "Loading sqlite3 as DB engine"
except: from pysqlite2 									import dbapi2 as sqlite; print "Loading pysqlite2 as DB engine"
#try: 		from script.module.metahandler 	import metahandlers
#except: from metahandler 								import metahandlers
### 
from teh_tools 		import *
import teh_tools as teh_tool
from config 			import *
##### /\ ##### Imports #####
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
__plugin__=ps('__plugin__'); __authors__=ps('__authors__'); __credits__=ps('__credits__'); _addon_id=ps('_addon_id'); _domain_url=ps('_domain_url'); _database_name=ps('_database_name'); _plugin_id=ps('_addon_id')
_database_file=os.path.join(xbmc.translatePath("special://database"),ps('_database_name')+'.db'); 
### 
_addon=Addon(ps('_addon_id'), sys.argv); addon=_addon; _plugin=xbmcaddon.Addon(id=ps('_addon_id')); cache=StorageServer.StorageServer(ps('_addon_id'))
### 
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Paths #####
### # ps('')
_addonPath	=xbmc.translatePath(_plugin.getAddonInfo('path'))
_artPath		=xbmc.translatePath(os.path.join(_addonPath,ps('_addon_path_art')))
_datapath 	=xbmc.translatePath(_addon.get_profile()); _artIcon		=_addon.get_icon(); _artFanart	=_addon.get_fanart()
##### /\ ##### Paths #####
##### Important Functions with some dependencies #####
def art(f,fe=ps('default_art_ext')): return xbmc.translatePath(os.path.join(_artPath,f+fe)) ### for Making path+filename+ext data for Art Images. ###
##### /\ ##### Important Functions with some dependencies #####
##### Settings #####
_setting={}; _setting['enableMeta']	=	_enableMeta			=tfalse(addst("enableMeta"))
_setting['debug-enable']=	_debugging			=tfalse(addst("debug-enable")); _setting['debug-show']	=	_shoDebugging		=tfalse(addst("debug-show"))
_setting['meta.movie.domain']=ps('meta.movie.domain'); _setting['meta.movie.search']=ps('meta.movie.search')
_setting['meta.tv.domain']   =ps('meta.tv.domain');    _setting['meta.tv.search']   =ps('meta.tv.search')
_setting['meta.tv.page']=ps('meta.tv.page'); _setting['meta.tv.fanart.url']=ps('meta.tv.fanart.url'); _setting['meta.tv.fanart.url2']=ps('meta.tv.fanart.url2'); _setting['label-empty-favorites']=tfalse(addst('label-empty-favorites'))
CurrentPercent=0; CancelDownload=False

##### /\ ##### Settings #####
##### Variables #####
_art404=ps('img_hot') #'http://www.solarmovie.so/images/404.png' #_art404=art('404')
_art150=ps('img_hot') #'http://www.solarmovie.so/images/thumb150.png' #_art150=art('thumb150')
_artDead=ps('img_hot') #'http://www.solarmovie.so/images/deadplanet.png' #_artDead=art('deadplanet')
_artSun=ps('img_hot') #art('sun'); 
COUNTRIES=ps('COUNTRIES'); GENRES=ps('GENRES'); _default_section_=ps('default_section'); net=Net(); DB=_database_file; BASE_URL=_domain_url;
#_artFanart=xbmc.translatePath(os.path.join(_addonPath,'fanart5.jpg'))
##### /\ ##### Variables #####
deb('Addon Path',_addonPath);  deb('Art Path',_artPath); deb('Addon Icon Path',_artIcon); deb('Addon Fanart Path',_artFanart)
### ############################################################################################################
def eod(): _addon.end_of_directory()
def deadNote(header='',msg='',delay=5000,image=_artDead): _addon.show_small_popup(title=header,msg=msg,delay=delay,image=image)
def sunNote( header='',msg='',delay=5000,image=_artSun):
	header=cFL(header,ps('cFL_color')); msg=cFL(msg,ps('cFL_color2'))
	_addon.show_small_popup(title=header,msg=msg,delay=delay,image=image)
def messupText(t,_html=False,_ende=False,_a=False,Slashes=False):
	if (_html==True): t=ParseDescription(HTMLParser.HTMLParser().unescape(t))
	if (_ende==True): t=t.encode('ascii', 'ignore'); t=t.decode('iso-8859-1')
	if (_a==True): t=_addon.decode(t); t=_addon.unescape(t)
	if (Slashes==True): t=t.replace( '_',' ')
	return t
def name2path(name):  return (((name.lower()).replace('.','-')).replace(' ','-')).replace('--','-')
def name2pathU(name): return (((name.replace(' and ','-')).replace('.','-')).replace(' ','-')).replace('--','-')
### ############################################################################################################
### ############################################################################################################
##### Queries #####
_param={}
_param['mode']=addpr('mode',''); _param['url']=addpr('url',''); _param['pagesource'],_param['pageurl'],_param['pageno'],_param['pagecount']=addpr('pagesource',''),addpr('pageurl',''),addpr('pageno',0),addpr('pagecount',1)
_param['img']=addpr('img',''); _param['fanart']=addpr('fanart',''); _param['thumbnail'],_param['thumbnail'],_param['thumbnail']=addpr('thumbnail',''),addpr('thumbnailshow',''),addpr('thumbnailepisode','')
_param['section']=addpr('section','movies'); _param['title']=addpr('title',''); _param['year']=addpr('year',''); _param['genre']=addpr('genre','')
_param['by']=addpr('by',''); _param['letter']=addpr('letter',''); _param['showtitle']=addpr('showtitle',''); _param['showyear']=addpr('showyear',''); _param['listitem']=addpr('listitem',''); _param['infoLabels']=addpr('infoLabels',''); _param['season']=addpr('season',''); _param['episode']=addpr('episode','')
_param['pars']=addpr('pars',''); _param['labs']=addpr('labs',''); _param['name']=addpr('name',''); _param['thetvdbid']=addpr('thetvdbid','')
_param['plot']=addpr('plot',''); _param['tomode']=addpr('tomode',''); _param['country']=addpr('country','')
_param['thetvdb_series_id']=addpr('thetvdb_series_id',''); _param['dbid']=addpr('dbid',''); _param['user']=addpr('user','')
_param['subfav']=addpr('subfav',''); _param['episodetitle']=addpr('episodetitle',''); _param['special']=addpr('special',''); _param['studio']=addpr('studio','')

#_param['']=_addon.queries.get('','')
#_param['']=_addon.queries.get('','')
##_param['pagestart']=addpr('pagestart',0)
##### /\
### ############################################################################################################
### ############################################################################################################
def initDatabase():
	print "Building solarmovie Database"
	if ( not os.path.isdir( os.path.dirname(_database_file) ) ): os.makedirs( os.path.dirname( _database_file ) )
	db=sqlite.connect(_database_file); cursor=db.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS seasons (season UNIQUE, contents);')
	cursor.execute('CREATE TABLE IF NOT EXISTS favorites (type, name, url, img);')
	db.commit(); db.close()

### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Player Functions #####
def PlayImage(url):
	play=xbmc.Player(xbmc.PLAYER_CORE_AUTO) ### xbmc.PLAYER_CORE_AUTO | xbmc.PLAYER_CORE_DVDPLAYER | xbmc.PLAYER_CORE_MPLAYER | xbmc.PLAYER_CORE_PAPLAYER
	try: _addon.resolve_url(url)
	except: t=''
	try: play.play(url)
	except: t=''

def PlayManga(url):
	play=xbmc.Player(xbmc.PLAYER_CORE_AUTO) ### xbmc.PLAYER_CORE_AUTO | xbmc.PLAYER_CORE_DVDPLAYER | xbmc.PLAYER_CORE_MPLAYER | xbmc.PLAYER_CORE_PAPLAYER
	try: _addon.resolve_url(url)
	except: t=''
	try: play.play(url)
	except: t=''

def PlayURL(url):
	play=xbmc.Player(xbmc.PLAYER_CORE_AUTO) ### xbmc.PLAYER_CORE_AUTO | xbmc.PLAYER_CORE_DVDPLAYER | xbmc.PLAYER_CORE_MPLAYER | xbmc.PLAYER_CORE_PAPLAYER
	try: _addon.resolve_url(url)
	except: t=''
	try: play.play(url)
	except: t=''

def PlayVideo(url, title='', studio='', img='', showtitle='', plot=''): #PlayVideo(url, infoLabels, listitem)
	WhereAmI('@ PlayVideo -- Getting ID From:  %s' % url)
	if (img==''): img=_artIcon
	infoLabels={"Studio":studio,"ShowTitle":showtitle,"Title":title,"Plot":plot}
	li=xbmcgui.ListItem(title,iconImage=img,thumbnailImage=img)
	li.setInfo(type="Video", infoLabels=infoLabels ); li.setProperty('IsPlayable', 'true')
	eod()
	#xbmc.Player().stop()
	try: _addon.resolve_url(url)
	except: t=''
	play=xbmc.Player(xbmc.PLAYER_CORE_AUTO) ### xbmc.PLAYER_CORE_AUTO | xbmc.PLAYER_CORE_DVDPLAYER | xbmc.PLAYER_CORE_MPLAYER | xbmc.PLAYER_CORE_PAPLAYER
	try: play.play(url, li); xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
	except: t=''
	#xbmcplugin.setResolvedUrl(int(sys.argv[1]), True)
	try: _addon.resolve_url(url)
	except: t=''
	#xbmc.sleep(7000)

def PlayLibrary(section, url, showtitle='', showyear=''): ### Menu for Listing Hosters (Host Sites of the actual Videos)
	WhereAmI('@ Play Library: %s' % url); sources=[]; listitem=xbmcgui.ListItem()
	#eod()
	#_addon.resolve_url(url)
	if (url==''): return
	html=net.http_GET(url).content; html=html.encode("ascii", "ignore")
	##if (_debugging==True): print html
	#if  ( section == 'tv'): ## TV Show ## Title (Year) - Info
	#	match=re.compile(ps('LLinks.compile.show_episode.info'), re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0] ### <title>Watch The Walking Dead Online for Free - Prey - S03E14 - 3x14 - SolarMovie</title>
	#	if (_debugging==True): print match
	#	if (match==None):  return
	#	ShowYear=_param['year'] #ShowYear=showyear
	#	ShowTitle=match[0].strip(); EpisodeTitle=match[1].strip(); Season=match[2].strip(); Episode=match[3].strip()
	#	ShowTitle=HTMLParser.HTMLParser().unescape(ShowTitle); ShowTitle=ParseDescription(ShowTitle); ShowTitle=ShowTitle.encode('ascii', 'ignore'); ShowTitle=ShowTitle.decode('iso-8859-1'); EpisodeTitle=HTMLParser.HTMLParser().unescape(EpisodeTitle); EpisodeTitle=ParseDescription(EpisodeTitle); EpisodeTitle=EpisodeTitle.encode('ascii', 'ignore'); EpisodeTitle=EpisodeTitle.decode('iso-8859-1')
	#	if ('<p id="plot_' in html):
	#		ShowPlot=(re.compile(ps('LLinks.compile.show.plot'), re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0]).strip(); ShowPlot=HTMLParser.HTMLParser().unescape(ShowPlot); ShowPlot=ParseDescription(ShowPlot); ShowPlot=ShowPlot.encode('ascii', 'ignore'); ShowPlot=ShowPlot.decode('iso-8859-1')
	#	else: ShowPlot=''
	#	match=re.compile(ps('LLinks.compile.imdb.url_id'), re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0]
	#	if (_debugging==True): print match
	#	(IMDbURL,IMDbID)=match; IMDbURL=IMDbURL.strip(); IMDbID=IMDbID.strip(); My_infoLabels={ "Studio": ShowTitle+'  ('+ShowYear+'):  '+Season+'x'+Episode+' - '+EpisodeTitle, "Title": ShowTitle, "ShowTitle": ShowTitle, "Year": ShowYear, "Plot": ShowPlot, 'Season': Season, 'Episode': Episode, 'EpisodeTitle': EpisodeTitle, 'IMDbURL': IMDbURL, 'IMDbID': IMDbID, 'IMDb': IMDbID }; listitem.setInfo(type="Video", infoLabels=My_infoLabels )
	#else:	#################### Movie ## Title (Year) - Info
	#	match=re.compile(ps('LLinks.compile.show.title_year'), re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0]
	#	if (_debugging==True): print match
	#	if (match==None): return
	#	ShowYear=match[1].strip(); ShowTitle=match[0].strip(); ShowTitle=HTMLParser.HTMLParser().unescape(ShowTitle); ShowTitle=ParseDescription(ShowTitle); ShowTitle=ShowTitle.encode('ascii', 'ignore'); ShowTitle=ShowTitle.decode('iso-8859-1'); ShowPlot=(re.compile(ps('LLinks.compile.show.plot'), re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0]).strip(); ShowPlot=HTMLParser.HTMLParser().unescape(ShowPlot); ShowPlot=ParseDescription(ShowPlot); ShowPlot=ShowPlot.encode('ascii', 'ignore'); ShowPlot=ShowPlot.decode('iso-8859-1'); match=re.compile(ps('LLinks.compile.imdb.url_id'), re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0]
	#	if (_debugging==True): print match
	#	(IMDbURL,IMDbID)=match; IMDbURL=IMDbURL.strip(); IMDbID=IMDbID.strip(); My_infoLabels={ "Studio": ShowTitle+'  ('+ShowYear+')', "Title": ShowTitle, "ShowTitle": ShowTitle, "Year": ShowYear, "Plot": ShowPlot, 'IMDbURL': IMDbURL, 'IMDbID': IMDbID, 'IMDb': IMDbID }; listitem.setInfo(type="Video", infoLabels=My_infoLabels )
	### Both -Movies- and -TV Shows- ### Hosters
	try:		matchH=re.compile(ps('LLinks.compile.hosters2'), re.MULTILINE | re.DOTALL | re.IGNORECASE).findall(html)
	except:	matchH=''
	#deb('length of matchH',str(len(matchH)))
	#print matchH
	if (len(matchH) > 0):
		oList=[]; hList=[]; matchH=sorted(matchH, key=lambda item: item[3], reverse=True)
		for url, host, quality, age in matchH:
			url=url.strip(); host=host.strip(); quality=quality.strip(); age=age.strip()
			try:		mID=re.compile('/.+?/.+?/([0-9]+)/', re.DOTALL | re.IGNORECASE).findall(url)[0]
			except: mID=''
			#deb('Media Passed',str(host)+' | '+str(quality)+' | '+str(age)+' | '+str(url)+' | '+str(mID))
			if (mID is not ''):
				oList.append(host+'  ['+quality+']  ('+age+')')
				hList.append([url,host,quality,age,mID])
		try:		rt=askSelection(oList,'Select Source:')
		except:	rt=''
		print rt
		if (rt==None) or (rt=='none') or (rt==False) or (rt==''): return
		hItem=hList[rt]
		deb('ID',hItem[4])
		urlB='%s/link/play/%s/' % (ps('_domain_url'),hItem[4])
		html=net.http_GET(urlB).content
		try: url=re.compile('<iframe.+?src="(.+?)"', re.MULTILINE | re.DOTALL | re.IGNORECASE).findall(html)[0]
		except: url=''
		url=url.replace('/embed/', '/file/'); deb('hoster url',url)
		#oList=[]
		#for url, host, quality, age in match:
		#	url=url.strip(); host=host.strip(); quality=quality.strip(); age=age.strip()
		#	print 'Media Failed:  '+str(host)+' | '+str(quality)+' | '+str(age)+' | '+url
		#	if (urlresolver.HostedMediaFile(url=url.strip()).valid_url()):
		#		try:		MediaID=urlresolver.HostedMediaFile(url=url).get_media_url()
		#		except: MediaID=''
		#		try:		MediaHost=urlresolver.HostedMediaFile(url=url).get_host()
		#		except: MediaHost=''
		#		print 'Media Passed:  '+str(MediaHost)+' | '+str(MediaID)+' | '+url
		#		if (MediaHost is not '') and (MediaID is not ''):
		#			oList.append(urlresolver.HostedMediaFile(host=MediaHost, media_id=MediaID))
		##
		#
		#try: url=urlresolver.choose_source(oList)
		#except: return
		#
		#MediaID=urlresolver.HostedMediaFile(url=url).get_media_url()
		#MediaHost=urlresolver.HostedMediaFile(url=url).get_host()
		#print 'Media:  '+str(MediaHost)+' | '+str(MediaID)+' | '+url
		#print str(urlresolver.HostedMediaFile(url=url.strip()).valid_url())
		#if (urlresolver.HostedMediaFile(url=url.strip()).valid_url()):
		#
		#
		#
		#
		#videoId=match.group(1); deb('Solar ID',videoId); url=BASE_URL + '/link/play/' + videoId + '/' ## Example: http://www.solarmovie.so/link/play/1052387/ ##
		#html=net.http_GET(url).content; match=re.search( '<iframe.+?src="(.+?)"', html, re.IGNORECASE | re.MULTILINE | re.DOTALL); link=match.group(1); link=link.replace('/embed/', '/file/'); deb('hoster link',link)
		#
		deb('video',url)
		liz=xbmcgui.ListItem(_param['showtitle'], iconImage="DefaultVideo.png", thumbnailImage=_param['img'])
		if  ( section == 'tv'): ## TV Show ## Title (Year) - Info
			liz.setInfo( type="Video", infoLabels={ "Title": _param['showtitle']+'  ('+_param['showyear']+')', "Studio": 'SolarMovie.so' } )
		else:	#################### Movies ### Title (Year) - Info
			liz.setInfo( type="Video", infoLabels={ "Title": _param['showtitle']+'  ('+_param['showyear']+')', "Studio": 'SolarMovie.so' } )
		liz.setProperty("IsPlayable","true")
		##pl=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		##pl.clear()
		##pl.add(url, liz)
		##xbmc.Player().play(pl)
		play=xbmc.Player(xbmc.PLAYER_CORE_AUTO) ### xbmc.PLAYER_CORE_AUTO | xbmc.PLAYER_CORE_DVDPLAYER | xbmc.PLAYER_CORE_MPLAYER | xbmc.PLAYER_CORE_PAPLAYER
		print url
		stream_url = urlresolver.HostedMediaFile(url).resolve()
		print stream_url
		play.play(stream_url, liz)
		#play.play(url, liz)
		liz.setPath(url)
		xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
		_addon.resolve_url(url)
		_addon.resolve_url(stream_url)
		##
		##
		##
		##count=1
		##for url, host, quality, age in match:
		##	host=host.strip(); quality=quality.strip(); name=str(count)+". "+host+' - [[B]'+quality+'[/B]] - ([I]'+age+'[/I])'
		##	if urlresolver.HostedMediaFile(host=host, media_id='xxx'):
		##		img=ps('Hosters.icon.url')+host; My_infoLabels['quality']=quality; My_infoLabels['age']=age; My_infoLabels['host']=host; _addon.add_directory({'section': section, 'img': _param['img'], 'mode': 'PlayVideo', 'url': url, 'quality': quality, 'age': age, 'infoLabels': My_infoLabels, 'listitem': listitem}, {'title':  name}, img=img, is_folder=False); count=count+1 
		eod()
	else: return
	### ################################################################

def DownloadStop():  ## Testing ## Doesn't work yet.
	global CancelDownload
	CancelDownload=True
	#global CancelDownload
	eod()
	#download_method=addst('download_method') ### 'Progress|ProgressBG|Hidden'
	#if   (download_method=='Progress'):
	#	dp=xbmcgui.DialogProgress()   ## For Frodo and earlier.
	#	dp.close()
	#elif (download_method=='ProgressBG'):
	#	dp=xbmcgui.DialogProgressBG() ## Only works on daily build of XBMC.
	#	dp.close()
	#elif (download_method=='Test'):
	#	t=''
	#elif (download_method=='Hidden'):
	#	t=''
	#else: deb('Download Error','Incorrect download method.'); myNote('Download Error','Incorrect download method.'); return
	#try:		t=''
	#except: t=''

def DownloadStatus(numblocks, blocksize, filesize, dlg, download_method, start_time, section, url, img, LabelName, ext, LabelFile):
	if (CancelDownload==True):
		try:
			if   (download_method=='Progress'): ## For Frodo and earlier.
				dlg.close()
			elif (download_method=='ProgressBG'): ## Only works on daily build of XBMC.
				dlg.close()
			elif (download_method=='Test'): t=''
			elif (download_method=='Hidden'): t=''
		except: t=''
	try:
		percent = min(numblocks * blocksize * 100 / filesize, 100)
		currently_downloaded = float(numblocks) * blocksize / (1024 * 1024)
		kbps_speed = numblocks * blocksize / (time.time() - start_time)
		if kbps_speed > 0:	eta = (filesize - numblocks * blocksize) / kbps_speed
		else:								eta = 0
		kbps_speed /= 1024
		total = float(filesize) / (1024 * 1024)
		#if   (download_method=='Progress'): ## For Frodo and earlier.
		#	line1 = '%.02f MB of %.02f MB' % (currently_downloaded, total)
		#	line1 +='  '+percent+'%'
		#	line2 = 'Speed: %.02f Kb/s ' % kbps_speed
		#	line3 = 'ETA: %02d:%02d' % divmod(eta, 60)
		#	dlg.update(percent, line1, line2, line3)
		#elif (download_method=='ProgressBG'): ## Only works on daily build of XBMC.
		#	line1  ='%.02f MB of %.02f MB' % (currently_downloaded, total)
		#	line1 +='  '+percent+'%'
		#	line2  ='Speed: %.02f Kb/s ' % kbps_speed
		#	line2 +='ETA: %02d:%02d' % divmod(eta, 60)
		#	dlg.update(percent, line1, line2)
		#elif (download_method=='Test'):
		#	mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total)
		#	spd = 'Speed: %.02f Kb/s ' % kbps_speed
		#	est = 'ETA: %02d:%02d' % divmod(eta, 60)
		#	Header=		ext+'  '+mbs+'  '+percent+'%'
		#	Message=	est+'  '+spd
		#elif (download_method=='Hidden'): t=''
		#if (time.time()==start_time) or (int(str(time.time())[-5:1]) == 0): # and (int(str(time.time())[-5:2]) < 10):
		#if (int(time.strptime(time.time(),fmt='%S')) == 0):
		#if (str(percent) in ['0','1','5','10','15','20','25','30','35','40','45','50','55','60','65','70','75','80','85','90','91','92','93','94','95','96','97','98','99','100']):
		#if (str(percent) == '0' or '1' or '5' or '10' or '15' or '20' or '25' or '30' or '35' or '40' or '45' or '50' or '55' or '60' or '65' or '70' or '75' or '80' or '85' or '90' or '91' or '92' or '93' or '94' or '95' or '96' or '97' or '98' or '99' or '100'):
		#if ('.' in str(percent)): pCheck=int(str(percent).split('.')[0])
		#else: pCheck=percent
		#pCheck=int(str(percent)[1:])
		#if (CurrentPercent is not pCheck):
		#	global CurrentPercent
		#	CurrentPercent=pCheck
		#	myNote(header=Header,msg=Message,delay=100,image=img)
		##myNote(header=Header,msg=Message,delay=1,image=img)
	except:
		percent=100
		if   (download_method=='Progress'): ## For Frodo and earlier.
			t=''
			dlg.update(percent)
		elif (download_method=='ProgressBG'): ## Only works on daily build of XBMC.
			t=''
			dlg.update(percent)
		elif (download_method=='Test'): t=''
		#myNote(header='100%',msg='Download Completed',delay=15000,image=img)
		elif (download_method=='Hidden'): t=''
	if   (download_method=='Progress'): ## For Frodo and earlier.
		line1 = '%.02f MB of %.02f MB' % (currently_downloaded, total)
		line1 +='  '+str(percent)+'%'
		line2 = 'Speed: %.02f Kb/s ' % kbps_speed
		line3 = 'ETA: %02d:%02d' % divmod(eta, 60)
		dlg.update(percent, line1, line2, line3)
	elif (download_method=='ProgressBG'): ## Only works on daily build of XBMC.
		line1  ='%.02f MB of %.02f MB' % (currently_downloaded, total)
		line1 +='  '+str(percent)+'%'
		line2  ='Speed: %.02f Kb/s ' % kbps_speed
		line2 +='ETA: %02d:%02d' % divmod(eta, 60)
		dlg.update(percent, line1, line2)
	elif (download_method=='Test'):
		mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total)
		spd = 'Speed: %.02f Kb/s ' % kbps_speed
		est = 'ETA: %02d:%02d' % divmod(eta, 60)
		Header=		ext+'  '+mbs+'  '+str(percent)+'%'
		Message=	est+'  '+spd
	elif (download_method=='Hidden'): t=''
	if   (download_method=='Progress'): ## For Frodo and earlier.
		try:
			if dlg.iscanceled(): ## used for xbmcgui.DialogProgress() but causes an error with xbmcgui.DialogProgressBG()
				dlg.close()
				#deb('Download Error','Download canceled.'); myNote('Download Error','Download canceled.')
				#raise StopDownloading('Stopped Downloading')
		except: t=''
	elif (download_method=='ProgressBG'): ## Only works on daily build of XBMC.
		try:
			if (dlg.isFinished()): 
				dlg.close()
		except: t=''

def DownloadRequest(section,url,img,LabelName):
	if (LabelName=='') and     (_param['title'] is not ''): LabelName==_param['title']
	if (LabelName=='') and (_param['showtitle'] is not ''): LabelName==_param['showtitle']
	LabelFile=clean_filename(LabelName)
	deb('LabelName',LabelName)
	if (LabelName==''): deb('Download Error','Missing Filename String.'); myNote('Download Error','Missing Filename String.'); return
	if (section==ps('section.wallpaper')):	FolderDest=xbmc.translatePath(addst("download_folder_wallpapers"))
	elif (section==ps('section.tv')):				FolderDest=xbmc.translatePath(addst("download_folder_tv"))
	elif (section==ps('section.movie')):		FolderDest=xbmc.translatePath(addst("download_folder_movies"))
	else:																		FolderDest=xbmc.translatePath(addst("download_folder_movies"))
	if os.path.exists(FolderDest)==False: os.mkdir(FolderDest)
	if os.path.exists(FolderDest):
		if (section==ps('section.tv')) or (section==ps('section.movie')):
			### param >> url:  /link/show/1466546/
			#match=re.search( '/.+?/.+?/(.+?)/', url) ## Example: http://www.solarmovie.so/link/show/1052387/ ##
			#videoId=match.group(1); deb('Solar ID',videoId); url=BASE_URL + '/link/play/' + videoId + '/' ## Example: http://www.solarmovie.so/link/play/1052387/ ##
			#html=net.http_GET(url).content; match=re.search( '<iframe.+?src="(.+?)"', html, re.IGNORECASE | re.MULTILINE | re.DOTALL); link=match.group(1); link=link.replace('/embed/', '/file/'); deb('hoster link',link)
			#try: stream_url = urlresolver.HostedMediaFile(link).resolve()
			#except: stream_url=''
			stream_url=url
			if ('.mp4' in LabelName) or ('.mp4' in stream_url): ext='.mp4'
			elif ('.avi' in LabelName) or ('.avi' in stream_url): ext='.avi'
			elif ('.mkv' in LabelName) or ('.mkv' in stream_url): ext='.mkv'
			else: ext='.flv'
			ext=Download_PrepExt(stream_url,ext)
		else:
			stream_url=url
			if ('.png' in LabelName) or ('.png' in stream_url): ext='.png'
			else: ext='.jpg'
			ext=Download_PrepExt(stream_url,ext)
		t=1; c=1
		if os.path.isfile(xbmc.translatePath(os.path.join(FolderDest,LabelFile+ext))):
			t=LabelFile
			while t==LabelFile:
				if os.path.isfile(xbmc.translatePath(os.path.join(FolderDest,LabelFile+'['+str(c)+']'+ext)))==False:
					LabelFile=LabelFile+'['+str(c)+']'
				c=c+1
		start_time = time.time()
		deb('start_time',str(start_time))
		download_method=addst('download_method') ### 'Progress|ProgressBG|Hidden'
		urllib.urlcleanup()
		if   (download_method=='Progress'):
			dp=xbmcgui.DialogProgress(); dialogType=12 ## For Frodo and earlier.
			dp.create('Downloading', LabelFile+ext)
			urllib.urlretrieve(stream_url, xbmc.translatePath(os.path.join(FolderDest,LabelFile+ext)), lambda nb, bs, fs: DownloadStatus(nb, bs, fs, dp, download_method, start_time, section, url, img, LabelName, ext, LabelFile)) #urllib.urlretrieve(url, localfilewithpath)
			myNote('Download Complete',LabelFile+ext,15000)
		elif (download_method=='ProgressBG'):
			dp=xbmcgui.DialogProgressBG(); dialogType=13 ## Only works on daily build of XBMC.
			dp.create('Downloading', LabelFile+ext)
			urllib.urlretrieve(stream_url, xbmc.translatePath(os.path.join(FolderDest,LabelFile+ext)), lambda nb, bs, fs: DownloadStatus(nb, bs, fs, dp, download_method, start_time, section, url, img, LabelName, ext, LabelFile)) #urllib.urlretrieve(url, localfilewithpath)
			myNote('Download Complete',LabelFile+ext,15000)
		elif (download_method=='Test'):
			dp=xbmcgui.DialogProgress()
			myNote('Download Started',LabelFile+ext,15000)
			urllib.urlretrieve(stream_url, xbmc.translatePath(os.path.join(FolderDest,LabelFile+ext)), lambda nb, bs, fs: DownloadStatus(nb, bs, fs, dp, download_method, start_time, section, url, img, LabelName, ext, LabelFile)) #urllib.urlretrieve(url, localfilewithpath)
			myNote('Download Complete',LabelFile+ext,15000)
		elif (download_method=='Hidden'):
			dp=xbmcgui.DialogProgress()
			myNote('Download Started',LabelFile+ext,15000)
			urllib.urlretrieve(stream_url, xbmc.translatePath(os.path.join(FolderDest,LabelFile+ext)), lambda nb, bs, fs: DownloadStatus(nb, bs, fs, dp, download_method, start_time, section, url, img, LabelName, ext, LabelFile)) #urllib.urlretrieve(url, localfilewithpath)
			myNote('Download Complete',LabelFile+ext,15000)
		elif (download_method=='jDownloader (StreamURL)'):
			myNote('Download','sending to jDownloader plugin',15000)
			xbmc.executebuiltin("XBMC.RunPlugin(plugin://plugin.program.jdownloader/?action=addlink&url=%s)" % stream_url)
			#return
		elif (download_method=='jDownloader (Link)'):
			myNote('Download','sending to jDownloader plugin',15000)
			xbmc.executebuiltin("XBMC.RunPlugin(plugin://plugin.program.jdownloader/?action=addlink&url=%s)" % link)
			#return
		else: deb('Download Error','Incorrect download method.'); myNote('Download Error','Incorrect download method.'); return
		##
		##urllib.urlretrieve(stream_url, xbmc.translatePath(os.path.join(FolderDest,LabelFile+ext)), lambda nb, bs, fs: DownloadStatus(nb, bs, fs, dp, download_method, start_time, section, url, img, LabelName, ext, LabelFile)) #urllib.urlretrieve(url, localfilewithpath)
		##
		#myNote('Download Complete',LabelFile+ext,15000)
		##
		#### xbmc.translatePath(os.path.join(FolderDest,localfilewithpath+ext))
		_addon.resolve_url(url)
		_addon.resolve_url(stream_url)
		#
		#
	else:	deb('Download Error','Unable to create destination path.'); myNote('Download Error','Unable to create destination path.'); return

def PlayTrailer(url,_title,_year,_image): ### Not currently used ###
	WhereAmI('@ PlayVideo:  %s' % url) #; sources=[]; url=url.decode('base-64')
	#if ('<h2>Movie trailer</h2>' not in url): eod(); return
	EmbedID=''; html=net.http_GET(url).content #getURL(url)
	html=messupText(html,True,True,True,False)
	#print str(html)
	if ('traileraddict.com/emd/' in html):
		deb('Found','traileraddict.com/emd/')
		#EmbedID=re.compile('traileraddict.com/emd/(\d+)"', re.DOTALL).findall(html)[0].strip()
		try: 		EmbedID=re.compile('traileraddict.com/emd/(\d+)"', re.DOTALL).findall(html)[0].strip()
		except: EmbedID=''
	if (EmbedID==''):
		#print html
		#ImdbID=re.compile('<strong>IMDb ID:</strong>[\n]\s+<a href=".+?">(\d+)</a>"', re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0].strip()
		try:		ImdbID=re.compile('%2Ftitle%2Ftt(\d+)%2F"', re.DOTALL).findall(html)[0].strip()
		except:	ImdbID=''
		if (ImdbID==''): eod(); deb('Error Playing Trailer','No Imdb ID.'); deadNote('Problem with the Trailer','Trailer is Unavailable.'); return
		deb('ImdbID',ImdbID)
		thtml=getURL('http://api.traileraddict.com/?imdb='+ImdbID)
		try: 		EmbedID=re.compile('"http://www.traileraddict.com/emd/([0-9]+)"', re.DOTALL).findall(thtml)[0].strip()
		except: EmbedID=''
	if (EmbedID==''): eod(); deb('Error Playing Trailer','No Embed Video ID.'); deadNote('Problem with the Trailer','Trailer is Unavailable.'); return
	deb('EmbedID',EmbedID)
	vhtml=getURL('http://www.traileraddict.com/fvar.php?tid='+EmbedID) #vhtml=getURL('http://www.traileraddict.com/fvarhd.php?tid='+EmbedID)
	#print vhtml
	if ('Error: Trailer is (Possibly Temporarily) Unavailable' in vhtml): deadNote('Problem with the Trailer','Trailer is Unavailable.'); return
	try:		thumb=re.compile('&image=(.+?)&', re.DOTALL).findall(vhtml)[0].strip()
	except:	thumb=_param['img']
	try: 		title=re.compile('&filmtitle=(.+?)&', re.DOTALL).findall(vhtml)[0].strip()
	except: title=_param['title']
	try: 			url=re.compile('&fileurl=(.+?)&', re.DOTALL).findall(vhtml)[0].strip()
	except: 
		try: 		url=re.compile('&fileurl=(.+?)[\n]\s+&', re.DOTALL).findall(vhtml)[0].strip()
		except: url=''
	if (url==''): eod(); deb('Error Playing Trailer','No Url was found from vhtml.'); deadNote('Problem with the Trailer','Trailer is Unavailable.'); return
	url=urllib.unquote_plus(url)
	deb('video',url)
	liz=xbmcgui.ListItem(_param['showtitle'], iconImage=thumb, thumbnailImage=_image)
	liz.setInfo( type="Video", infoLabels={ "Title": title, "Studio": _title+'  ('+_year+')' } )
	liz.setProperty("IsPlayable","true")
	play=xbmc.Player(xbmc.PLAYER_CORE_AUTO) ### xbmc.PLAYER_CORE_AUTO | xbmc.PLAYER_CORE_DVDPLAYER | xbmc.PLAYER_CORE_MPLAYER | xbmc.PLAYER_CORE_PAPLAYER
	play.play(url, liz)
	#liz.setPath(url)
	#xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
	_addon.resolve_url(url)
	#eod(); return

##### /\ ##### Player Functions #####
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Weird, Stupid, or Plain up Annoying Functions. #####
def netURL(url): ### Doesn't seem to work.
	return net.http_GET(url).content
def remove_accents(input_str): ### Not even sure rather this one works or not.
	#nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
	#return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
	return input_str
##### /\ ##### Weird, Stupid, or Plain up Annoying Functions. #####
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Menus #####
def mGetItemPage(url):
	deb('Fetching html from Url',url)
	try: html=net.http_GET(url).content
	except: html=''
	if (html=='') or (html=='none') or (html==None) or (html==False): return ''
	else:
		html=HTMLParser.HTMLParser().unescape(html); html=_addon.decode(html); html=_addon.unescape(html); html=ParseDescription(html); html=html.encode('ascii', 'ignore'); html=html.decode('iso-8859-1'); deb('Length of HTML fetched',str(len(html)))
	return html

def mGetDataGroup2String(html,parseTag='',ifTag='',startTag='',endTag='',Topic=''):
	if (ifTag in html):
		html=(((html.split(startTag)[1])).split(endTag)[0]).strip()
		try: results=re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)
		except: return ''
		i=0; r=''
		for result in results:
			if (i==0): 	r=result.strip()
			else: 			r=r+', '+result.strip()
			i=i+1
		deb(Topic,r); return r
	else: return ''

def mdGetSplitFindGroup(html,ifTag='', parseTag='',startTag='',endTag=''): 
	if (ifTag=='') or (parseTag=='') or (startTag=='') or (endTag==''): return ''
	if (ifTag in html):
		html=(((html.split(startTag)[1])).split(endTag)[0]).strip()
		try: return re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)
		except: return ''
	else: return ''

def listLinks(section, url, showtitle='', showyear=''): ### Menu for Listing Hosters (Host Sites of the actual Videos)
	WhereAmI('@ the Link List: %s' % url); sources=[]; listitem=xbmcgui.ListItem()
	if (url==''): return
	try: html=net.http_GET(url).content
	except: html=''
	if (html==''): return
	try: html=html.encode("ascii", "ignore")
	except: t=''
	html=messupText(html,True,True,True,False)
	img=_param['img']
	if (img==''): img=re.compile('<link\s*rel="image_src"\s*href="(http://.+?\.jpg)"').findall(html)[0].replace(' ','%20')
	pimg=''+img
	fimg=''+img
	ptitle=_param['title']
	#s='<a\s*\n*\s*href="(http://redirector.googlevideo.com/videoplayback.+?)"\s*\n*\s*>((\d+)x(\d+)\.([0-9A-Za-z]+))</a>'
	s='lstImages\.push\("(http://.+?\..+?/.+?/[A-Za-z\-_]*(\d*)[A-Za-z\-_]*\.[jpg|png]+\?imgmax=(\d+))"\);'
	matches=re.compile(s).findall(html) # , re.DOTALL
	try: contentURL=re.compile('<meta\s*itemprop="contentURL"\s*content="(http://.+?)"\s*/*>').findall(html)[0]
	except: contentURL=''
	try: fTitle=re.compile('<meta\s*itemprop="contentURL"\s*content="http://.+?(&title=.*?)"\s*/*>').findall(html)[0]
	except: fTitle=''
	#if (len(contentURL) > 0):
	#	contextMenuItems=[]; labs={}; labs['title']='[ Default URL ]' +'  [I]<-- Play This One Only[/I]'
	#	pars={'img':pimg,'mode':'PlayVideo','url':contentURL,'title':'Default URL','studio':ptitle}
	#	_addon.add_directory(pars,labs,img=img,fanart=fimg,is_folder=False,contextmenu_items=contextMenuItems)
	if (len(matches) > 0):
		count=1; ItemCount=len(matches); #match=sorted(match, key=lambda item: (item[3],item[2],item[1]))
		deb('No. of matches',str(ItemCount))
		#print matches
		MaxNoLinks=int(addst('linksmaxshown'))
		#
		#liz=xbmcgui.ListItem(ptitle,iconImage=pimg,thumbnailImage=pimg)
		#liz.setInfo('image',{'Title':ptitle}) # ,"Duration" : duration
		##liz.setProperty('mimetype', 'image/jpg')
		#liz.setProperty('IsPlayable', 'false')	#play=xbmc.Player(xbmc.PLAYER_CORE_AUTO) ### xbmc.PLAYER_CORE_AUTO | xbmc.PLAYER_CORE_DVDPLAYER | xbmc.PLAYER_CORE_MPLAYER | xbmc.PLAYER_CORE_PAPLAYER
		#pl=xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
		#pl.clear()
		#
		#for mUrl,mName,mWidth,mHeight,mFileExt in matches:
		for mUrl,mNo,imgmax in matches:
			#if   (mFileExt.lower()=='mkv'): img=art('mkv') #'http://convertmkvtomp4.info/images/mkv.png'
			#elif (mFileExt.lower()=='mp4'): img=art('mp4') #'http://zamzar.files.wordpress.com/2013/03/mp4.png?w=480'
			#elif (mFileExt.lower()=='flv'): img=art('flv') #'http://images.wikia.com/fileformats/images/a/ab/Icon_FLV.png'
			contextMenuItems=[]; labs={}
			#if (fTitle not in mUrl): mUrl+=fTitle
			pars={'img':pimg,'mode':'PlayManga','url':mUrl,'title':'Page '+str(count),'studio':ptitle}
			deb('gv redirector url',mUrl)
			#pars2={'img':img,'mode':'Download','url':url,'title':mName,'studio':ptitle}
			#contextMenuItems.append(('Download', 'XBMC.RunPlugin(%s)' % _addon.build_plugin_url(pars2)))
			#contextMenuItems.append(('jDownloader', ps('cMI.jDownloader.addlink.url') % (urllib.quote_plus(url))))
			labs['title']='Page '+str(count)
			#_addon.add_directory(pars,labs,img=mUrl,fanart=mUrl,is_folder=False,contextmenu_items=contextMenuItems,total_items=ItemCount)
			#pl.add(mUrl, liz)
			name=ptitle+' - '+mNo #str(count)
			
			liz=xbmcgui.ListItem(name,iconImage=mUrl,thumbnailImage=mUrl)
			
			contextMenuItems.append(('Download Wallpaper', 'XBMC.RunPlugin(%s)' % _addon.build_plugin_url( { 'mode':'Download','section':ps('section.wallpaper'),'studio':name,'img':mUrl,'url':mUrl } ) ))
			##if (fanart is not ''): contextMenuItems.append(('Download Wallpaper', 'XBMC.RunPlugin(%s)' % _addon.build_plugin_url( { 'mode': 'Download' , 'section': ps('section.wallpaper') , 'studio': name+' ('+year+')' , 'img': img , 'url': fanart } ) ))
			liz.addContextMenuItems(contextMenuItems, replaceItems=False)
			xbmcplugin.addDirectoryItem(int(sys.argv[1]),mUrl,liz,False)
			count=count+1
		xbmcplugin.endOfDirectory(int(sys.argv[1]))
		return
		play=xbmc.Player(xbmc.PLAYER_CORE_AUTO) ### xbmc.PLAYER_CORE_AUTO | xbmc.PLAYER_CORE_DVDPLAYER | xbmc.PLAYER_CORE_MPLAYER | xbmc.PLAYER_CORE_PAPLAYER
		#try: _addon.resolve_url(url)
		#except: t=''
		try: play.play(pl) # url
		except: t=''
		return
	set_view(ps('content_links'),addst('links-view')); eod()
	### ################################################################

def Library_SaveTo_TV(section,url,img,name,year,country,season_number,episode_number,episode_title):
	##def listEpisodes(section, url, img='', season='') #_param['img']
	show_name=name
	xbmcplugin.setContent( int( sys.argv[1] ), 'episodes' ); WhereAmI('@ the Episodes List for TV Show -- url: %s' % url); html=net.http_GET(url).content
	if (html=='') or (html=='none') or (html==None):
		if (_debugging==True): print 'Html is empty.'
		return
	if (img==''):
		match=re.search( 'coverImage">.+?src="(.+?)"', html, re.IGNORECASE | re.MULTILINE | re.DOTALL); img=match.group(1)
	episodes=re.compile('<span class="epname">[\n].+?<a href="(.+?)"[\n]\s+title=".+?">(.+?)</a>[\n]\s+<a href="/.+?/season-(\d+)/episode-(\d+)/" class=".+?">[\n]\s+(\d+) links</a>', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(html) #; if (_debugging==True): print episodes
	if not episodes: 
		if (_debugging==True): print 'couldn\'t find episodes'
		return
	if (_param['thetvdb_series_id']=='') or (_param['thetvdb_series_id']=='none') or (_param['thetvdb_series_id']==None) or (_param['thetvdb_series_id']==False): thetvdb_episodes=None
	else: thetvdb_episodes=thetvdb_com_episodes2(_param['thetvdb_series_id'])
	#print 'thetvdb_episodes',thetvdb_episodes
	woot=False
	for ep_url, episode_name, season_number, episode_number, num_links in episodes:
		labs={}; s_no=season_number; e_no=episode_number
		if (int(episode_number) > -1) and (int(episode_number) < 10): episode_number='0'+episode_number
		labs['thumbnail']=img; labs['fanart']=_param['fanart']
		labs['EpisodeTitle']=episode_name #; labs['ShowTitle']=''
		labs['title']=season_number+'x'+episode_number+' - '+episode_name+'  [[I]'+num_links+' Links [/I]]'
		ep_url=_domain_url+ep_url; episode_name=messupText(episode_name,True,True,True,True)
		if (thetvdb_episodes==None) or (_param['thetvdb_series_id']==None) or (_param['thetvdb_series_id']==False) or (_param['thetvdb_series_id'] is not '') or (_param['thetvdb_series_id']=='none'): t=''
		if (thetvdb_episodes):
			for db_ep_url, db_sxe_no, db_ep_url2, db_ep_name, db_dateYear, db_dateMonth, db_dateDay, db_hasImage in thetvdb_episodes:
				db_ep_url=ps('meta.tv.domain')+db_ep_url
				db_ep_url2=ps('meta.tv.domain')+db_ep_url2
				if (db_sxe_no.strip()==(s_no+' x '+e_no)):
					if ('Episode #' in episode_name): episode_name=db_ep_name.strip()
					labs['Premeired']=labs['DateAired']=labs['Date']=db_dateYear+'-'+db_dateMonth+'-'+db_dateDay
					labs['year']=db_dateYear; labs['month']=db_dateMonth; labs['day']=db_dateDay
					(db_thumb,labs['thetvdb_series_id'],labs['thetvdb_episode_id']) = Episode__get_thumb(db_ep_url2.strip(),img)
					if (check_ifUrl_isHTML(db_thumb)==True): labs['thumbnail']=db_thumb
					labs['title']=cFL(season_number+cFL('x',ps('cFL_color4'))+episode_number,ps('cFL_color5'))+' - '+cFL(episode_name,ps('cFL_color4'))+cFL('  [[I]'+cFL(num_links+' Links ',ps('cFL_color3'))+'[/I]]',ps('cFL_color'))
					ep_html=mGetItemPage(db_ep_url2); deb('thetvdb - episode - url',db_ep_url2)
					deb('Length of ep_html',str(len(ep_html)))
					if (ep_html is not None) or (ep_html is not False) or (ep_html is not '') or (ep_html is not 'none'):
						labs['PlotOutline']=labs['plot']=mdGetTV(ep_html,['thetvdb.episode.overview1'])['thetvdb.episode.overview1']
		contextMenuItems=[]; labs['season']=season_number; labs['episode']=episode_number
		#contextMenuItems.append((ps('cMI.showinfo.name'),ps('cMI.showinfo.url')))
		#contextMenuItems.append(('Add - Library','XBMC.RunPlugin(%s?mode=%s&section=%s&title=%s&showtitle=%s&showyear=%s&url=%s&img=%s&season=%s&episode=%s&episodetitle=%s)' % ( sys.argv[0],'LibrarySaveEpisode',section, urllib.quote_plus(_param['title']), urllib.quote_plus(_param['showtitle']), urllib.quote_plus(_param['year']), urllib.quote_plus(ep_url), urllib.quote_plus(labs['thumbnail']), urllib.quote_plus(season_number), urllib.quote_plus(episode_number), urllib.quote_plus(episode_name) )))
		labs['title']=messupText(labs['title'],True,True,True,False)
		deb('Episode Name',labs['title'])
		deb('episode thumbnail',labs['thumbnail'])
		#
		Library_SaveTo_Episode(ep_url,labs['thumbnail'],show_name,year,country,season_number,episode_number,episode_name)
		### Library_SaveTo_Episode(url,iconimage,name,year,country,season_number,episode_number,episode_title)
		#
		#if (season==season_number) or (season==''): _addon.add_directory({'mode': 'GetLinks', 'year': _param['year'], 'section': section, 'img': img, 'url': ep_url, 'season': season_number, 'episode': episode_number, 'episodetitle': episode_name}, labs, img=labs['thumbnail'], fanart=labs['fanart'], contextmenu_items=contextMenuItems)
	set_view('episodes',ps('setview.episodes')); eod()


def Menu_BrowseByGenre(section=_default_section_):
	url=''; WhereAmI('@ the Genre Menu')#print 'Browse by genres screen'
	browsebyImg=checkImgLocal(art('genre','.jpg'))
	ItemCount=len(GENRES)*4 # , total_items=ItemCount
	for genre in GENRES:
		gt=addst("genre-thumbs"); img=''; imgName=genre #; pre='http://icons.iconarchive.com/icons/sirubico/movie-genre/128/'
		#if (img==''): img=checkImgLocal(os.path.join(ps('special.home'),'addons','skin.primal','extras','moviegenresposter',imgName+'.jpg'))
		#if (img==''): img=checkImgLocal(os.path.join(ps('special.home'),'addons','skin.tangency','extras','moviegenresposter',imgName+'.jpg'))
		#if (img==''): img=checkImgLocal(os.path.join(ps('special.home'),'addons','plugin.video.1channel','art','themes','PrimeWire',imgName+'.png'))
		#if (img==''): img=checkImgLocal(os.path.join(ps('special.home'),'addons','plugin.video.1channel','art','themes','Glossy_Black',imgName+'.png'))
		#if (img=='') and (browsebyImg is not ''): img=browsebyImg
		#if (img==''): img=_artIcon
		if (gt=='icon.png'): img=_artIcon
		if (gt=='sitelogo'): img=ps('img_kisslogo')
		if (gt=='next'): img=ps('img_next')
		if (gt=='prev'): img=ps('img_prev')
		if (gt=='hot'): img=ps('img_hot')
		if (gt=='updated'): img=ps('img_updated')
		if (gt=='skin.primal'): img=checkImgLocal(os.path.join(ps('special.home'),'addons','skin.primal','extras','moviegenresposter',imgName+'.jpg'))
		if (gt=='skin.tangency'): img=checkImgLocal(os.path.join(ps('special.home'),'addons','skin.tangency','extras','moviegenresposter',imgName+'.jpg'))
		if (gt=='1ch.PrimeWire'): img=checkImgLocal(os.path.join(ps('special.home'),'addons','plugin.video.1channel','art','themes','PrimeWire',imgName+'.png'))
		if (gt=='1ch.Glossy_Black'): img=checkImgLocal(os.path.join(ps('special.home'),'addons','plugin.video.1channel','art','themes','Glossy_Black',imgName+'.png'))
		if (gt=='kiss.png'): img=art('kiss')
		if (gt=='genre.jpg'): img=art('genre','.jpg')
		if (gt=='turtle.jpg'): img=art('turtle','.jpg')
		if (gt=='mkv.png'): img=art('mkv')
		if (gt=='mp4.png'): img=art('mp4')
		if (gt=='flv.png'): img=art('flv')
		if (img==''): img=_artIcon
		_addon.add_directory({'mode': 'SelectSort','url': _domain_url+'/Genre/'+genre.replace(' ','-')},{'title':genre},img=img,fanart=_artFanart,total_items=ItemCount)
	set_view('list',addst('default-view')); eod()

def Select_Genre(url=''):
	if (url==''): url=_domain_url+'/'+ps('common_word')+'List'
	WhereAmI('@ the Select Genre Menu'); option_list=GENRES; r=askSelection(option_list,'Select Genre')
	#if   (r==0): Select_Sort(url+option_list[r].lower(),AZ='')
	if (r== -1): eod(); return
	else: Select_Sort(url+'/Genre/'+option_list[r].replace(' ','-'),AZ='')

def Select_Sort(url='',AZ='all'):
	if (url==''): url=_domain_url+'/'+ps('common_word')+'List'
	WhereAmI('@ the Select Sort Menu'); AZ=AZ.lower();
	option_list=['Alphabetical','Most Popular','Latest Update','New '+ps('common_word')]
	path_list  =['','/MostPopular','/LatestUpdate','/Newest']
	if (AZ=='') or (AZ=='all'): AZTag=''
	elif ('?' in url): AZTag='&c='+AZ
	else: AZTag='?c='+AZ
	pn='1'; pc=addst('pages'); ItemCount=4 #len(GENRES)
	_addon.add_directory({'mode':'GetTitles','url':url+''+AZTag,'pageno':pn,'pagecount':pc},{'title':'Alphabetical'},img=_artIcon,fanart=_artFanart,total_items=ItemCount)
	_addon.add_directory({'mode':'GetTitles','url':url+'/MostPopular'+AZTag,'pageno':pn,'pagecount':pc},{'title':'Most Popular'},img=ps('img_hot'),fanart=_artFanart,total_items=ItemCount)
	_addon.add_directory({'mode':'GetTitles','url':url+'/LatestUpdate'+AZTag,'pageno':pn,'pagecount':pc},{'title':'Latest Update'},img=ps('img_updated'),fanart=_artFanart,total_items=ItemCount)
	_addon.add_directory({'mode':'GetTitles','url':url+'/Newest'+AZTag,'pageno':pn,'pagecount':pc},{'title':'New '+ps('common_word')},img=_artIcon,fanart=_artFanart,total_items=ItemCount)
	set_view('list',addst('default-view')); eod()

def Select_AZ(url=''):
	if (url==''): url=_domain_url+'/'+ps('common_word')+'List'
	option_list=['All','0','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
	WhereAmI('@ the Select AZ Menu')
	pn='1'; pc=addst('pages'); ItemCount=len(option_list)
	for oo in option_list:
		if (oo=='All'): ooo=''
		else: ooo=oo.lower()
		gt=addst("az-thumbs"); img='';
		if (gt=='icon.png'): img=_artIcon
		if (gt=='sitelogo'): img=ps('img_kisslogo')
		if (gt=='next'): img=ps('img_next')
		if (gt=='prev'): img=ps('img_prev')
		if (gt=='hot'): img=ps('img_hot')
		if (gt=='updated'): img=ps('img_updated')
		if (gt=='kiss.png'): img=art('kiss')
		if (gt=='genre.jpg'): img=art('genre','.jpg')
		if (gt=='turtle.jpg'): img=art('turtle','.jpg')
		if (gt=='mkv.png'): img=art('mkv')
		if (gt=='mp4.png'): img=art('mp4')
		if (gt=='flv.png'): img=art('flv')
		if (gt=='chromatix.lower'): 
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/chromatix/keyboard-keys/128/alt-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/chromatix/keyboard-keys/128/hash-icon.png'
			else:						img='http://icons.iconarchive.com/icons/chromatix/keyboard-keys/128/letter-'+oo.lower()+'-icon.png'
		if (gt=='chromatix.upper'): 
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/chromatix/keyboard-keys/128/alt-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/chromatix/keyboard-keys/128/hash-icon.png'
			else:						img='http://icons.iconarchive.com/icons/chromatix/keyboard-keys/128/letter-uppercase-'+oo.upper()+'-icon.png'
		if (gt=='dooffy.lower'): 
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/dooffy/characters/256/At-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/dooffy/characters/256/0-Hash-icon.png'
			else:						img='http://icons.iconarchive.com/icons/dooffy/characters/256/'+oo.upper()+'1-icon.png'
		if (gt=='dooffy.upper'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/dooffy/characters/256/At-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/dooffy/characters/256/0-Hash-icon.png'
			else:						img='http://icons.iconarchive.com/icons/dooffy/characters/256/'+oo.upper()+'2-icon.png'
		if (gt=='balloon-green'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/iconexpo/speech-balloon-green/256/speech-balloon-green-a-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/iconexpo/speech-balloon-green/256/speech-balloon-green-o-icon.png'
			else:						img='http://icons.iconarchive.com/icons/iconexpo/speech-balloon-green/256/speech-balloon-green-'+oo.lower()+'-icon.png'
		if (gt=='balloon-orange'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/iconexpo/speech-balloon-orange/256/speech-balloon-orange-a-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/iconexpo/speech-balloon-orange/256/speech-balloon-orange-o-icon.png'
			else:						img='http://icons.iconarchive.com/icons/iconexpo/speech-balloon-orange/256/speech-balloon-orange-'+oo.lower()+'-icon.png'
		if (gt=='balloon-grey'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/iconexpo/speech-balloon-grey/256/speech-balloon-white-a-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/iconexpo/speech-balloon-grey/256/speech-balloon-white-o-icon.png'
			else:						img='http://icons.iconarchive.com/icons/iconexpo/speech-balloon-grey/256/speech-balloon-white-'+oo.lower()+'-icon.png'
		if (gt=='red-orb'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/iconarchive/red-orb-alphabet/256/At-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/iconarchive/red-orb-alphabet/256/Hash-icon.png'
			else:						img='http://icons.iconarchive.com/icons/iconarchive/red-orb-alphabet/256/Letter-A-icon.png'
		if (gt=='ariil.letter'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/ariil/alphabet/256/Letter-A-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/ariil/alphabet/256/Letter-O-icon.png'
			else:						img='http://icons.iconarchive.com/icons/ariil/alphabet/256/Letter-'+oo.upper()+'-icon.png'
		if (gt=='hydrattz.pink'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-pink-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-pink-icon.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-pink-icon.png'
		if (gt=='hydrattz.blue'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-blue-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-blue-icon.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-blue-icon.png'
		if (gt=='hydrattz.gold'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-blue-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-blue-icon.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-blue-icon.png'
		if (gt=='hydrattz.red'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-red-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-red-icon.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-red-icon.png'
		if (gt=='hydrattz.black'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-black-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-black-icon.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-black-icon.png'
		if (gt=='hydrattz.grey'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-blue-grey.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-blue-grey.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-grey-icon.png'
		if (gt=='hydrattz.lg'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-lg-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-lg-icon.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-lg-icon.png'
		if (gt=='hydrattz.dg'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-dg-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-dg-icon.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-dg-icon.png'
		if (gt=='hydrattz.violet'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-violet-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-violet-icon.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-violet-icon.png'
		if (gt=='hydrattz.orange'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-orange-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-orange-icon.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-orange-icon.png'
		if (gt=='mattahan'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/mattahan/umicons/256/Letter-A-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/mattahan/umicons/256/Number-9-icon.png'
			else:						img='http://icons.iconarchive.com/icons/mattahan/umicons/256/Letter-'+oo.upper()+'-icon.png'
		#if (gt==''):
		#	if (oo=='all'):	img=''
		#	if (oo=='0'):		img=''
		#	else:						img=''
		#if (gt==''): img=''
		#if (gt==''): img=
		if (img==''): img=_artIcon
		_addon.add_directory({'mode':'SelectSort','url':url,'title':ooo,'pageno':pn,'pagecount':pc},{'title':oo},img=_artIcon,fanart=_artFanart,total_items=ItemCount)
	set_view('list',addst('default-view')); eod()

def _DoGetItems(url): 
	#xbmc.executebuiltin("XBMC.RunPlugin(%s)" % _addon.build_plugin_url({'mode':'GetTitles','url':url,'pageno':'1','pagecount':addst('pages')}))
	xbmc.executebuiltin("XBMC.Container.Update(%s)" % _addon.build_plugin_url({'mode':'GetTitles','url':url,'pageno':'1','pagecount':addst('pages')}))
	#listItems('',url,'1',addst('pages'))

##def listItems(section=_default_section_, url='', html='', episode=False, startPage='1', numOfPages='1', genre='', year='', stitle=''): # List: Movies or TV Shows
def listItems(section=_default_section_, url='', startPage='1', numOfPages='1', genre='', year='', stitle='', season='', episode='', html='', chck=''): # List: Movies or TV Shows
	if (url==''): return
	#if (chck=='Latest'): url=url+chr(35)+'latest'
	WhereAmI('@ the Item List -- url: %s' % url)
	start=int(startPage); end=(start+int(numOfPages)); html=''; html_last=''; nextpage=startPage; deb('page start',str(start)); deb('page end',str(end))
	try: html_=net.http_GET(url).content
	except: 
		try: html_=getURL(url)
		except: 
			try: html_=getURLr(url,_domain_url)
			except: html_=''
	#print html_
	if (html_=='') or (html_=='none') or (html_==None): 
		deb('Error','Problem with page'); deadNote('Results:  '+section,'No results were found.')
		return
	try:		last=int(re.compile('<li><a href="http://.+?page=\d+">(\d+)</a></li>[\n]\s+<li class="next">', re.IGNORECASE | re.DOTALL).findall(html_))[0]
	except:	last=2
	deb('number of pages',str(last))
	#print min(last,end)
	if ('<h1>Nothing was found by your request</h1>' in html_):
		deadNote('Results:  '+section,'Nothing was found by your request'); eod(); return
	pmatch=re.findall(ps('LI.page.find'), html_)
	if pmatch: last=pmatch[-1]
	if ('?' in url):	urlSplitter='&page='; deb('urlSplitter',urlSplitter) ## Quick fix for urls that already have '?' in it.
	else:							urlSplitter='?page='; deb('urlSplitter',urlSplitter)
	for page in range(start,min(last,end)):
		if (int(page)> 1): #if (int(startPage)> 1):
			if ('&page=' in url): pageUrl=url.replace('&page=','&pagenull=')+'&page='+str(page) ## Quick fix.
			if ('?page=' in url): pageUrl=url.replace('?page=','?pagenull=')+'&page='+str(page) ## Quick fix.
			else: pageUrl=url+urlSplitter+str(page) #ps('LI.page.param')+startPage
		else: pageUrl=url
		deb('item listings for',pageUrl)
		try: 
			try: html_last=net.http_GET(pageUrl).content
			except: 
				try: html_=getURL(url)
				except: t=''
			if (_shoDebugging==True) and (html_last==''): deadNote('Testing','html_last is empty')
			if (html_last in html): t=''
			else: html=html+'\r\n'+html_last
			##if (_debugging==True): print html_last
		except: t=''
	if (ps('LI.nextpage.check') in html_last): 
		if (_debugging==True): print 'A next-page has been found.'
		nextpage=re.findall(ps('LI.nextpage.match'), html_last)[0] #nextpage=re.compile('<li class="next"><a href="http://www.solarmovie.so/.+?.html?page=(\d+)"></a></li>').findall(html_last)[0]
		if (int(nextpage) <= last) and (end < last) and (start < last) and (start is not int(nextpage)): #(int(nextpage) > end) and (int(nextpage) <= last): # and (end < last): ## Do Show Next Page Link ##
			if (_debugging==True): print 'A next-page is being added.'
			#print {'mode': 'GetTitles', 'url': url, 'pageno': nextpage, 'pagecount': numOfPages}
			_addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': nextpage, 'pagecount': numOfPages}, {'title': ps('LI.nextpage.name')}, img=ps('img_next'))
			#print {'start':str(start),'end':str(end),'last':str(last),'nextpage':str(nextpage)}
	###	### _addon.add_directory({'mode': 'GetTitles', 'url': url, 'startPage': str(end), 'numOfPages': numOfPages}, {'title': 'Next...'})
	###html=nolines(html)
	html=ParseDescription(html); html=remove_accents(html) #if (_debugging==True): print html
	html=messupText(html,_html=True,_ende=True,_a=False,Slashes=False)
	deb('Length of HTML',str(len(html))); #debob(nolines(html)); 
	######
	if (len(html)==0): deb('Error','html is empty.'); return
	#s='<a\n*\s*href="(/'+ps('common_word')+'/[A-Za-z0-9\-/_]+)"\n*\s*title=\'(.*?)\'\n*\s*/*>\n*\s*(.+?)\s*\n*\s*</a>'
	s='<tr.*?>\s*<td\s+title=\'(.*?)\'\s*[/]*>\s*<a\s+href="(/'+ps('common_word')+'/.+?)"\s*[/]*>\s*(.+?)\s*</a>\s*(.*?)\s*</td>\s*<td>\s*(.*?)\s*</td>\s*</tr'
	iitems=re.compile(s, re.DOTALL).findall(nolines(html)) ### , re.MULTILINE | re.IGNORECASE | re.DOTALL
	if (iitems is not None):
		ItemCount=len(iitems) # , total_items=ItemCount
		deb('# of items',str(ItemCount))
		EnableMeta=tfalse(addst("enableMeta"))
		for tInfo,item_url,name,TD1,TD2 in iitems:
			contextMenuItems=[]; item_url=_domain_url+item_url; labs={}; 
			try: img=re.compile('"(http://.+?\.jpg)"').findall(tInfo)[0].replace(' ','%20')
			except: img=_artIcon
			fimg=''+img
			if ('<p>' in tInfo) and ('</p>' in tInfo):
				try: labs['plot']=re.compile('<p>\s*\n*\s*(.+?)\s*\n*\s*</p>').findall(tInfo)[0].strip()
				except: labs['plot']=''
			else: labs['plot']=''
			#
			#	### [ KissAnime Stuff Removed. ] ###
			#
			#mlabs['']  mlabs['backdrop_url']
			#try: img=re.compile('("http://kissanime.com/Uploads/Etc/[0-9\-]+/[0-9]+[A-Za-z0-9\-_/\s]*.jpg)"').findall(tInfo)[0]
			labs['title']=name #.replace(' (Dub)',' [COLOR green](Dub)[/COLOR]').replace(' (Sub)',' [COLOR blue](Sub)[/COLOR]').replace(' OVA',' [COLOR red]OVA[/COLOR]').replace(' Movie',' [COLOR maroon]Movie[/COLOR]').replace(': ',':[CR] ').replace(' New',' [COLOR yellow]New[/COLOR]').replace(' (TV)',' [COLOR cornflowerblue](TV)[/COLOR]').replace(' Specials',' [COLOR deeppink]Specials[/COLOR]') #.replace('','')
			deb('title',labs['title']); deb('url',item_url); deb('plot',labs['plot']); deb('img',img); deb('fanart',fimg)
			##### Right Click Menu for: Anime #####
			contextMenuItems.append((ps('cMI.showinfo.name'),ps('cMI.showinfo.url')))
			contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.1.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url), '' )))
			if (tfalse(addst("enable-fav-movies-2"))==True): contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.2.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url),'2' )))
			if (tfalse(addst("enable-fav-movies-3"))==True): contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.3.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url),'3' )))
			if (tfalse(addst("enable-fav-movies-4"))==True): contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.4.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url),'4' )))
			##if (labs['fanart'] is not ''): contextMenuItems.append(('Download Wallpaper', 'XBMC.RunPlugin(%s)' % _addon.build_plugin_url( { 'mode': 'Download' , 'section': ps('section.wallpaper') , 'studio': name+'  ('+year+')' , 'img': labs['thumbnail'] , 'url': labs['fanart'] } ) ))
			##contextMenuItems.append(('Add - Library','XBMC.RunPlugin(%s?mode=%s&section=%s&title=%s&showtitle=%s&showyear=%s&url=%s&img=%s)' % ( sys.argv[0],'LibrarySaveMovie',section, urllib.quote_plus(name), urllib.quote_plus(name), urllib.quote_plus(year), urllib.quote_plus(_domain_url+item_url), urllib.quote_plus(thumbnail))))
			##if os.path.exists(xbmc.translatePath(ps('special.home.addons'))+ps('cMI.1ch.search.folder')):
			##	contextMenuItems.append((ps('cMI.1ch.search.name'), 					ps('cMI.1ch.search.url') 				% (ps('cMI.1ch.search.plugin'), 			ps('cMI.1ch.search.section'), 			name)))
			##if os.path.exists(xbmc.translatePath(ps('special.home.addons'))+ps('cMI.primewire.search.folder')):
			##	contextMenuItems.append((ps('cMI.primewire.search.name'), 		ps('cMI.primewire.search.url') 	% (ps('cMI.primewire.search.plugin'), ps('cMI.primewire.search.section'), name)))
			##### Right Click Menu for: Anime ##### /\ #####
			pars={'mode':'GetEpisodes','url':item_url,'img':img,'title':labs['title']}
			_addon.add_directory(pars, labs, img=img, fanart=fimg, contextmenu_items=contextMenuItems, total_items=ItemCount)
	else: deb('Error','no items found.')
	set_view(ps('content_tvshows'),addst('anime-view')); eod(); return
	################################################################################

def listEpisodes(section, url, img='', showtitle='', season=''): #_param['img']
	xbmcplugin.setContent( int( sys.argv[1] ), 'episodes' ); WhereAmI('@ the Episodes List for TV Show -- url: %s' % url); 
	html=net.http_GET(url).content; 
	#html=nURL(url); 
	deb("length of html",str(len(html))); 
	if (html=='') or (html=='none') or (html==None): deb('Html','is empty.' ); return
	#if 'confirm=yes">Yes</a>|<a href="/">No</a></p>' in html: 
	
	if "This series has been categorized as 'mature', therefore may contain intense violence, blood/gore, sexual content and/or strong language. So if you're above the legal age of 18, do you want to continue the reading?</p>" in html:
		if tfalse(addst("mature-content"))==True:
			myNote("Mature Content","Make sure your of appropriate age.")
			html=net.http_GET(url+'?confirm=yes').content; 
			#html=nURL(url+'?confirm=yes'); 
		else:
			myNote("Mature Content","Check -General- Addon Settings.");
			eod(); return
	
	_addon.addon.setSetting(id="LastShowListedURL", value=url)
	_addon.addon.setSetting(id="LastShowListedIMG", value=img)
	_addon.addon.setSetting(id="LastShowListedNAME", value=showtitle)
	metadata_tv_episodes=tfalse(addst("metadata_tv_episodes")); metadata_tv_ep_plot=tfalse(addst("metadata_tv_ep_plot"))
	if (html=='') or (html=='none') or (html==None): deb('Html','is empty.' ); return
	html=messupText(html,_html=True,_ende=True,_a=False,Slashes=False)
	#teh_tool._SaveFile(os.path.join(addonPath,'testing.txt'),html); 
	#if (img==''): match=re.search( 'coverImage">.+?src="(.+?)"', html, re.IGNORECASE | re.MULTILINE | re.DOTALL); img=match.group(1)
	if (img==''): img=_artIcon
	s='<tr>\s*\n*\s*<td>\s*\n*\s*<a\s*\n*\s*href="(/'+ps('common_word')+'/.+?\?id=[0-9]+)"\s*\n*\s*title="'+ps('common_word2')+' .+?"\s*\n*\s*>\s*\n*\s*(.+?)\s*\n*\s*</a>\s*\n*\s*</td>\s*\n*\s*<td>\s*\n*\s*([0-9/]*)\s*\n*\s*</td>'
	try:		episodes=re.compile(s, re.DOTALL).findall(html)
	except:	episodes=''
	if (not episodes) or (episodes==None) or (episodes==False) or (episodes==''): deb('Episodes','couldn\'t find episodes'); eod(); return
	ItemCount=len(episodes) # , total_items=ItemCount
	for ep_url, ep_name, ep_date in episodes:
		contextMenuItems=[]; labs={}; ep_url=_domain_url+ep_url
		contextMenuItems.append((ps('cMI.showinfo.name'),ps('cMI.showinfo.url')))
		#contextMenuItems.append(('Add - Library','XBMC.RunPlugin(%s?mode=%s&section=%s&title=%s&showtitle=%s&showyear=%s&url=%s&img=%s&season=%s&episode=%s&episodetitle=%s)' % ( sys.argv[0],'LibrarySaveEpisode',section, urllib.quote_plus(_param['title']), urllib.quote_plus(_param['showtitle']), urllib.quote_plus(_param['year']), urllib.quote_plus(ep_url), urllib.quote_plus(labs['thumbnail']), urllib.quote_plus(season_number), urllib.quote_plus(episode_number), urllib.quote_plus(episode_name) )))
		labs['title']=''+ep_name
		if ('[CR]' not in labs['title']): labs['title']=labs['title'].replace(' The Movie',' [CR]The Movie')
		if ('[CR]' not in labs['title']): labs['title']=labs['title'].replace(' Movie',' [CR]Movie')
		if ('[CR]' not in labs['title']): labs['title']=labs['title'].replace(' Episode',' [CR]Episode')
		if ('[CR]' not in labs['title']): labs['title']=labs['title'].replace(' OVA',' [CR]OVA')
		if ('[CR]' not in labs['title']): labs['title']=labs['title'].replace(' _Special',' [CR]Special')
		if ('[CR]' not in labs['title']): labs['title']=labs['title'].replace(' _Preview',' [CR]Preview')
		if ('[CR]' in labs['title']): labs['title']=labs['title'].split('[CR]')[1]
		labs['title']=labs['title'].replace(' '+ps('common_word2')+' Online','')
		#labs['title']=labs['title']+cFL('  ['+cFL(ep_date.replace('/',cFL('/','pink')),'blue')+']','pink')
		try: (labs['month'],labs['day'],labs['year'])=ep_date.split('/')
		except: labs['month']=''; labs['day']; labs['year']
		mdy=cFL('  ['+cFL(labs['month'],'deeppink')+'/'+cFL(labs['day'],'deepskyblue')+'/'+cFL(labs['year'],'blueviolet')+']','pink')
		if (len(labs['month']) > 0) and (len(labs['day']) > 0) and (len(labs['year']) > 0): labs['title']+=mdy
		else: labs['title']+=cFL('  ['+cFL(ep_date.replace('/',cFL('/','pink')),'blue')+']','pink')
		labs['plot']=cFL(ep_name,'red')
		labs['plot']+=cFL('[CR]Date Added:  ['+cFL(ep_date.replace('/',cFL('/','pink')),'blue')+'][CR]','pink'); labs['Date']=ep_date.replace('/','-')
		labs['premiered']=ep_date.replace('/','-')
		deb('Episode Name',labs['title']); deb('episode thumbnail',img)
		pars={'mode':'GetLinks','img':img,'url':ep_url,'title':ep_name}
		_addon.add_directory(pars,labs,img=img,fanart=img,contextmenu_items=contextMenuItems,total_items=ItemCount)
		#
	set_view(ps('content_episodes'),addst('episode-view')); eod() #set_view('episodes',ps('setview.episodes')); eod()

def Menu_LoadCategories(section=_default_section_): #Categories
	WhereAmI('@ the Category Menu')
	### ###################################################################################################################################################################################################################################
	### ###################################################################################################################################################################################################################################
	if  ( section == ps('section.trailers')): ## Trailers #################################################################################################################################################################################
		_addon.add_directory({'section': section, 'mode': 'TrailersGenres', 'url': 'http://www.solarmovie.so/coming-soon/date/' },	 				{'title':  cFL('G',ps('cFL_color'))+'enre By Release Date'},fanart=_artFanart,img=art('genre','.jpg'))
		_addon.add_directory({'section': section, 'mode': 'TrailersGenres', 'url': 'http://www.solarmovie.so/coming-soon/popularity/' },	 	{'title':  cFL('G',ps('cFL_color'))+'enre By Popularity'}, 	fanart=_artFanart,img=art('genre','.jpg'))
	#elif  ( section == ps('sectoin.trailers.popular')): ###### Trailers Popular #############################################################################################################################################################
	#elif  ( section == ps('sectoin.trailers.releasedate')): ## Trailers Release Date ########################################################################################################################################################
	elif  ( section == ps('section.users')): ## Users #######################################################################################################################################################################################
		_addon.add_directory({'section': section, 'mode': 'listUsers', 'url': 'http://www.solarmovie.so/ratings/moderator/' },	 				{'title':  cFL('M',ps('cFL_color'))+'oderators'}, 	fanart=_artFanart,img=ps('img.usersection'))
		_addon.add_directory({'section': section, 'mode': 'listUsers', 'url': 'http://www.solarmovie.so/ratings/linker/' },	 						{'title':  cFL('L',ps('cFL_color'))+'inkers'}, 			fanart=_artFanart,img=ps('img.usersection'))
		_addon.add_directory({'section': section, 'mode': 'listUsers', 'url': 'http://www.solarmovie.so/ratings/linker/' },	 						{'title':  cFL('U',ps('cFL_color'))+'ploaders'}, 		fanart=_artFanart,img=ps('img.usersection'))
		_addon.add_directory({'section': section, 'mode': 'listUsers', 'url': 'http://www.solarmovie.so/ratings/linker/' },	 						{'title':  cFL('U',ps('cFL_color'))+'sers'}, 				fanart=_artFanart,img=ps('img.usersection'))
	elif  ( section == ps('section.tv')): ######## TV Shows #################################################################################################################################################################################
		_addon.add_directory({'section': section, 'mode': 'Search', 				'pageno': '1', 'pagecount': addst('pages')},			{'title':  cFL('S',ps('cFL_color'))+'earch'}, 						fanart=_artFanart,img=art('icon-search'))
		_addon.add_directory({'section': section, 'mode': 'AdvancedSearch', 'pageno': '1', 'pagecount': addst('pages')},	 		{'title':  cFL('A',ps('cFL_color'))+'dvanced Search'}, 		fanart=_artFanart,img=art('icon-search'))
		_addon.add_directory({'section': section, 'mode': 'GetTitlesLatestWatched', 'url': _domain_url+'/latest-watched-movies.html', 'pageno': '1','pagecount': '1'}, 			{'title':  cFL('L',ps('cFL_color'))+'atest Watched'}, 		img=_art150,fanart=_artFanart)
		_addon.add_directory({'section': section, 'mode': 'GetTitlesLatest', 				'url': _domain_url+'/', 'pageno': '1','pagecount': '1'}, 																{'title':  cFL('L',ps('cFL_color'))+'atest Added'}, 			img=_art150,fanart=_artFanart)
		_addon.add_directory({'section': section, 'mode': 'GetTitlesPopular', 			'url': _domain_url+ps('domain.url.tv')+'/', 'pageno': '1','pagecount': '1'}, 						{'title':  cFL('P',ps('cFL_color'))+'opular (ALL TIME)'}, img=_art150,fanart=_artFanart)
		_addon.add_directory({'section': section, 'mode': 'GetTitlesNewPopular', 		'url': _domain_url+ps('domain.url.tv')+'/', 'pageno': '1','pagecount': '1'}, 						{'title':  cFL('P',ps('cFL_color'))+'opular (NEW)'}, 			img=_art150,fanart=_artFanart)
		_addon.add_directory({'section': section, 'mode': 'BrowseCountry'},	 			{'title':  cFL('C',ps('cFL_color'))+'ountry'}, 		fanart=_artFanart,img=art('countries','.jpg'))
		_addon.add_directory({'section': section, 'mode': 'BrowseGenre'},	 				{'title':  cFL('G',ps('cFL_color'))+'enre'}, 			fanart=_artFanart,img=art('genre','.jpg'))
		_addon.add_directory({'section': section, 'mode': 'BrowseYear'}, 					{'title':  cFL('Y',ps('cFL_color'))+'ear'}, 			fanart=_artFanart,img=art('year','.gif'))
		_addon.add_directory(  {'section': section, 'mode': 'FavoritesList'},	 										{'title':  cFL('F',ps('cFL_color'))+'avorites '+addst('fav.tv.1.name')},fanart=_artFanart,img=_art404)
		_addon.add_directory(  {'section': section, 'mode': 'FavoritesList', 	'subfav': '2'},	 		{'title':  cFL('F',ps('cFL_color'))+'avorites '+addst('fav.tv.2.name')},fanart=_artFanart,img=_art404)
		_addon.add_directory(  {'section': section, 'mode': 'FavoritesList', 	'subfav': '3'},	 		{'title':  cFL('F',ps('cFL_color'))+'avorites '+addst('fav.tv.3.name')},fanart=_artFanart,img=_art404)
		if (_setting['label-empty-favorites']==True):
			_addon.add_directory({'section': section, 'mode': 'FavoritesEmpty', 'subfav': ''},	 		{'title':  cFL('E',ps('cFL_color'))+'mpty Favorites '+addst('fav.tv.1.name')},img=art('trash','.gif'),fanart=_artFanart,is_folder=False)
			_addon.add_directory({'section': section, 'mode': 'FavoritesEmpty', 'subfav': '2'},	 		{'title':  cFL('E',ps('cFL_color'))+'mpty Favorites '+addst('fav.tv.2.name')},img=art('trash','.gif'),fanart=_artFanart,is_folder=False)
			_addon.add_directory({'section': section, 'mode': 'FavoritesEmpty', 'subfav': '3'},	 		{'title':  cFL('E',ps('cFL_color'))+'mpty Favorites '+addst('fav.tv.3.name')},img=art('trash','.gif'),fanart=_artFanart,is_folder=False)
		_addon.add_directory(  {'section': section, 'mode': ps('cMI.airdates.find.mode'), 	'title': ''},	 		{'title':  cFL('F',ps('cFL_color'))+'ind Air-Dates'},fanart=_artFanart,img=_art404)
	elif  ( section == ps('section.movie')): ##### Movies ###################################################################################################################################################################################
		_addon.add_directory({'section': section, 'mode': 'Search', 				'pageno': '1', 'pagecount': addst('pages')},			{'title':  cFL('S',ps('cFL_color'))+'earch'}, 						fanart=_artFanart,img=art('icon-search'))
		_addon.add_directory({'section': section, 'mode': 'AdvancedSearch', 'pageno': '1', 'pagecount': addst('pages')},	 		{'title':  cFL('A',ps('cFL_color'))+'dvanced Search'}, 		fanart=_artFanart,img=art('icon-search'))
		_addon.add_directory({'section': section, 'mode': 'GetTitles', 							'url': _domain_url+'/latest-watched-movies.html', 'pageno': '1','pagecount': '1'}, 			{'title':  cFL('L',ps('cFL_color'))+'atest Watched'}, 		img=_art150,fanart=_artFanart)
		_addon.add_directory({'section': section, 'mode': 'GetTitlesLatest', 				'url': _domain_url+'/', 'pageno': '1','pagecount': '1'}, 																{'title':  cFL('L',ps('cFL_color'))+'atest Added'}, 			img=_art150,fanart=_artFanart)
		_addon.add_directory({'section': section, 'mode': 'GetTitlesNewPopular', 		'url': _domain_url+'/', 'pageno': '1','pagecount': '1'}, 																{'title':  cFL('P',ps('cFL_color'))+'opular (NEW)'}, 			img=_art150,fanart=_artFanart)
		_addon.add_directory({'section': section, 'mode': 'GetTitlesHDPopular', 		'url': _domain_url+'/', 'pageno': '1','pagecount': '1'}, 																{'title':  cFL('P',ps('cFL_color'))+'opular (HD)'}, 			img=_art150,fanart=_artFanart)
		_addon.add_directory({'section': section, 'mode': 'GetTitlesOtherPopular', 	'url': _domain_url+'/', 'pageno': '1','pagecount': '1'}, 																{'title':  cFL('P',ps('cFL_color'))+'opular (OTHER)'}, 		img=_art150,fanart=_artFanart)
		_addon.add_directory({'section': section, 'mode': 'BrowseCountry'},	 			{'title':  cFL('C',ps('cFL_color'))+'ountry'}, 		fanart=_artFanart,img=art('countries','.jpg'))
		_addon.add_directory({'section': section, 'mode': 'BrowseGenre'},	 				{'title':  cFL('G',ps('cFL_color'))+'enre'}, 			fanart=_artFanart,img=art('genre','.jpg'))
		_addon.add_directory({'section': section, 'mode': 'BrowseYear'}, 					{'title':  cFL('Y',ps('cFL_color'))+'ear'}, 			fanart=_artFanart,img=art('year','.gif'))
		#_addon.add_directory(  {'section': section, 'mode': 'ComingSoon'},	 											{'title':  cFL('C',ps('cFL_color'))+'oming Soon'},fanart=_artFanart,img='http://www.mirrorservice.org/sites/addons.superrepo.org/Frodo/.metadata/plugin.video.trailer.addict.png')
		_addon.add_directory(  {'section': section, 'mode': 'FavoritesList'},	 										{'title':  cFL('F',ps('cFL_color'))+'avorites '+addst('fav.movies.1.name')},fanart=_artFanart,img=_art404)
		_addon.add_directory(  {'section': section, 'mode': 'FavoritesList', 	'subfav': '2'},	 		{'title':  cFL('F',ps('cFL_color'))+'avorites '+addst('fav.movies.2.name')},fanart=_artFanart,img=_art404)
		if (_setting['label-empty-favorites']==True):
			_addon.add_directory({'section': section, 'mode': 'FavoritesEmpty', 'subfav':  ''},	 		{'title':  cFL('E',ps('cFL_color'))+'mpty Favorites '+addst('fav.movies.1.name')},fanart=_artFanart,img=art('trash','.gif'),is_folder=False)
			_addon.add_directory({'section': section, 'mode': 'FavoritesEmpty', 'subfav': '2'},	 		{'title':  cFL('E',ps('cFL_color'))+'mpty Favorites '+addst('fav.movies.2.name')},fanart=_artFanart,img=art('trash','.gif'),is_folder=False)
	### ###################################################################################################################################################################################################################################
	### ###################################################################################################################################################################################################################################
	### 
	###_addon.add_directory({'section': section, 'mode': 'BrowseAtoZ'}, 			{'title':  'A-Z'})
	#_addon.add_directory({'section': section, 'mode': 'GetSearchQuery'}, 		{'title':  'Search'})
	###_addon.add_directory({'section': section, 'mode': 'GetTitles'}, 				{'title':  'Favorites'})
	set_view('list',addst('default-view')); eod()
	### http://www.solarmovie.so/latest-movies.html
	### 
	### 

def Menu_Last():
	WhereAmI('@ the Last Menu')
	if (len(addst("LastShowListedURL")) > 0): _addon.add_directory({'mode':'GetEpisodes','url':addst("LastShowListedURL")},{'title':cFL_('Last '+ps('common_word')+' Visited:[CR]'+cFL(addst("LastShowListedNAME"),'blue'),ps('cFL_color'))},fanart=addst("LastShowListedIMG"),img=addst("LastShowListedIMG"))
	#if (len(addst("LastVideoPlayItemUrl")) > 0): _addon.add_directory({'mode':'PlayVideo','url':addst("LastVideoPlayItemUrl"),'title':addst('LastVideoPlayItemName'),'studio':addst('LastVideoPlayItemStudio')},{'title':cFL_('Last Video [Played]: '+cFL(addst('LastVideoPlayItemName'),ps('cFL_color3'))+'[CR]'+cFL(addst('LastVideoPlayItemStudio'),'blue'),ps('cFL_color'))},fanart=addst("LastVideoPlayItemImg"),img=addst("LastVideoPlayItemImg"))
	#if (len(addst("LastAutoPlayItemUrl")) > 0): _addon.add_directory({'mode':'PlayVideo','url':addst("LastAutoPlayItemUrl"),'title':addst('LastAutoPlayItemName')},{'title':cFL_('Last Video [AutoPlay]:[CR]'+cFL(addst('LastAutoPlayItemName'),'blue'),ps('cFL_color'))},fanart=addst("LastShowListedIMG"),img=addst("LastShowListedIMG"))
	set_view('list',addst('default-view')); eod()

def Menu_MainMenu(): #The Main Menu
	WhereAmI('@ the Main Menu')
	_addon.add_directory({'mode':'SelectAZ','url':_domain_url+'/'+ps('common_word')+'List'},{'title':cFL_(ps('common_word')+' List ( All | # | A-Z )',ps('cFL_color'))},fanart=_artFanart,img=ps('img_kisslogo'))
	_addon.add_directory({'mode':'GetTitles','url':_domain_url+'/Status/Ongoing'},{'title':cFL_('Ongoing',ps('cFL_color'))},fanart=_artFanart,img=ps('img_kisslogo'))
	_addon.add_directory({'mode':'GetTitles','url':_domain_url+'/Status/Completed'},{'title':cFL_('Completed',ps('cFL_color'))},fanart=_artFanart,img=ps('img_kisslogo'))
	_addon.add_directory({'mode':'BrowseGenre','url':_domain_url+'/'},{'title':cFL_('Genre',ps('cFL_color'))},fanart=_artFanart,img=art('genre','.jpg'))
	_addon.add_directory({'mode':'GetTitles','url':_domain_url+'/'+ps('common_word')+'List/Newest'},{'title':cFL_(ps('common_word')+' List [Newest]',ps('cFL_color'))},fanart=_artFanart,img=ps('img_kisslogo'))
	_addon.add_directory({'mode':'GetTitles','url':_domain_url+'/'+ps('common_word')+'List/LatestUpdate'},{'title':cFL_(ps('common_word')+' List [Latest Update]',ps('cFL_color'))},fanart=_artFanart,img=ps('img_kisslogo'))
	_addon.add_directory({'mode':'GetTitles','url':_domain_url+'/'+ps('common_word')+'List/MostPopular'},{'title':cFL_(ps('common_word')+' List [Popularity]',ps('cFL_color'))},fanart=_artFanart,img=ps('img_kisslogo'))
	#
	if (tfalse(addst("oldmenu"))==True):
		_addon.add_directory({'mode':'SelectGenre','url':_domain_url+'/'},{'title':cFL_('Genre (Select)',ps('cFL_color'))},fanart=_artFanart,img=art('genre','.jpg'))
	_addon.add_directory({'mode':'GetTitles','url':_domain_url+'/'+ps('common_word')+'List'},{'title':cFL_(ps('common_word')+' List [Alphabet]',ps('cFL_color'))},fanart=_artFanart,img=ps('img_kisslogo'))
	##_addon.add_directory({'mode':'BrowseGenre2'},{'title':cFL_('Genres',ps('cFL_color'))},fanart=_artFanart,img=art('genre','.jpg'))
	_addon.add_directory({'mode':'Search','pageno': '1', 'pagecount': addst('pages')},{'title':cFL_('Search',ps('cFL_color'))},fanart=_artFanart,img=ps('img_search'))
	#
	if (len(addst("LastShowListedURL")) > 0) and (tfalse(addst("enable-autoplay-lsv"))==True): _addon.add_directory({'mode':'GetEpisodes','url':addst("LastShowListedURL")},{'title':cFL_('Last '+ps('common_word')+' Visited:[CR]'+cFL(addst("LastShowListedNAME"),'blue'),ps('cFL_color'))},fanart=addst("LastShowListedIMG"),img=addst("LastShowListedIMG"))
	#if (len(addst("LastVideoPlayItemUrl")) > 0) and (tfalse(addst("enable-autoplay-lvp"))==True): _addon.add_directory({'mode':'PlayVideo','url':addst("LastVideoPlayItemUrl"),'title':addst('LastVideoPlayItemName'),'studio':addst('LastVideoPlayItemStudio')},{'title':cFL_('Last Video [Played]: '+cFL(addst('LastVideoPlayItemName'),ps('cFL_color3'))+'[CR]'+cFL(addst('LastVideoPlayItemStudio'),'blue'),ps('cFL_color'))},fanart=addst("LastVideoPlayItemImg"),img=addst("LastVideoPlayItemImg"))
	#if (len(addst("LastAutoPlayItemUrl")) > 0) and (tfalse(addst("enable-autoplay-lvap"))==True): _addon.add_directory({'mode':'PlayVideo','url':addst("LastAutoPlayItemUrl"),'title':addst('LastAutoPlayItemName')},{'title':cFL_('Last Video [AutoPlay]:[CR]'+cFL(addst('LastAutoPlayItemName'),'blue'),ps('cFL_color'))},fanart=addst("LastShowListedIMG"),img=addst("LastShowListedIMG"))
	#
	_addon.add_directory({'mode': 'FavoritesList'},{'title':  cFL_('Favorites '+addst('fav.movies.1.name'),ps('cFL_color3'))},fanart=_artFanart,img=_art404)
	if (tfalse(addst("enable-fav-movies-2"))==True): _addon.add_directory({'mode': 'FavoritesList','subfav': '2'},{'title':  cFL_('Favorites '+addst('fav.movies.2.name'),ps('cFL_color3'))},fanart=_artFanart,img=_art404)
	if (tfalse(addst("enable-fav-movies-3"))==True): _addon.add_directory({'mode': 'FavoritesList','subfav': '3'},{'title':  cFL_('Favorites '+addst('fav.movies.3.name'),ps('cFL_color3'))},fanart=_artFanart,img=_art404)
	if (tfalse(addst("enable-fav-movies-4"))==True): _addon.add_directory({'mode': 'FavoritesList','subfav': '4'},{'title':  cFL_('Favorites '+addst('fav.movies.4.name'),ps('cFL_color3'))},fanart=_artFanart,img=_art404)
	#
	_addon.add_directory({'mode': 'ResolverSettings'}, {'title':  cFL('U',ps('cFL_color2'))+'rl-Resolver Settings'},is_folder=False		,img=art('turtle','.jpg')	,fanart=_artFanart)
	_addon.add_directory({'mode': 'Settings'}, 				 {'title':  cFL('P',ps('cFL_color2'))+'lugin Settings'}			,is_folder=False		,img=art('kiss')							,fanart=_artFanart)
	##_addon.add_directory({'mode': 'DownloadStop'}, 		 {'title':  cFL('S',ps('cFL_color'))+'top Current Download'},is_folder=False		,img=_artDead							,fanart=_artFanart)
	_addon.add_directory({'mode': 'TextBoxFile',  'title': "[COLOR cornflowerblue]Local Change Log:[/COLOR]  %s"  % (__plugin__), 'url': ps('changelog.local')}, 	{'title': cFL_('Local Change Log',ps('cFL_color3'))},					img=art('thechangelog','.jpg'), is_folder=False ,fanart=_artFanart)
	if (tfalse(addst("label-empty-favorites"))==True):
		_addon.add_directory({'section': '', 'mode': 'FavoritesEmpty', 'subfav':  ''},	 		{'title':  cFL('E',ps('cFL_color'))+'mpty Favorites '+addst('fav.movies.1.name')},fanart=_artFanart,img=art('trash','.gif'),is_folder=False)
		if (tfalse(addst("enable-fav-movies-2"))==True): _addon.add_directory({'section': '', 'mode': 'FavoritesEmpty', 'subfav': '2'},	 		{'title':  cFL('E',ps('cFL_color'))+'mpty Favorites '+addst('fav.movies.2.name')},fanart=_artFanart,img=art('trash','.gif'),is_folder=False)
		if (tfalse(addst("enable-fav-movies-3"))==True): _addon.add_directory({'section': '', 'mode': 'FavoritesEmpty', 'subfav': '3'},	 		{'title':  cFL('E',ps('cFL_color'))+'mpty Favorites '+addst('fav.movies.3.name')},fanart=_artFanart,img=art('trash','.gif'),is_folder=False)
		if (tfalse(addst("enable-fav-movies-4"))==True): _addon.add_directory({'section': '', 'mode': 'FavoritesEmpty', 'subfav': '4'},	 		{'title':  cFL('E',ps('cFL_color'))+'mpty Favorites '+addst('fav.movies.4.name')},fanart=_artFanart,img=art('trash','.gif'),is_folder=False)
	##_addon.add_directory({'mode': 'TextBoxUrl',   'title': "[COLOR cornflowerblue]Latest Change Log:[/COLOR]  %s" % (__plugin__), 'url': ps('changelog.url')}, 		{'title': cFL('L',ps('cFL_color'))+'atest Online Change Log'},	img=art('thechangelog','.jpg'), is_folder=False ,fanart=_artFanart)
	##_addon.add_directory({'mode': 'TextBoxUrl',   'title': "[COLOR cornflowerblue]Latest News:[/COLOR]  %s"       % (__plugin__), 'url': ps('news.url')}, 				{'title': cFL('L',ps('cFL_color'))+'atest Online News'},				img=_art404										, is_folder=False ,fanart=_artFanart)
	##_addon.add_directory({'mode': 'LatestThreads','title': "[COLOR cornflowerblue]Latest Threads[/COLOR]", 'url': ps('LatestThreads.url')}, 											{'title': cFL('L',ps('cFL_color'))+'atest Threads'},						img=_art404										, is_folder=False ,fanart=_artFanart)
	##_addon.add_directory({'mode': 'PrivacyPolicy','title': "", 'url': ''}, 																																												{'title': cFL('P',ps('cFL_color'))+'rivacy Policy'},						img=_art404										, is_folder=False ,fanart=_artFanart)
	##_addon.add_directory({'mode': 'TermsOfService','title': "", 'url': ''}, 																																											{'title': cFL('T',ps('cFL_color'))+'erms of Service'},					img=_art404										, is_folder=False ,fanart=_artFanart)
	### ############ 
	set_view('list',addst('default-view')); eod()
	### ############ 
	### _addon.show_countdown(9000,'Testing','Working...') ### Time seems to be in seconds.

##### /\ ##### Menus #####
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Favorites #####
def fav__empty(section,subfav=''):
  WhereAmI('@ Favorites - Empty - %s%s' % (section,subfav)); favs=[]; cache.set('favs_'+section+subfav+'__', str(favs)); sunNote(bFL('Favorites'),bFL('Your Favorites Have Been Wiped Clean. Bye Bye.'))
def fav__remove(section,name,year,subfav=''):
	WhereAmI('@ Favorites - Remove - %s%s' % (section,subfav)); deb('fav__remove() '+section,name+'  ('+year+')'); saved_favs=cache.get('favs_'+section+subfav+'__'); tf=False
	if saved_favs:
		favs=eval(saved_favs)
		if favs:
			for (_name,_year,_img,_fanart,_country,_url,_plot,_genre,_dbid) in favs: 
				if (name==_name) and (year==_year):
					favs.remove((_name,_year,_img,_fanart,_country,_url,_plot,_genre,_dbid)); cache.set('favs_'+section+subfav+'__', str(favs)); tf=True; sunNote(bFL(name.upper()+'  ('+year+')'),bFL('Removed from Favorites')); deb(name+'  ('+year+')','Removed from Favorites. (Hopefully)'); xbmc.executebuiltin("XBMC.Container.Refresh"); return
			if (tf==False): sunNote(bFL(name.upper()),bFL('not found in your Favorites'))
		else: sunNote(bFL(name.upper()+'  ('+year+')'),bFL('not found in your Favorites'))
def fav__add(section,name,year='',img=_art150,fanart=_artFanart,subfav=''):
	WhereAmI('@ Favorites - Add - %s%s' % (section,subfav))
	if (debugging==True): print 'fav__add()',section,name+'  ('+year+')',img,fanart
	saved_favs=cache.get('favs_'+section+subfav+'__'); favs=[]; fav_found=False
	if saved_favs:
		if (debugging==True): print saved_favs
		favs=eval(saved_favs)
		if favs:
			if (debugging==True): print favs
			for (_name,_year,_img,_fanart,_country,_url,_plot,_genre,_dbid) in favs:
				if (name==_name) and (year==_year): 
					fav_found=True; sunNote(bFL(section+':  '+name.upper()+'  ('+year+')'),bFL('Already in your Favorites')); return
	if   (section==ps('section.tv')):    favs.append((name,year,img,fanart,_param['country'],_param['url'],_param['plot'],_param['genre'],_param['dbid']))
	elif (section==ps('section.movie')): favs.append((name,year,img,fanart,_param['country'],_param['url'],_param['plot'],_param['genre'],''))
	cache.set('favs_'+section+subfav+'__', str(favs)); sunNote(bFL(name+'  ('+year+')'),bFL('Added to Favorites'))
def fav__list(section,subfav=''):
	WhereAmI('@ Favorites - List - %s%s' % (section,subfav)); saved_favs=cache.get('favs_'+section+subfav+'__'); favs=[]
	if saved_favs:
		if (debugging==True): print saved_favs
		favs=sorted(eval(saved_favs), key=lambda fav: (fav[1],fav[0]),reverse=True)
		ItemCount=len(favs) # , total_items=ItemCount
		if favs:
			#if   (section==ps('section.tv')): 		xbmcplugin.setContent( int( sys.argv[1] ), 'tvshows' )
			#elif (section==ps('section.movie')): 	xbmcplugin.setContent( int( sys.argv[1] ), 'movies' )
			for (name,year,img,fanart,country,url,plot,genre,dbid) in favs:
				if (debugging==True): print '----------------------------'
				if (debugging==True): print name,year,img,fanart,country,url,plot,genre,dbid #,pars,labs
				contextMenuItems=[]; labs2={}; labs2['fanart']=''
				labs2['title']=cFL(name,ps('cFL_color3'))
				#labs2['title']=cFL(name+'  ('+cFL(year,ps('cFL_color2'))+')',ps('cFL_color')); 
				labs2['image']=img; labs2['fanart']=fanart; labs2['ShowTitle']=name; labs2['year']=year; labs2['plot']=plot
				#pars2={'mode': 'GetLinks', 'section': section, 'url': url, 'img': img, 'image': img, 'fanart': fanart, 'title': name, 'year': year }; 
				pars2={'mode': 'GetEpisodes', 'section': section, 'url': url, 'img': img, 'image': img, 'fanart': fanart, 'title': name, 'year': year }; 
				##labs2['title']=cFL(name+'  ('+cFL(year,ps('cFL_color2'))+')  ['+cFL(country,ps('cFL_color3'))+']',ps('cFL_color'))
				##labs2[u'overlay']=xbmcgui.ICON_OVERLAY_WATCHED
				##labs2['overlay']=xbmcgui.ICON_OVERLAY_WATCHED
				#labs2['overlay']=7
				#
				##### Right Click Menu for: TV #####
				contextMenuItems.append((ps('cMI.showinfo.name'),ps('cMI.showinfo.url')))
				##
				if (subfav is not ''): contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.1.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fanart),urllib.quote_plus(country),urllib.quote_plus(plot),urllib.quote_plus(genre),urllib.quote_plus(url), '' )))
				if (tfalse(addst("enable-fav-movies-2"))==True) and (subfav is not '2'): contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.2.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fanart),urllib.quote_plus(country),urllib.quote_plus(plot),urllib.quote_plus(genre),urllib.quote_plus(url),'2' )))
				if (tfalse(addst("enable-fav-movies-3"))==True) and (subfav is not '3'): contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.3.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fanart),urllib.quote_plus(country),urllib.quote_plus(plot),urllib.quote_plus(genre),urllib.quote_plus(url),'3' )))
				if (tfalse(addst("enable-fav-movies-4"))==True) and (subfav is not '4'): contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.4.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fanart),urllib.quote_plus(country),urllib.quote_plus(plot),urllib.quote_plus(genre),urllib.quote_plus(url),'4' )))
				##
				#contextMenuItems.append((ps('cMI.favorites.tv.remove.name'), 	   ps('cMI.favorites.movie.remove.url') % (sys.argv[0],ps('cMI.favorites.tv.remove.mode'),section,urllib.quote_plus(name),year,urllib.quote_plus(img),urllib.quote_plus(fanart),urllib.quote_plus(country),urllib.quote_plus(plot),urllib.quote_plus(genre),urllib.quote_plus(url), '' )))
				contextMenuItems.append((ps('cMI.favorites.tv.remove.name'),ps('cMI.favorites.movie.remove.url') % (sys.argv[0],ps('cMI.favorites.tv.remove.mode'),section,urllib.quote_plus(name),year,urllib.quote_plus(img),urllib.quote_plus(fanart),urllib.quote_plus(country),urllib.quote_plus(plot),urllib.quote_plus(genre),urllib.quote_plus(url),subfav )))
				#if (fanart is not ''): contextMenuItems.append(('Download Wallpaper', 'XBMC.RunPlugin(%s)' % _addon.build_plugin_url( { 'mode': 'Download' , 'section': ps('section.wallpaper') , 'studio': name+' ('+year+')' , 'img': img , 'url': fanart } ) ))
				##### Right Click Menu for: TV ##### /\ #####
				try: _addon.add_directory(pars2, labs2, img=img, fanart=fanart, contextmenu_items=contextMenuItems)
				except: deb('Error Listing Item',name+'  ('+year+')')
			set_view('episodes',addst('episode-view'))
			#set_view('movies' ,ps('setview.movies')	,True)
		else: sunNote('Favorites:  '+section,'No favorites found *'); set_view('list',addst('default-view')); eod(); return
	else: sunNote('Favorites:  '+section,'No favorites found **'); set_view('list',addst('default-view')); eod(); return
	#set_view('list',addst('default-view')); 
	eod()

def ChangeFanartUpdate(section,subfav,fanart,dbid):
	WhereAmI('@ Favorites - Update Fanart - %s%s' % (section,subfav))
	saved_favs=cache.get('favs_'+section+subfav+'__'); favs=[]; favs_new=[]; fav_found=False; name=''; year=''
	if saved_favs:
		if (debugging==True): print saved_favs
		favs=eval(saved_favs)
		if favs:
			for (_name,_year,_img,_fanart,_country,_url,_plot,_genre,_dbid) in favs:
				if (dbid==_dbid):	favs_new.append((_name,_year,_img, fanart,_country,_url,_plot,_genre,_dbid)); name=_name; year=_year
				else:							favs_new.append((_name,_year,_img,_fanart,_country,_url,_plot,_genre,_dbid))
			cache.set('favs_'+section+subfav+'__', str(favs_new)); sunNote(bFL(name+'  ('+year+')'),bFL('Updated Fanart'))
	eod(); #xbmc.executebuiltin('XBMC.Container.Update(%s)' % _addon.build_plugin_url({'mode': 'FavoritesList' , 'section': section , 'subfav': subfav}))

def ChangeFanartList(section,subfav,dbid,current,img,title):
	WhereAmI('@ Favorites - List - %s%s - %s' % (section,subfav,dbid)); 
	if   (section==ps('section.tv')):
		url=ps('meta.tv.fanart.all.url') % dbid
		html=mGetItemPage(url)
		deb('length of HTML',str(len(html)))
		try:		iitems=re.compile(ps('meta.tv.fanart.all.match')).findall(html)
		except:	iitems=None
		if (iitems==None) or (iitems==''): deb('Error','No Items Found.'); return
		ItemCount=len(iitems) # , total_items=ItemCount
		deb('Items Found',str(ItemCount))
		parsC={'section':section,'subfav':subfav,'mode':'ChangeFanartUpdate','url':current, 'title': dbid}
		#_addon.add_directory(parsC,{ 'title': title, 'studio': title },img=img,fanart=current)
		_addon.add_directory(parsC,{ 'title': title, 'studio': title },img=current,fanart=current)
		#_addon.add_item(parsC,{ 'title': title, 'studio': title },img=img,fanart=current)
		#_addon.add_directory({'mode':'test'}, {'title':title}, img=img)
		#_addon.add_directory({'mode':'test'}, {'title':'title'})
		#_addon.end_of_directory(); return
		iitems=sorted(iitems, key=lambda item: item[0], reverse=False)
		#print iitems
		for fanart_url,fanart_name in iitems:
			fanart_url=ps('meta.tv.fanart.all.prefix')+fanart_url
			pars={ 'section': section, 'subfav': subfav, 'mode': 'ChangeFanartUpdate', 'url': fanart_url, 'title': dbid }
			deb('fanart url ',fanart_url); deb('fanart name',fanart_name); #print pars
			#_addon.add_directory(pars, {'title':'Fanart No. '+fanart_name}, img=img, fanart=fanart_url, total_items=ItemCount)
			_addon.add_directory(pars, {'title':'Fanart No. '+fanart_name}, img=fanart_url, fanart=fanart_url, total_items=ItemCount)
			#_addon.add_directory(pars, {'title':'Fanart No. '+fanart_name}, img=img, fanart=fanart_url)
			#_addon.add_directory(pars, {'title':'Fanart No. '+str(fanart_name)})
		#eod()
		#sunNote('Testing - '+section,'lala a la la la!')
		set_view('list',addst('default-view')); 
		eod()
		#xbmc.executebuiltin("XBMC.Container.Refresh")
	elif (section==ps('section.movie')):
		url=''
		return
	else: return
	set_view('list',addst('default-view')); eod()


##### /\ ##### Favorites #####
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Search #####
def doSearchNormal (section,title=''):
	SearchPrefix=_domain_url+'/Search/'+ps('common_word')+'?keyword=%s'
	if (title==''):
		title=showkeyboard(txtMessage=title,txtHeader="Title:  ("+section+")")
		if (title=='') or (title=='none') or (title==None) or (title==False): return
	title=title.replace(' ','-')
	#title=title.replace(' ','+')
	_param['url']=SearchPrefix % title; deb('Searching for',_param['url']); listItems(section, _param['url'], _param['pageno'], addst('pages'), _param['genre'], _param['year'], _param['title'])

def doSearchAdvanced (section,title=''):
	txtHeader='Advanced Search'; options={}; r= -1
	#########################
	options[ps('AdvSearch.tags.1')]				=''
	options[ps('AdvSearch.tags.2')]				=''
	options[ps('AdvSearch.tags.3')]				=''
	options[ps('AdvSearch.tags.4')]				='0'
	options[ps('AdvSearch.tags.5')]				=str(ps('BrowseByYear.earliestyear'))
	options[ps('AdvSearch.tags.6')]				=str(int(datetime.date.today().strftime("%Y"))+1)
	options[ps('AdvSearch.tags.7')]				=''						### &q[genre][]=2&q[genre][]=13
	#########################
	options['startPage']		='1'
	options['numOfPages']		=addst('pages') #'1'
	#########################
	if   (section==ps('section.tv')   ): options[ps('AdvSearch.tags.0')]='1'; options['url']=ps('AdvSearch.url.tv')
	elif (section==ps('section.movie')): options[ps('AdvSearch.tags.0')]='0'; options['url']=ps('AdvSearch.url.movie')
	else: 															 options[ps('AdvSearch.tags.0')]='0'; options['url']=ps('AdvSearch.url.movie')
	options['url']+='['+ps('AdvSearch.tags.0')+']='+options[ps('AdvSearch.tags.0')]; _param['url']=options['url']
	#options['']=''
	#options['']=''
	### [year_from]=2013&q[year_to]=2014&q[country]=132&q[genre][]=2&q[genre][]=13
	### http://www.solarmovie.so/advanced-search/?q[title]=maveric&q[is_series]=0&q[actor]=&q[description]=&q[year_from]=2013&q[year_to]=2014&q[country]=0
	### http://www.solarmovie.so/advanced-search/?q[title]=maveric&q[is_series]=0&q[actor]=testb&q[description]=testa&q[year_from]=2013&q[year_to]=2014&q[country]=132&q[genre][]=2&q[genre][]=13
	while (r is not 0):
		option_list=[]
		option_list.append(																						 ps('AdvSearch.menu.0'))
		if (''==options[ps('AdvSearch.tags.1')]): 	option_list.append(ps('AdvSearch.menu.1'))
		else:																				option_list.append(ps('AdvSearch.menu.1')+':  '+options[ps('AdvSearch.tags.1')])
		if (''==options[ps('AdvSearch.tags.2')]): 	option_list.append(ps('AdvSearch.menu.2'))
		else:																				option_list.append(ps('AdvSearch.menu.2')+':  '+options[ps('AdvSearch.tags.2')])
		if (''==options[ps('AdvSearch.tags.3')]): 	option_list.append(ps('AdvSearch.menu.3'))
		else:																				option_list.append(ps('AdvSearch.menu.3')+':  '+options[ps('AdvSearch.tags.3')])
		if (''==options[ps('AdvSearch.tags.4')]): 	option_list.append(ps('AdvSearch.menu.4'))
		else:																				option_list.append(ps('AdvSearch.menu.4')+':  '+options[ps('AdvSearch.tags.4')])
		if (''==options[ps('AdvSearch.tags.5')]): 	option_list.append(ps('AdvSearch.menu.5'))
		else:																				option_list.append(ps('AdvSearch.menu.5')+':  '+options[ps('AdvSearch.tags.5')])
		if (''==options[ps('AdvSearch.tags.6')]): 	option_list.append(ps('AdvSearch.menu.6'))
		else:																				option_list.append(ps('AdvSearch.menu.6')+':  '+options[ps('AdvSearch.tags.6')])
		if (''==options[ps('AdvSearch.tags.7')]): 	option_list.append(ps('AdvSearch.menu.7'))
		else:																				option_list.append(ps('AdvSearch.menu.7')+':  '+options[ps('AdvSearch.tags.7')])
		option_list.append(																						 ps('AdvSearch.menu.8'))
		r=askSelection(option_list,txtHeader)
		if   (r==0): ### Do Advanced Search
			_param['url']+='&q['+ps('AdvSearch.tags.1')+']='+options[ps('AdvSearch.tags.1')]; 
			_param['url']+='&q['+ps('AdvSearch.tags.2')+']='+options[ps('AdvSearch.tags.2')]; 
			_param['url']+='&q['+ps('AdvSearch.tags.3')+']='+options[ps('AdvSearch.tags.3')]; 
			_param['url']+='&q['+ps('AdvSearch.tags.5')+']='+options[ps('AdvSearch.tags.5')]; 
			_param['url']+='&q['+ps('AdvSearch.tags.6')+']='+options[ps('AdvSearch.tags.6')]; 
			_param['url']+='&q['+ps('AdvSearch.tags.4')+']='+options[ps('AdvSearch.tags.4')]; 
			### if (options['year_to'] is not ''): _param['url']+='&q[year_to]='+options['year_to']; 
			deb('Advanced Searching',_param['url'])
			listItems(section, _param['url'], startPage=options['startPage'], numOfPages=options['numOfPages'], chck='AdvancedSearch')
			### listItems(section, _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'],chck='AdvancedSearch')
			### listItems(section=, url=, startPage='1', numOfPages='1', genre='', year='', stitle='', season='', episode='', html='', chck=''): # List: Movies or TV Shows
		elif (r==1): ### Change Title
			r2=showkeyboard(txtMessage=options[ps('AdvSearch.tags.1')],txtHeader="Title:  "+options[ps('AdvSearch.tags.1')],passwordField=False)
			if (r2 is not False): options[ps('AdvSearch.tags.1')]=r2
		elif (r==2): ### Change Description
			r2=showkeyboard(txtMessage=options['description'],txtHeader="Description:  "+options['description'],passwordField=False)
			if (r2 is not False): options['description']=r2
		elif (r==3): ### Change Actor
			r2=showkeyboard(txtMessage=options[ps('AdvSearch.tags.2')],txtHeader="Actor:  "+options[ps('AdvSearch.tags.2')],passwordField=False)
			if (r2 is not False): options[ps('AdvSearch.tags.2')]=r2
		#elif (r==4): ### Change Country
		elif (r==5): ### Change Year From
			r2=dialogbox_number(Header='Year From:'+options[ps('AdvSearch.tags.5')],n='01/01/'+options[ps('AdvSearch.tags.5')],type=0)
			if (r2 is not False) and (len(r2)==4): options[ps('AdvSearch.tags.5')]=r2
			if (r2 is not False) and ('/' in r2):  options[ps('AdvSearch.tags.5')]=r2.split('/')[2] ## <<<
			if (r2 is not False) and ('-' in r2):  options[ps('AdvSearch.tags.5')]=r2.split('-')[2]
		elif (r==6): ### Change Year To
			r2=dialogbox_number(Header='Year To:'  +options[ps('AdvSearch.tags.6')],n='01/01/'+options[ps('AdvSearch.tags.6')],type=0)
			if (r2 is not False) and (len(r2)==4): options[ps('AdvSearch.tags.6')]=r2
			if (r2 is not False) and ('/' in r2):  options[ps('AdvSearch.tags.6')]=r2.split('/')[2] ## <<<
			if (r2 is not False) and ('-' in r2):  options[ps('AdvSearch.tags.6')]=r2.split('-')[2]
		#elif (r==7): ### Change Genre
		elif (r==8): ### Cancel Advanced Search
			eod(); return
		#elif (r== -1): ### escape // right click or such.
		#	eod(); return
		## 
		## 
	#
	#
	#
	eod()
	return



##### /\ ##### Search #####
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Modes #####
def check_mode(mode=''):
	deb('Mode',mode)
	if (mode=='') or (mode=='main') or (mode=='MainMenu'): 
		initDatabase(); Menu_MainMenu()
	#elif (mode=='PlayVideo'): 						PlayVideo(_param['url'], _param['infoLabels'], _param['listitem'])
	elif (mode=='PlayVideo'): 						PlayVideo(_param['url'],title=_param['title'],studio=_param['studio'],img=_param['img'],showtitle=_param['showtitle'],plot=_param['plot'])
	elif (mode=='PlayURL'): 							PlayURL(_param['url'])
	elif (mode=='PlayImage'): 						PlayImage(_param['url'])
	elif (mode=='PlayManga'): 						PlayManga(_param['url'])
	elif (mode=='PlayTrailer'): 					PlayTrailer(_param['url'], _param['title'], _param['year'], _param['img'])
	elif (mode=='Settings'): 							_addon.addon.openSettings() #_plugin.openSettings()
	elif (mode=='ResolverSettings'): 			urlresolver.display_settings()
	elif (mode=='LoadCategories'): 				Menu_LoadCategories(_param['section'])
	#elif (mode=='BrowseAtoZ'): 					BrowseAtoZ(_param['section'])
	#elif (mode=='BrowseYear'): 						Menu_BrowseByYear(_param['section'])
	elif (mode=='BrowseLast'): 						Menu_Last()
	elif (mode=='BrowseGenre'): 					Menu_BrowseByGenre(_param['section'])
	elif (mode=='BrowseAZ'): 							Menu_BrowseByAZ(_param['section'],_param['url'])
	elif (mode=='SelectAZ'): 							Select_AZ(_param['url'])
	elif (mode=='SelectSort'): 						Select_Sort(_param['url'],_param['title'])
	elif (mode=='SelectGenre'): 					Select_Genre(_param['url'])
	#elif (mode=='BrowseCountry'): 				Menu_BrowseByCountry(_param['section'])
	#elif (mode=='BrowseLatest'): 				BrowseLatest(_param['section'])
	#elif (mode=='BrowsePopular'): 				BrowsePopular(_param['section'])
	#elif (mode=='GetResults'): 					GetResults(_param['section'], genre, letter, page)
	elif (mode=='GetTitles'): 						listItems(_param['section'], _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'])
	elif (mode=='GetTitlesLatest'): 			listItems(_param['section'], _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'], chck=ps('LI.tv.latest.check'))
	elif (mode=='GetTitlesLatestWatched'): listItems(_param['section'],_param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'], chck=ps('LI.tv.latest.watched.check'))
	elif (mode=='GetTitlesPopular'): 			listItems(_param['section'], _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'], chck=ps('LI.tv.popular.all.check'))
	elif (mode=='GetTitlesHDPopular'): 		listItems(_param['section'], _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'], chck=ps('LI.movies.popular.hd.check'))
	elif (mode=='GetTitlesOtherPopular'): listItems(_param['section'], _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'], chck=ps('LI.movies.popular.other.check'))
	elif (mode=='GetTitlesNewPopular'): 	listItems(_param['section'], _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'], chck=ps('LI.movies.popular.new.check'))
	elif (mode=='GetLinks'): 							listLinks(_param['section'], _param['url'], showtitle=_param['showtitle'], showyear=_param['showyear'])
	elif (mode=='GetEpisodes'): 					listEpisodes(_param['section'], _param['url'], _param['img'], _param['title'], _param['season'])
	elif (mode=='TextBoxFile'): 					TextBox2().load_file(_param['url'],_param['title']); eod()
	elif (mode=='TextBoxUrl'):  					TextBox2().load_url( _param['url'],_param['title']); eod()
	elif (mode=='SearchForAirDates'):  		search_for_airdates(_param['title']); eod()
	elif (mode=='Search'):  							doSearchNormal(_param['section'],_param['title'])
	elif (mode=='AdvancedSearch'):  			doSearchAdvanced(_param['section'],_param['title'])
	elif (mode=='FavoritesList'):  		  	fav__list(_param['section'],_param['subfav'])
	elif (mode=='FavoritesEmpty'):  	 		fav__empty(_param['section'],_param['subfav'])
	elif (mode=='FavoritesRemove'):  			fav__remove(_param['section'],_param['title'],_param['year'],_param['subfav'])
	elif (mode=='FavoritesAdd'):  		  	fav__add(_param['section'],_param['title'],_param['year'],_param['img'],_param['fanart'],_param['subfav'])
	elif (mode=='sunNote'):  		   				sunNote( header=_param['title'],msg=_param['plot'])
	elif (mode=='deadNote'):  		   			deadNote(header=_param['title'],msg=_param['plot'])
	elif (mode=='LibrarySaveMovie'):  		Library_SaveTo_Movies(_param['url'],_param['img'],_param['showtitle'],_param['showyear'])
	elif (mode=='LibrarySaveTV'):  				Library_SaveTo_TV(_param['section'], _param['url'],_param['img'],_param['showtitle'],_param['showyear'],_param['country'],_param['season'],_param['episode'],_param['episodetitle'])
	elif (mode=='LibrarySaveEpisode'):  	Library_SaveTo_Episode(_param['url'],_param['img'],_param['title'],_param['showyear'],_param['country'],_param['season'],_param['episode'],_param['episodetitle'])
	elif (mode=='PlayLibrary'): 					PlayLibrary(_param['section'], _param['url'], showtitle=_param['showtitle'], showyear=_param['showyear'])
	elif (mode=='Download'): 							print _param; DownloadRequest(_param['section'], _param['url'],_param['img'],_param['studio']); eod()
	elif (mode=='DownloadStop'): 					DownloadStop(); eod()
	elif (mode=='TrailersGenres'): 				Trailers_Genres(_param['section'], _param['url'])
	elif (mode=='TrailersList'): 					Trailers_List(_param['section'], _param['url'], _param['genre'])
	elif (mode=='LatestThreads'): 				News_LatestThreads(_param['url'],_param['title'])
	elif (mode=='listUsers'): 						UsersList(_param['section'],_param['url'])
	elif (mode=='UsersChooseSection'): 		UsersChooseSection(_param['section'],_param['url'])
	elif (mode=='UsersShowFavorites'): 		UsersShowFavorites(_param['section'],_param['url'])
	#elif (mode=='UsersShowWatchList'): 		UsersShowWatchList(_param['section'],_param['url'])
	elif (mode=='UsersShowUploads'): 			UsersShowUploads(_param['section'],_param['url'])
	elif (mode=='PrivacyPolicy'): 				Site__PrivacyPolicy()
	elif (mode=='TermsOfService'): 				Site__TermsOfService()
	elif (mode=='GetLatestSearches'): 		listLatestSearches(_param['section'],_param['url'])
	elif (mode=='UsersShowProfileAccountInfo'): UsersShowPersonInfo(mode, _param['section'],_param['url'])
	elif (mode=='ChangeFanartList'):			ChangeFanartList(_param['section'],_param['subfav'],_param['url'],_param['fanart'],_param['img'],_param['studio'])
	elif (mode=='ChangeFanartUpdate'):		ChangeFanartUpdate(_param['section'],_param['subfav'],_param['url'],_param['title'])
	else: deadNote(header='Mode:  "'+mode+'"',msg='[ mode ] not found.'); initDatabase(); Menu_MainMenu()

# {'showyear': '', 'infoLabels': "
# {'Plot': '', 'Episode': '11', 'Title': u'Transformers Prime', 'IMDbID': '2961014', 'host': 'filenuke.com', 
# 'IMDbURL': 'http://anonym.to/?http%3A%2F%2Fwww.imdb.com%2Ftitle%2Ftt2961014%2F', 
# 'ShowTitle': u'Transformers Prime', 'quality': 'HDTV', 'Season': '3', 'age': '25 days', 
# 'Studio': u'Transformers Prime  (2010):  3x11 - Persuasion', 'Year': '2010', 'IMDb': '2961014', 
# 'EpisodeTitle': u'Persuasion'}", 'thetvdbid': '', 'year': '', 'special': '', 'plot': '', 
# 'img': 'http://static.solarmovie.so/images/movies/1659175_150x220.jpg', 'title': '', 'fanart': '', 'dbid': '', 'section': 'tv', 'pagesource': '', 'listitem': '<xbmcgui.ListItem object at 0x14C799B0>', 'episodetitle': '', 'thumbnail': '', 'thetvdb_series_id': '', 'season': '', 'labs': '', 'pageurl': '', 'pars': '', 'user': '', 'letter': '', 'genre': '', 'by': '', 'showtitle': '', 'episode': '', 'name': '', 'pageno': 0, 'pagecount': 1, 'url': '/link/show/1466546/', 'country': '', 'subfav': '', 'mode': 'Download', 'tomode': ''}

##### /\ ##### Modes #####
### ############################################################################################################
deb('param >> studio',_param['studio'])
deb('param >> season',_param['season'])
deb('param >> section',_param['section'])
deb('param >> img',_param['img'])
deb('param >> showyear',_param['showyear'])
deb('param >> showtitle',_param['showtitle'])
deb('param >> title',_param['title'])
deb('param >> url',_param['url']) ### Simply Logging the current query-passed / param -- URL
check_mode(_param['mode']) ### Runs the function that checks the mode and decides what the plugin should do. This should be at or near the end of the file.
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
