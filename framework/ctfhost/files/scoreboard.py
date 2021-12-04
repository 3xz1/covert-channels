#!//usr/bin/python
from flask import render_template, redirect, Flask, request, session, g, redirect, url_for, abort, flash, Response
from flask_basicauth import BasicAuth

from collections import OrderedDict
from operator import itemgetter, attrgetter
from jinja2 import Template
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timedelta
import time
from modules import config
import re
from model import model
from modules.frameworklogging import log
from os import urandom
from hashlib import sha1
from modules import flagreceiver
from modules import sniffer
import multiprocessing
from time import sleep


base_path = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=base_path+"/scoreboard/templates/")	


# init flask
app.config["SECRET_KEY"] = os.urandom(32)


# basic auth
basic_auth = BasicAuth(app)
app.config['BASIC_AUTH_USERNAME'] = config.get_basic_auth_username()
app.config['BASIC_AUTH_PASSWORD'] = config.get_basic_auth_password() 

# utils
active_processes = {'flagreceiver': None, "sniffer":None}
available_modules = {'flagreceiver': flagreceiver.serve, "sniffer": sniffer.serve}

def validate_module(module_name):
	"""
	Validates a module name and verifes if it exists.
	Returns True if the input is a valid module name.
	"""
	if module_name in available_modules:
		return True
	return False

def is_ip_address(ip_address):
	"""
	Validates a ip address with a regex.
	Returns True if the input is a valid ip address.
	"""
	res = re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip_address)
	if res:
		return True
	return False

@app.route('/')
def show_all():
	session = model.open_session()
	teams = model.get_teams(session)
	model.remove_session()
	return render_template('main.html', teams=teams)

@app.route('/flagreceiver/')
def show_flagreceiver():
	flag_receiver_state = 'Inactive'
	if active_processes['flagreceiver'] is not None and active_processes['flagreceiver'].is_alive():
		flag_receiver_state = 'Active'
	sniffer_state = 'Inactive'
	if active_processes['sniffer'] is not None and active_processes['sniffer'].is_alive():
		sniffer_state = 'Active'

	return render_template("show_main.html",flag_receiver_state=flag_receiver_state, sniffer_state=sniffer_state)

@app.route('/rules')
def show_rules():
	return render_template('layout.html')


@app.route('/teams/<team_id>/flags/')
@basic_auth.required
def show_flags(team_id):
	""" Args: team_id (int)
	Flask route to see all flags
	"""
	session = model.open_session()
	flags = model.get_flags_by_team_id(session, team_id)
	return render_template("show_flags.html", flags=flags)
	#else:
	#	flash("Not a valid team id.", "danger")
	#	model.remove_session()
	#	return redirect(url_for("show_teams"))
	
	#return render_template("show_flags", flags=flags)


@app.route('/teams/add/', methods=["POST", "GET"])
@basic_auth.required
def add_team():
	if request.method == "GET":
		return render_template("add_team.html")

	if not is_ip_address(request.form["team_address"]):
		flash("Not a valid IP address.", "danger")
		return render_template("add_team.html")

	session = model.open_session()

	#check if team already exists
	session = model.open_session()
	team_temp = model.get_team_by_name(session, request.form["team_name"])	

	if(len(team_temp) == 1):
		flash("Name already exists.", "danger")
		model.remove_session()
		return redirect(url_for("show_teams"))


	if model.add_team(session, request.form["team_name"], request.form["team_address"]) == False:
		model.remove_session()
		flash("Error occured.", "danger")
	session.commit()
	return redirect(url_for("show_teams"))

@app.route('/teams/<team_id>/add/flags/')
@basic_auth.required
def add_flags(team_id):
	session = model.open_session()
	team = model.get_team_by_id(session, team_id)
	if(len(team) == 1):
		generator = sha1()
		team = team[0]
		for i in range(0,10):
			generator.update((str(team.id) + str(team.address)+ str(urandom(64))).encode('utf-8')) # seed from /dev/urandom
			flag_content = "hso_"+ generator.hexdigest() + "_"
			model.save_flag(session, team.id, flag_content)
			session.commit()
	else:
		return redirect(url_for("show_rules"))
	return redirect(url_for("add_team"))

