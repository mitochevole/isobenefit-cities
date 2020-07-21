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



'''
import io
import random
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

@app.route('/plot.png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]
    axis.plot(xs, ys)
    return fig
    
Then you need to include the image in your HTML template:

<img src="/plot.png" alt="my plot">

https://stackoverflow.com/questions/50728328/python-how-to-show-matplotlib-in-flask
'''