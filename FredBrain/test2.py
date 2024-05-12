from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('Labor Market Analysis.html')  # Ensure the HTML file is in the templates folder within your project directory.

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Runs the server on localhost:5000