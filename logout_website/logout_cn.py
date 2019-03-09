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

@app.route('/logout', methods=['GET', 'POST'])
def logout_api():
    userid = request.values.get('userid')
    token = request.values.get('token')
    if request.method == 'GET':
        if userid == '201624131440' and token == 'test123':
            return ''
        else:
            abort(404)
    elif request.method == 'POST':
        return '<h1>REMOTE LOGOUT SUCCESS!</h1>'

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001,debug=False)

# %tb
