#! /usr/bin/python
# -*- coding:utf-8 -*-


import json
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
import logging
from logging.handlers import RotatingFileHandler
from configobj import ConfigObj
from jinja2 import Environment, FileSystemLoader
import requests

CONFIG = ConfigObj("config.ini")
# Logger configuration:
# General log configuration
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)
FORMATTER = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
# Rotate log file configuration:  Rotate when size = 1mo. Keep only 1 backup
FILE_HANDLER = RotatingFileHandler('plexWeeklyRecap.log', 'a', 1000000, 1)
FILE_HANDLER.setLevel(logging.DEBUG)
FILE_HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(FILE_HANDLER)
# Log stream configuration
STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setLevel(logging.DEBUG)
LOGGER.addHandler(STREAM_HANDLER)

# Plex configuration
PLEXSERVERIP = CONFIG['Plex']['ServerIP']
PLEXSERVERPORT = CONFIG['Plex']['ServerPort']
PLEXTOKEN = CONFIG['Plex']['Token']
PLEXSERVERID = CONFIG['Plex']['ServerID']

# Mail configuration
MAILRECIPIENTS = CONFIG['Mail']['Recipients']
MAILSENDER = CONFIG['Mail']['Sender']
MAILSUBJECT = CONFIG['Mail']['Subject']
SMTPSERVER = CONFIG['Mail']['SmtpServer']
SMTPPORT = CONFIG['Mail']['SmtpPort']
SMTPLOGIN = CONFIG['Mail']['Login']
SMTPPASSWORD = CONFIG['Mail']['Password']

# Mail template Configuration
ENV = Environment(
    loader=FileSystemLoader('./templates')
)
JINJATEMPLATE = ENV.get_template('template.html')


class Plex:
    def __init__(self, plexServerIP, plexServerPort, plexToken, plexServerID):
        self.server_ip = plexServerIP
        self.server_port = plexServerPort
        self.token = plexToken
        self.url = 'http://'+self.server_ip+':'+self.server_port
        self.server_id = plexServerID
        self.movie_count = ""
        self.movie_list = []

    # Connect to Plex Media Server and grab all the movie added from "period" (period = seconds)
    def get_new_movies(self, period):
        LOGGER.debug("Launching getNewMovies")
        # get actual time and subtract period parameter
        added_from = round(time.time()-period)
        # Build the query URL
        url = (self.url +
               '/library/sections/1/all?X-Plex-Token=' +
               self.token + '&addedAt%3E=' + str(added_from)
              )
        # Try GET request
        try:
            req = requests.get(url, headers={'Accept': 'application/json'})
            req.raise_for_status()
        # If RequestException catched, log error and exit program
        except requests.exceptions.RequestException as err:
            LOGGER.error("There is a problem with getNewMovies request : %s \nExiting...", err)
            sys.exit(1)
        # Decoding request response as JSON
        response = json.loads(req.text)

        # Build thumb & key URL and rewrite over for less complexity
        for i in response["MediaContainer"]["Metadata"]:
            i["thumb"] = (self.url + i["thumb"] + '?X-Plex-Token=' + self.token)
            i["key"] = (self.url + "/web/index.html#!/server/" + self.server_id + "/details?key=" + i["key"])

        # Populate MovieCount attribute counting items in JSON
        self.movie_count = len(response["MediaContainer"]["Metadata"])
        # Push the modified Metadatas to movieList attribute
        self.movie_list = response["MediaContainer"]["Metadata"]
        LOGGER.debug("getNewMovies finished")


class Smtp:
    def __init__(self, smtpServer, smtpPort, login, password):
        self.smtp_server = smtpServer
        self.smtp_port = smtpPort
        self.login = login
        self.password = password

    # Send newsletter email with generated jinja2 template
    def send_email(self, jinja_render, subject, sender, recipients):
        LOGGER.debug("Launching sendEmail")
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        # Check if "recipients" is a list of multiple recipients or a string with only one recipient
        if isinstance(recipients, list):
            msg['To'] = ", ".join(recipients)
        else:
            msg['To'] = recipients
        # Attach the jinja template
        msg.attach(MIMEText(jinja_render, 'html'))
        # Create SMTP instance
        smtp = smtplib.SMTP(self.smtp_server + ":" + self.smtp_port)
        # Try to connect and send the email
        try:
            smtp.starttls()
            smtp.login(self.login, self.password)
            smtp.sendmail(sender, recipients, msg.as_string())
        # if SMTPException catched, log error and exit program
        except smtplib.SMTPException as err:
            LOGGER.error("There is a problem with sendEmail : %s \nExiting...", err)
            sys.exit(1)
        LOGGER.info("Mail sended to %s", msg['To'])
        smtp.quit()
        LOGGER.debug("sendEmail finished")


def main():
    LOGGER.info("plexWeeklyRecap started")
    # instantiate Plex media server class
    plex = Plex(PLEXSERVERIP, PLEXSERVERPORT, PLEXTOKEN, PLEXSERVERID)
    # instantiate SMTP class
    email = Smtp(SMTPSERVER, SMTPPORT, SMTPLOGIN, SMTPPASSWORD)
    # launch getNewMovies for the last 7 days (days*hours*minutes*seconds)
    plex.get_new_movies(7*24*60*60)
    # render with jinja2 template
    jinja_render = JINJATEMPLATE.render(movieList=plex.movie_list, total=plex.movie_count)
    # Send the email
    email.send_email(jinja_render, MAILSUBJECT, MAILSENDER, MAILRECIPIENTS)
    LOGGER.info("plexWeeklyRecap finished succesfully")


if __name__ == "__main__":
    main()
