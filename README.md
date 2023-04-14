# Graphical User Interface application for simulating and exporting Load Profile of Electrical Vehicle
The application interface is created by PyQT5 designer


## Installation (packages)
Python 3.9.8
* PyQT5
* yaml: 6.0
* numpy: 1.24.2
* matplotlib: 3.6.3
* csv: 1.0
* pandas: 1.5.3


## File Description
* app.py: GUI program
* computation.py: computation program
* Core.ipynb: combination of computation.py and app.py (just for testing)
* Customer.yml: input file (.yml)
* data.csv: vehicle database
* gui.ui: user interface source file
* gui.py: user interface program (converted from gui.ui)


## Usage
* Adjust interface: open terminal and run the command 'qt5-tools designer'. Choose the file 'gui.ui' to modify.
* Convert 'gui.ui' to 'gui.py': open terminal and run the command 'pyuic5 -x gui.ui -o gui.py'.
* Run the application: open terminal and run 'python app.py'. Click button 'Input file' and choose one YAML file as the application's input


## Contact
Developer: Tung L. Nguyen [email](tln229@nau.edu)
