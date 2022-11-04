from ctypes import alignment
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

#from PIL import Image

from pymxs import runtime as rt
import pymxs

import qtmax
import os, shutil

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
        
        # Create planes from material
        create_plane_groupbox = QtWidgets.QGroupBox("Create planes from scene materials")
        create_plane_layout = QtWidgets.QVBoxLayout(create_plane_groupbox)
        create_plane_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        label = QtWidgets.QLabel("Click \"Create\" button to create planes from material names", alignment = QtCore.Qt.AlignCenter)
        
        create_plane_btn = QtWidgets.QPushButton("Create")
        create_plane_btn.setFixedSize(QtCore.QSize(300, 30))
        create_plane_btn.clicked.connect(create_plane_objecs)
        
        create_plane_layout.addWidget(label)
        create_plane_layout.addWidget(create_plane_btn)
        
        # Collecting of assets
        collect_asset_groupbox = QtWidgets.QGroupBox("Collecting of assets")
        
        collect_asset_layout = QtWidgets.QVBoxLayout(collect_asset_groupbox)
        
        collect_label_folder_path = QtWidgets.QLabel("Selected Output Directory")
        
        collect_textField_layout = QtWidgets.QHBoxLayout()
        self.collect_textEdit = QtWidgets.QLineEdit()
        collect_textField_selectFolder_btn = QtWidgets.QPushButton("...")
        collect_textField_selectFolder_btn.setFixedSize(QtCore.QSize(30, 20))
        collect_textField_selectFolder_btn.clicked.connect(self.select_output_folder)
        
        collect_assets_btn = QtWidgets.QPushButton("Collect")
        collect_assets_btn.setFixedSize(QtCore.QSize(80, 50))
        collect_assets_btn.clicked.connect(self.collect_textures_of_material)
        
        collect_textField_layout.addWidget(self.collect_textEdit)
        collect_textField_layout.addWidget(collect_textField_selectFolder_btn)
        
        collect_asset_layout.addWidget(collect_label_folder_path)
        collect_asset_layout.addLayout(collect_textField_layout)
        collect_asset_layout.addWidget(collect_assets_btn)
        
        # Edit Material Texture
        texture_editor_groupbox = QtWidgets.QGroupBox("Edit Material Textures")
        
        texture_editor_layout = QtWidgets.QVBoxLayout(texture_editor_groupbox)
        
        texture_editor_basemap_label_usage = QtWidgets.QLabel(
            "** HINTS: All materials' base map textures for plane object will be replaced with the textures from selected folder and reflectivity and refl color map will be removed. **"
        )
        texture_editor_basemap_label_folder_path = QtWidgets.QLabel("Selected Root Directory For Base Map")
        
        texture_editor_basemap_textField_layout = QtWidgets.QHBoxLayout()
        self.texture_editor_basemap_textEdit = QtWidgets.QLineEdit()
        texture_editor_basemap_textField_selectFolder_btn = QtWidgets.QPushButton("...")
        texture_editor_basemap_textField_selectFolder_btn.setFixedSize(QtCore.QSize(30, 20))
        texture_editor_basemap_textField_selectFolder_btn.clicked.connect(self.select_edit_texture_output_folder)
        
        texture_editor_btn = QtWidgets.QPushButton("Change")
        texture_editor_btn.setFixedSize(QtCore.QSize(80, 25))
        texture_editor_btn.clicked.connect(self.edit_textures_of_material)
        
        texture_editor_basemap_textField_layout.addWidget(self.texture_editor_basemap_textEdit)
        texture_editor_basemap_textField_layout.addWidget(texture_editor_basemap_textField_selectFolder_btn)
        
        texture_editor_layout.addWidget(texture_editor_basemap_label_usage)
        texture_editor_layout.addWidget(texture_editor_basemap_label_folder_path)
        texture_editor_layout.addLayout(texture_editor_basemap_textField_layout)
        texture_editor_layout.addWidget(texture_editor_btn) 
        
        main_layout.addWidget(create_plane_groupbox)
        main_layout.addWidget(collect_asset_groupbox)
        main_layout.addWidget(texture_editor_groupbox)
        
        widget = QtWidgets.QWidget()
        widget.setLayout(main_layout)
        self.setWidget(widget)
        self.resize(250, 200)
        
    def select_output_folder(self):
        output_folder = QtWidgets.QFileDialog.getExistingDirectory()
        self.collect_textEdit.setText(output_folder)
        
    def select_edit_texture_output_folder(self):
        output_folder = QtWidgets.QFileDialog.getExistingDirectory()
        self.texture_editor_basemap_textEdit.setText(output_folder)
        
    def collect_textures_of_material(self):
        outputFolderPath = self.collect_textEdit.text()
        print("outputFolderPath: {}".format(outputFolderPath))
        plane_objects = get_plane_objects()
        for plane in plane_objects:
            material = plane.getmxsprop("material")
            if material is None:
                continue
            
            #create a folder for each material with the name of the material
            material_folder = os.path.join(outputFolderPath, material.name)
            if not os.path.exists(material_folder):
                os.makedirs(material_folder)
                
            #copy the base color map
            if material.base_color_map != None:
                base_color_map_path = material.base_color_map.fileName
                base_color_map_new_path = os.path.join(material_folder, os.path.basename(base_color_map_path))
                shutil.copyfile(base_color_map_path, base_color_map_new_path)
            else:
                print("Syslog: No base color map for material: {}".format(material.name))
            
            #copy the reflectivity map
            if material.reflectivity_map != None:
                reflectivity_map = material.reflectivity_map.fileName
                reflectivity_map_new_path = os.path.join(material_folder, os.path.basename(reflectivity_map))
                shutil.copyfile(reflectivity_map, reflectivity_map_new_path)
            else:
                print("Syslog: No reflectivity map for material: {}".format(material.name))
                
            #copy the refl color map
            if material.refl_color_map != None:
                refl_color_map = material.refl_color_map.fileName
                refl_color_map_new_path = os.path.join(material_folder, os.path.basename(refl_color_map))
                shutil.copyfile(refl_color_map, refl_color_map_new_path)
                
                #convert the refl color map to .tga
                """refl_color_map_tga = refl_color_map.replace(".dds", ".tga")
                
                if not os.path.exists(refl_color_map_tga):
                    img = Image.open(refl_color_map_new_path)
                    img.save(refl_color_map_tga)"""
            else:
                print("Syslog: no refl_color_map for material: {}".format(material.name))

    def edit_textures_of_material(self):
        outputFolderPath = self.texture_editor_basemap_textEdit.text()
        print("outputFolderPath: {}".format(outputFolderPath))
        plane_objects = get_plane_objects()
        for plane in plane_objects:
            material = plane.getmxsprop("material")
            if material is None:
                continue
            
            material_folder = os.path.join(outputFolderPath, "".join([material.name, "_Albedo.dds"]))
            print("material_folder: {}".format(material_folder))
            
            if not os.path.exists(material_folder):
                print("Syslog: No material exists in folder: {}".format(material.name))
                continue
            
            # Create BitMapTexture for base color map
            bitmap = rt.openBitMap(material_folder)
            bmt = rt.bitmapTex()
            bmt.bitmap = bitmap
            material.setmxsprop("base_color_map", bmt)
            
            # Remove reflectivity and refl color map
            if material.reflectivity_map != None:
                material.setmxsprop("reflectivity_map", None)
                
            if material.refl_color_map != None:
                material.setmxsprop("refl_color_map", None)

def main():
    main_window = qtmax.GetQMaxMainWindow()
    w = PyMaxDockWidget(parent=main_window)
    w.setFloating(True)
    w.show()

if __name__ == '__main__':
    main()