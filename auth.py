#!/usr/bin/env python
"""
Flask micro-weight authentication module for flask and mongoDb inspired from passport.js and express sessions
Author : Jean-Philippe Beaudet
version : 1.0.0

"""
#imports
import hashlib, binascii
from pymongo import MongoClient
from functools import wraps
from flask import Flask, request, session, redirect, url_for
from uuid import getnode as get_mac

#main class
class Auth(object):
	'''
	@params users: mongoDb collection dedicated for user authentication (( can be overriden directly in authenticate and register functions for flexibility))
	@params strategy: authentication strategy deafult='default'
	@params salt: salt used for password digest default='<this is a secret>'
	@params session_secret: (str) stalt used for session cobject default='<this is a session secret>'
	@params redirect: callback url for failed login default='/login'
	'''
	def __init__(self, users, strategy='default', salt='<this is a secret>', session_secret='<this is a session secret>', redirect = 'login'):
		# set initials values
		self.users = users
		self.salt = str.encode(salt)
		self.strategy = strategy
		self.session = session
		self.redirect = redirect
		self.supersecret = str.encode(session_secret)
		# add strategy here
		self.authenticate_strategy_list = {
			'default': 'authenticate_default'
		}
		self.register_strategy_list = {
			'default': 'register_default'
		}
		
	### Main functions ###
	######################
			
	#authenticate bootsrap function	
	def authenticate(self, username, password, cb,  strategy = None, users = None):
		'''
		@params username: (str) username to search in user db colelction
		@params password: (str) current passsword to check against
		@params cb: (func) callback for async
		@params strategy: (str) overrride argument for strategy choosing
		@params users: (str) override argument for user db collection
		@return function(): callback
		'''
		# run ovveride if necessary
		if strategy:
			self.strategy = strategy
		if users:
			self.users = users	
		#call the appropriate strategy function	
		ret = getattr(self, self.authenticate_strategy_list[self.strategy])(username, password)
		#update session
		self.update(ret)		
		#run callback
		return cb(ret)
	
	#register bootsrap function
	def register(self, username, password, cb,  strategy = None, users = None, payload = None, role='user'):
		'''
		@params username: (str) username to add in user db colelction 
		@params password: (str) current passsword to add in db collection
		@params cb: (func) callback for async
		@params payload: (dict) optional payload for the user
		'''
		# run ovveride if necessary
		if strategy:
			self.strategy = strategy
		if users:
			self.users = users
		#call the appropriate strategy function	
		ret = getattr(self,self.register_strategy_list[self.strategy])(username, password, payload, role=role)	
		#run callback
		return cb(ret)

	#logout function
	def logout(self):
		'''
		@params: None 
		@return: (str) return "session updated" or err message
		'''
		try:
			self.session.pop(self.digest(str(get_mac())))
			ret = "session updated"	
			return ret	
		except Exception as e:
			print(e)
			# Error while trying to create the resource
			ret = e
			return ret	

	### Utils ###
	#############	
		
	# digest function for password (using SHA-256)
	def digest(self, string):
		psw = str.encode(string)
		dk = hashlib.pbkdf2_hmac('sha256', psw, self.salt, 100000)	
		return str(binascii.hexlify(dk))		
	
	# digest function for session(using SHA-256)
	def record(self, record):
		psw = str.encode(record)
		dk = hashlib.pbkdf2_hmac('sha256', psw, self.supersecret, 100000)	
		return str(binascii.hexlify(dk))
			
	# session update function
	def update(self, ret):
		'''
		@params ret: (bool) indicate succesful or failed login
		'''
		print('update fired')
		# if attempt was succesful
		if ret:
			# update session object for the current user
			self.session[self.digest(str(get_mac()))] = self.record('true')
			return True
		else:
			print('ret is '+str(ret))
			return True
	
	# function to get current session object
	def is_logged_in(self):
		'''
		check in Session() object for the g.current_user to see if logged in
		'''

		# check if user exist in session object
		try:
			test = self.session[self.digest(str(get_mac()))]
			#check if user is logged in
			if test == self.record('true'):
				return True
			else:
				return False
		except Exception as e:
			print(e)
			# Error while trying to create the resource
			return False
						
	# function to get current user data
	def current_user(self):
		'''
		@return user: (list) a user object for retreiving information about current user
		'''
		user = User()
		user.origin = self.digest(str(get_mac()))
		query = self.session[self.digest(str(get_mac()))]	
		if query is not None:
			records_fetched = self.users.find({"origin": query})
			if records_fetched.count() > 0:
				user.user.update(list(records_fetched))
				user.isLoggedIn = True
				return user
			else:
				return user
		else:
			records_fetched = self.users.find({"origin": str(get_mac())})
			if records_fetched.count() > 0:
				user.user.update(list(records_fetched))
				return user
			else:
				return user		
					
	### Srategies ###
	#################
	
	#default strategy for login	 
	def authenticate_default(self, username, password):
		'''
		@params username: (str) username to check in db
		@params password: (str) password to check against
		@return status: (bool) return True or False indicating succesful login or not
		'''
		#search for the user in mongoDb collection
		user_record = self.users.find({"username":username})
		# if a user is found
		if user_record.count() > 0:
			print('default auth user was found')
			req_pass = list(user_record)[0]["password"]
			# if password matches
			if self.digest(password) == req_pass:
				#successful login
				return True 
			else:
				#failed login
				return False
		else:
			# user does not exist
			return False	
			
	def register_default(self, username, password, payload, role='user'):
		'''
		@params username: (str) username to add in user db colelction 
		@params password: (str) current passsword to add in db collection
		@params payload: (dict) optional payload for the user
		@return ret: (str) new user hash or err message 
		'''
		try:
			#prepare password digest
			password_digest = self.digest(password)
			#create body
			body = {"username": username, "password": password_digest, "origin":str(get_mac()), "role": role}
			#append other value if present
			if payload:
				body.update(payload)
			#create new user
			record_created = self.users.insert(body)
			#return new user hash
			ret = record_created		
		except Exception as e:
			print(e)
			# Error while trying to create the resource
			ret = e		
		return ret		

	### Decorator ###
	#################
		
	#decorator for secured page
	def secure(self, f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			# if not loggedIN redirect to login
			if not self.is_logged_in():
				return redirect(url_for(self.redirect, next=request.url))
			else:
				return f(*args, **kwargs)
		return decorated_function		

class User(object):
	'''
	class to create user object
	'''
	def __init__(self):
		self.origin = ""
		self.is_logged_in: False
		self.user ={}
