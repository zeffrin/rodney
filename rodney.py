#!/usr/bin/env python

import time, os, string, rodlib, re, rodfeed, tinyurl, sys, glob, nethackmoon
import unicodedata
from operator import itemgetter
from socket import *

def main():
	""" Rodney the nethack death announcer, inspired by Rodney
	at nethack.alt.org, coded by Tylinial for eotl

	"""
	#Set the filename and open the file
	global nhpath
	global feed
	global feedpoll

	#nhpath = '/var/lib/dgamelaunch/home/zeffrin/nethack-3.4.3/dat/'
	nhpath = '/usr/local/dglroot/var/games/nethack/'
	crawl071path = '/usr/local/dglroot/usr/games/crawl-071/saves/'
	crawl060path = '/usr/local/dglroot/usr/games/crawl-060/saves/'
	crawl050path = '/usr/local/dglroot/usr/games/crawl-050/saves/'
	crawl043path = '/usr/local/dglroot/usr/games/crawl-043/saves/'
	ESC = 'q\n\n'	#include before all sends, exit any prompts	

	nhpoll = [] # define the scope
	crawlpoll = []
	crawlfilenames = []
	crawllog = []
	feedpoll = [] # define the scope for our feedpoll
	feedtimer = 0 # countdown between feed displays

	# create our hackmoon instance and get the current luckmsg
	hackmoon = nethackmoon.NethackMoon()
	global luckmsg
	luckmsg = hackmoon.luckmsg()
	# counter to act as timer for checking moon phase
	moonchk = 0

	feed = rodfeed.Feed()

	# Tail NH logfile
	filename = nhpath+'logfile'
	nhlog = open(filename,'r')

	#Find the size of the file and move to the end
	st_results = os.stat(filename)
	st_size = st_results[6]
	nhlog.seek(st_size)

	# Tail crawl logfiles
	crawlfilenames.append(crawl043path+'milestones.txt')
	crawlfilenames.append(crawl043path+'logfile')
	crawlfilenames.append(crawl050path+'milestones.txt')
	crawlfilenames.append(crawl050path+'logfile')
	crawlfilenames.append(crawl060path+'milestones.txt')
	crawlfilenames.append(crawl060path+'logfile')
	# crawl 0.7.1 has "sprint mode" files, dropped the '.txt' suffix
	crawlfilenames.append(crawl071path+'milestones')
	crawlfilenames.append(crawl071path+'milestones-sprint')
	crawlfilenames.append(crawl071path+'logfile')
	crawlfilenames.append(crawl071path+'logfile-sprint')

	for filename in crawlfilenames:
		crawllog.append(open(filename,"r"))
		st_results = os.stat(filename)
		st_size = st_results[6]
		crawllog[-1].seek(st_size)

	# Socket for EotL connection
	host = "eotl.org"
	port = 2010
	buf = 1024
	addr = (host,port)

	#Connect, wait for eotl to send welcome and login
	EOTLSock = socket(AF_INET,SOCK_STREAM)
	try:
		EOTLSock.connect(addr)
	except:
		sys.exit(1)

	EOTLSock.setblocking(0)
	while 1:
		try:
			EOTLSock.recv(buf)
		except error, msg:
			if(msg[0] != 11):
				sys.exit(1)
		else:
			break

	EOTLSock.send("rodney\n"+getpass()+"\n\n\nprompt >\nset ansi off\n")
	""" Subscribes to only the games page - removed
	while 1:
		EOTLSock.send("\n")
		data = EOTLSock.recv(buf)
		#print data
		m = re.search("(\d+) The Games Page",data)
		if m:
			#print "sent: q\n]s "+m.group(1)+"\n]p 1\n]w test\n\n.\n"
			EOTLSock.send("q\n]s "+m.group(1)+"\n]p 1\nq\n")
			break
	"""


	while 1:
		curpos = nhlog.tell()
		line = nhlog.readline()
		# Aww someone died, fix permissions and add death to the nhpoll
		if line:
			os.popen("sudo -u dgl /usr/local/bin/chmod-dumps")
			nhpoll.append(line)
			continue
		nhlog.seek(curpos)

		for fh in crawllog:
			curpos = fh.tell()
			line = fh.readline()
			#print "cms readline: " + line
			if line:
				crawlpoll.append(line)
				continue
			fh.seek(curpos)

		time.sleep(0.5)

		# process next viable nhpoll item
		s = nhlog_pollnext(nhpoll)
		if s:
			nhpoll.remove(s)
			msg = nhlog_parse(s)
			if msg:
				#print msg
				EOTLSock.send(ESC+"game "+msg[2:]+"\n") 
				if msg[0] is '1':
					stmp = ''  #scope, and nothing for male
					if msg[1] is '1':
						stmp = 'dess'
					EOTLSock.send(ESC+"do clone -s /usr/felzin/etc/firecracker##shoot "\
					"firecracker "+msg.split(' ')[0][2:]+ \
					" ascends to the rank of demi-god"+stmp+"!\n")
			
		s = crawl_pollnext(crawlpoll)
		if s:
			crawlpoll.remove(s)
			msg = crawl_parse(s)
			if msg:
				#print msg
				EOTLSock.send(ESC+"game "+msg+"\n")
				"""
				if msg[0] is '1':
					stmp = ''  #scope, and nothing for male
					if msg[1] is '1':
						stmp = 'dess'
					EOTLSock.send(ESC+"do clone -s /usr/felzin/etc/firecracker##shoot "\
					"firecracker "+msg.split(' ')[0][2:]+ \
					" ascends to the rank of demi-god"+stmp+"!\n")
				"""

		# Disabled until complete
		# get socket buffer and act on any requests
		try:
			data = EOTLSock.recv(buf)
			if data == "":
				sys.exit(1)
		except error, merr:
			data = ""
			if(merr[0] != 11):
				sys.exit(1)

		if data:
			msg = procinput(data)
			# print data
		if msg:
			EOTLSock.send(ESC+msg+'\n')

		# get moon phase message and if different announce

		# if moonshk higher than 90 check for the moonphase and report
		if moonchk > 90:
			#reset the timer
			moonchk = 0
			tmp = hackmoon.luckmsg()
			if tmp != luckmsg:
				# Dont show normal scenarios, no msg
				if tmp:
					EOTLSock.send(ESC+"game "+tmp+'\n')
				if luckmsg and not tmp:
					EOTLSock.send(ESC+"game The moon moves into its " +\
					numsuffix(hackmoon.phase_of_the_moon())+" phase.\n")
				luckmsg = tmp
		else:
			# if its not yet time increment the timer
			moonchk = moonchk + 1
		
		#request update, if done advise
		if rodlib.update():
			rodlib.loaddata()
			print "Rodney:  Done update.\n"

		# if theres some new feed items add them to poll 
		# for display
		feeditems = feed.update()
		if feeditems:
			feedpoll += feeditems
	
		# if there is news outstanding and its been more than 45 secs since the last display item
		if feedpoll and feedtimer < time.time():
			entry = feedpoll.pop(0)
			# hack because some feeds have some antiascii bs - if it doesnt work, forget it
	
			try:
				EOTLSock.send(ESC+'channel '+entry[2]+' '+toascii(entry[1]['title'] +' '+tinyurl.getTinyurl(entry[1]['link'])+'\n'))
				EOTLSock.send(ESC+'channel hl-all ('+ toascii(entry[0]+') '+entry[1]['title']) +' '+tinyurl.getTinyurl(entry[1]['link'])+'\n')

			except:
				print "Failed to post a link"
				pass

			# set 45 seconds before displaying another item
			feedtimer = time.time()+45


