import library_API as la
import time
import math as m

class Agent(object):

	def __init__(self, id_market lambda1, lambda2, tau, qty, spread, api_key, funcs):
		self.api_key = api_key
		self.lambda1 = lambda1
		self.lambda2 = lambda2
		self.tau = tau
		self.qty = qty
		self.spread = spread
		self.position1 = 0
		self.position2 = None
		self.pnl = 0
		self.target = 50
		self.last_trade = None
		self.limits = {}
		self.mytrades = {}
		self.mylimits = {}
		self.balance = 0
		self.funcs = funcs
		self.id_market = id_market
		
	def HasChanged(self):
		values = {'key' : self.api_key, 'function' : 'get_change'}
		time.sleep(0.01)
		data = funcs.call(values)
		return -1 if data['status']==1 else data['change']
	
	def GetBalance(self):
		values = {'key' : self.api_key, 'function' : 'get_balance'}
		time.sleep(sleep_time)
		data = funcs.call(values)
		return -1 if data['status']==1 else data['balance']
	
	def GetLastTrade(self):
		values = {'key' : self.api_key, 'function' : 'get_trades', 'id_market' : self.id_market}
		time.sleep(sleep_time)
		data = funcs.call(values)
		self.last_trade  = data['trades']
		return -1 if data['status']==1 else data['trades']
	
	def GetMyTrades(self):
		values = {'key' : self.api_key, 'function' : 'get_my_trades', 'id_market' : self.id_market}
		time.sleep(sleep_time)
		data = funcs.call(values)
		self.mytrades = data['trades']
		return -1 if data['status']==1 else len(data['trades'])
	
	def GetLimits(self):
		values = {'key' : self.api_key, 'function' : 'get_limits', 'id_market' : self.id_market}
		time.sleep(sleep_time)
		data = funcs.call(values)
		self.limits=data['limits']
		return -1 if data['status']==1 else len(data['limits'])
	
	def GetMyLimits(self):
		values = {'key' : self.api_key, 'function' : 'get_my_limits', 'id_market' : self.id_market}
		time.sleep(sleep_time)
		data = funcs.call(values)
		self.mylimits=data['limits']
		return -1 if data['status']==1 else len(data['limits'])
			
	def DoIt(self):
		last = self.last_trade
		buy_volume = funcs.get_buy_volume(self.mytrades)
		sell_volume = funcs.get_sell_volume(self.mytrades)
		if last != None:
			self.pnl = 0.01*(sell_volume*funcs.get_sell_avg_price(self.mytrades) - buy_volume*funcs.get_buy_avg_price(self.mytrades) + (buy_volume - sell_volume)*last)
				
		self.position1 = buy_volume - sell_volume
		if self.position2==None:
			self.position2 = buy_volume - sell_volume
		self.position2 = self.position2 * (1.0 -  m.exp(-1.0/self.tau)) + self.position1 * m.exp(-1.0/self.tau)
		
		mid = self.target - self.lambda1 * self.position1 - self.lambda2 * (self.position1 - self.position2)
		s = self.spread + self.qty * 0.5 * (self.lambda1 + self.lambda2)

		buy_target_price = 0.5*m.floor(2*mid-s)
		sell_target_price = 0.5*m.ceil(2*mid+s)
		
		my_first = funcs.get_depth(self.mylimits, 1)		
		my_buy_price = -1 if len(my_first['bid'])==0 else my_first['bid'][0]['price']
		my_sell_price = -1 if len(my_first['ask'])==0 else my_first['ask'][0]['price']
		
		success_send = True
		success_cancel = True
		sent = 0
		canceled = 0
		sent_prices=[]	
			
		if my_buy_price != buy_target_price:
			if my_buy_price != -1:
				for id in my_first['bid'][0]['id_orders']:
					values = {'key' : self.api_key, 'function' : 'cancel_order', 'id_order' : id}
					time.sleep(sleep_time)
					data = funcs.call(values)
					if data['status'] == 1:
						success_cancel = False
					else:
						canceled += 1						
			values = {'key' : self.api_key, 'function' : 'send_order', 'id_market' : self.id_market, 'side' : 1, 'price' : buy_target_price, 'volume' : self.qty}	
			time.sleep(sleep_time)
			data = funcs.call(values)
			if data['status'] == 1:
				success_send = False
			else:
				sent += 1
				sent_prices.append(buy_target_price)
		
		if my_sell_price != sell_target_price:
			if my_sell_price != -1:
				for id in my_first['ask'][0]['id_orders']:
					values = {'key' : self.api_key, 'function' : 'cancel_order', 'id_order' : id}
					time.sleep(sleep_time)
					data = funcs.call(values)
					if data['status'] == 1:
						success_cancel = False
					else:
						canceled += 1
			values = {'key' : self.api_key, 'function' : 'send_order', 'id_market' : self.id_market, 'side' : -1, 'price' : sell_target_price, 'volume' : self.qty}	
			time.sleep(sleep_time)
			data = funcs.call(values)
			if data['status'] == 1:
				success_send = False
			else:
				sent += 1
				sent_prices.append(sell_target_price)
			
		return success_send, sent, success_cancel, canceled, mid, s, sent_prices
	
	
sleep_time = 0.1
		
funcs = la.functions()
key = 	'8@0S4PYLF187MK5L3U5BWUMKMI70FEMX'#'1\G746OIV9SDMFRS26Z4H9OGM3J1VRYM',#

id_markets = [1,2]
agents = {}
for id_market in id_markets:
	agents[id_market] = Agent(id_market = id_market,  lambda1 = 0.05, lambda2 = 0.05, tau = 1, qty = 10, spread = 0, api_key = key, funcs = funcs)

for key, agent in agents.iteritems():
	try:
		print 'Agent on market ', key
		agent.balance = agent.GetBalance()
		print 'balance : ', agent.balance
		status = agent.GetLastTrade()
		print 'Fetch trades : ', status
		status = agent.GetMyTrades()
		print 'Fetch my trades : ', status
		status = agent.GetMyLimits()
		print 'Fetch my limits : ', status	
		success_send, sent, success_cancel, canceled, mid, spread, sent_prices = agent.DoIt()
		print 'Mid-price :',  mid, ' Spread : ', spread, ' Position : ', agent.position1, ' PNL : ', agent.pnl
		print 'Send_success : ', success_send, ', Sent : ', sent, ', prices : ', sent_prices
		print 'Cancel_success : ', success_cancel, ', Canceled : ', canceled
	except:
		print 'Failed to initialize'
	
while(True):
	try:
		time.sleep(1)
		response = agents[id_markets[0]].HasChanged()
		for id_market in response:
			agent = agents[id_market]
			print ''
			agent.balance = agent.GetBalance()
			print 'balance : ', agent.balance
			status = agent.GetLastTrade()
			print 'Fetch trades : ', status
			status = agent.GetMyTrades()
			print 'Fetch my trades : ', status
			status = agent.GetMyLimits()
			print 'Fetch my limits : ', status
			success_send, sent, success_cancel, canceled, mid, spread, sent_prices= agent.DoIt()
			print 'Mid-price :',  mid, ' Spread : ', spread, ' Position : ', agent.position1, ' PNL : ', agent.pnl
			print 'Send_success : ', success_send, ', Sent : ', sent, ', prices : ', sent_prices
			print 'Cancel_success : ', success_cancel, ', Canceled : ', canceled
	except:
		print 'Connection monmentarily lost'
		
# print obj.get_depth(data['limits'], 3)

# print 'Response: ', response.status, response.reason
# print 'Data:'

# print data