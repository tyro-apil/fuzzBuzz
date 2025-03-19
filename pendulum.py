# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from Box2D.examples.framework import (Framework, Keys, main)
from Box2D import (b2EdgeShape, b2FixtureDef, b2PolygonShape, b2CircleShape)
import numpy as np

# Import custom FIS components
from src.fis import FuzzyInferenceSystem
from src.linguisticVariable import LinguisticVariable
from src.membershipFunction import MembershipFunctionFactory

class BodyPendulum(Framework):
    name = "Inverted Pendulum"
    description = "(n) new world"

    def __init__(self):
        super(BodyPendulum, self).__init__()

        self.createWorld()
        self.createFuzzy()

    def createFuzzy(self):
        # Create fuzzy inference system
        self.fis = FuzzyInferenceSystem()
        
        # Create input variable for pendulum angle
        self.pendulum_angle = LinguisticVariable("join1", [-1, 1])
        
        # Create membership functions with sufficient overlap
        # Using trapezoidal functions for the extremes and triangular for the middle
        self.pendulum_angle.add_membership_function(
            MembershipFunctionFactory.create_trapezoidal("neg_large", [-1.0, -1.0, -0.6, -0.4])
        )
        self.pendulum_angle.add_membership_function(
            MembershipFunctionFactory.create_triangular("neg_medium", [-0.6, -0.4, -0.2])
        )
        self.pendulum_angle.add_membership_function(
            MembershipFunctionFactory.create_triangular("neg_small", [-0.3, -0.1, 0.0])
        )
        self.pendulum_angle.add_membership_function(
            MembershipFunctionFactory.create_triangular("zero", [-0.1, 0.0, 0.1])
        )
        self.pendulum_angle.add_membership_function(
            MembershipFunctionFactory.create_triangular("pos_small", [0.0, 0.1, 0.3])
        )
        self.pendulum_angle.add_membership_function(
            MembershipFunctionFactory.create_triangular("pos_medium", [0.2, 0.4, 0.6])
        )
        self.pendulum_angle.add_membership_function(
            MembershipFunctionFactory.create_trapezoidal("pos_large", [0.4, 0.6, 1.0, 1.0])
        )
        
        # Create output variable for motor speed
        self.motor_speed = LinguisticVariable("motor", [-300, 300])
        
        # Create membership functions for motor speed with sufficient overlap
        self.motor_speed.add_membership_function(
            MembershipFunctionFactory.create_trapezoidal("neg_large", [-300, -300, -200, -100])
        )
        self.motor_speed.add_membership_function(
            MembershipFunctionFactory.create_triangular("neg_medium", [-150, -100, -50])
        )
        self.motor_speed.add_membership_function(
            MembershipFunctionFactory.create_triangular("neg_small", [-75, -25, 0])
        )
        self.motor_speed.add_membership_function(
            MembershipFunctionFactory.create_triangular("zero", [-25, 0, 25])
        )
        self.motor_speed.add_membership_function(
            MembershipFunctionFactory.create_triangular("pos_small", [0, 25, 75])
        )
        self.motor_speed.add_membership_function(
            MembershipFunctionFactory.create_triangular("pos_medium", [50, 100, 150])
        )
        self.motor_speed.add_membership_function(
            MembershipFunctionFactory.create_trapezoidal("pos_large", [100, 200, 300, 300])
        )
        
        # Add variables to FIS
        self.fis.add_input_variable(self.pendulum_angle)
        self.fis.add_output_variable(self.motor_speed)
        
        # Add rules with inverse relationship between angle and motor speed
        rules_str = """
        IF join1 is neg_large THEN motor is pos_large;
        IF join1 is neg_medium THEN motor is pos_medium;
        IF join1 is neg_small THEN motor is pos_small;
        IF join1 is zero THEN motor is zero;
        IF join1 is pos_small THEN motor is neg_small;
        IF join1 is pos_medium THEN motor is neg_medium;
        IF join1 is pos_large THEN motor is neg_large
        """
        
        self.fis.add_rules_from_string(rules_str)

    def createWorld(self):
        self._isLiving = True
        self._auto = False  # Start with auto mode off

        self.ground = self.world.CreateBody(
            shapes=b2EdgeShape(vertices=[(-25, 0), (25, 0)])
        )

        self.carBody = self.world.CreateDynamicBody(
            position=(0, 3),
            fixtures=b2FixtureDef(
                shape=b2PolygonShape(box=(5, 1)), density=1)
        )

        self.carLwheel = self.world.CreateDynamicBody(
            position=(-3, 1),
            fixtures=b2FixtureDef(
                shape=b2CircleShape(radius=1), density=2, friction=1)
        )

        self.carRwheel = self.world.CreateDynamicBody(
            position=(3, 1),
            fixtures=b2FixtureDef(
                shape=b2CircleShape(radius=1), density=2, friction=1)
        )

        self.pendulum = self.world.CreateDynamicBody(
            position=(0, 13),
            fixtures=b2FixtureDef(
                shape=b2PolygonShape(box=(0.5, 10)), density=1),
        )

        self.pendelumJoin = self.world.CreateRevoluteJoint(
            bodyA=self.carBody,
            bodyB=self.pendulum,
            anchor=(0, 3),
            maxMotorTorque=1,
            enableMotor=True
        )

        self.pendelumRJoin = self.world.CreateRevoluteJoint(
            bodyA=self.carBody,
            bodyB=self.carRwheel,
            anchor=(3, 1),
            maxMotorTorque=1,
            enableMotor=True,
        )

        self.pendelumLJoin = self.world.CreateRevoluteJoint(
            bodyA=self.carBody,
            bodyB=self.carLwheel,
            anchor=(-3, 1),
            maxMotorTorque=1,
            enableMotor=True,
        )

    def destroyWorld(self):
        self.world.DestroyBody(self.carBody)
        self.world.DestroyBody(self.carLwheel)
        self.world.DestroyBody(self.carRwheel)
        self.world.DestroyBody(self.pendulum)
        self._isLiving = False

    def Keyboard(self, key):
        if key == Keys.K_a:
            if self._isLiving:
                self.pendelumLJoin.motorSpeed = 0
                self.pendelumLJoin.maxMotorTorque = 1000
                self.pendelumRJoin.motorSpeed = 0
                self.pendelumRJoin.maxMotorTorque = 1000
                self._auto = True
                print("Auto-balance mode enabled")

        elif key == Keys.K_n:
            if self._isLiving:
                self.destroyWorld()
                self.createWorld()
                print("New world created")

    def Step(self, settings):
        super(BodyPendulum, self).Step(settings)

        # Only apply control when auto mode is enabled
        if self._auto:
            self.pendelumLJoin.maxMotorTorque = 1000
            self.pendelumRJoin.maxMotorTorque = 1000
            
            # Get the current angle, ensuring it's within the defined range
            angle = max(min(self.pendulum.angle, 1.0), -1.0)
            
            try:
                # Only apply control if angle is outside a small deadzone
                if abs(angle) < 0.01:
                    motor_speed = 0
                else:
                    # Infer using custom FIS
                    inputs = {"join1": angle}
                    output = self.fis.infer(inputs)
                    motor_speed = output["motor"]
                
                # Apply the inferred motor speed
                self.pendelumLJoin.motorSpeed = motor_speed
                self.pendelumRJoin.motorSpeed = motor_speed
            except Exception as e:
                print(f"Fuzzy inference error: {e}")
                # Fallback to a simple proportional control
                motor_speed = -angle * 200  # Simple proportional control
                self.pendelumLJoin.motorSpeed = motor_speed
                self.pendelumRJoin.motorSpeed = motor_speed

if __name__ == "__main__":
    main(BodyPendulum)