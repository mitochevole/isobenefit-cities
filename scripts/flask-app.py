import time
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    username = None
    value = 0
    if request.method == 'POST':
        username = request.form.get("username", None)

    def calculate_value_based_on_username(user_given_name):
        time.sleep(1)
        return len(user_given_name)

    if username:
        value = calculate_value_based_on_username(username)
        return render_template('app.html', username=username, value=value)
    return render_template('app.html')

if __name__ == '__main__':
    app.run(debug=True)