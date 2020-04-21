# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 10:20:54 2018
"""

PGMname = 'PGM:python_learning_flask_cors'

from flask import Flask
from flask import request
from flask import render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime

app = Flask(__name__)
moment = Moment(app)
bootstrap = Bootstrap(app)

@app.route('/',methods=['GET','POST'])
def home():
    current_time=datetime.utcnow()
    return render_template('index.html', current_time=current_time)

@app.route('/signin',methods=['GET'])
def signin_form():
    return '''
        <form action='/signin' method='post'>
        <p><input name='username'></p>
        <p><input name='password' type='password'></p>
        <p><button type='submit'>Sign In</button></p>
        </form>
        '''

@app.route('/signin',methods=['post'])
def signin():
    # 需要从request对象读取表单内容
    if request.form['username'] == 'admin' and \
        request.form['password'] == 'password':
        return '<h3>Hello,admin!</h3>'

    return '<h3>Bad username or password.</h3>'


@app.route('/user/<name>')
def user(name):
    return render_template('user.html',name=name)


if __name__ == '__main__':

    app.run(debug=True, port=8000)
