from flask import Flask, render_template, request
from waitress import serve

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    # return render_template('index.html')
    return "hello world"


@app.route('/help')
@app.route('/docs')
def help():
    return render_template('help.html')

@app.route('/sources')
@app.route('/streamsources')
def sources():
    return render_template('streamsource.html')

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)