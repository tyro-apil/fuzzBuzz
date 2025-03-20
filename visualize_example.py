import matplotlib.pyplot as plt
import numpy as np
from src.fis import FuzzyInferenceSystem
from src.linguisticVariable import LinguisticVariable
from src.membershipFunction import MembershipFunctionFactory
from utils.visualize import (
    plot_linguistic_variable,
    plot_rule_activation,
    plot_all_rules,
    plot_defuzzification
)

def create_temperature_control_system():
    """Create a fuzzy inference system for temperature control"""
    # Create fuzzy inference system
    fis = FuzzyInferenceSystem()
    
    # Create input variable: temperature
    temperature = LinguisticVariable("temperature", range=[0, 50])
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
    humidity = LinguisticVariable("humidity", range=[0, 100])
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
    fan_speed = LinguisticVariable("fan_speed", range=[0, 100])
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
    
    return fis

def run_inference_with_visualization(fis, inputs):
    """Run inference and visualize the results"""
    # Display input values
    print(f"Input: Temperature = {inputs['temperature']}°C, Humidity = {inputs['humidity']}%")
    
    # 1. Visualize linguistic variables
    print("\nVisualizing linguistic variables:")
    for var_name, variable in fis.input_variables.items():
        print(f"Plotting {var_name} linguistic variable...")
        plot_linguistic_variable(variable)
    
    # Also visualize the output variable
    print("Plotting output linguistic variable...")
    for var_name, variable in fis.output_variables.items():
        plot_linguistic_variable(variable)
    
    # 2. Visualize rule activations
    print("\nVisualizing rule activations:")
    plot_all_rules(fis, inputs)
    
    # 3. Visualize individual rule activations
    print("\nVisualizing individual rule details:")
    for i in range(len(fis.rules)):
        print(f"Rule {i+1} activation:")
        plot_rule_activation(fis, inputs, i)
    
    # 4. Perform inference and visualize defuzzification
    print("\nPerforming inference and visualizing defuzzification:")
    for var_name in fis.output_variables.keys():
        plot_defuzzification(fis, inputs, var_name)
    
    # 5. Get the final result
    result = fis.infer(inputs)
    print(f"\nOutput: Fan Speed = {result['fan_speed']:.2f}%")
    
    return result

def sensitivity_analysis(fis, variable_name, range_values, fixed_inputs):
    """Perform sensitivity analysis for a specific variable"""
    results = []
    
    for value in range_values:
        # Create a copy of fixed inputs and update the variable
        inputs = fixed_inputs.copy()
        inputs[variable_name] = value
        
        # Run inference
        result = fis.infer(inputs)
        results.append(result['fan_speed'])
    
    # Plot results
    plt.figure(figsize=(10, 6))
    plt.plot(range_values, results, marker='o')
    plt.xlabel(variable_name)
    plt.ylabel('fan_speed')
    plt.title(f'Sensitivity Analysis of {variable_name} on fan_speed')
    plt.grid(True)
    plt.show()
    
    return results

def main():
    # Create the fuzzy inference system
    fis = create_temperature_control_system()
    
    # Test with specific inputs
    inputs = {
        "temperature": 38,  # Hot
        "humidity": 70      # High
    }
    
    # Run inference with visualization
    result = run_inference_with_visualization(fis, inputs)
    
    # Perform sensitivity analysis for temperature (keeping humidity fixed)
    print("\nPerforming sensitivity analysis for temperature:")
    temperature_range = np.linspace(0, 50, 25)
    fixed_humidity = inputs["humidity"]
    sensitivity_inputs = {"humidity": fixed_humidity}
    temperature_sensitivity = sensitivity_analysis(fis, "temperature", temperature_range, sensitivity_inputs)
    
    # Perform sensitivity analysis for humidity (keeping temperature fixed)
    print("\nPerforming sensitivity analysis for humidity:")
    humidity_range = np.linspace(0, 100, 25)
    fixed_temperature = inputs["temperature"]
    sensitivity_inputs = {"temperature": fixed_temperature}
    humidity_sensitivity = sensitivity_analysis(fis, "humidity", humidity_range, sensitivity_inputs)
    
    # Create a 3D surface plot showing the relationship between both inputs and output
    print("\nCreating 3D surface plot:")
    temp_range = np.linspace(0, 50, 15)
    humidity_range = np.linspace(0, 100, 15)
    
    X, Y = np.meshgrid(temp_range, humidity_range)
    Z = np.zeros_like(X)
    
    for i in range(len(humidity_range)):
        for j in range(len(temp_range)):
            inputs = {
                "temperature": temp_range[j],
                "humidity": humidity_range[i]
            }
            result = fis.infer(inputs)
            Z[i, j] = result['fan_speed']
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none', alpha=0.8)
    
    ax.set_xlabel('Temperature (°C)')
    ax.set_ylabel('Humidity (%)')
    ax.set_zlabel('Fan Speed (%)')
    ax.set_title('3D Surface Plot of Temperature Control System')
    
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()