def nhlog_parse(line):
	""" parses a line of nethack logfile and returns string, first 2 characters of the string represent death code
	and gender respectively.  Codes as below:
	deaths (first character):
	0	Normal death
	1	Ascended
	gender (second character):
	0	Male
	1	Female
	
	"""
	d = string.split(line,None, 15)
	n = string.split(d[15],',',1)
	m = string.split(n[1])	
	moves = '0'
	asc = '0'	#string 'flag' appended to beginning of return string, sliced off before outputting indicates type of game
	n[1] = string.strip(n[1],'\n')

	# If it was a quit, wizard or explorer game return
	if re.search('{(exp|wiz)}',n[1]):
		return
	
	moves = re.search('{(\d+)}',n[1]).group(1)
	n[1] = re.sub('{([0-9A-Za-z]*)}',"",n[1])

	if re.match('(quit|escaped)',n[1]) and int(moves) <1000:
		return

	if re.match('ascended',n[1]):
		gamedump(n[0])
		asc = '1'

	# Grab the gender to pass back as 2nd character in return string, for use with congratulatory message should
	# it be needed
	gender = '' #scope
	if d[14]=='Fem':
		gender = '1'
	else:
		gender = '0'

	""" Some extra info we're no longer using, leave code incase
		we want it later
		
	db = ['The Dungeons of Doom','Gehennom','The Gnomish Mines','The Quest','Sokoban','Fort Ludios','Vlad\'s Tower','Endgame']

	if d[3] < 0:
		where = "on the Plane of "
		if d[3] == -1: where = where + "Earth"
		elif d[3] == -2: where = where + "Air"
		elif d[3] == -3: where = where + "Fire"
		elif d[3] == -4: where = where + "Water"
		elif d[3] == -5: where = "the Astral Plane"
		dlvl = ""
	else:
		where = "in "+db[int(d[2])]
		dlvl = " on dlvl"+d[3]
	if d[4] != d[3] and d[3]>0:
		dlvl = dlvl + "[max: "+d[4]+"]"
	
	"""

	# Check to see if the players maxdlvl is higher than their current level, if so display the lowest they'd reached.
	if int(d[4]) > int(d[3]):
		maxdlvl = "/"+d[4]
	else:
		maxdlvl = ""

	return asc+gender+n[0]+" (XL:"+getxpl(n[0])+" "+d[11]+" "+d[12]+" "+d[13]+" "+d[14]+" DL"+d[3]+maxdlvl+" T:"+moves+") "+n[1]