@app.route("/teams/<team_id>/edit/", methods=["POST", "GET"])
@basic_auth.required
def edit_team(team_id):
	"""
	Args: team_id (int)
	Flask route to edit a team.
	"""
	session = model.open_session()
	team = model.get_team_by_id(session, team_id)

	if len(team) != 1:
		flash("Not a valid team id.", "danger")
		model.remove_session()
		return redirect(url_for("show_teams"))

	team = team[0]

	if request.method == "GET":
		return render_template("edit_team.html", team=team)

	if not is_ip_address(request.form["team_address"]):
		flash("Not a valid IP address.", "danger")
		model.remove_session()
		return render_template("add_team.html")

	if team.name != request.form["team_name"]:
		#check if team already exists
		team_temp = model.get_team_by_name(session, request.form["team_name"])

		if len(team_temp) == 1:
			flash("Name already exists.", "danger")
			model.remove_session()
			return redirect(url_for("show_teams"))

	# save edited team object
	team.name = request.form["team_name"]
	team.address = request.form["team_address"]
	if not model.commit(session):
		flash("Commit error.", "danger")
	model.remove_session()
	return redirect(url_for("show_teams"))

@app.route("/teams/<team_id>/delete/")
@basic_auth.required
def delete_team(team_id):
	"""
	Args: team_id (int)
	Flask route to delete a team.
	"""
	session = model.open_session()
	team = model.get_team_by_id(session, team_id)

	if len(team) != 1:
		flash("Not a valid team id.", "danger")
		model.remove_session()
		return redirect(url_for("show_teams"))

	team = team[0]
	team_name = team.name
	session.delete(team)
	if not model.commit(session):
		flash("Commit error.", "danger")
	else:
		flash("Deleted %s" % str(team_name), "info")
	model.remove_session()
	return redirect(url_for("show_teams"))

@app.route("/teams/")
@basic_auth.required
def show_teams():
	"""
	Args: None
	Flask route to show a teams.
	"""
	session = model.open_session()
	teams = model.get_teams(session)
	model.remove_session()
	return render_template("show_teams.html", teams=teams, count=len(teams))

@app.route("/module/<module_name>/start")
@basic_auth.required
def start_module(module_name):
	"""
	Args: module_name (String)
	Flask route to start a threaded module.
	"""
	if validate_module(module_name):
		if active_processes[module_name] is not None and active_processes[module_name].is_alive():
			flash('%s already running.' % module_name, "danger")
			return redirect("/")
		log.debug('starting %s ...' % module_name)
		active_processes[module_name] = multiprocessing.Process(target=available_modules[module_name])
		active_processes[module_name].start()
		flash('%s started.' % module_name.title(), "info")
	else:
		flash('Wrong module name. Cannot start %s.' % module_name.title(), "danger")
	sleep(2)
	return redirect("/")

@app.route("/module/<module_name>/stop")
@basic_auth.required
def stop_module(module_name):
	"""
	Args: module_name (String)
	Flask route to stop a threaded module.
	"""
	if validate_module(module_name):
		if active_processes[module_name] is None or not active_processes[module_name].is_alive():
			flash('%s is not running.' % module_name, "danger")
			return redirect("/")
		log.debug('stopping %s ...' % module_name)
		active_processes[module_name].terminate()
		active_processes[module_name] = None
		flash('%s stopped.' % module_name.title(), "info")
	else:
		flash('Wrong module name. Cannot stop %s.' % module_name, "danger")
	return redirect("/")

@app.route("/module/<module_name>/restart")
@basic_auth.required


def restart_module(module_name):
	"""
	Args: module_name (String)
	Flask route to restart a threaded module.
	"""
	if validate_module(module_name):
		if active_processes[module_name] is None or not active_processes[module_name].is_alive():
			flash('%s is not running.' % module_name, "danger")
			return redirect("/")
		log.debug('restarting %s ...' % module_name)
		stop_module(module_name)
		start_module(module_name)
	else:
		flash('Wrong module name. Cannot restart %s.' % module_name.title(), "danger")
	return redirect("/")


if __name__=='__main__':
	"""
	Entry point of the framework.
	Start web interface and create a database.
	"""
	log.debug('Create database')
	model.startup()
	model.create_database()
	app.run("0.0.0.0", 80, True)
