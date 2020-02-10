# isobenefit-cities

To install, create a virtual environment
and activate it, then run:
```bash
pip install -r requirements.txt
python setup.py develop

```

Example runs
```bash
 python run-isobenefit-simulation.py --size-x 69 --size-y 100 --n-steps 20 --initialization-mode image --input-filepath initial_config_1.png
 python run-isobenefit-simulation.py --size-x 69 --size-y 100 --n-steps 20 --initialization-mode list --build-probability 0.3 --neighboring-centrality-probability 0.01 --isolated-centrality-probability 0.05

```