import urllib2
import json

TOKEN = "9f90cfc866720f9c6ef6bae19e5e31f17e2b29ea"
ROOT_URL = "https://api-ssl.bitly.com"
SHORTEN = "/v3/shorten?access_token={}&longUrl={}"

class BitlyHelper:
	def shorten_url(self, longurl):
		try:
			url = ROOT_URL + SHORTEN.format(TOKEN, longurl)
			response = urllib2.urlopen(url).read()
			jr = json.loads(response)
			return jr['data']['url']
		except Exception as e:
			print e

