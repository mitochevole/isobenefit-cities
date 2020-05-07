# Isobenefit Urbanism
*An urban genetic code to generate low carbon, adaptive, connected, compact, multifunctional settlements 
throughout nature, with unplanned forms and unlimitedly extendible, 
in which one does not need cars and can feel both urbanity and nature.*

This project presents generative simulations of urban growth in the [isobenefit urbanism scenario](https://lucadacci.wixsite.com/dacci/isobenefit-urbanism-morphogenesis)

## Getting started

### Prerequisites

You will need [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and python installed, if don't have it on your machine already, the [anaconda distribution](https://docs.anaconda.com/anaconda/install/) is the easiest place to start.

%% todo check if git included in anaconda installation 


### Install
Open the terminal (On Windows search for `Anaconda Prompt`)
Navigate to the directory where you want to install the package and then clone the repository to the local folder of your choice via
```bash
git clone https://github.com/mitochevole/isobenefit-cities.git
```

If you are using anaconda, create a new environment:
```bash
conda create --name [my_env] python=3.6
```

activate the environment typing `conda activate [my_env]`
navigate inside the project directory 
```bash
cd isobenefit-cities
```

then run `make install`
On windows if the `make` command is not available, run instead
```bash
pip install -r requirements.txt
python setup.py develop
```

## Run the simulations

![GUI interface](gui-interface-example.png?raw=true)

Running `make run-gui` opens a `tk-inter`-based GUI 
where you can: 
- choose the type of development
- set the size of the map both in X and Y direction in number of cells
- set the maximum number of iterations for the simulation
- set the maximum population that the simulation will reach
- set the maximum population density
- set the probability of building a new urban block (provided that all other conditions for constructions are satisfied)
- set the probability P1 of creating a new centrality adjacent to constructed areas
- set the probability P2 of creating a new isolated centrality
- set the size in units of simulation cells of the critical distance T*
- random seed for the simulation

If again `make` is not available just run:
```bash
python scripts/tkinter-gui-interface.py
```


You can also run the simulations directly fom command line.
```bash
 python run-isobenefit-simulation.py --size-x 69 --size-y 100 --n-steps 20 --initialization-mode image --input-filepath initial_config_1.png
 python run-isobenefit-simulation.py --size-x 69 --size-y 100 --n-steps 20 --initialization-mode list --build-probability 0.3 --neighboring-centrality-probability 0.01 --isolated-centrality-probability 0.05

```

When you run the simulation, it will create a folder at `[current_directory]/simulations/yyyymmdd-hhMMss`
where `yyyymmdd-hhMMss` is the timestamp at which the simulation is run.

Inside the folder are stored:
- a png snapshot of the simulated scenario at each step of the iteration
- `metadata.json` file with the parameters of the simulation
- `current_counts.csv` a comma separated text file storing the per-step and cumulative counts of population increase and built blocks and centralities for each step of the iteration

## Technical details
The value T* sets the scale for the simulation. 
In the literature (citation needed) the critical value T* refers to the distance that can be covered in 15 minutes on foot.
If we assume that a human can walk at a pace of 4 km/h then the distance T* is roughly one km.

Setting `T* = x cells` means that we are giving to each square cell a side of 1000/x metres.

This is then used to compute the population to be associated with each cell.

In the isboenefit scenario a cell can be densely populated ( having max density)
or moderately populated (having max density/10 ).

In the classical scenario cells can also be scarcely populated, having a density of max density/100. 


## Aknowledgments

This repository gets its inspiration and it's driven by the work of [Luca D'Acci](https://sites.google.com/view/lucadacci).

The code benefits of the comments and fruitful discussions with [Stefano Ugliano](https://about.me/stefanougliano).