def crawl_parse(line):
	"""
	death:
	v=0.4.3:lv=0.1:name=dorf:uid=9000:race=Grey Elf:cls=Air Elementalist:char=GEAE:xl=3:sk=Air Magic:sklev=5:title=Gusty:place=D::2:br=D:lvl=2:ltyp=D:hp=0:mhp=17:mmhp=17:str=7:int=19:dex=14:start=20080901190719S:dur=1013:turn=1056:sc=159:ktyp=mon:killer=a snake:dam=2:end=20080901192429S:tmsg=slain by a snake
	milestones:
	v=0.4.3:lv=0.1:name=Whitewolf:uid=9000:race=Mountain Dwarf:cls=Fighter:char=MDFi:xl=11:sk=Axes:sklev=12:title=Cleaver:place=D::5:br=D:lvl=5:ltyp=D:hp=102:mhp=102:mmhp=102:str=24:int=6:dex=11:god=Okawaru:start=20080901180823S:dur=9995:turn=13916:time=20080901213147S:type=unique:milestone=killed Ijyb.
	v=0.4.3:lv=0.1:name=Whitewolf:uid=9000:race=Mountain Dwarf:cls=Fighter:char=MDFi:xl=11:sk=Axes:sklev=12:title=Cleaver:place=Orc::1:br=Orc:lvl=1:ltyp=D:hp=102:mhp=102:mmhp=102:str=24:int=6:dex=11:god=Okawaru:start=20080901180823S:dur=10058:turn=14251:time=20080901213250S:type=enter:milestone=entered the Orcish Mines.
	"""
	l = string.replace(line, '::', '____~~~~____')
	d = string.split(l, ':')
	h = {}
	for pair in d:
		p = string.replace(pair, '____~~~~____', ':')
		kv = string.split(p, '=', 2)
		#print "k='"+kv[0]+"'   ##   v='"+kv[1]+"'"
		h[kv[0]] = kv[1]
	if int(h['turn']) == 0:
		return
	god = ''
	if h.has_key('god'):
		god = ' of '+h['god']
	part1 = h['name']+' (XL:'+h['xl']+' '+h['char']+god+' '+h['place']+' T:'+h['turn']+') '
	#print "cp6 "+part1
	if h.has_key('milestone'):
		msg = h['milestone']
	elif h.has_key('vmsg'):
		msg = h['vmsg']
	else:
		msg = h['tmsg']
	return part1 + re.sub('\.$', '', msg)

def getxpl(plname):
	""" takes string playername as an arg and retrieves Exp:n or Xp:n/
	that players lastgame dump.

	"""
	filename = nhpath+'dumps/'+plname+'.lastgame.txt'
	
	try:
		file = open(filename, 'r')
		rg = re.compile(" (Exp|Xp|HD):(\d+)[ \/]")
		i=0	#counter
		for line in file:
			if i == 25:
				t = rg.search(line)
				if t:
					file.close()
					return t.group(2)
				else:
					file.close()
					return None
			else:
				i = i + 1
	except:
		return None


