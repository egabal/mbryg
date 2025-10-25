from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/metabolite/<name>')
def show_metabolite(name):
    # show the user profile for that user
    return f"I will show you metabolite {name}"
