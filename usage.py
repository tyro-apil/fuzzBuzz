"""
usage.py

This is an example of how to use the fuzzy inference system with a simple
temperature control system.
"""
from src.fis import FuzzyInferenceSystem
from src.linguisticVariable import LinguisticVariable
from src.membershipFunction import MembershipFunctionFactory

def main():
    # Create fuzzy inference system
    fis = FuzzyInferenceSystem()
    
    # Create input variable: temperature
    temperature = LinguisticVariable("temperature", [0,50])
    temperature.add_membership_function(
        MembershipFunctionFactory.create_triangular("cold", [0, 10, 20])
    )
    temperature.add_membership_function(
        MembershipFunctionFactory.create_triangular("normal", [15, 25, 35])
    )
    temperature.add_membership_function(
        MembershipFunctionFactory.create_triangular("hot", [30, 40, 50])
    )
    
    # Create input variable: humidity
    humidity = LinguisticVariable("humidity",[0,100])
    humidity.add_membership_function(
        MembershipFunctionFactory.create_triangular("low", [0, 25, 50])
    )
    humidity.add_membership_function(
        MembershipFunctionFactory.create_triangular("medium", [25, 50, 75])
    )
    humidity.add_membership_function(
        MembershipFunctionFactory.create_triangular("high", [50, 75, 100])
    )
    
    # Create output variable: fan_speed
    fan_speed = LinguisticVariable("fan_speed", [0,100])
    fan_speed.add_membership_function(
        MembershipFunctionFactory.create_triangular("slow", [0, 25, 50])
    )
    fan_speed.add_membership_function(
        MembershipFunctionFactory.create_triangular("medium", [25, 50, 75])
    )
    fan_speed.add_membership_function(
        MembershipFunctionFactory.create_triangular("fast", [50, 75, 100])
    )
    
    # Add variables to the fuzzy inference system
    fis.add_input_variable(temperature)
    fis.add_input_variable(humidity)
    fis.add_output_variable(fan_speed)
    
    # Add rules from string
    rules_str = """
    IF temperature is hot AND humidity is high THEN fan_speed is fast;
    IF temperature is hot AND humidity is medium THEN fan_speed is medium;
    IF temperature is normal AND humidity is high THEN fan_speed is medium;
    IF temperature is normal AND humidity is medium THEN fan_speed is slow;
    IF temperature is cold THEN fan_speed is slow
    """
    
    fis.add_rules_from_string(rules_str)
    
    # Test the fuzzy inference system
    inputs = {
        "temperature": 38,  # Hot
        "humidity": 70      # High
    }
    
    result = fis.infer(inputs)
    print(f"Input: Temperature = {inputs['temperature']}°C, Humidity = {inputs['humidity']}%")
    print(f"Output: Fan Speed = {result['fan_speed']}%")

if __name__ == "__main__":
    main()