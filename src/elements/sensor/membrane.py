import Sofa
from splib3.numerics import vec3
from stlib3.components import addOrientedBoxRoi
from stlib3.physics.mixedmaterial import Rigidify


def hadamard_product(a, b):
    return [a[i] * b[i] for i in range(len(a))]


def Membrane(
    rotation=[0.0, 0.0, 0.0],
    translation=[0.0, 0.0, 0.0],
    scale3d=[1.0, 1.0, 1.0],
    color=[1.0, 1.0, 1.0, 1.0],
    collisionGroup="",
):

    # Add boxes to select the borders of the membrane
    def __rigidify(self, mechanicalModel):
        mechanicalModel.dofs.init()

        x_base = 13.5
        y_base = 19
        z_base = 11.5
        box_translation = hadamard_product(
            vec3.vadd(translation, [x_base, y_base, 0.0]), scale3d
        )
        box_scale = hadamard_product([2, 2.5, 30], scale3d)

        box_position = [list(i) for i in mechanicalModel.dofs.rest_position.value]

        group_indices = []

        box1 = addOrientedBoxRoi(
            self,
            position=box_position,
            name="BoxROI0",
            translation=box_translation,
            eulerRotation=[0, 0, 0],
            scale=box_scale,
            drawBoxes=True,
        )

        box1.init()
        group_indices.append([ind for ind in box1.indices.value])

        box_translation = hadamard_product(
            vec3.vadd(translation, [-x_base, y_base, 0.0]), scale3d
        )

        box2 = addOrientedBoxRoi(
            self,
            position=box_position,
            name="BoxROI1",
            translation=box_translation,
            eulerRotation=[0, 180, 0],
            scale=box_scale,
            drawBoxes=True,
        )

        box2.init()
        group_indices.append([ind for ind in box2.indices.value])

        box_translation = hadamard_product(
            vec3.vadd(translation, [0.0, y_base, -z_base]), scale3d
        )

        box3 = addOrientedBoxRoi(
            self,
            position=box_position,
            name="BoxROI2",
            translation=box_translation,
            eulerRotation=[0, 90, 0],
            scale=box_scale,
            drawBoxes=True,
        )

        box3.init()
        group_indices.append([ind for ind in box3.indices.value])

        box_translation = hadamard_product(
            vec3.vadd(translation, [0.0, y_base, z_base]), scale3d
        )

        box4 = addOrientedBoxRoi(
            self,
            position=box_position,
            name="BoxROI3",
            translation=box_translation,
            eulerRotation=[0, 270, 0],
            scale=box_scale,
            drawBoxes=True,
        )

        box4.init()
        group_indices.append([ind for ind in box4.indices.value])

        # Rigidify the deformable part at extremity to attach arms
        rigidifiedstruct = Rigidify(
            self,
            mechanicalModel,
            groupIndices=group_indices,
            name="RigidifiedStructure",
        )

    self = Sofa.Core.Node("Membrane")

    femMeshPath = "../data/mesh/sensor/Low-Even-Mesh.msh"
    visualMeshPath = "../data/mesh/sensor/Low-Even-Mesh.stl"

    mechanicalModel = self.addChild("MechanicalModel")
    mechanicalModel.addObject(
        "MeshGmshLoader",
        name="loader",
        filename=femMeshPath,
        rotation=rotation,
        translation=translation,
        scale3d=scale3d,
    )
    mechanicalModel.addObject(
        "MeshTopology", src=mechanicalModel.loader.getLinkPath(), name="container"
    )

    mechanicalModel.addObject(
        "MechanicalObject",
        name="dofs",
        position=mechanicalModel.loader.position.getLinkPath(),
        showObject=False,
        showObjectScale=5.0,
    )
    mechanicalModel.addObject("UniformMass", name="mass", totalMass=0.032)

    # ForceField components
    mechanicalModel.addObject(
        "TetrahedronFEMForceField",
        name="linearElasticBehavior",
        youngModulus=250,
        poissonRatio=0.45,
    )

    # collisionModel = mechanicalModel.addChild("MechanicalModel")

    # collisionModel.addObject(
    #     "MeshSTLLoader",
    #     name="loader",
    #     filename=visualMeshPath,
    #     rotation=rotation,
    #     translation=translation,
    #     scale3d=scale3d,
    # )

    # collisionModel.addObject("MeshTopology", src=collisionModel.loader.getLinkPath())
    # collisionModel.addObject("MechanicalObject")
    # collisionModel.addObject("PointCollisionModel", group=collisionGroup)
    # collisionModel.addObject("LineCollisionModel", group=collisionGroup)
    # collisionModel.addObject("TriangleCollisionModel", group=collisionGroup)
    # collisionModel.addObject("BarycentricMapping")

    # Visual model
    visualModel = Sofa.Core.Node("VisualModel")
    # Specific loader for the visual model
    visualModel.addObject(
        "MeshSTLLoader",
        name="loader",
        filename=visualMeshPath,
        rotation=rotation,
        translation=translation,
        scale3d=scale3d,
    )
    visualModel.addObject(
        "OglModel", src=visualModel.loader.getLinkPath(), name="renderer", color=color
    )
    self.addChild(visualModel)

    visualModel.addObject(
        "BarycentricMapping",
        input=mechanicalModel.dofs.getLinkPath(),
        output=visualModel.renderer.getLinkPath(),
    )

    __rigidify(self, mechanicalModel)

    return self
