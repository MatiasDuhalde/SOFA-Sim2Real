import math

import Sofa


class ObjectController(Sofa.Core.Controller):
    """
    Control the movement of a controller.
    Moves the object up and down on the y-axis over a period of time.

    """

    def __init__(self, *args, **kwargs):
        Sofa.Core.Controller.__init__(self, *args, **kwargs)

        self.node = kwargs["node"]
        self.object = kwargs["object"]
        self.period = 0.5 if "period" not in kwargs else kwargs["period"]
        self.time = 0.0
        self.delta_y = 0.004 if "delta_y" not in kwargs else kwargs["delta_y"]

    def init(self):
        pass

    def onAnimateBeginEvent(self, eventType):
        self.time += self.node.dt.value
        base_position = list(self.object.reset_position.value[0])
        # Start from the top
        base_position[1] = base_position[1] + self.delta_y / 2 * (
            math.cos(2 * math.pi * self.time / self.period) - 1
        )
        # Change position of object
        self.object.position.value = [base_position]
