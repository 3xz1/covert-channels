from ubuntu:18.04
RUN apt-get update; apt-get install -y python python-pip python-dev 
#python3 python3-pip python3-dev
RUN pip install configparser sqlalchemy psycopg2-binary requests flask Flask-BasicAuth user_agent flask_sqlalchemy scapy
#RUN pip3 install configparser sqlalchemy psycopg2-binary requests flask 

RUN groupadd ctf && useradd -m -g ctf ctf

# add files
ADD files /home/ctf/

# set permissions
RUN chown -R ctf:ctf /home/ctf
RUN chmod 750 /home/ctf/scoreboard.py

# wait for database to start
CMD /home/ctf/scoreboard.py
