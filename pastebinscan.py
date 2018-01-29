########################################
########################################
##         							  ##
##         Pastebin Search            ##
##                                    ##
##            count_zero              ##
##									  ## 
########################################
########################################

from flask import Flask, render_template, flash, redirect, render_template, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId 
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired
import requests
import re
from re import split
from google import search
import os

#Fill in your pastebin.com details!
parameters = {
	"api_dev_key": "", 
	"api_user_name": "", 
	"api_user_password": ""
	}

WTF_CSRF_ENABLED = False

class SearchForm(Form):
	searchterm = StringField('searchterm', validators =[DataRequired()])

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'what-a-coup'

def googleSearch(address, i):
	search_results = []
	for url in search(address, stop=10):
		pieces = re.split('/', url)
		search_results.append(pieces[3])
	pastebinScraper(search_results, i)

def pastebinScraper(results,question):
	for i in results:
		scrapeData = requests.get("https://pastebin.com/api_scrape_item.php?i=%s" % i, params = parameters)
		result = mongo.db.pastebinDB.insert_one(
			{
				"searchterm": question,
				"pastebinID": i,
				"data": scrapeData.text
			}
		)

####### INITIALISE MY FLASK APPLICATION #######
app = Flask(__name__)
app.config.from_object(Config)
mongo = PyMongo(app)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	form = SearchForm()
	if form.validate_on_submit():
		searchform = form.searchterm.data + ' site:pastebin.com'
		googleSearch(searchform, form.searchterm.data)
		flash('You have just searched for: "%s"' % (form.searchterm.data))
		return redirect('/index')
	return render_template('search.html', title='Search form', form=form)

@app.route('/viewall')
def viewall():
	searchterm = mongo.db.pastebinDB.distinct("searchterm")
	counting = []
	for x in searchterm:
		counting.append(mongo.db.pastebinDB.find({"searchterm": x}).count())
	viewall = dict(zip(searchterm, counting))
	return render_template('viewall.html', title='View all', viewall=viewall, allsearch=True)

@app.route('/deleteterm/<searchterm>')
def deleteterm(searchterm):
	mongo.db.pastebinDB.remove({'searchterm': searchterm})
	search = mongo.db.pastebinDB.distinct("searchterm")
	counting = []
	for x in search:
		counting.append(mongo.db.pastebinDB.find({"searchterm": x}).count())
	viewall = dict(zip(search, counting))
	return render_template('viewall.html', title='View all', viewall=viewall, allsearch=True)

@app.route('/deletepaste/<listsearch>/<searchterm>')
def deletepaste(searchterm, listsearch):
	mongo.db.pastebinDB.remove({'pastebinID': searchterm})
	search = mongo.db.pastebinDB.find({'searchterm': listsearch})
	viewall = []
	for x in search:
		viewall.append(x)
	return render_template('viewall.html', title='View all', viewall=viewall, listsearch=True)

@app.route('/listsearch/<listsearch>')
def listsearch(listsearch):
	# I want viewall to be [(pastebinid, data)]
	search = mongo.db.pastebinDB.find({'searchterm': listsearch})
	viewall = []
	for x in search:
		viewall.append(x)
	return render_template('viewall.html', title='View all', viewall=viewall, listsearch=True)

@app.route('/listpaste/<listsearch>')
def listpaste(listsearch):
	# I want viewall to be [(pastebinid, data)]
	search = mongo.db.pastebinDB.find({'pastebinID': listsearch})
	return render_template('viewall.html', title='View all', viewall=search, pastesearch=True)

@app.route('/about')
def about():
	form = 'Pastebin search'
	return render_template('about.html', title='About Pastebin Search')

if __name__ == '__main__':
	app.run(debug=True)

