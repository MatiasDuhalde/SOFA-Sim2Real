import math
from gettext import translation
from os import path
import pathlib

import numpy as np
import Sofa
from PIL import Image
from splib3.constants import Key
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

        # Add a box at the top of the membrane to read the indexes of the top nodes
        self.top_box = self.addTopBoundingBox()

        # Fix the membrane in place, by adding a spring force field to the sides
        self.fixMembrane()


        print(len(self.getMembraneSurfaceIndexes()))

    def addBottomBoundingBox(self):
        box_position = [list(i) for i in self.membrane.dofs.rest_position.value]

        box_translation = [0, 0.018, 0]
        box_scale = [0.04, 0.001, 0.04]

        box = addOrientedBoxRoi(
            self,
            position=box_position,
            name="BottomBoxROI",
            translation=box_translation,
            eulerRotation=[0, 0, 0],
            scale=box_scale,
            drawBoxes=True,
        )

        box.init()

        return box
        
    def addSidesBoundingBoxes(self):
        x_base = 0.0135
        y_base = 0.019
        z_base = 0.0115
        box_position = [list(i) for i in self.membrane.dofs.rest_position.value]

        eulerRotation = [0, 0, 0]

        boxes = []

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

            boxes.append(box)

        return boxes      

    def fixMembrane(self):
        self.bottom_box = self.addBottomBoundingBox()

        indices = [[ind for ind in self.bottom_box.indices.value]]

        rigidifiedStruct = Rigidify(
            targetObject=self,
            sourceObject=self.membrane,
            groupIndices=indices,
            name="RigidifiedStructure",
        )

    def addTopBoundingBox(self):
        box_position = [list(i) for i in self.membrane.dofs.rest_position.value]

        box_translation = [0, 0.023, 0]
        box_scale = [0.04, 0.0015, 0.04]

        box = addOrientedBoxRoi(
            self,
            position=box_position,
            name="BottomBoxROI",
            translation=box_translation,
            eulerRotation=[0, 0, 0],
            scale=box_scale,
            drawBoxes=True,
        )

        box.init()

        return box

    def getMembraneSurfaceIndexes(self):
        return [ind for ind in self.top_box.indices.value]

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

        self.node = kwargs["node"]
        self.sensor = kwargs["sensor"]

    def onKeypressedEvent(self, event):
        output_path = pathlib.Path(__file__).parent.parent.parent.resolve()
        key = event["key"]
        if key == Key.P:
            print("P key pressed")
            indexes = self.sensor.getMembraneSurfaceIndexes()
            positions = self.sensor.Membrane.Membrane.dofs.position.value
            surfaceValues = [positions[i] for i in indexes]
            # Dump to file
            with open(path.join(output_path, "depth_map_points.txt"), "w") as f:
                for item in surfaceValues:
                    f.write(",".join([str(i) for i in item]) + "\n")

            # Generate depth map
            depth_map = self.map_to_image(np.array(surfaceValues), 256)
            depth_map = Image.fromarray((depth_map * 255).astype(np.uint8))
            depth_map.save(path.join(output_path, "depth_map.png"))

    def nearest_neighbor(self, data, i, j):
        """
        Finds the nearest neighbor (X, Z) coordinates in the data for a given point.

        Args:
            data: A NumPy array of shape (N, 3) containing triplets of (X, Y, Z) values.
            i: The x-coordinate of the desired point.
            j: The y-coordinate of the desired point.

        Returns:
            A tuple containing the (X, Y, Z) values of the nearest neighbor.
        """
        # Calculate Euclidean distances between the point and all triplets
        distances = np.sqrt(np.sum((data[:, [0, 2]] - [i, j]) ** 2, axis=1))
        # Find the index of the minimum distance (nearest neighbor)
        nearest_neighbor_index = np.argmin(distances)

        return data[nearest_neighbor_index]

    def map_to_image(self, triplets, image_size):
        """
        Maps triplets of values (X, Y, Z) to a square image using bilinear interpolation.

        Args:
            triplets: A NumPy array of shape (N, 3) where each row is (X, Y, Z).
            image_size: The size of the square image (e.g., 256).

        Returns:
            A 2D NumPy array representing the grayscale image.
        """

        # Create an empty image
        image = np.zeros((image_size, image_size))

        # Get min and max values
        min_x = np.min(triplets[:, 0])
        max_x = np.max(triplets[:, 0])
        min_y = np.min(triplets[:, 1])
        max_y = np.max(triplets[:, 1])
        min_z = np.min(triplets[:, 2])
        max_z = np.max(triplets[:, 2])

        # normalize all triplets coordinates between 0 and 1
        triplets[:, 0] = (triplets[:, 0] - min_x) / (max_x - min_x)
        triplets[:, 1] = (triplets[:, 1] - min_y) / (max_y - min_y)
        triplets[:, 2] = (triplets[:, 2] - min_z) / (max_z - min_z)

        # Loop through each pixel in the image
        for i in range(image_size):
            for j in range(image_size):
                # Convert pixel coordinates to normalized coordinates (between 0 and 1)
                x = (j + 0.5) / image_size
                y = (i + 0.5) / image_size

                nearest_neighbor_data = self.nearest_neighbor(triplets, x, y)

                # Get the Y value of the nearest neighbor
                value = nearest_neighbor_data[1]

                # Normalize the value between 0 and 1
                normalized = value

                image[i, j] = normalized

        return image
