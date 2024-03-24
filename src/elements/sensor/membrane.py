import Sofa


def Membrane(
    rotation=[0.0, 0.0, 0.0],
    translation=[0.0, 0.0, 0.0],
    scale3d=[1.0, 1.0, 1.0],
    color=[1.0, 1.0, 1.0, 1.0],
    collisionGroup="",
):
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

    collisionModel = mechanicalModel.addChild("MechanicalModel")

    collisionModel.addObject(
        "MeshSTLLoader",
        name="loader",
        filename=visualMeshPath,
        rotation=rotation,
        translation=translation,
        scale3d=scale3d,
    )

    collisionModel.addObject("MeshTopology", src=collisionModel.loader.getLinkPath())
    collisionModel.addObject("MechanicalObject")
    collisionModel.addObject("PointCollisionModel", group=collisionGroup)
    collisionModel.addObject("LineCollisionModel", group=collisionGroup)
    collisionModel.addObject("TriangleCollisionModel", group=collisionGroup)
    collisionModel.addObject("BarycentricMapping")

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
    return self
