# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui.autosave'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1036, 837)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.pushButton = QtWidgets.QPushButton(self.centralWidget)
        self.pushButton.setGeometry(QtCore.QRect(50, 60, 101, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralWidget)
        self.pushButton_2.setGeometry(QtCore.QRect(180, 60, 101, 31))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralWidget)
        self.pushButton_3.setGeometry(QtCore.QRect(310, 60, 101, 31))
        self.pushButton_3.setObjectName("pushButton_3")
        self.imglabel = QtWidgets.QLabel(self.centralWidget)
        self.imglabel.setGeometry(QtCore.QRect(60, 150, 331, 331))
        self.imglabel.setFrameShape(QtWidgets.QFrame.Box)
        self.imglabel.setObjectName("imglabel")
        MainWindow.setCentralWidget(self.centralWidget)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1036, 22))
        self.menuBar.setObjectName("menuBar")
        self.menuDataset_labelling_using_Polygons = QtWidgets.QMenu(self.menuBar)
        self.menuDataset_labelling_using_Polygons.setObjectName("menuDataset_labelling_using_Polygons")
        MainWindow.setMenuBar(self.menuBar)
        self.menuBar.addAction(self.menuDataset_labelling_using_Polygons.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.image = None
        self.loadButton.clicked.connect(self.loadClicked) 

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Load Image"))
        self.pushButton_2.setText(_translate("MainWindow", "Process Image"))
        self.pushButton_3.setText(_translate("MainWindow", "Get Poly"))
        self.imglabel.setText(_translate("MainWindow", "TextLabel"))
        self.menuDataset_labelling_using_Polygons.setTitle(_translate("MainWindow", "Dataset labelling using Polygons"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
