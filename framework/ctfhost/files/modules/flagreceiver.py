#!/bin/python
from modules.frameworklogging import log
from modules import config
from time import sleep
from model import model
from modules.state import STATE
import traceback
import threading
import SocketServer
import datetime
import socket
import errno

# import STATE codes

def validate(connection, flag_content, team_id):
	"""
	Validates a submitted flag of a client.
	If the flag is accepted it is saved to the database.
	Sends a response via socket to the client.
	"""
	session = model.open_session()

	try:
		flag = model.get_flag_by_content(session, flag_content)
		model.remove_session()
		if(len(flag) ==1):
			flag = flag[0]
			session = model.open_session()
			flag_submission = model.get_flag_submission_by_flag_id_team_id(session, flag.id, team_id)
			if flag.team_id == team_id:
				connection.sendall('this is your own flag\n')
			elif(len(flag_submission) == 0):
				if(model.submit_flag(session, flag.id, team_id)):
					team = model.get_team_by_id(session, team_id)
					if(len(team) ==1):
						team[0].score = team[0]	.score + 25
						session.commit()
						connection.sendall('accepted\n')
					else:
						connection.sendall('try again later')
			elif len(flag_submission) >= 1:
				connection.sendall('already submitted\n')
			else:
				connection.sendall("No such Flag")
		else:
			connection.sendall('no such flag\n')
	except socket.error as e:
		if e.errno != errno.EPIPE and e.errno != errno.ECONNRESET: # pass	 if BrokenPipe
				log.error(traceback.format_exc())	
	except Exception:	
			log.error(traceback.format_exc())
	model.remove_session()

	return


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
	"""
	Handle client in threads.
	"""
	def handle(self):
		"""
		Handle a client within a loop. Simple authentication with the team name.
		"""
		# open database session
		session = model.open_session()

		connection = self.request
		try:	
			connection.sendall('Team name?\n')
			team_name = connection.recv(1024).strip('\n')

			# get team
			team = model.get_team_by_name(session, team_name)
			model.remove_session()
			if len(team) == 1:
				connection.sendall('Hello ' + team_name + '\n')
				while True:
					data = connection.recv(1024).strip('\n')
					validate(connection, data, team[0].id)
			else:
				connection.sendall('Invalid team name.\n')
				connection.close()
		except socket.error as e:
			if e.errno != errno.EPIPE and e.errno != errno.ECONNRESET: # pass if BrokenPipe
				log.error(traceback.format_exc())
		except Exception:
			log.error(traceback.format_exc())
		model.remove_session()

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	pass

def serve():
	"""
	Startup function of the flagservice which is called by the interface.
	Serves forever.
	"""
	# start threaded tcp server
	while 1:
		try:
			server = ThreadedTCPServer(("0.0.0.0", 1337), ThreadedTCPRequestHandler)
			log.info('Starting flagreceiver...')
			server.serve_forever()
		except SystemExit:
			log.info('Shutting down flagreceiver...')
			break
		except:
			log.error('Startup of flagreceiver failed. Waiting for %s seconds. Err: %s' % ("5",traceback.format_exc()))
			sleep(5)