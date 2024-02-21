""""""

import Sofa


class Object(Sofa.Prefab):

    prefabData = [
        {
            "name": "meshPath",
            "type": "string",
            "help": "Path to the mesh file",
            "default": "",
        },
        {
            "name": "rotation",
            "type": "Vec3d",
            "help": "Rotation of the object",
            "default": [0.0, 0.0, 0.0],
        },
        {
            "name": "translation",
            "type": "Vec3d",
            "help": "Translation of the object",
            "default": [0.0, 0.0, 0.0],
        },
        {
            "name": "scale3d",
            "type": "Vec3d",
            "help": "Scale of the object",
            "default": [1.0, 1.0, 1.0],
        },
        {
            "name": "color",
            "type": "Vec4d",
            "help": "Color of the object",
            "default": [1.0, 1.0, 1.0, 1.0],
        },
        {
            "name": "collisionGroup",
            "type": "string",
            "help": "Collision group of the object",
            "default": "",
        },
        {
            "name": "isStatic",
            "type": "bool",
            "help": "Is the object static",
            "default": False,
        },
        {
            "name": "totalMass",
            "type": "float",
            "help": "Total mass of the object",
            "default": 1.0,
        },
        {
            "name": "volume",
            "type": "float",
            "help": "Volume of the object",
            "default": 1.0,
        },
        {
            "name": "inertiaMatrix",
            "type": "Mat3x3d",
            "help": "Inertia matrix of the object",
            "default": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
        },
    ]

    def __init__(self, *args, **kwargs):
        Sofa.Prefab.__init__(self, *args, **kwargs)

    def init(self):
        self.requiredPlugins = [
            "Sofa.Component.Collision.Geometry",
            "Sofa.Component.Mapping.NonLinear",
            "Sofa.Component.StateContainer",
            "Sofa.Component.Topology.Container.Constant",
            "Sofa.Component.Mass",
        ]

        self.addObject(
            "MechanicalObject",
            name="mstate",
            template="Rigid3",
            translation=self.translation.value,
            rotation=self.rotation.value,
            scale3d=self.scale3d.value,
        )

        self.addObject(
            "UniformMass",
            name="mass",
            vertexMass=[
                self.totalMass.value,
                self.volume.value,
                self.inertiaMatrix.value,
            ],
        )

        if not self.isStatic.value:
            self.addObject("EulerImplicitSolver")
            self.addObject(
                "CGLinearSolver", iterations=25, tolerance=1e-5, threshold=1e-5
            )

        if self.meshPath.value:
            self.addVisualModel()
            self.addCollisionModel()

        self.addObject(
            "RequiredPlugin",
            pluginName=self.requiredPlugins,
        )

    def addMeshSTLLoader(self, obj):
        self.requiredPlugins.append("Sofa.Component.IO.Mesh")
        meshLoader = obj.addObject(
            "MeshSTLLoader",
            name="loader",
            filename=self.meshPath.value,
            triangulate=True,
            scale3d=self.scale3d.value,
        )

    def addCollisionModel(self):
        collision = self.addChild("Collision")
        self.addMeshSTLLoader(collision)

        collision.addObject("MeshTopology", src=collision.loader.getLinkPath())
        collision.addObject("MechanicalObject")

        if self.isStatic.value:
            collision.addObject(
                "TriangleCollisionModel",
                moving=False,
                simulated=False,
                group=self.collisionGroup.value,
            )
            collision.addObject(
                "LineCollisionModel",
                moving=False,
                simulated=False,
                group=self.collisionGroup.value,
            )
            collision.addObject(
                "PointCollisionModel",
                moving=False,
                simulated=False,
                group=self.collisionGroup.value,
            )
        else:
            collision.addObject(
                "TriangleCollisionModel", group=self.collisionGroup.value
            )
            collision.addObject("LineCollisionModel", group=self.collisionGroup.value)
            collision.addObject("PointCollisionModel", group=self.collisionGroup.value)
        collision.addObject("RigidMapping")

    def addVisualModel(self):
        self.requiredPlugins.append("Sofa.GL.Component.Rendering3D")

        visual = self.addChild("Visual")
        self.addMeshSTLLoader(visual)
        visual.addObject(
            "OglModel", src=visual.loader.getLinkPath(), color=self.color.value
        )
        visual.addObject("RigidMapping")
