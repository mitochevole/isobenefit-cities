import numpy as np

circular_coords = [(12 + int(10*np.sin(2*t*np.pi)),12 + int(10*np.cos(2*t*np.pi))) for t in np.arange(0,1,0.1) ]
random_coords = [(int(50*np.random.random()),int(50*np.random.random())) for _ in range(30)]
AMENITIES_COORDINATES = random_coords