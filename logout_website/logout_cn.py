from model import *

from flask import Flask, render_template, request, url_for, redirect, abort

app = Flask('logout')


@app.route('/result', methods=['POST'])
def test_form_func():
    print(request.form['number'])
    print(request.form['token'])
    return redirect(url_for('main'))


@app.route('/')
def main():
    return render_template('logout.html')

@app.route('/logout', methods=['GET', 'POST', 'DELETE'])
def logout_api():
    userid = request.values.get('userid')
    token = request.values.get('token')
    if request.headers.getlist("X-Forwarded-For"):
       ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
       ip = request.remote_addr
    if request.method == 'GET':
        try:
            logout_comment.get(userid=userid, token=token)
            return ''
        except DoesNotExist:
            abort(404)
    elif request.method == 'POST':
        if userid == '' or token == '':
            return '<h1>ERROR!</h1>'
        if len(logout_comment.select().where(logout_comment.ip == ip)) >= 3:
            return abort(403)
        try:
            a = logout_comment.get(userid=userid)
            a.token = token
            a.ip = ip
            a.save()
        except DoesNotExist:
            logout_comment.create(userid=userid, token=token, ip=ip)
        return '<h1>REMOTE LOGOUT SUCCESS!</h1>'
    elif request.method == 'DELETE':
        try:
            del_item = logout_comment.get(userid=userid, token=token)
            del_item.delete_instance()
            return ''
        except DoesNotExist:
            abort(404)

if __name__ == '__main__':
    app.run(host='localhost',port=5001,debug=False)

# %tb
