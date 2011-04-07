
import httplib, sys, time, re

def find(str, n = None):
	""" returns a str of definitions matching str, if n is supplied
	only the nth match is returned
	"""
	buf = []	# list for output

	str = str.replace(' ','_').lower()

	for item in tehdata:
		if item[1].lower() == str:
			rg = re.match('^[S|s]ee \{(.*)\}$',item[2])
			if rg:
				ref = rg.group(1).replace(' ','_')
				for it in tehdata:
					if it[1] == ref:
						buf += [it]
			else:
				buf += [item]
	if n:
		if n >= len(buf):
			return []
		return [buf[n]]
	return buf
	
def search(str):
        buf = []        # list for output

        str = str.lower()

	sstr = str.split('&&')
	
	for s in range(len(sstr)):
		sstr[s] = sstr[s].strip()
	
	for item in tehdata:
		cc = 0
		bufs = []
		for s in sstr:
	                if s in item[1].lower().replace('_',' ') or s in item[2].lower():
        	                bufs += [[item]]
				cc = cc + 1
		if cc == len(sstr):
			buf += bufs[0]
	return buf
	

def update(forced=False):
	""" Attempts to retrieve the most recent version of Rodney's
	info from nethack.alt.org. Keeps a copy of the current incase
	and then reinitialises tehdata
	"""

	global utime
	
	#Check whether update is necessary, if utime exists and is 
	#>24 hours(60*60*24==86400)
	#return False;
	
	if int(time.time())-86400 < utime and not forced:
		return False
	
	#print "Rodney:  Doing update..."
	# Store a backup of our current data if it exists
	try:
		file = open('learn.dat', 'r')
		s = file.read()
		file.close
		file = open('learn.dat.bak', 'w')
		file.write(s)
		file.close
	except:
		pass

	# get the new stuff hot off the presses

	conn = httplib.HTTPConnection("alt.org")
	conn.request("GET", "/nethack/Rodney/learn.dat.txt")
	# function spits exception if it fails to connect, catch
	# and retry later
	try:
		res = conn.getresponse()
	except:
                if not forced:
                        print "Rodney: Update failed, retrying in one hour"
                        utime = time.time()-3600
                return False

	# if there was any problem retrieving file just return now
	if res.status != 200:
		if not forced:
			print "Rodney: Update failed, retrying in one hour"
			utime = time.time()-3600
		return False

	

	s = res.read()
	conn.close()

	file = open('learn.dat', 'w')
	file.write(s)
	file.close

	#update time of update
	utime = time.time()
	#print "Rodney:  Update done."

	return True

def loaddata():
	""" Function which reloads tehdata with info from learn.dat
	attempts to retrieve if it doesnt already exist but will
	exit the system if fails. Called during init
	"""

	global tehdata
	tehdata = []

	for filen in ("learn.dat", "empty.txt"):

		try:
			file = open(filen)
		except:
			if not update(True):
				print "initialisation failed"
				sys.exit(0)
			file = open(filen)

		for line in file:	
			if( len(line.split('	', 2)) < 3):
				continue
			tehdata.append(line.split('	',2))
		file.close

def lastupdate():
	""" returns time of last update in seconds since the Epoch

	"""
	return utime


""" Initialisation code here, executed when the module is imported
    open the existing datafile and load it to a list of lists
"""
utime = 0
loaddata()

