from stlib3.physics.rigid import Floor, Sphere
from stlib3.scene import Scene

from elements.object.object import Object
from elements.sensor.membrane import Membrane


def createScene(rootNode):

    plugins = [
        "Sofa.Component.AnimationLoop",
        "Sofa.Component.Collision.Detection.Algorithm",
        "Sofa.Component.Collision.Detection.Intersection",
        "Sofa.Component.Collision.Response.Contact",
        "Sofa.Component.Collision.Geometry",
        "Sofa.Component.Mapping.NonLinear",
        "Sofa.Component.StateContainer",
        "Sofa.Component.Topology.Container.Constant",
        "Sofa.Component.Constraint.Lagrangian.Correction",
        "Sofa.Component.Constraint.Lagrangian.Solver",
        "Sofa.Component.LinearSolver.Iterative",
        "Sofa.Component.Visual",
        "Sofa.GL.Component.Rendering3D",
        "Sofa.GUI.Component",
        "SofaPython3",
        "Sofa.Component.IO.Mesh",
        "Sofa.Component.Mapping.Linear",
        "Sofa.Component.Mass",
        "Sofa.Component.SolidMechanics.FEM.Elastic",
        "Sofa.Component.MechanicalLoad",
    ]

    scene = Scene(rootNode, plugins=plugins)
    scene.addMainHeader()
    scene.addObject("DefaultVisualManagerLoop")
    scene.addContact(alarmDistance=0.1, contactDistance=0.01, frictionCoef=1.0)
    scene.VisualStyle.displayFlags = "showVisual showBehavior showCollisionModels"

    # coin = Object(
    #     name="Coin",
    #     meshPath="../data/mesh/coin/One-Euro.stl",
    #     rotation=[-90.0, 0.0, 0.0],
    #     translation=[0.0, 20.0, 0.0],
    #     color=[219.0 / 255.0, 172.0 / 255.0, 52.0 / 255.0, 1.0],
    #     isStatic=False,
    # )

    # coin.addObject("UncoupledConstraintCorrection")

    # scene.Modelling.addChild(coin)

    sphere = Sphere(
        None,
        name="Sphere",
        translation=[0.0, 18.0, 0.0],
        uniformScale=3.0,
        isAStaticObject=False,
        totalMass=0.032,
    )
    sphere.addObject("UncoupledConstraintCorrection")

    scene.Modelling.addChild(sphere)

    # floor = Floor(
    #     None,
    #     name="FloorObstacle",
    #     translation=[0.0, 0.0, 0.0],
    #     color=[0.0, 1.0, 0.0, 1.0],
    #     uniformScale=0.1,
    #     isAStaticObject=True,
    # )

    # scene.Modelling.addChild(floor)

    shell = Object(
        name="Shell",
        meshPath="../data/mesh/sensor/Shell-Low.stl",
        scale3d=[0.5, 0.5, 0.5],
        color=[1.0, 1.0, 1.0, 1.0],
        isStatic=True,
    )

    scene.Modelling.addChild(shell)

    membrane = Membrane(
        name="Membrane",
        meshPath="../data/mesh/sensor/Membrane-High.stl",
        scale3d=[0.5, 0.5, 0.5],
        color=[135.0 / 255.0, 133.0 / 255.0, 147.0 / 255.0, 1.0],
    )

    scene.Modelling.addChild(membrane)

    return rootNode
