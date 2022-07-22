from PIL import Image
import numpy as np
from matplotlib import cm


def import_2Darray_from_image(filepath):
    pic = Image.open(filepath)
    data = np.array(pic.getdata()).reshape(pic.size[1], pic.size[0], -1).mean(axis=2)
    data_rescaled = (data - data.min()) / (data.max() - data.min())
    return data_rescaled


def plot_image_from_2Darray(normalized_data_array, color_map=cm.gist_earth):
    data_mapped = np.uint8(255 * color_map(normalized_data_array))
    img = Image.fromarray(data_mapped)
    img.show()


def save_image_from_2Darray(canvas, filepath, format='png'):
    data_mapped = np.uint8(255 * canvas)
    img = Image.fromarray(data_mapped)
    img.save(filepath, format=format)
