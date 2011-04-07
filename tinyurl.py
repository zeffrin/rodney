import urllib


def getTinyurl(url):
	""" http://huacn.blogbus.com/logs/26387436.html """
	if len(url) < 24:
		return url
	apiurl = "http://tinyurl.com/api-create.php?url="
	tinyurl = urllib.urlopen(apiurl + url).readline()
	if tinyurl == "ERROR" or tinyurl == "Error":
		return url
	return tinyurl

