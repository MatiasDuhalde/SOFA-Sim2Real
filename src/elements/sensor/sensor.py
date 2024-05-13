import math
import pathlib
from os import path

import numpy as np
import Sofa
from PIL import Image
from stlib3.components import addOrientedBoxRoi
from stlib3.physics.mixedmaterial import Rigidify

from params import (
    DEPTH_MAP_KEY,
    IMAGE_FILE_NAME,
    MEMBRANE_POISSON_RATIO,
    MEMBRANE_SURFACE_MESH_PATH,
    MEMBRANE_TOTAL_MASS,
    MEMBRANE_VOLUME_MESH_PATH,
    MEMBRANE_YOUNG_MODULUS,
    OUTPUT_IMAGE_SIZE,
    OUTPUT_PATH,
    POINTS_FILE_NAME,
    SHELL_MESH_PATH,
)

from .elasticmaterialobject import ElasticMaterialObject


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
        self.membraneVolumeMeshPath = MEMBRANE_VOLUME_MESH_PATH
        self.membraneSurfaceMeshPath = MEMBRANE_SURFACE_MESH_PATH

        self.membraneRotation = [0.0, 0.0, 0.0]
        self.membraneTranslation = [0.0, 0.0, 0.0]
        self.membraneScale = [0.001, 0.001, 0.001]
        self.membraneSurfaceColor = [
            135.0 / 255.0,
            133.0 / 255.0,
            147.0 / 255.0,
            1.0,
        ]  # RGBA

        self.membraneTotalMass = MEMBRANE_TOTAL_MASS
        self.membraneYoungModulus = MEMBRANE_YOUNG_MODULUS
        self.membranePoissonRatio = MEMBRANE_POISSON_RATIO

        # Shell values
        self.shellMeshPath = SHELL_MESH_PATH

        self.shellRotation = [0.0, 0.0, 0.0]
        self.shellTranslation = [0.0, 0.0, 0.0]
        self.shellScale = [0.001, 0.001, 0.001]
        self.shellColor = [1.0, 1.0, 1.0, 1.0]  # RGBA

        # Create the elastic part of the sensor
        self.membrane = self.add_membrane()

        # Initialize the elastic body to eagerly compute positions
        self.Membrane.init()

        # Save the membrane's collision model
        self.collision_model = self.membrane.CollisionModel

        # Add the shell of the sensor (only visual model)
        self.shell = self.add_shell()

        self.top_box = self.add_top_bounding_box()

        # Save indexes of the top nodes
        self.top_indexes = [ind for ind in self.top_box.indices.value]

        self.fix_membrane()

    def add_bottom_bounding_box(self):
        """
        Add a box at the bottom of the membrane to fix it in place, simulating the contact with the acrylic window.
        """
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

    def add_sides_bounding_boxes(self):
        """
        Add bounding boxes to the sides of the membrane to fix them in place, simulating the borders of the sensor.
        """
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

    def fix_membrane(self):
        """
        Fix the membrane in place by adding a spring force field to the sides of the membrane.
        """
        self.bottom_box = self.add_bottom_bounding_box()

        indices = [[ind for ind in self.bottom_box.indices.value]]

        rigidifiedStruct = Rigidify(
            targetObject=self,
            sourceObject=self.membrane,
            groupIndices=indices,
            name="RigidifiedStructure",
        )

    def add_top_bounding_box(self):
        """
        Add a box at the top of the membrane to read the indexes of the top nodes
        """
        collision_model_vertices = self.collision_model.dofs.rest_position.value

        box_position = [list(i) for i in collision_model_vertices]

        box_translation = [0, 0.023, 0]
        box_scale = [0.04, 0.0015, 0.04]

        box = addOrientedBoxRoi(
            self,
            position=box_position,
            name="TopBoxROI",
            translation=box_translation,
            eulerRotation=[0, 0, 0],
            scale=box_scale,
            drawBoxes=True,
        )

        box.init()

        return box

    def get_membrane_surface_positions(self):
        return [self.collision_model.dofs.position.value[i] for i in self.top_indexes]

    def add_membrane(self):

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

    def add_shell(self):

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

        return shell


class SensorController(Sofa.Core.Controller):

    def __init__(self, *args, **kwargs):
        Sofa.Core.Controller.__init__(self, *args, **kwargs)

        self.node = kwargs["node"]
        self.sensor = kwargs["sensor"]

    def onKeypressedEvent(self, event):
        key = event["key"]
        if key == DEPTH_MAP_KEY:
            print("Capturing depth map...")
            self.capture_depth_map()
            print("Depth map captured")

    def capture_depth_map(self):
        surface_positions = self.sensor.get_membrane_surface_positions()

        self.create_output_directory()

        self.save_depth_map_points(surface_positions)

        depth_map_array = self.map_to_image(
            np.array(surface_positions), OUTPUT_IMAGE_SIZE
        )
        self.save_depth_map_image(depth_map_array)

    def create_output_directory(self):
        pathlib.Path(OUTPUT_PATH).mkdir(parents=True, exist_ok=True)

    def save_depth_map_points(self, surface_positions):
        file_path = path.join(OUTPUT_PATH, POINTS_FILE_NAME)
        with open(file_path, "w") as f:
            for item in surface_positions:
                f.write(",".join([str(i) for i in item]) + "\n")

    def save_depth_map_image(self, depth_map_array):
        file_path = path.join(OUTPUT_PATH, IMAGE_FILE_NAME)
        depth_map_image = Image.fromarray((depth_map_array * 255).astype(np.uint8))
        depth_map_image.save(file_path)

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
        Maps triplets of values (X, Y, Z) to an image using a nearest neighbor strategy.

        Args:
            triplets: A NumPy array of shape (N, 3) where each row is (X, Y, Z).
            image_size: The size of the image (e.g., (83, 101)).

        Returns:
            A 2D NumPy array representing the grayscale image.
        """

        # Create an empty image
        image = np.zeros(image_size)

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
        for i in range(image_size[0]):
            for j in range(image_size[1]):
                # Convert pixel coordinates to normalized coordinates (between 0 and 1)
                x = (j + 0.5) / image_size[1]
                y = (i + 0.5) / image_size[0]

                nearest_neighbor_data = self.nearest_neighbor(triplets, x, y)

                # Get the Y value of the nearest neighbor
                value = nearest_neighbor_data[1]

                # Normalize the value between 0 and 1
                normalized = value

                image[i, j] = normalized

        return image
