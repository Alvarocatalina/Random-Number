import urllib.request, re
import requests, json
import time

while(1):
	fileWeb = urllib.request.urlopen("https://www.numeroalazar.com.ar/")
	web = fileWeb.read().decode("utf-8")
	RandomNumber =re.search('\d\d\.\d\d',str(web)).group(0)
	UrlW = 'https://api.thingspeak.com/update?api_key=ZL3SLW04HRLYSD5Z&field1='
	TSwURL = urllib.request.urlopen(UrlW + str(RandomNumber))
	v=r.lpush("RandomNumber",RandomNumber)
	time.sleep(120)