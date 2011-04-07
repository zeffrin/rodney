import feedparser, time, cPickle as pickle, random

class Feed:
	" Object to retrieve and stream rss news feeds "
	def __init__(self):
		""" Initialization function, loads all feeds into global
		feeds - Warning:  Use sparingly as this will suspend the
		process until all feeds are updated.
	
		"""


		self.usedurls = {}	  # initialise as a list
		self.feeds = {}	  # feed is dict will be feed_url: [feed]
		self.feed_name = {}	  # feed_name is a dict holding our friendly names
		self.feed_freq = {}	  # stores utimes of new articles to guage frequency
		self.feed_urls = [ "http://www.fark.com/fark.rss", \
				"http://feeds.digg.com/digg/popular.rss", \
				"http://rss.cnn.com/rss/edition.rss", \
				"http://feeds.bbci.co.uk/news/world/rss.xml", \
				"http://rss.slashdot.org/Slashdot/slashdot", \
				"http://feeds.arstechnica.com/arstechnica/index?format=xml", \
				"http://www.nintendo.com/rss.xml?page=systemWii" \
				#"http://rss.cnn.com/rss/cnn_tech.rss" \
				#"http://rss.cnn.com/rss/cnn_world.rss" \
				]
		
		self.feed_chan = { "http://www.fark.com/fark.rss": "hl-fark", \
			"http://feeds.digg.com/digg/popular.rss": "hl-digg", \
			"http://rss.cnn.com/rss/edition.rss": "hl-cnn", \
			"http://feeds.bbci.co.uk/news/world/rss.xml": "hl-bbc", \
			"http://rss.slashdot.org/Slashdot/slashdot": "hl-slashdot", \
			"http://feeds.arstechnica.com/arstechnica/index?format=xml": "hl-ars", \
			"http://www.nintendo.com/rss.xml?page=systemWii": "hl-wii" \
			#"http://rss.cnn.com/rss/cnn_tech.rss": "hl-cnn" \
			#"http://rss.cnn.com/rss/cnn_world.rss": "hl-cnn" \
			}		

		self.feed_name = { "http://www.fark.com/fark.rss": "Fark", \
			"http://feeds.digg.com/digg/popular.rss": "Digg", \
			"http://rss.cnn.com/rss/edition.rss": "CNN", \
			"http://feeds.bbci.co.uk/news/world/rss.xml": "BBC", \
			"http://rss.slashdot.org/Slashdot/slashdot": "/.", \
			"http://feeds.arstechnica.com/arstechnica/index?format=xml": "Ars", \
			"http://www.nintendo.com/rss.xml?page=systemWii": "Wii" \
			#"http://rss.cnn.com/rss/cnn_tech.rss": "CNN Tech" \
			#"http://rss.cnn.com/rss/cnn_world.rss": "CNN"
			}
		
		try:
			self.feeds, self.usedurls, self.feed_freq = pickle.load(open("feeds.rod"))
		except:
			pass
		

		for feed_url in self.feed_urls:
			try: 
				self.feeds[feed_url]
			except:
				self.feeds[feed_url] = feedparser.parse(feed_url)
				self.feeds[feed_url]['utime'] = self.__calcutime(feed_url)
				for entry in self.feeds[feed_url]['entries']:
					entry['title'] = entry['title'].replace("&#39;", "'")
					entry['title'] = entry['title'].replace("&#34;", '"')
					entry['title'] = entry['title'].replace("&apos;", "'")
					entry['title'] = entry['title'].replace("&rsquo;", "'")
					entry['title'] = entry['title'].replace("&eacute;", "e")
					entry['title'] = entry['title'].replace("&quot;", '"')
					entry['title'] = entry['title'].replace("&amp;", '&')
					entry['title'] = entry['title'].replace("&ldquo;", '"')
					entry['title'] = entry['title'].replace("&rdquo;", '"')
					entry['title'] = entry['title'].replace("&pound;", '#')
					entry['title'] = entry['title'].replace("&hellip;", '...')
					entry['title'] = entry['title'].replace("&gt;", '>')
					entry['title'] = entry['title'].replace("&lt;", '<')
					entry['title'] = entry['title'].replace("&mdash;", '-')
					
				self.usedurls[feed_url] = []
				self.feed_freq[feed_url] = []
				for entry in self.feeds[feed_url]['entries']:
					self.usedurls[feed_url].append(entry['link'])
				print "Got new feed "+feed_url

		tmp = self.feeds.copy()
		for feed in tmp:
			if feed not in self.feed_urls:
				del self.feeds[feed]
				del self.usedurls[feed]
				del self.feed_freq[feed]
				print "Removed feed "+feed


	def __del__(self):
		self.save()

	def save(self):
		pickle.dump([self.feeds, self.usedurls, self.feed_freq], open("feeds.rod", "w"))
			

	def update(self):
		""" called during rodneys cycle to check whether any feeds
		are ready to update, process if so and return a list of 
		new entries for display etc					

		"""		

		buf = []
		for feed_url in self.feed_urls:
			if self.feeds[feed_url]['utime'] < time.time():
				tmp = self.__update_feed(feed_url)
				for entry in tmp:
					buf.append([self.feed_name[feed_url], entry, self.feed_chan[feed_url]])
		return buf
		


	def __update_feed(self, feed_url):
		""" process update of passed url and return a list of new
		news items	

		"""

		# store current feed away and grab new one
		buf = self.feeds[feed_url]
		self.feeds[feed_url] = feedparser.parse(feed_url)
		self.feeds[feed_url]['utime'] = self.__calcutime(feed_url)

		for entry in self.feeds[feed_url]['entries']:
			entry['title'] = entry['title'].replace("&#39;", "'")
			entry['title'] = entry['title'].replace("&#34;", '"')
			entry['title'] = entry['title'].replace("&apos;", "'")
			entry['title'] = entry['title'].replace("&rsquo;", "'")
			entry['title'] = entry['title'].replace("&eacute", "e")
			entry['title'] = entry['title'].replace("&quot;", '"')
			entry['title'] = entry['title'].replace("&amp;", '&')
			entry['title'] = entry['title'].replace("&ldquo;", '"')
			entry['title'] = entry['title'].replace("&rdquo;", '"')
			entry['title'] = entry['title'].replace("&pound;", '#')
			entry['title'] = entry['title'].replace("&hellip;", '...')
			entry['title'] = entry['title'].replace("&gt;", '>')
			entry['title'] = entry['title'].replace("&lt;", '<')
			entry['title'] = entry['title'].replace("&mdash;", '-')

			
		# list concat items which are new to the list
		newitems = [entry for entry in self.feeds[feed_url]['entries'] if entry not in buf['entries'] and entry['link'] not in self.usedurls[feed_url]]
		
		for item in newitems:
			self.usedurls[feed_url].append(item['link'])
			self.feed_freq[feed_url].append(time.time())

		while len(self.usedurls[feed_url]) > 100:
			self.usedurls[feed_url].pop(0)

		return newitems


	def __calcutime(self, feed_url):
		""" Calculates how long before polling this thread again	

		"""
		
		t = 0	

		try:
			loop = self.feed_freq[feed_url].copy()
			for entry in loop:
				if entry >= time.time()-3600:
					t += 1
				else: 
					self.feed_freq[feed_url].remove(entry)
		except:
			t=5	

		print 'RODNEY DEBUG: '+feed_url+' '+str(t)
		if t < 1:
			return time.time()+3600+random.randint(0,200)
		elif t < 4:
			return time.time()+2700+random.randint(0,200)
		elif t < 10:
			return time.time()+1800+random.randint(0,200)
		else:
			return time.time()+900+random.randint(0,200)



