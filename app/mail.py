from flask.ext.mail import Message
from app import mail
from flask import render_template
from config import ADMIN

def send_email(sender, recipients, subject, message=None):
	msg = Message(subject, sender=sender, recipients=recipients)
	msg.html = message
	mail.send(msg)

def follower_email(followed, follower):
	if follower.nickname:
		send_email(ADMIN[0],
			[followed.email],
			"%s is following you" % follower.nickname,
			render_template('mail_temp.html',
				user = followed, follower=follower)
			)
	else:
		send_email(ADMIN[0],
			[followed.email],
			"%s is following you" % follower.email,
			render_template('mail_temp.html',
				user = followed, follower=follower)
			)