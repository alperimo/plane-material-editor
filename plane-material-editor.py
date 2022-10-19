from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
import qtmax

from pymxs import runtime as rt
import pymxs

def get_plane_objects():
    objects = [obj for obj in rt.objects if rt.isKindOf(obj, rt.Plane)]
    return objects

def create_plane_objecs():
    startX = 0
    x, y = 0, 0
    spaceBetween = 40
    rowCount = 0
    
    print("count of SceneMaterials: {}".format(len(rt.sceneMaterials)))
    for mat in rt.sceneMaterials:
        plane = rt.Plane(width=20, length=20, pos = rt.Point3(x, y, 0))
        plane.name = "Plane_{}".format(mat.name[mat.name.find("_")+1:])
        plane.setmxsprop("material", mat)
        rowCount += 1
        x += spaceBetween
        if (rowCount == 10):
            x = startX
            y -= spaceBetween
            rowCount = 0

class PyMaxDockWidget(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super(PyMaxDockWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setWindowTitle('Plane Material Editor')
        self.initUI()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("Click \"Create\" button to create planes from material names")
        main_layout.addWidget(label)

        create_plane_btn = QtWidgets.QPushButton("Create")
        create_plane_btn.clicked.connect(create_plane_objecs)
        main_layout.addWidget(create_plane_btn)
        widget = QtWidgets.QWidget()
        widget.setLayout(main_layout)
        self.setWidget(widget)
        self.resize(250, 100)

def main():
    rt.resetMaxFile(rt.name('noPrompt'))
    main_window = qtmax.GetQMaxMainWindow()
    w = PyMaxDockWidget(parent=main_window)
    w.setFloating(True)
    w.show()

if __name__ == '__main__':
    main()