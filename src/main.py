from os import path

from stlib3.scene import Scene

from elements.sensor.sensor import Sensor


def createScene(rootNode):

    # The list of plugins this simulation requires
    plugins = [
        "Sofa.Component.AnimationLoop",
        "Sofa.Component.Collision.Detection.Algorithm",
        "Sofa.Component.Collision.Detection.Intersection",
        "Sofa.Component.Collision.Response.Contact",
        "Sofa.Component.Collision.Geometry",
        "Sofa.Component.Mapping.NonLinear",
        "Sofa.Component.StateContainer",
        "Sofa.Component.Topology.Container.Constant",
        "Sofa.Component.Topology.Container.Dynamic",
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
        "Sofa.Component.Engine.Select",
        "Sofa.Component.LinearSolver.Direct",
    ]

    # Y axis is the vertical axis
    gravity = [0.0, -9.81, 0.0]
    # Time step
    dt = 0.01

    # We define the Scene object with the root node, gravity, plugins
    # iterative=False means using SparseLDLSolver as the linear solver
    scene = Scene(
        rootNode,
        dt=dt,
        gravity=gravity,
        plugins=plugins,
        iterative=False,
    )

    # This initializes the architecture of the scene, with Modelling, Setting and Simulation nodes
    scene.addMainHeader()

    # This configures the contact parameters (collision detection and response)
    scene.addContact(alarmDistance=15e-3, contactDistance=0.5e-3, frictionCoef=0.1)

    # The default view of the scene on SOFA
    scene.addObject("DefaultVisualManagerLoop")

    # We configure the initial flags for the visual representation of the scene
    scene.VisualStyle.displayFlags = [
        "hideVisual",
        "showBehavior",
        "showCollisionModels",
    ]

    # Set up the pipeline for the collision computation
    scene.Simulation.addObject("GenericConstraintCorrection")

    # Adjust mouse interaction
    scene.Settings.mouseButton.stiffness = 10

    # Add the sensor to the scene
    sensor = Sensor()
    scene.Modelling.addChild(sensor)

    # Add dynamic parts to the scene
    # scene.Simulation.addChild(sensor.RigidifiedStructure.DeformableParts)

    # scene.Simulation.TimeIntegrationSchema.rayleighStiffness = 0.005

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

    # sphere = Sphere(
    #     None,
    #     name="Sphere",
    #     translation=[0.0, 40.0, 0.0],
    #     uniformScale=6.0,
    #     isAStaticObject=False,
    #     totalMass=0.032,
    # )
    # sphere.addObject("UncoupledConstraintCorrection")

    # scene.Modelling.addChild(sphere)

    # floor = Floor(
    #     None,
    #     name="FloorObstacle",
    #     translation=[0.0, 0.0, 0.0],
    #     color=[0.0, 1.0, 0.0, 1.0],
    #     uniformScale=0.1,
    #     isAStaticObject=True,
    # )

    # scene.Modelling.addChild(floor)

    return rootNode
