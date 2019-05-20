# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import re
import bcrypt
from datetime import datetime

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\_\-\+\.]+\@[a-zA-Z0-9\_\-\+\.]+\.[a-zA-Z]+$')

class UserManager(models.Manager):
	def register(self, postdata):
		m_first = postdata["first"]
		m_last = postdata["last"]
		m_username = postdata["username"]
		m_email = postdata["email"]
		m_dob = postdata["dob"]
		m_password = postdata["password"]
		m_confirm = postdata["confirm"]
		response = {
			"isValid": True,
			"errors": [],
			"user": None
		}
		#print(m_first, "first")
		if len(m_first) < 1:
			response["errors"].append("First Name is Required")
		elif len(m_first) < 2:
			response["errors"].append("First Name must be 2 characters or longer")

		#print(m_last, "last")
		if len(m_last) < 1:
			response["errors"].append("Last Name is Required")
		elif len(m_last) < 2:
			response["errors"].append("Last Name must be 2 characters or longer")

		#print(m_username, "username")
		if len(m_username) < 1:
			response["errors"].append("Username is Required")
		elif len(m_username) < 3:
			response["errors"].append("Username must be 3 characters or longer")

		#print(m_email, "email")
		if len(m_email) < 1:
			response["errors"].append("Email is Required")
		elif not EMAIL_REGEX.match(m_email):
			response["errors"].append("Invalid Email.")

		#print(m_dob, "dob")
		if len(m_dob) < 1:
			response["errors"].append("Date of Birth is Required")
		else:
			m_date = datetime.strptime(m_dob, '%Y-%m-%d')
			today = datetime.now()
			if m_date > today:
				response["errors"].append("Date of Birth must be in the past!")

		#print(m_password, "password")
		if len(m_password) < 1:
			response["errors"].append("Password is Required")
		elif len(m_password) < 8:
			response["errors"].append("Password must be 8 characters or longer")

		#print(m_confirm, "confirm")
		if len(m_confirm) < 1:
			response["errors"].append("Password Confirmation is Required")
		elif m_confirm != m_password:
			response["errors"].append("Password must match Password Confirmation.")

		if len(response["errors"]) > 0:
			response["isValid"] = False # why hit the database if they left out data?
		else: # now we can work with the database and find subtle errors
			list_of_users = User.objects.filter(email=m_email.lower())
			if len(list_of_users)>0:
				response["isValid"] = False
				response["errors"].append("Email exists already.")
			else:
				response["user"] = User.objects.create(
					first = m_first,
					last = m_last,
					username = m_username,
					email = m_email.lower(),
					dob = m_date,
					password = bcrypt.hashpw(m_password.encode(), bcrypt.gensalt())
				)
		return response
	# def register()

	def login(self, postdata):
		m_email = postdata["email"]
		m_password = postdata["password"]
		response = {
			"isValid": True,
			"errors": [],
			"user": None
		}
		#print(m_email, "email")
		if len(m_email) < 1:
			response["errors"].append("Email is Required")
		elif not EMAIL_REGEX.match(m_email):
			response["errors"].append("Invalid Email.")

		#print(m_password, "password")
		if len(m_password) < 1:
			response["errors"].append("Password is Required")
		elif len(m_password) < 8:
			response["errors"].append("Password must be 8 characters or longer")

		#---final walkthough---
		if len(response["errors"]) > 0:
			response["isValid"] = False # why hit the database if they left out data?
		else: # now we can work with the database and find subtle errors
			list_of_users = User.objects.filter(email=m_email.lower())
			if len(list_of_users) < 1:
				response["isValid"] = False
				############ CHANGE THIS BACK
				response["errors"].append("Incorrect Login. email") # user noexist
			else:
				hashed_pw = list_of_users[0].password
				if bcrypt.checkpw(m_password.encode(), hashed_pw.encode()):
					response["user"] = list_of_users[0]
				else:
					response["isValid"] = False
					############ CHANGE THIS BACK
					response["errors"].append("Incorrect Login. password") # password nomatch
		#---final walkthough---

		return response
	# def login
# class UserManager

class User(models.Model):
	first = models.CharField(max_length=255)
	last = models.CharField(max_length=255)
	username = models.CharField(max_length=255)
	email = models.CharField(max_length=255)
	dob = models.DateField()
	password = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = UserManager()
# class User()


class NoteManager(models.Manager):
	def sendNote(self, req, rec_id):
		if len(req.POST["content"]) > 0:
			note = Note.objects.create(
				content=req.POST["content"],
				sent_by_id=req.session["user_id"],
				received_by_id=rec_id
			)
			return note
		else:
			return "Message cannot be blank!"
	# def sendNote()
# class NoteManager()

class Note(models.Model):
	content = models.TextField(max_length=1023)
	sent_by = models.ForeignKey(User, related_name="sent_messages")
	received_by = models.ForeignKey(User, related_name="received_messages")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = NoteManager()
# class Note()