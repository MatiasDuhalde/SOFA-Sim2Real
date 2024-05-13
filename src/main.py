from os import path

from stlib3.physics.rigid import Floor, Sphere
from stlib3.scene import Scene

from elements.object.object import Object
from elements.object.object_controller import ObjectController
from elements.sensor.sensor import Sensor, SensorController
from params import ALARM_DISTANCE, ANGLE_CONE, CONTACT_DISTANCE, FRICTION_COEF


def add_star(scene):
    star = Object(
        name="Star",
        meshPath="../data/mesh/star/star.stl",
        rotation=[0.0, 45.0, 0.0],
        translation=[0.0, 0.03, 0.0],
        scale3d=[0.0075, 0.0075, 0.0075],
        color=[1.0, 1.0, 0.0, 1.0],
        isStatic=False,
    )
    star.addObject("UncoupledConstraintCorrection")
    scene.Modelling.addChild(star)
    return star


def add_coin(scene):
    coin = Object(
        name="Coin",
        meshPath="../data/mesh/coin/One-Euro.stl",
        rotation=[-90.0, 0.0, 0.0],
        translation=[0.0, 20.0, 0.0],
        color=[219.0 / 255.0, 172.0 / 255.0, 52.0 / 255.0, 1.0],
        isStatic=False,
    )
    coin.addObject("UncoupledConstraintCorrection")
    scene.Modelling.addChild(coin)
    return coin


def add_sphere(scene):
    sphere = Sphere(
        None,
        name="Sphere",
        translation=[0.0, 0.03, 0.0],
        uniformScale=0.005,
        isAStaticObject=False,
        totalMass=0.064,
    )
    sphere.addObject("UncoupledConstraintCorrection")
    scene.Modelling.addChild(sphere)
    return sphere


def add_monkey(scene):
    monkey = Object(
        name="monkey",
        meshPath="../data/mesh/monkey/monkey.stl",
        rotation=[0.0, 90.0, 0.0],
        translation=[0.0, 0.035, 0.0],
        scale3d=[0.0075, 0.0075, 0.0075],
        color=[1.0, 1.0, 0.0, 1.0],
        totalMass=0.25,
        isStatic=False,
    )
    monkey.addObject("UncoupledConstraintCorrection")
    scene.Modelling.addChild(monkey)
    return monkey


def set_internal_camera(scene):
    """Add static camera to look at the bottom of the sensor"""
    scene.addObject(
        "Camera",
        position=[90.0, 0.0, 0.0],
        orientation=[90.0, 0.0, 0.0, 1.0],
        distance=[0.0, 0.0, 0.0],
        fieldOfView=90.0,
        projectionType="Orthographic",
    )


def createScene(rootNode):

    # The list of plugins this simulation requires
    plugins = [
        "MultiThreading",
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
    scene.addContact(
        alarmDistance=ALARM_DISTANCE,
        contactDistance=CONTACT_DISTANCE,
        frictionCoef=FRICTION_COEF,
    )

    scene.LocalMinDistance.angleCone = ANGLE_CONE

    # The default view of the scene on SOFA
    scene.addObject("DefaultVisualManagerLoop")

    # We configure the initial flags for the visual representation of the scene
    scene.VisualStyle.displayFlags = [
        "hideVisual",
        "showInteractionForceFields",
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
    scene.Simulation.addChild(sensor.RigidifiedStructure.DeformableParts)

    # Add controller
    scene.addObject(
        SensorController(name="SensorController", sensor=sensor, node=rootNode)
    )

    add_monkey(scene)

    # controller = ObjectController(
    #     name="SphereController", node=rootNode, object=sphere.mstate
    # )
    # scene.addObject(controller)
    # scene.Simulation.TimeIntegrationSchema.rayleighStiffness = 0.005

    return rootNode