def getpass():
	filename = '/home/tylinial/.rodney'
	file = open(filename,'r')
	pss = file.readline()
	file.close()
	return pss	

def nhlog_pollnext(nhpoll):
	""" takes a list of nethack logfiles and checks for the first one
	with a complete gamedump, returns the element or None if none 
	ready

	"""
	for item in nhpoll:
		d = string.split(item,None, 15)
		n = string.split(d[15],',',1)
		lvl = getxpl(n[0])
		if lvl:
			return item
	return None

def crawl_pollnext(cp):
	for item in cp:
		return item
	return None

def gamedump(plname):
	""" Archive a player dump with timestamp

	"""
	filename = nhpath+'dumps/'+plname+'.lastgame.txt'
	try:
		file = open(filename, 'r')
	except:
		print "RODNEY: Error opening file. "+filename
		return
	filename2 = "/home/tylinial/public_html/"+plname+"."+time.strftime('%Y%m%j-%H%M%S')+".ascended.txt"
	try:
		file2 = open(filename2, 'w')
		for line in file:
			file2.write(line)
	except:
		print "RODNEY: Error writing to file. "+filename2
		return
	file.close()
	file2.close()
	return


def procinput(inp):
	""" processes data received from eotl for potential
	user requests

	"""
	buf = ""	# Define scope for the buffer
	global feed
	#print inp

	# extract tells from input and acts on them, output is buffered
	# and returned in a block for delivery
	m = re.findall('^([A-Za-z]+) tells you: (.*)$', inp, re.M)
	m += re.findall('^\[-Gamez-\] ([A-Za-z]+): (.*)$', inp, re.M)
	for data in m:
		plname = string.lower(data[0])
		s = data[1][:-1].lstrip().rstrip()
		
		rg = re.match('!help$', s)
		if rg:
			buf += "echo ' Get a tinyurl with !tiny <url>' "+plname+"\n" \
				"echo ' ??foo   search by entry title' "+plname+"\n" \
				"echo ' **bar   search for bar within entry bodies' "+plname+"\n" \
				"echo '    - Multipe search terms can be seperated by &&' "+plname+"\n" \
				"echo '    - ie: tell rodney ** fire resistance && eating' "+plname+"\n" \
				"echo ' !rank  player rankings by ascensions' "+plname+"\n" \
				"echo ' !moonphase  lists current effects from the moon if any' "+plname+"\n" \
				"echo ' !gamesby <player>  shows statistics from players games' "+plname+"\n" \
				"echo ' -- Ascension gamedumps available at:' "+plname+"\n" \
				"echo '    'http://nethack.eotl.org/~tylinial/' "+plname+"\n"
			continue
			
		rg = re.match('!rank$', s)
		if rg:
			count = 0
			foo = halloffame()
			buf += "tell "+plname+" Ranking by Ascensions\n"
			for [name,score] in foo:
				count += 1
				buf += "tell "+plname+" "+str(count)+"..  "+name+": "+str(score)+"\n"

		rg = re.match('!gamesby (.*)$', s)
		if rg:
			foo = gamesby(rg.group(1))
			buf += "tell "+plname+" "+rg.group(1).capitalize()+" has played "+str(foo[0])+ \
			" with highest score "+str(foo[1])+", ascended "+str(foo[2])+", died "+str(foo[3])+\
			", lifesaved "+str(foo[4])+", quit "+str(foo[5])+", escaped "+str(foo[6])+" times."

		rg = re.match('^\?\?(.*)\[(\d)\]$', s)
		if rg:
			d = rodlib.find(rg.group(1).lstrip(), int(rg.group(2)))
			for item in d:
				buf += "tell "+plname+" "+item[1]+": "+item[2]+"\n"
			if not d:
				buf += "tell "+plname+" No results, try without the index.\n"
			continue
		rg = re.match('^\?\?(.*)$', s)
		if rg:
			d = rodlib.find(rg.group(1).lstrip())
			for item in d:			
				buf += "tell "+plname+" "+item[1]+": "+item[2]+"\n"
			if not d:		
				buf += "tell "+plname+" No results, try a search.\n"
			continue

		rg = re.match('^\*\*(.*)$', s)
		if rg:
			d = rodlib.search(rg.group(1).lstrip())
			for item in d:
				buf += "tell "+plname+" "+item[1]+": "+item[2]+"\n"
			if not d:
				buf += "tell "+plname+" No results.\n"
			continue

		rg = re.match('^!tiny (.*)$', s)
		if rg:
			buf += "tell "+plname+" "+tinyurl.getTinyurl(rg.group(1))+"\n"
			continue

		rg = re.match('^!doupdatenow$', s)
		if rg:
			buf += "tell "+plname+" "
			if rodlib.update(True):
				rodlib.loaddata()
				buf += "Update complete.\n"
			else:
				buf += "Update failed.\n"
			continue

		rg = re.match('^!lastupdate$', s)
		if rg:
			buf += "tell "+plname+" Last update : "+time.ctime(rodlib.lastupdate())+"\n"
			buf += "tell "+plname+" Current time: "+time.ctime()+"\n"
			continue

		rg = re.match('^!lastgame (.*)$', s)
		if rg:
			s = lastgame(rg.group(1))
			if s:
				buf += "tell "+plname+" "+s+"\n"
			else:
				buf += "tell "+plname+" Couldn't find a lastgame for "+rg.group(1)+"\n"
			continue

		rg = re.match('^!moonphase$', s)
		if rg:
			if luckmsg:
				buf += "tell "+plname+" "+luckmsg+'\n'
			else:
				buf += "tell "+plname+" No unusual moon phase info right now\n"
			continue

		rg = re.match('^!updatefeed$', s)
		if rg:
			try:
				del feed
				reload(rodfeed)
				feed = rodfeed.Feed()
				buf += "tell "+plname+" Reloaded.\n"
			except:
				buf += "tell "+plname+" Reload failed.\n"
			continue

		rg = re.match('^!updatelib$', s)
		if rg:
			try:
				reload(rodlib)
				buf += "tell "+plname+" Reloaded.\n"
			except:
				buf += "tell "+plname+" Reload failed.\n"
			continue

		rg = re.match('^!clearfeed$', s)
		if rg:
			feedpoll = []
			buf += "tell "+plname+" Feeds cleared.\n"
			continue
	
	return buf

