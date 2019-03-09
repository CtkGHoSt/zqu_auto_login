from flask import Flask, render_template, request, url_for, redirect

app = Flask('logout')


@app.route('/result', methods=['POST'])
def test_form_func():
    print(request.form['number'])
    print(request.form['token'])
    return redirect(url_for('main'))


@app.route('/')
def main():
    return render_template('logout.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001,debug=False)

# %tb
