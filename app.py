import yaml
import numpy as np
import matplotlib
import csv
import sys
import pandas as pd
from tkinter import filedialog
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog
from computation import read_data, all_distributions, compute_total_LP
matplotlib.use('Qt5Agg')

class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        self.input_loaded = 0
        self.simulated = 0
        
        # INTERFACE
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1264, 869)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 60, 1241, 721))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.Btn_Simulate = QtWidgets.QPushButton(self.centralwidget)
        self.Btn_Simulate.setGeometry(QtCore.QRect(670, 790, 121, 41))
        self.Btn_Simulate.setObjectName("Btn_Simulate")
        self.Btn_Export = QtWidgets.QPushButton(self.centralwidget)
        self.Btn_Export.setGeometry(QtCore.QRect(470, 790, 121, 41))
        self.Btn_Export.setObjectName("Btn_Export")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(510, 10, 101, 31))
        self.label.setObjectName("label")
        self.cBox_Customer = QtWidgets.QComboBox(self.centralwidget)
        self.cBox_Customer.setGeometry(QtCore.QRect(620, 10, 161, 31))
        self.cBox_Customer.setObjectName("cBox_Customer")
        self.Btn_Input = QtWidgets.QPushButton(self.centralwidget)
        self.Btn_Input.setGeometry(QtCore.QRect(230, 10, 91, 31))
        self.Btn_Input.setObjectName("Btn_Input")
        self.label_noti = QtWidgets.QLabel(self.centralwidget)
        self.label_noti.setGeometry(QtCore.QRect(220, 40, 151, 21))
        self.label_noti.setObjectName("label_noti")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(886, 5, 151, 41))
        self.label_2.setObjectName("label_2")
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(1050, 10, 101, 31))
        self.comboBox.setObjectName("comboBox")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # button
        self.Btn_Export.clicked.connect(self.export)
        self.Btn_Simulate.clicked.connect(self.simulate)
        self.Btn_Input.clicked.connect(self.select_input)

        # label notification (loaded input)
        self.label.setAlignment(Qt.AlignCenter)
        self.label_noti.setStyleSheet('color: red;')

        # combobox
        self.comboBox.addItems(list(['1','15','30','60']))
        self.comboBox.currentIndexChanged.connect(self.cBox_step_change)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.Btn_Simulate.setText(_translate("MainWindow", "Simulate"))
        self.Btn_Export.setText(_translate("MainWindow", "Export"))
        self.label.setText(_translate("MainWindow", "Customer:"))
        self.Btn_Input.setText(_translate("MainWindow", "Input file"))
        self.label_noti.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" color:#ff0000;\"><br/></span></p></body></html>"))
        self.label_2.setText(_translate("MainWindow", "Time step (minutes):"))


    def cBox_step_change(self):
        if(self.simulated == 1):
            for i in reversed(range(self.verticalLayout.count())): 
                self.verticalLayout.itemAt(i).widget().setParent(None)

            # plot
            sc = MplCanvas(self, width=5, height=4, dpi=90)

            time_step = self.comboBox.currentText()
            time_step = int(time_step)
            length = int(2880/time_step)

            x_value = np.linspace(0, 48, num=length)
            Total_LP = self.Total_LP.reshape((length, time_step))
            Total_LP = np.sum(Total_LP, axis=1)
            sc.axes.plot(x_value, Total_LP/1000.0)

            # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
            toolbar = NavigationToolbar(sc)
            self.verticalLayout.addWidget(toolbar)
            self.verticalLayout.addWidget(sc)

    
    def select_input(self):
        filename, _ = QFileDialog.getOpenFileName(None, "Select input file...", "", "YAML Files (*.yml)")
        self.customers_data = read_data(filename)
        self.cBox_Customer.clear()
        self.cBox_Customer.addItem("All")
        self.cBox_Customer.addItems(list(self.customers_data.keys())[1:])
        self.label_noti.setText("Input file is loaded")
        self.input_loaded = 1


    def export(self):
        filename, _ = QFileDialog.getSaveFileName(filter="CSV Files (*.csv)")

        file_export = "Individuals"
        if(file_export == "Total_LP"):
            if filename:
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(self.Total_LP)
        
        if(file_export == "Individuals"):
            self.individuals_df.to_csv(filename, index=False)

    
    def simulate(self):
        # check if input is loaded
        if(self.input_loaded == 0):
            self.label_noti.setText("Input is not loaded")
        else:
            self.simulated = 1

            # clear
            for i in reversed(range(self.verticalLayout.count())): 
                self.verticalLayout.itemAt(i).widget().setParent(None)

            # compute Total_LP and individuals_data
            customer = self.cBox_Customer.currentText()
            self.Total_LP, self.individuals_df = compute_total_LP(all_distributions, self.customers_data, customer)

            # plot
            sc = MplCanvas(self, width=5, height=4, dpi=90)

            time_step = self.comboBox.currentText()
            time_step = int(time_step)
            length = int(2880/time_step)

            x_value = np.linspace(0, 48, num=length)
            Total_LP = self.Total_LP.reshape((length, time_step))
            Total_LP = np.sum(Total_LP, axis=1)
            sc.axes.plot(x_value, Total_LP/1000.0)

            # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
            toolbar = NavigationToolbar(sc)
            self.verticalLayout.addWidget(toolbar)
            self.verticalLayout.addWidget(sc)


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=200):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.set_ylabel('Load Profile (kW)')
        self.axes.set_xlabel('Time (hour)')
        super(MplCanvas, self).__init__(fig)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.setWindowTitle("Load Profile Application")
    MainWindow.setFixedSize(1264, 869)
    MainWindow.setStyleSheet("QWidget {font-size: 8pt; }")

    MainWindow.show()
    sys.exit(app.exec_())