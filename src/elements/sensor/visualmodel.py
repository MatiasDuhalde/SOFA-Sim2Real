# -*- coding: utf-8 -*-
"""
Templates for rendering.

Copy-paste from the visualmodel.py file in the stlib3 repository to fix a bug.
"""
import Sofa.Core


class VisualModel(Sofa.Prefab):
    """ """

    prefabParameters = [
        {
            "name": "visualMeshPath",
            "type": "string",
            "help": "Path to visual mesh file",
            "default": "",
        },
        {
            "name": "translation",
            "type": "Vec3d",
            "help": "translate visual model",
            "default": [0.0, 0.0, 0.0],
        },
        {
            "name": "rotation",
            "type": "Vec3d",
            "help": "rotate visual model",
            "default": [0.0, 0.0, 0.0],
        },
        {
            "name": "scale",
            "type": "Vec3d",
            "help": "scale visual model",
            "default": [1.0, 1.0, 1.0],
        },
        {
            "name": "color",
            "type": "Vec4d",
            "help": "color put to visual model",
            "default": [1.0, 1.0, 1.0, 1.0],
        },
    ]

    def __init__(self, *args, **kwargs):
        Sofa.Prefab.__init__(self, *args, **kwargs)

    def init(self):
        self.addObject(
            "RequiredPlugin",
            pluginName=["Sofa.GL.Component.Rendering3D", "Sofa.Component.IO.Mesh"],
        )
        path = self.visualMeshPath.value
        if path.endswith(".stl"):
            self.addObject(
                "MeshSTLLoader",
                name="loader",
                filename=path,
                scale3d=list(self.scale.value),
            )
        elif path.endswith(".obj"):
            self.addObject(
                "MeshOBJLoader",
                name="loader",
                filename=path,
                scale3d=list(self.scale.value),
            )
        else:
            print(
                "Extension not handled in STLIB/python3/stlib3/visuals for file: "
                + str(path)
            )

        self.addObject(
            "OglModel",
            name="OglModel",
            src="@loader",
            rotation=list(self.rotation.value),
            translation=list(self.translation.value),
            # scale3d=list(self.scale.value),
            color=list(self.color.value),
            updateNormals=False,
        )

    def showGrid(self, nbSubdiv=10, size=1000):
        self.addObject("OglGrid", nbSubdiv=nbSubdiv, size=size)


def createScene(root):
    from stlib3.scene import Scene

    scene = Scene(root)
    scene.addSettings()
    scene.addModelling()
    scene.addSimulation()

    visu = VisualModel(visualMeshPath="mesh/smCube27.obj")
    visu.showGrid()
    scene.Modelling.addChild(visu)
