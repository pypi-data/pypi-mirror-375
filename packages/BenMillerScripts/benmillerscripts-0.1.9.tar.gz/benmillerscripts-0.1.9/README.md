BenMillerScripts
---
This is a collection of Python Modules that I've written to support my Python scripts that can be run from the embedded Python in Gatan's [DigitalMicrograph](https://www.gatan.com/resources/software) software 

For more information on using Python in DigitalMicrograph, visit this page on [Gatan's Website](https://www.gatan.com/resources/python-scripts).



Installing
---
If you don't yet have Python in DigitalMicrograph, first install DigitalMicrograph 3.4 or greater, and during installation, choose to install Python. More details can be found at the links above. 

Next, open an Anaconda prompt. This should be listed in the Windows start menu program list. You may want to run this as an admin. 
In the Anaconda prompt enter the following:

`activate GMS_VENV_PYTHON`

This will activate the virtual environment that DigitalMicrograph uses. 

Next, install the package by entering the following command.

`pip install BenMillerScripts`

Usage
---

This module is used by several of my scripts on the Gatan website including [Live FFT Color Map script](https://www.gatan.com/sites/default/files/Scripts/Live%20FFT%20Color%20Map.py) and [Process 2D in-situ datasets](https://www.gatan.com/sites/default/files/Scripts/Process%202D%20IS%20Datasets.py).