def halloffame():
	buf = []
	rank = {}
	
	file = open(nhpath+'logfile', 'r')
	
	s = file.readlines()
	file.close()

	for item in s:
	
		rg = re.match('^(.*),ascended(.*)',item)
		if rg:
			tr = rg.group(1)
			buf += [ tr.rsplit(" ",1)[1] ]
		
	if buf:
		for name in buf:
			if not rank.has_key(name):
				rank[name] = buf.count(name)
				
		return sorted(rank.items(), key=itemgetter(1), reverse=True)
	return ["None on file!",0]

def gamesby(player):
	""" Display game statistics for player
	"""
	
	file = open(nhpath+'logfile', 'r')

	#s = []
	#for line in file:
	#	s.append(line)
	#file.close()

	gcount = 0
	hscore = 0
	ascended = 0
	died = 0
	lifesaved = 0
	quit = 0
	escaped = 0

	for line in file:
		buf = line.split()
		nand = buf[15].split(',')
		
		if nand[0].lower() == player.lower() and line[-6:-1] != "{wiz}" and line[-6:-1] != "{exp}":
			gcount = gcount + 1
			if hscore < int(buf[1]):
				hscore = int(buf[1])
			lifesaved += int(buf[7])
			if nand[1].split()[0] == "ascended":
				ascended = ascended + 1
			elif nand[1].split()[0] == "quit":
				quit = quit + 1
			elif nand[1].split()[0] == "escaped":
				escaped = escaped + 1
			else:
				lifesaved -= 1
				died = died + 1
	file.close()
	return ( gcount, hscore, ascended, died, lifesaved, quit, escaped )
	
def toascii(arg):
	return unicodedata.normalize('NFKC', arg).encode('ascii','ignore')

def numsuffix(num):
	snum = str(num)

	if snum[-1:] is '1':
		return snum+'st'
	if snum[-1:] is '2':
		return snum+'nd'
	if snum[-1:] is '3':
		return snum+'rd'
	#otherwise th
	return snum+'th'

if __name__ == "__main__":
	main()
