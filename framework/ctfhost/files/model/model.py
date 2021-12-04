from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Float, Boolean, update, func, desc, or_, create_engine
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import traceback
from time import sleep


from modules import config
from modules.frameworklogging import log

base = declarative_base()

engine = create_engine('postgresql+psycopg2://%s:%s@%s/ctf_framework' % (config.get_database_user(), config.get_database_password(), config.get_database_url()), pool_pre_ping=True, pool_size=50)
Session = None



def startup():
	global Session
	global engine
	error = True

	while error:
		try:
			engine.connect()
			session_factory = sessionmaker(expire_on_commit=False)
			session_factory.configure(bind=engine)
			Session = scoped_session(session_factory)
			error = False
		except:
			log.error("Database connect error: %s", traceback.format_exc())
			log.info("Retrying database connection in 3 seconds.")
			sleep(3)

class Team(base):
	"""
	Model of table team
	"""

	__tablename__ = "teams"

	id = Column(Integer, primary_key=True)
	name = Column(String(256))
	address = Column(String(256))
	score = Column(Integer(), default = 0)
	flags = relationship('Flag', back_populates='teams')
	flag_submissions = relationship('FlagSubmission', back_populates='teams')

class Flag(base):
	"""
	Model of table flag
	"""
	__tablename__ = 'flags'

	#PK
	id = Column(Integer, primary_key=True)
	#FK
	team_id = Column(Integer, ForeignKey('teams.id'))
	teams = relationship('Team', back_populates='flags')

	flag_content = Column(String(256)) # the flag
	flag_submissions = relationship('FlagSubmission', back_populates='flags')

class FlagSubmission(base):
	"""
	Model of table flagsubmission
	"""
	__tablename__ = 'flag_submissions'

	#PK
	id = Column(Integer, primary_key=True)
	#FK
	flag_id = Column(Integer, ForeignKey('flags.id'))
	flags = relationship('Flag', back_populates='flag_submissions')

	team_id = Column(Integer, ForeignKey('teams.id'))
	teams = relationship('Team', back_populates='flag_submissions')

def get_flag_submission_by_flag_id_team_id(session, flag_id, team_id):
	"""
	Returns a list of flagsubmissions objects by its flag id and team id.
	"""
	return session.query(FlagSubmission).filter(FlagSubmission.team_id == team_id).filter(FlagSubmission.flag_id == flag_id).all()


def submit_flag(session, flag_id, team_id):
	"""
	Saves a flagsubmission object.
	Returns True if the transaction succeeded else false.
	"""
	try:
		session.add(FlagSubmission(flag_id=flag_id, team_id=team_id))
		session.commit()
		return True
	except:
		session.rollback()
	return False

def create_database():
	"""
	Creates a database and all its models with the given engine.
	"""
	try:
		base.metadata.create_all(bind=engine)
	except:
		log.error("Database error %s" % traceback.format_exc())

def remove_session():
	"""
	Removes a session of the scoped_session object.
	"""
	try:
		Session.remove()
	except:
		log.error("Database error %s" % traceback.format_exc())

def open_session():
	"""
	Removes a session of the scoped_session object.
	Returns a session object.
	"""
	try:
		return Session()
	except:
		log.error("Database error %s" % traceback.format_exc())
		return None

def commit(session):
	"""
	Commits uncommited transaction of the session.
	Returns True if the commit succeeded.
	"""
	try:
		session.commit()
		return True
	except:
		session.rollback()
	return False

def add_team(session, name, address):
	"""
	Add a team to the database.
	Returns True if the transaction succeeded else false.
	"""
	try:

		session.add(Team(name=name, address=address))
		session.commit()
		return True
	except:
		session.rollback()
	return False

def get_team_by_name(session, name):
	"""
	Get team objects by name.
	Return a list of teams with this name. Should only be one team object.
	"""
	return session.query(Team).filter(Team.name==name).all()

def get_team_by_id(session, id):
	"""
	Get team objects by id.
	Return a list of team objects with this id. Should only be one team object.
	"""
	return session.query(Team).filter(Team.id==id).all()

def get_teams(session):
	"""
	Get all team objects.
	Return a list of all team objects.	
	"""
	return session.query(Team).all()


def get_flag_by_content(session, content):
	"""
	Returns a list of flag objects by its content. Should only be one flag object.
	"""
	return session.query(Flag).filter(Flag.flag_content==content).all()

def get_flags_by_team_id(session, team_id):
	"""
	Returns a list of flag objects by its team id. Should only be one flag object.
	"""
	return session.query(Flag).filter(Flag.team_id==team_id).all()

def save_flag(session, team_id, flag):
	"""
	Saves a flag object.
	Returns True if the transaction succeeded else false.
	"""
	try:
		session.add(Flag(team_id=team_id, flag_content=flag))
		session.commit()
		return True
	except:
		session.rollback()
	return False