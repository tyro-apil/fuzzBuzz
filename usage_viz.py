import matplotlib.pyplot as plt

# Import the Fuzzy Inference System components
from src.fis import FuzzyInferenceSystem
from src.linguisticVariable import LinguisticVariable
from src.membershipFunction import MembershipFunctionFactory
from utils.visualize import *

def main():
    # Create fuzzy inference system (copied from usage.py)
    fis = FuzzyInferenceSystem()
    
    # Create input variable: temperature
    temperature = LinguisticVariable("temperature", [0, 50])
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
    humidity = LinguisticVariable("humidity", [0, 100])
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
    fan_speed = LinguisticVariable("fan_speed", [0, 100])
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
        "temperature": 38,  
        "humidity": 70      
    }
    
    result = fis.infer(inputs)
    print(f"Input: Temperature = {inputs['temperature']}°C, Humidity = {inputs['humidity']}%")
    print(f"Output: Fan Speed = {result['fan_speed']}%")
    
    # Visualize the membership functions
    temp_plot = visualize_membership_functions(temperature, inputs["temperature"])
    # temp_plot.savefig("temperature_membership.png")
    
    humidity_plot = visualize_membership_functions(humidity, inputs["humidity"])
    # humidity_plot.savefig("humidity_membership.png")
    
    # Visualize rule activation
    rule_plot, rule_activations = visualize_rule_activation(fis, inputs)
    # rule_plot.savefig("rule_activation.png")

    detailed_rule_plot = visualize_detailed_rule_activation(fis, inputs)
    # rule_plot.savefig("rule_activation.png")

    
    # Print rule activations
    print("\nRule Activations:")
    for i, activation in enumerate(rule_activations):
        print(f"Rule {i+1}: {activation:.2f}")
    
    # Visualize defuzzification
    defuzz_plot = visualize_defuzzification(fis, inputs)
    # defuzz_plot.savefig("defuzzification.png")
    
    plt.show()

if __name__ == "__main__":
    main()