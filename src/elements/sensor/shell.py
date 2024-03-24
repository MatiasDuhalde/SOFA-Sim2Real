""""""

import Sofa


def Shell(
    rotation=[0.0, 0.0, 0.0],
    translation=[0.0, 0.0, 0.0],
    scale3d=[1.0, 1.0, 1.0],
    color=[1.0, 1.0, 1.0, 1.0],
    collisionGroup="",
):
    self = Sofa.Core.Node("Shell")

    # We only need the visual model for the shell
    visual = self.addChild("Visual")
    visual.addObject(
        "MeshSTLLoader",
        name="loader",
        filename="../data/mesh/sensor/Shell-Low.stl",
        triangulate=True,
        rotation=rotation,
        translation=translation,
        scale3d=scale3d,
    )
    visual.addObject("OglModel", src=visual.loader.getLinkPath(), color=color)
    # visual.addObject("RigidMapping")

    return self
