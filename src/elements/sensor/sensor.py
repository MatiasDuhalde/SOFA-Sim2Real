import math
from os import path

import Sofa
from stlib3.components import addOrientedBoxRoi
from stlib3.physics.collision import CollisionMesh
from stlib3.physics.mixedmaterial import Rigidify

from .elasticmaterialobject import ElasticMaterialObject
from .fixing_box import FixingBox


class Sensor(Sofa.Prefab):
    prefabParameters = [
        {
            "name": "rotation",
            "type": "Vec3d",
            "help": "Rotation in base frame",
            "default": [0.0, 0.0, 0.0],
        },
        {
            "name": "translation",
            "type": "Vec3d",
            "help": "Translation in base frame",
            "default": [0.0, 0.0, 0.0],
        },
        {
            "name": "scale",
            "type": "Vec3d",
            "help": "Scale in base frame",
            "default": [1.0, 1.0, 1.0],
        },
    ]

    def __init__(self, *args, **kwargs):
        Sofa.Prefab.__init__(self, *args, **kwargs)

    # Build the sensor
    def init(self):

        # Membrane values
        self.membraneVolumeMeshPath = path.join(
            "..", "data", "mesh", "sensor", "Low-Even-Mesh.msh"
        )
        self.membraneSurfaceMeshPath = path.join(
            "..", "data", "mesh", "sensor", "Low-Even-Mesh.stl"
        )

        self.membraneRotation = [0.0, 0.0, 0.0]
        self.membraneTranslation = [0.0, 0.0, 0.0]
        self.membraneScale = [0.001, 0.001, 0.001]
        self.membraneSurfaceColor = [
            135.0 / 255.0,
            133.0 / 255.0,
            147.0 / 255.0,
            1.0,
        ]  # RGBA

        self.membraneTotalMass = 0.015  # kg
        self.membraneYoungModulus = 35000  # Pa
        self.membranePoissonRatio = 0.25

        # Shell values
        self.shellMeshPath = path.join("..", "data", "mesh", "sensor", "Shell-Low.stl")

        self.shellRotation = [0.0, 0.0, 0.0]
        self.shellTranslation = [0.0, 0.0, 0.0]
        self.shellScale = [0.001, 0.001, 0.001]
        self.shellColor = [1.0, 1.0, 1.0, 1.0]  # RGBA

        # Create the elastic part of the sensor
        self.membrane = self.addMembrane()

        # Initialize the elastic body to eagerly compute positions
        self.Membrane.init()

        # Add the shell of the sensor (only visual model)
        self.shell = self.addShell()

        # Fix the membrane in place, by adding a spring force field to the sides
        self.fixMembrane()

    def fixMembrane(self):

        x_base = 0.0135
        y_base = 0.019
        z_base = 0.0115
        box_position = [list(i) for i in self.membrane.dofs.rest_position.value]

        eulerRotation = [0, 0, 0]

        indices = []

        for i in range(4):
            box_translation = [
                x_base * math.cos(math.radians(90 * i)),
                y_base,
                z_base * math.sin(math.radians(90 * i)),
            ]

            box_scale = [0.002, 0.002, 0.03]

            box = addOrientedBoxRoi(
                self,
                position=box_position,
                name=f"BoxROI{i}",
                translation=box_translation,
                eulerRotation=eulerRotation,
                scale=box_scale,
                drawBoxes=True,
            )

            eulerRotation = [0, 90 * (i + 1), 0]

            box.init()

            indices.append([ind for ind in box.indices.value])

        rigidifiedStruct = Rigidify(
            targetObject=self,
            sourceObject=self.membrane,
            groupIndices=indices,
            name="RigidifiedStructure",
        )

    def addMembrane(self):

        # Create the membrane as a child of the parent
        membrane = self.addChild("Membrane")

        # This creates an ElasticMaterialObject
        elasticMaterial = ElasticMaterialObject(
            name="Membrane",
            volumeMeshFileName=self.membraneVolumeMeshPath,
            rotation=self.membraneRotation,
            translation=self.membraneTranslation,
            scale=self.membraneScale,
            surfaceMeshFileName=self.membraneSurfaceMeshPath,
            collisionMesh=self.membraneSurfaceMeshPath,
            withConstrain=True,
            surfaceColor=self.membraneSurfaceColor,
            poissonRatio=self.membranePoissonRatio,
            youngModulus=self.membraneYoungModulus,
            totalMass=self.membraneTotalMass,
            solverName="",
        )

        return membrane.addChild(elasticMaterial)

    def addShell(self):

        shell = self.addChild("Shell")

        # We only need the visual model for the shell
        visual = shell.addChild("Visual")

        # Load the mesh
        visual.addObject(
            "MeshSTLLoader",
            name="loader",
            filename=self.shellMeshPath,
            triangulate=True,
            rotation=self.shellRotation,
            translation=self.shellTranslation,
            scale3d=self.shellScale,
        )

        # OpenGL model
        visual.addObject(
            "OglModel", src=visual.loader.getLinkPath(), color=self.shellColor
        )

        # Mapping between the shell and the visual model
        # visual.addObject("RigidMapping")

        return shell


class SensorController(Sofa.Core.Controller):

    def __init__(self, *args, **kwargs):
        Sofa.Core.Controller.__init__(self, *args, **kwargs)
