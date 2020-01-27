import numpy as np

def amenities_coordinates(size_x, size_y, n_amenities, type = "random"):
    
    np.random.seed(42)
    
    if type == "circular":
        amenities_coords = [(12 + int(10*np.sin(2*t*np.pi)), 12 + int(10*np.cos(2*t*np.pi))) 
                            for t in np.arange(0,1,0.1) ]
    elif type == "random":
        amenities_coords = [(int(size_x*np.random.random()),int(size_y*np.random.random())) 
                            for _ in range(10)]
        
    return(amenities_coords)

#AMENITIES_COORDINATES = random_coords#circular_coords