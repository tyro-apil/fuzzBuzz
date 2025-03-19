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
        # Range from -1 to 1 (similar to original skfuzzy range)
        self.pendulum_angle = LinguisticVariable("join1", [-1, 1])
        
        # Create membership functions using your custom system
        # Creating 7 triangular membership functions to match original 'automf(7)'
        # We'll use similar terms to the skfuzzy ones: dismal, poor, mediocre, average, decent, good, excellent
        
        # Calculate positions for 7 evenly distributed triangular membership functions
        step = 2.0 / 6  # Range is 2 (-1 to 1), divided into 6 segments for 7 points
        
        self.pendulum_angle.add_membership_function(
            MembershipFunctionFactory.create_triangular("dismal", [-1.0, -1.0 + step/2, -1.0 + step])
        )
        self.pendulum_angle.add_membership_function(
            MembershipFunctionFactory.create_triangular("poor", [-1.0 + step/2, -1.0 + step, -1.0 + 1.5*step])
        )
        self.pendulum_angle.add_membership_function(
            MembershipFunctionFactory.create_triangular("mediocre", [-1.0 + step, -1.0 + 1.5*step, -1.0 + 2*step])
        )
        self.pendulum_angle.add_membership_function(
            MembershipFunctionFactory.create_triangular("average", [-1.0 + 1.5*step, -1.0 + 2*step, -1.0 + 2.5*step])
        )
        self.pendulum_angle.add_membership_function(
            MembershipFunctionFactory.create_triangular("decent", [-1.0 + 2*step, -1.0 + 2.5*step, -1.0 + 3*step])
        )
        self.pendulum_angle.add_membership_function(
            MembershipFunctionFactory.create_triangular("good", [-1.0 + 2.5*step, -1.0 + 3*step, 1.0])
        )
        self.pendulum_angle.add_membership_function(
            MembershipFunctionFactory.create_triangular("excellent", [-1.0 + 3*step, 1.0, 1.0])
        )
        
        # Create output variable for motor speed
        # Range from -300 to 300 (similar to original skfuzzy range)
        self.motor_speed = LinguisticVariable("motor", [-300, 300])
        
        # Create membership functions for output
        step_motor = 600.0 / 6  # Range is 600 (-300 to 300)
        
        self.motor_speed.add_membership_function(
            MembershipFunctionFactory.create_triangular("dismal", [-300, -300 + step_motor/2, -300 + step_motor])
        )
        self.motor_speed.add_membership_function(
            MembershipFunctionFactory.create_triangular("poor", [-300 + step_motor/2, -300 + step_motor, -300 + 1.5*step_motor])
        )
        self.motor_speed.add_membership_function(
            MembershipFunctionFactory.create_triangular("mediocre", [-300 + step_motor, -300 + 1.5*step_motor, -300 + 2*step_motor])
        )
        self.motor_speed.add_membership_function(
            MembershipFunctionFactory.create_triangular("average", [-300 + 1.5*step_motor, -300 + 2*step_motor, -300 + 2.5*step_motor])
        )
        self.motor_speed.add_membership_function(
            MembershipFunctionFactory.create_triangular("decent", [-300 + 2*step_motor, -300 + 2.5*step_motor, -300 + 3*step_motor])
        )
        self.motor_speed.add_membership_function(
            MembershipFunctionFactory.create_triangular("good", [-300 + 2.5*step_motor, -300 + 3*step_motor, 300])
        )
        self.motor_speed.add_membership_function(
            MembershipFunctionFactory.create_triangular("excellent", [-300 + 3*step_motor, 300, 300])
        )
        
        # Add variables to FIS
        self.fis.add_input_variable(self.pendulum_angle)
        self.fis.add_output_variable(self.motor_speed)
        
        # Add rules to match the original skfuzzy rules
        rules_str = """
        IF join1 is dismal THEN motor is dismal;
        IF join1 is poor THEN motor is poor;
        IF join1 is mediocre THEN motor is mediocre;
        IF join1 is average THEN motor is average;
        IF join1 is decent THEN motor is decent;
        IF join1 is good THEN motor is good;
        IF join1 is excellent THEN motor is excellent
        """
        
        self.fis.add_rules_from_string(rules_str)

    def createWorld(self):
        self._isLiving = True
        self._auto = True


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

        self.pendelumRJoin =self.world.CreateRevoluteJoint(
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

        elif key == Keys.K_n:
            if self._isLiving:
                self.destroyWorld()
                self.createWorld()


    def Step(self, settings):
        super(BodyPendulum, self).Step(settings)

        self.pendelumLJoin.maxMotorTorque = 1000
        self.pendelumRJoin.maxMotorTorque = 1000
        
        # Use custom FIS instead of skfuzzy
        # Ensure the angle is within the defined range (-1 to 1)
        angle = max(min(self.pendulum.angle, 1.0), -1.0)
        
        # Infer using custom FIS
        inputs = {"join1": angle}
        output = self.fis.infer(inputs)
        
        # Apply the inferred motor speed
        motor_speed = output["motor"]
        
        self.pendelumLJoin.motorSpeed = motor_speed
        self.pendelumRJoin.motorSpeed = motor_speed

if __name__ == "__main__":
    main(BodyPendulum)