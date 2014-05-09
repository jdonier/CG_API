import httplib, urllib
import json
import math as m
import time

class functions(object):

	def __init__(self):
		return None
	
	def call(self, values):
		host = 'localhost:8000'#'crowdguess2.herokuapp.com'#
		url = '/API/'	
		headers = {
			'User-Agent': 'python',
			'Content-Type': 'application/x-www-form-urlencoded',
		}
		values = urllib.urlencode(values)
		conn = httplib.HTTPConnection(host)
		conn.request("POST", url, values, headers)
		response = conn.getresponse()
		data = response.read()
		data= json.loads(data)
		return data
		
	def get_last_price(self, trades):
		return trades[len(trades)-1]['price']

	def get_price_exp_MA(self, trades, n):
		p = 0
		norm = 0
		i=0
		for trade in trades[::-1]:
			p += m.exp(-i*1.0/n)*trade['price']
			norm += m.exp(-i*1.0/n)
			i+=1
		return 0 if norm==0 else p/norm

	def get_volume(self, trades):
		volume=0
		for trade in trades:
			if trade.has_key('null'):
				if not trade['null']:
					volume += trade['volume']
		return volume

	def get_buy_volume(self, trades):
		volume=0
		for trade in trades:
			if trade['side']==1:
				if trade.has_key('null'):
					if not trade['null']:
						volume += trade['volume']
				else:			
					volume += trade['volume']
		return volume
		
	def get_sell_volume(self, trades):
		volume=0
		for trade in trades:
			if trade['side']==-1:
				if trade.has_key('null'):
					if not trade['null']:
						volume += trade['volume']
				else:			
					volume += trade['volume']	
		return volume

	def get_buy_avg_price(self, trades):
		p=0
		norm = 0
		for trade in trades:
			if trade['side']==1:
				if trade.has_key('nulltrade'):
					if not trade['nulltrade']:
						p += trade['volume']*trade['price']
						norm += trade['volume']
				else:
					p += trade['volume']*trade['price']
					norm += trade['volume']	
		return 0 if norm==0 else p/norm
		
	def get_sell_avg_price(self, trades):
		p=0
		norm = 0
		for trade in trades:
			if trade['side'] == -1:
				if trade.has_key('nulltrade'):
					if not trade['nulltrade']:
						p += trade['volume']*trade['price']
						norm += trade['volume']
				else:
					p += trade['volume']*trade['price']
					norm += trade['volume']	
		return 0 if norm==0 else p/norm
			
	def get_depth(self, limits, n):
		bid=[]
		ask=[]
		i=0
		level = 0
		while i<len(limits) and level<n:
			if limits[i]['side'] == -1:
				j=0
				price = limits[i]['price']
				volume = 0
				ids=[]
				while i+j<len(limits) and limits[i+j]['price']==price:
					volume += limits[i+j]['volume']
					ids.append(limits[i+j]['id'])
					j+=1
				level+=1	
				ask.append({'price' : price, 'volume' : volume, 'id_orders' : ids})
				i = i+j-1
			i+=1
		i = len(limits)-1
		level = 0
		while i>=0 and level<n:
			if limits[i]['side'] == 1:
				j=0
				price = limits[i]['price']
				volume = 0
				ids=[]
				while i-j>=0 and limits[i-j]['price']==price:
					volume += limits[i-j]['volume']
					ids.append(limits[i-j]['id'])
					j+=1
				level+=1	
				bid.append({'price' : price, 'volume' : volume, 'id_orders' : ids})
				i = i-j+1
			i-=1
		return {'bid': bid, 'ask' : ask}
			
	def get_related_markets(self, events, id_market):
		is_right_event = False
		for event in events:
			markets = []
			for market in event['markets']:
				markets.append({'id_market' : market['id_market'], 'outcome' : market['outcome']})
				if market['id_market']==id_market:
					is_right_event=True
			if is_right_event:
				return markets
		return None
			
	def get_markets_in_event(self, events, id_event):
		markets=[]
		for event in events:
			if event['id_event']==id_event:
				for market in event['markets']:
					markets.append({'id_market' : market['id_market'], 'outcome' : market['outcome']})
		return markets			
		
	def get_position(self, trades):
		pos = 0
		for trade in trades:
			if not trade['null']:
				if trade['side']==1:
					pos+=trade['volume']
				else:
					pos -= trade['volume']
		return pos		

	def get_position_exp_MA(self, trades, n):
		position = [0]
		pos = 0
		for trade in trades:
			if not trade['null']:
				if trade['side']==1:
					pos+=trade['volume']
				else:
					pos -= trade['volume']
				position.append(pos)	
		p = 0
		norm = 0
		i=0
		for po in position[::-1]:
			p += m.exp(-i*1.0/n)*po
			norm += m.exp(-i*1.0/n)
			i+=1
		return 0 if norm==0 else p/norm

# get_balance_for_each_outcome(id_event)   => PNL par outcome si settlement immediat
	


