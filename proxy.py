import requests
import re
import sys
from time import localtime, strftime
from lxml import html
import socket
from unittest.mock import patch

country="India"

def current_time(expression):
	if expression=='date':
		tme=strftime("%d-%m", localtime())
	elif expression=='time':
		tme=strftime("%H:%M:%S", localtime())
	elif expression=='date-time':
		tme=strftime("%Y-%m-%d %H:%M:%S", localtime())
	return tme
	
def check_ip(proxy,protocol):
	try:
		s = requests.Session()
		if proxy != "":
			print("[!] Checking IP address using proxy...")
			ipv4data=s.get(protocol+'://ipv4.ipleak.net/?mode=ajax&_=1536493386474', proxies=proxy, allow_redirects=True,timeout=10)
			ipv6data=s.get(protocol+'://ipleak.net/', proxies=proxy, allow_redirects=True,timeout=10)
		elif proxy == "":
			print("[!] Checking IP address without proxy...")
			ipv4data=s.get(protocol+'://ipv4.ipleak.net/?mode=ajax&_=1536493386474', allow_redirects=True,timeout=10)
			ipv6data=s.get(protocol+'://ipleak.net/', allow_redirects=True,timeout=10)
		else:
			print("[X] Error Occured !")
			sys.exit(0)
		if ipv4data.status_code==200:
			pass
		else:
			print(current_time("date-time")+" [X] Data request failed. Response Code - ",ipv4data.status_code)
			sys.exit(0)
		ipv4=re.compile(r'nofollow" href=".*?">(.*?)</a>').findall(ipv4data.text)
		location=re.compile(r'<div data-tooltip="(.*?)" class="location"').findall(ipv4data.text)
		print("[i] IPv4 Address:")
		print("	[*] IP: "+ipv4[0]+", Location: "+location[0])


		if ipv6data.status_code==200:
			pass
		else:
			print(current_time("date-time")+" [X] Data request failed.")
			return False
		# print(ipv6data.text)
		ipv6=re.compile(r'"ip":"(.*?)","reverse"').findall(ipv6data.text)
		country=re.compile(r'country_name":(.*?),"region_code').findall(ipv6data.text)
		region=re.compile(r'region_name":(.*?),"continent_code').findall(ipv6data.text)
		# print(country)
		# print(region)
		country=re.findall(r'^"(.*?)"$',country[0])
		region=re.findall(r'(.*?)',region[0])
		print("[i] IPv6 Address:")
		print("	[*] IP: "+ipv6[0]+", Location: "+country[0]+" - "+region[0])
		return True
	except requests.exceptions.ConnectionError:
		print("[X] Proxy Connection Error")
		return False
	except requests.exceptions.Timeout:
		print("[X] Timeout exception occured")
		return False

def check_proxies():
	s = requests.Session()
	proxydata = s.get('https://free-proxy-list.net/', allow_redirects=True, timeout=20)
	# <tr><th>IP Address</th><th>Port</th><th>Code</th><th class='hm'>Country</th><th>Anonymity</th><th class='hm'>Google</th><th class='hx'>Https</th><th class='hm'>Last Checked</th></tr>
	proxyvalues = re.compile(r"<tr><td>(.*?)</td><td>(.*?)</td><td>.*?</td><td class='hm'>(.*?)</td><td>(.*?)</td><td class='hm'>.*?</td><td class='hx'>(.*?)</td><td class='hm'>.*?</td></tr>").findall(proxydata.text)
	return proxyvalues

def get_proxy(protocol):
	proxyDict=""
	# protocol="https"
	check_ip(proxyDict,protocol)
	proxyvalues=check_proxies()
	# print(proxyvalues[1])
	i=0
	j=1
	while i < len(proxyvalues):
		# print(proxyvalues[i])
		if proxyvalues[i][2]==country:
			print("[X] Skipping "+country+" Proxy...")
			i+=1
		elif proxyvalues[i][3]=="elite proxy" or proxyvalues[i][3]=="anonymous":
			if protocol=="http" and proxyvalues[i][4]=="no":
				proxyDict = { "http"  : "http://"+proxyvalues[i][0]+":"+proxyvalues[i][1] }	
				print("[i] Trying ",protocol," proxy - "+proxyvalues[i][0]+":"+proxyvalues[i][1]+" - "+proxyvalues[i][3])			
				if check_ip(proxyDict,protocol):
					print("[i] "+protocol+" connection sucessfull with proxy - "+proxyvalues[i][0]+":"+proxyvalues[i][1])
					return proxyDict
				else:
					print("[i] "+protocol+" connection failed")
					i+=1		
			elif protocol=="https" and proxyvalues[i][4]=="yes":
				proxyDict = { "https"  : "https://"+proxyvalues[i][0]+":"+proxyvalues[i][1] }
				print("[i] Trying ",protocol," proxy - "+proxyvalues[i][0]+":"+proxyvalues[i][1]+" - "+proxyvalues[i][3])			
				if check_ip(proxyDict,protocol):
					print("[i] "+protocol+" connection sucessfull with proxy - "+proxyvalues[i][0]+":"+proxyvalues[i][1])
					return proxyDict
				else:
					print("[i] "+protocol+" connection failed")
					i+=1
			else:
				print("[i] Checking next proxy - ",i,"\r",end="")
				i+=1
		else:
			print("[i] Skipping proxy - "+proxyvalues[i][0]+":"+proxyvalues[i][1]+" - "+proxyvalues[i][3])
			i+=1
			
# get_proxy("http")