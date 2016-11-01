import os
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from scraper import * 
import os

PROJECT_DIR = os.getcwd()


f = PROJECT_DIR + '/static/data/health_data.html'

app = Flask(__name__)

@app.route("/")
def home():

    return render_template('index.html')

if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)