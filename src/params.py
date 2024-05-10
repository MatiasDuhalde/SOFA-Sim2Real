from os import path

from splib3.constants import Key

DEPTH_MAP_KEY = Key.P
MEMBRANE_TOTAL_MASS = 0.015  # kg
MEMBRANE_YOUNG_MODULUS = 35000  # Pa
MEMBRANE_POISSON_RATIO = 0.25

MEMBRANE_SURFACE_MESH_PATH = path.join(
    "..", "data", "mesh", "sensor", "Med-Even-Mesh.stl"
)
MEMBRANE_VOLUME_MESH_PATH = path.join(
    "..", "data", "mesh", "sensor", "Low-Even-Mesh.msh"
)
# MEMBRANE_VOLUME_MESH_PATH = path.join(
#     "..", "data", "mesh", "sensor", "Med-Even-Mesh.msh"
# )
# MEMBRANE_VOLUME_MESH_PATH = path.join(
#     "..", "data", "mesh", "sensor", "Low-Even-Mesh.msh"
# )

SHELL_MESH_PATH = path.join("..", "data", "mesh", "sensor", "Shell-Low.stl")

OUTPUT_PATH = path.join("..", "output")
POINTS_FILE_NAME = "depth_map_points.txt"
IMAGE_FILE_NAME = "depth_map_image.png"

OUTPUT_IMAGE_SIZE = (83 * 3, 101 * 3)
