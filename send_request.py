import library_API as la
import time
import math as m

class Agent(object):

	def __init__(self, id_market, target_price, lambda1, lambda2, tau, qty, spread, api_key, funcs):
		self.api_key = api_key
		self.lambda1 = lambda1
		self.lambda2 = lambda2
		self.tau = tau
		self.qty = qty
		self.spread = spread
		self.position1 = 0
		self.position2 = None
		self.pnl = 0
		self.target = target_price
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
		if data['status']==0:
			self.last_trade  = data['trades']
		return -1 if data['status']==1 else data['trades']
	
	def GetMyTrades(self):
		values = {'key' : self.api_key, 'function' : 'get_my_trades', 'id_market' : self.id_market}
		time.sleep(sleep_time)
		data = funcs.call(values)
		if data['status']==0:
			self.mytrades = data['trades']
		return -1 if data['status']==1 else len(data['trades'])
	
	def GetLimits(self):
		values = {'key' : self.api_key, 'function' : 'get_limits', 'id_market' : self.id_market}
		time.sleep(sleep_time)
		data = funcs.call(values)
		if data['status']==0:
			self.limits=data['limits']
		return -1 if data['status']==1 else len(data['limits'])
	
	def GetMyLimits(self):
		values = {'key' : self.api_key, 'function' : 'get_my_limits', 'id_market' : self.id_market}
		time.sleep(sleep_time)
		data = funcs.call(values)
		if data['status']==0:
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
key = 	'1@MDM4Y0SG18GFEP9WXNIIMHJ82679YV'#'1@NGC5KUO2TADMI69ZXEALGLR6G9CTVD'#

markets = [{'id' :7, 'price' : 0}\
, {'id' : 8, 'price' : 50}\
, {'id' : 9, 'price' : 19}\
, {'id' : 10, 'price' : 19}\
, {'id' : 11, 'price' : 10}\
, {'id' : 21, 'price' : 2}\
]
#markets = [{'id' :1, 'price' : 8}]
agents = {}
for market in markets:
	agents[market['id']] = Agent(id_market = market['id'], target_price =  market['price'], lambda1 = 0.05, lambda2 = 0.05, tau = 1, qty = 10, spread = 0, api_key = key, funcs = funcs)

for key, agent in agents.iteritems():
	try:
		print ''
		print 'Agent on market ', key, ' time : ', time.time()
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
		print 'Failed to initialize on market ', key
	
while(True):
	try:
		time.sleep(1)
		response = agents[markets[0]['id']].HasChanged()
		for id_market in response:
			try:
				agent = agents[id_market]
				print ''
				print 'Agent on market ', id_market, ' time : ', time.time()
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
				print 'No connection on market', id_market
	except:
		print 'Could not connect to the server'
		
# print obj.get_depth(data['limits'], 3)

# print 'Response: ', response.status, response.reason
# print 'Data:'

# print data