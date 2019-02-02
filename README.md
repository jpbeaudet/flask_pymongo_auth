
# flask_pymongo_auth
Flask micro-weight authentication module for flask and mongoDb inspired from passport.js and express sessions

I welcome contributors to add new strategy( login with: facebook, linkedin, google, github) or to propose ameliorations. 

NOT READY FOR PRODUCTION !!!!! The module works very fine but must be packages and test must be built

### Example usage:
	'''
	#!/usr/bin/env python
	"""
	Example usage of flask_mongo_auth
	Author : Jean-Philippe Beaudet
	version : 1.0.0

	# imports 
	import os
	from flask import Flask, request, json, url_for, render_template, redirect
	from config import client #pymongo client
	from auth import Auth


	# Select the database
	db = client.restfulapi
	# Select the collection
	# - user collection
	users = db.users

	#set Auth class by passing the user db collection
	a = Auth(users)
    
	#Create and configure an instance of the Flask application.
	def create_app(test_config=None):
	    app = Flask(__name__, instance_relative_config=True)
	    app.secret_key = 'any random string'
	    app.debug = True
	    #set auth object
	    if test_config is None:
	        # load the instance config, if it exists, when not testing
	        app.config.from_pyfile('config.py', silent=True)
	    else:
	        # load the test config if passed in
	        app.config.update(test_config)
	    # ensure the instance folder exists
	    try:
	        os.makedirs(app.instance_path)
	    except OSError:
	        pass
        
	    #routes 
	    #######################################################	
    
	    #homepage
	    @app.route('/')
	    def index():
	        return redirect('/login')
        
	    @app.route('/logout', methods=['GET'])
	    def logout():
	        return a.logout()
        
	    @app.route('/test', methods=['GET'])
	    @a.secure
	    def test():
	        print("test origin: "+a.current_user().origin)
	        return "success", 200

	    @app.route('/test2', methods=['GET'])
	    @a.has_role(roles =['user'])
	    def test2():
	        print("test origin: "+a.current_user().origin)
	        return "success", 200
		  
	    @app.route('/login', methods=['GET', 'POST'])
	    def login():
	        if request.method == 'POST':
	            username = request.form.get("username")
	            password = request.form.get("password")
	            def cb(ret): 
	                print("results: "+str(ret))
	                data = {"title": "Example | Login"}
	                return render_template('login.html', data=data), 200
	            a.authenticate(username, password, cb)
	            return "", 200
	        else:
	            data = {"title": "Example | Login"}
	            return render_template('login.html', data=data), 200
   
	    # register page
	    @app.route('/register', methods=['GET', 'POST'])
	    def register():
	        data = {"title": "Example | Register"}
	        if request.method == 'POST':
	            """
	            Function to create new users.
	            """
	            # extract form data
	            username = request.form.get("username")
	            password = request.form.get("password")
	            # define callback
	            def cb(ret): 
	                print("results: "+str(ret))
	                data = {"title": "Example | Register"}
	                return render_template('register.html', data=data), 200
	            # use register function
	            a.register(username, password, cb)
	            return "", 200
	        else:
	            return render_template('register.html', data=data), 200  
    
	    # error handler for non-existing URL's
	    @app.errorhandler(404)
	    def page_not_found(e):
			# will return to login, could add error page but dont seem necessary
	        return redirect('/login')
    
	    # Return app object (launch app)
	    #######################################################		
	    return app
    


   



#### Dependencies
python 3 must be installed, virtual env is recommended

* flask
* pymongo 
* functools
* hashlib
* binascii
* uuid

#### Author : Jean-Philippe Beaudet
#### Version : 0.0.1
#### copyrigths jpbeaudet@vsekur.com


