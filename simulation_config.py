import numpy as np

circular_coords = [(12 + int(10*np.sin(2*t*np.pi)),12 + int(10*np.cos(2*t*np.pi))) for t in np.arange(0,1,0.1) ]
AMENITIES_COORDINATES = circular_coords