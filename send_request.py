import library_API as la
import time
import math as m
import random as rd

class Agent(object):

	def __init__(self, id_market, target_price, lambda1, lambda2, alpha, tau, qty, max_loss, spread, fee, api_key, funcs):
		self.api_key = api_key
		self.lambda1 = lambda1
		self.lambda2 = lambda2
		self.alpha= alpha
		self.tau = tau
		self.qty = qty
		self.max_loss = max_loss
		self.spread = spread
		self.fee = fee
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
		
		#mid = self.target - self.lambda1 * self.position1 - self.lambda2 * (self.position1 - self.position2)
		#s = self.spread + self.qty * 0.5 * (self.lambda1 + self.lambda2)
		
		#buy_target_volume = self.qty
		#sell_target_volume = self.qty
	
		mid = funcs.get_price_from_position(self.position1, self.target, self.max_loss, self.alpha)
		
		#if self.position1>=0:
		#	mid = (self.alpha + self.target)*m.exp(-self.position1/self.qty/(self.alpha + self.target))-self.alpha
		#else:
		#	mid = (100.0 + self.alpha) - (self.alpha + 100.0 - self.target)*m.exp(self.position1/self.qty/(self.alpha + 100.0- self.target))

		s = self.spread
		
		mid_sup = mid+0.25+0.5*s
		mid_inf = mid-0.25-0.5*s

		buy_target_price = 0.5*m.floor(2.0*mid-0.5-s-self.fee)
		if buy_target_price>=100.0:
			buy_target_price = 99.5
			mid_inf = 99.5
		sell_target_price = 0.5*m.ceil(2.0*mid+0.5+s+self.fee)
		if sell_target_price<=0.0:
			sell_target_price = 0.5
			mid_sup = 0.5

		if mid_inf>0.0:
			buy_target_volume = funcs.get_position_from_price(mid_inf, self.target, self.max_loss, self.alpha) - self.position1
		#	if mid_inf>self.target:
		#		buy_target_volume = - self.position1 - self.qty*(self.alpha + 100.0 - self.target)*m.log((100.0 + self.alpha - self.target)/(100.0+ self.alpha - mid_inf)) 
		#	else:	
		#		buy_target_volume = - self.position1 + self.qty*(self.alpha + self.target)*m.log((self.alpha + self.target)/(self.alpha + mid_inf)) 
			buy_target_volume = rd.random()*0.5*buy_target_volume + 0.5*buy_target_volume
			buy_target_volume = 0.1*m.floor(10.0*buy_target_volume)

		if mid_sup<100.0:
			sell_target_volume = self.position1 - funcs.get_position_from_price(mid_sup, self.target, self.max_loss, self.alpha)
		#	if mid_sup>self.target:	
		#		sell_target_volume = self.position1 + self.qty*(self.alpha + 100.0- self.target)*m.log((100.0+ self.alpha - self.target)/(100.0+ self.alpha - mid_sup))
		#	else:
		#		sell_target_volume = self.position1 - self.qty*(self.alpha + self.target)*m.log((self.alpha + self.target)/(self.alpha + mid_sup))
			sell_target_volume = rd.random()*0.5*sell_target_volume + 0.5*sell_target_volume
			sell_target_volume = 0.1*m.floor(10.0*sell_target_volume)

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
			if buy_target_price>0:							
				values = {'key' : self.api_key, 'function' : 'send_order', 'id_market' : self.id_market, 'side' : 1, 'price' : buy_target_price, 'volume' : buy_target_volume}	
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
			if sell_target_price<100:		
				values = {'key' : self.api_key, 'function' : 'send_order', 'id_market' : self.id_market, 'side' : -1, 'price' : sell_target_price, 'volume' : sell_target_volume}	
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
key_1 = '1@MDM4Y0SG18GFEP9WXNIIMHJ82679YV'#'1@NGC5KUO2TADMI69ZXEALGLR6G9CTVD'#
key_2 = '20@0GGWXK0HVF6O4EHNNMDZQPIREYTA81'

markets = [\
{'id' : 12, 'price' : 40, 'what' : 'chomage'}\
, {'id' : 13, 'price' : 10, 'what' : 'croissance'}\
, {'id' : 14, 'price' : 50, 'what' : 'croissance'}\
, {'id' : 15, 'price' : 40, 'what' : 'croissance'}\
, {'id' : 22, 'price' : 10, 'what' : 'dissolution'}\
, {'id' : 24, 'price' : 20, 'what' : 'hollande'}\
, {'id' : 26, 'price' : 20, 'what' : 'ecosse'}\
, {'id' : 27, 'price' : 20, 'what' : 'quatargate'}\
]
#markets = [{'id' :1, 'price' : 8}]
agents_1 = {}
agents_2 = {}
for market in markets:
	agents_1[market['id']] = Agent(id_market = market['id'], target_price =  market['price'], lambda1 = 0.05, lambda2 = 0.05, alpha = 10., tau = 1, qty = 2, max_loss = 50, spread = 4, fee = 2, api_key = key_1, funcs = funcs)
	#agents_2[market['id']] = Agent(id_market = market['id'], target_price =  market['price'], lambda1 = 0.05, lambda2 = 0.05, alpha = 10., tau = 1, qty = 3, spread = 2, api_key = key_2, funcs = funcs)

for agents in [agents_1]:#, agents_2]:
	for key, agent in agents.iteritems():
		#try:
		print ''
		agent.balance = agent.GetBalance()
		status = agent.GetLastTrade()
		print 'Agent on market ', key, 'balance : ', agent.balance, 'Fetch trades : ', status
		status = agent.GetMyTrades()
		#print 'Fetch my trades : ', status
		status = agent.GetMyLimits()
		print 'Fetch my limits : ', status	
		success_send, sent, success_cancel, canceled, mid, spread, sent_prices = agent.DoIt()
		print 'Mid-price :',  mid, ' Spread : ', spread, ' Position : ', agent.position1, ' PNL : ', agent.pnl
		print 'Send_success : ', success_send, ', Sent : ', sent, ', prices : ', sent_prices
		print 'Cancel_success : ', success_cancel, ', Canceled : ', canceled
		#except:
		#	print 'Failed to initialize on market ', key
	
while(True):
	try:
		time.sleep(1)
		for agents in [agents_1]:#, agents_2]:
			response = agents[markets[0]['id']].HasChanged()
			for id_market in response:
				#try:
				agent = agents[id_market]
				print ''
				agent.balance = agent.GetBalance()
				status = agent.GetLastTrade()
				print 'Agent on market ', id_market, 'balance : ', agent.balance, 'Fetch trades : ', status
				status = agent.GetMyTrades()
				#print 'Fetch my trades : ', status
				status = agent.GetMyLimits()
				print 'Fetch my limits : ', status
				success_send, sent, success_cancel, canceled, mid, spread, sent_prices= agent.DoIt()
				print 'Mid-price :',  mid, ' Spread : ', spread, ' Position : ', agent.position1, ' PNL : ', agent.pnl
				print 'Send_success : ', success_send, ', Sent : ', sent, ', prices : ', sent_prices
				print 'Cancel_success : ', success_cancel, ', Canceled : ', canceled
				#except:
				#	print 'No connection on market', id_market
	except:
		print 'Could not connect to the server'
		
# print obj.get_depth(data['limits'], 3)

# print 'Response: ', response.status, response.reason
# print 'Data:'

# print data
