from time import sleep
from flask import Flask, render_template
from math import sqrt

app = Flask(__name__)

@app.route('/')
def index():
    # render the template (below) that will use JavaScript to read the stream
    return render_template('index.html')

@app.route('/stream_sqrt')
def stream():
    def generate():
        for i in range(500):
            yield '{}\n'.format(sqrt(i))
            sleep(0.01)

    return app.response_class(generate(), mimetype='text/plain')



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