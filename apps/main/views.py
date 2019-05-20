# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from .models import User, Note
from django.contrib import messages

def index(request):
	return render(request, "main/index.html")

def register(request):
	response = User.objects.register(request.POST)
	if response["isValid"]:
		request.session["user_id"] = response["user"].id
		return redirect("/home")
	else: # send errors to page
		for error_msg in response["errors"]:
			messages.error(request, error_msg)
		return redirect("/")

def login(request):
	response = User.objects.login(request.POST)
	if response["isValid"]:
		request.session["user_id"] = response["user"].id
		return redirect("/home")
	else: # send errors to page
		for error_msg in response["errors"]:
			messages.error(request, error_msg)
		return redirect("/")

def logout(request):
	request.session.clear()
	return redirect("/")
	
def home(request):  # this stuff could use a little more error checking...
	if "user_id" not in request.session:
		return redirect("/")
	else:
		context = {}
		context["user"]	= User.objects.filter(id=request.session["user_id"])[0]
		# note the following line eliminates the current user from the list
		context["users"] = User.objects.all().exclude(id=request.session["user_id"])
		# BUT... there is also code (that I left in) on the home.html page
		# that does the same thing
		context["your_messages"] = Note.objects.filter(received_by=request.session["user_id"])

		return render(request, "main/home.html", context)


def new_message(request, id):
	return render(request, "main/new_message.html", {"id": id})

def add_message(request, id):
	new_note = Note.objects.sendNote(request, id)
	if type(new_note) is unicode:
		messages.error(request, new_note)
		return redirect("/message/" + str(id))
	return redirect("/home")

def view_messages(request):
	context = {}
	context["your_messages"] = Note.objects.filter(received_by=request.session["user_id"])
	# Note.objects.filter(received_by=request.session["user_id"]).delete()
	# (too late now!)
	return render(request, "main/messages.html", context)

def done_reading_messages(request):
	Note.objects.filter(received_by=request.session["user_id"]).delete()
	return redirect ("/home")
