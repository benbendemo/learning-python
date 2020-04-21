# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 10:20:54 2018
"""

PGMname = 'PGM:python_learning_flask_cors_momentjs'

from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def home():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
