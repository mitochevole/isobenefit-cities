create-env:
	conda create --name $(name) python=3.6

install:
	pip install -r requirements.txt
	python setup.py develop

create-and-install:
	make create-env name=$(name)
	conda activate $(name)
	make install

run-gui:
	python scripts/tkinter-gui-interface.py

