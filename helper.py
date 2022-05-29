from flask import redirect, render_template, request, session

def error(message):
    return render_template("error.html", message=message)

def success(message):
    return render_template("success.html", message=message)