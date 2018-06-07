from flask import render_template, request, redirect, flash, url_for
from app import app, db
from forms import LoginForm, AdminForm
from app.models import User
import datetime
import socket
import pygal
from pygal.style import NeonStyle
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

#limiter config settings to prevent abuse
limiter=Limiter(
	app,
	key_func=get_remote_address,
	default_limits=["1 per 15 minutes"]
	)

@app.route('/', methods=['GET', 'POST'])

#this is our home page
@app.route('/index', methods=['GET', 'POST'])
@limiter.limit("1 per minute 30 minutes") #prevents abuse / one entry per machine ever 30 mins
def index():
	form = LoginForm()
	if form.validate_on_submit():
		#this is where we record the hostname / username and date for db
		hostname = socket.gethostbyaddr(request.remote_addr)[0]
		username = form.username.data.lower()
		date = datetime.datetime.utcnow()
		#prevent empty entries
		if len(username) <= 0:
			return redirect('/')

		#admin functions
		#this makes it easy to delete an entry. feel free to add your own
		if username.split("+")[0] == "delete":
			username = username.split("+")[1]
			User.query.filter_by(username=username).delete()
			db.session.commit()
			return redirect('http://www.google.com')

		#Check to see if our user already exists
		exists = User.query.filter(User.username == username).first()
		print(exists)
		if exists:
			exists.score += 1
			db.session.commit()
		else:
			score = 1
			data_block = User(username=username, hostname=hostname, score=score, date=date)
			db.session.add(data_block)
			db.session.commit()
		return redirect('/stats')
	return render_template('index.html', title='Welcome to Geocities', form=form)

#our scoreboard! #top 10 hackers in order descending
@app.route('/stats', methods=['GET'])
@limiter.limit("1 per second", error_message="omg chill!") #this setting is important. when limit redirects to /stats, it won't limit it as well.
def stats():
	top10 = db.session.query(User.username, User.score).order_by(User.score.desc()).limit(10).all()
	hackers = []
	user_scores = []
	#we have to divide the tuple into two lists to display the data
	for i in top10:
		hackers.append(i[0])
		user_scores.append(i[1])

	#here is the chart
	line_chart = pygal.Bar(rounded_bars=8, tooltip_border_radius=10, style=NeonStyle,)
	line_chart.title = 'top hax0rs'
	line_chart.x_labels = hackers
	chart_data = user_scores
	line_chart.add('# pwned', chart_data)
	chart = line_chart.render_data_uri()
	return render_template('stats.html', title='Stats', chart=chart)

#readme
@app.route('/readme', methods=['GET'])
@limiter.limit("1 per second", error_message="omg chill!")
def readme():
	return render_template('readme.html', title='readme.txt')

#sets the redirect for rate limiting back to the scoreboard
@app.errorhandler(429)
def ratelimit_handler(e):
	return redirect('/stats')
