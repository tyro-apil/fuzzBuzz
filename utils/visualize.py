import matplotlib.pyplot as plt
import matplotlib.patches as patches
from .line import Point
from .polygon import Polygon, combinePolygons
import numpy as np
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection
import matplotlib.cm as cm
from matplotlib.gridspec import GridSpec


def plot_polygon_with_centroid(poly:Polygon, centroid: Point ):
    fig, ax = plt.subplots()
    polygon_vertices = [(point.x,point.y) for point in poly.points]
    point = (centroid.x,centroid.y)
    point_x, point_y = point[0],point[1]

    poly = patches.Polygon(polygon_vertices)
    ax.add_patch(poly)
    ax.scatter(point_x, point_y, color='red', label='Point')


    plt.xlim(0,10)
    plt.ylim(0,10)
    plt.grid()
    plt.show()

def visualize_membership_functions(linguistic_variable, input_value=None):
    """
    Visualize the membership functions of a linguistic variable
    """
    plt.figure(figsize=(10, 6))
    
    # Get the range of the variable
    x_min, x_max = linguistic_variable.range
    x = np.linspace(x_min, x_max, 1000)
    
    # Plot each membership function
    for label, mem_fn in linguistic_variable.membership_functions.items():
        y = [mem_fn.calculateMembershipDegree(val) for val in x]
        plt.plot(x, y, label=label)
        
        # If an input value is provided, plot the membership degree
        if input_value is not None:
            membership_degree = mem_fn.calculateMembershipDegree(input_value)
            if membership_degree > 0:
                plt.plot([input_value, input_value], [0, membership_degree], 'r--')
                plt.plot([x_min, input_value], [membership_degree, membership_degree], 'r--')
                plt.scatter(input_value, membership_degree, color='red')
                plt.text(input_value, membership_degree + 0.05, f'{membership_degree:.2f}', 
                         ha='center', va='bottom')
    
    plt.grid(True)
    plt.xlabel(linguistic_variable.name)
    plt.ylabel('Membership Degree')
    plt.title(f'Membership Functions for {linguistic_variable.name}')
    plt.legend()
    if input_value is not None:
        plt.axvline(x=input_value, color='r', linestyle='-', alpha=0.3)
        plt.text(input_value, 0.01, f'{input_value}', ha='center', va='bottom', color='red')
    plt.tight_layout()
    
    return plt

def visualize_rule_activation(fis, inputs):
    """
    Visualize the rule activation and the resulting output fuzzy sets
    """
    plt.figure(figsize=(12, 8))
    
    # Number of rules
    num_rules = len(fis.rules)
    
    # Create a color map for the rules
    colors = cm.rainbow(np.linspace(0, 1, num_rules))
    
    # For each output variable
    for var_name, output_var in fis.output_variables.items():
        # Get the range of the output variable
        x_min, x_max = output_var.range
        x = np.linspace(x_min, x_max, 1000)
        
        # Dictionary to store the activated output membership functions
        activated_mem_fns = {}
        rule_activations = []
        
        # For each rule, calculate the activation and plot the activated membership function
        for i, rule in enumerate(fis.rules):
            # Calculate rule activation
            activation = rule.evaluate(inputs, fis.input_variables)
            rule_activations.append(activation)
            
            # Get the consequent membership function
            consequent_var_name, consequent_label, _ = rule.consequent
            if consequent_var_name == var_name:
                mem_fn = output_var.membership_functions[consequent_label]
                
                # Generate the activated membership function (clipped or scaled)
                if activation > 0:
                    portion_points = mem_fn.generatePortionPoints(activation)
                    
                    # Store the activated membership function
                    if consequent_label not in activated_mem_fns:
                        activated_mem_fns[consequent_label] = []
                    activated_mem_fns[consequent_label].append((portion_points, activation, i))
        
        # Plot the original membership functions
        for label, mem_fn in output_var.membership_functions.items():
            y = [mem_fn.calculateMembershipDegree(val) for val in x]
            plt.plot(x, y, '--', label=f'{label} (original)', alpha=0.5)
        
        # Plot the activated membership functions
        activated_polygons = []
        for label, activations in activated_mem_fns.items():
            for portion_points, activation, rule_idx in activations:
                # Convert to numpy array for plotting
                xy = np.array([(p.x, p.y) for p in portion_points])
                poly = MplPolygon(xy, closed=True, alpha=0.5, facecolor=colors[rule_idx])
                activated_polygons.append(poly)
                plt.text(np.mean(xy[:, 0]), 0.1 + rule_idx * 0.1, 
                         f'Rule {rule_idx+1}: {activation:.2f}', 
                         ha='center', color=colors[rule_idx])
        
        # Add the activated polygons to the plot
        p = PatchCollection(activated_polygons, match_original=True)
        plt.gca().add_collection(p)
    
    plt.grid(True)
    plt.xlabel(var_name)
    plt.ylabel('Membership Degree')
    plt.title(f'Rule Activation for {var_name}')
    plt.legend()
    plt.tight_layout()
    
    return plt, rule_activations

def visualize_defuzzification(fis, inputs):
    """
    Visualize the defuzzification process with the aggregated output
    """
    plt.figure(figsize=(12, 8))
    
    # Initialize output aggregation
    output_aggregations = {}
    for var_name, variable in fis.output_variables.items():
        output_aggregations[var_name] = {}
    
    # Evaluate rules
    for rule in fis.rules:
        # Calculate rule activation
        activation = rule.evaluate(inputs, fis.input_variables)
        
        # Apply activation to consequent
        var_name, label, operator = rule.consequent
        
        if operator == "is":
            mem_fn = fis.output_variables[var_name].membership_functions[label]
            portion_points = mem_fn.generatePortionPoints(activation)
            
            # Store points for aggregation
            if label not in output_aggregations[var_name]:
                output_aggregations[var_name][label] = portion_points
            else:
                # Aggregate using max
                current_polygon = Polygon(output_aggregations[var_name][label])
                new_polygon = Polygon(portion_points)
                combined = combinePolygons(current_polygon, new_polygon)
                output_aggregations[var_name][label] = combined.points
    
    # Plot the aggregated output and defuzzified value
    for var_name, aggregation in output_aggregations.items():
        # Get the range of the output variable
        x_min, x_max = fis.output_variables[var_name].range
        x = np.linspace(x_min, x_max, 1000)
        
        # For each aggregated label
        for label, points in aggregation.items():
            # Convert to numpy array for plotting
            xy = np.array([(p.x, p.y) for p in points])
            plt.fill(xy[:, 0], xy[:, 1], alpha=0.3, label=f'{label} (activated)')
        
        # Calculate the defuzzified value
        defuzzified_value = fis.infer(inputs)[var_name]
        
        # Plot the defuzzified value
        plt.axvline(x=defuzzified_value, color='r', linestyle='-', label='Defuzzified value')
        plt.text(defuzzified_value, 0.5, f'{defuzzified_value:.2f}', 
                 ha='center', va='center', color='red',
                 bbox=dict(facecolor='white', alpha=0.8))
    
    plt.grid(True)
    plt.xlabel(var_name)
    plt.ylabel('Membership Degree')
    plt.title(f'Defuzzification for {var_name}')
    plt.legend()
    plt.tight_layout()
    
    return plt

def visualize_detailed_rule_activation(fis, inputs):
    """
    Visualize the detailed rule activation process, showing AND/OR operations
    """
    # Import required libraries if not already imported
    import numpy as np
    from matplotlib.gridspec import GridSpec
    import matplotlib.pyplot as plt
    
    # Count number of rules
    num_rules = len(fis.rules)
    
    # Create a figure with multiple subplots - one row per rule
    fig = plt.figure(figsize=(15, 4 * num_rules))
    gs = GridSpec(num_rules, 4, figure=fig)
    
    # For each rule
    for rule_idx, rule in enumerate(fis.rules):
        # Create a title for the rule
        rule_text = "IF "
        for i, (var_name, label, operator, connector) in enumerate(rule.antecedents):
            rule_text += f"{var_name} {operator} {label}"
            if connector is not None:
                rule_text += f" {connector} "
        rule_text += f" THEN {rule.consequent[0]} {rule.consequent[2]} {rule.consequent[1]}"
        
        fig.text(0.5, 1 - rule_idx * (1/num_rules) - 0.02, f"Rule {rule_idx+1}: {rule_text}", 
                 ha='center', va='center', fontsize=12, fontweight='bold')
        
        # Create subplots for each antecedent
        antecedent_values = []
        for i, (var_name, label, operator, connector) in enumerate(rule.antecedents):
            ax = fig.add_subplot(gs[rule_idx, i])
            
            # Get the linguistic variable
            var = fis.input_variables[var_name]
            
            # Get the membership function
            mem_fn = var.membership_functions[label]
            
            # Plot the membership function
            x_min, x_max = var.range
            x = np.linspace(x_min, x_max, 1000)
            y = np.array([mem_fn.calculateMembershipDegree(val) for val in x], dtype=float)
            ax.plot(x, y, label=label)
            
            # Plot the input value and its membership degree
            input_value = float(inputs[var_name])
            membership_degree = mem_fn.calculateMembershipDegree(input_value)
            
            # Apply operator
            if operator == "is":
                final_degree = membership_degree
            elif operator == "is not":
                final_degree = 1.0 - membership_degree
                ax.text(input_value, membership_degree + 0.1, f"1 - {membership_degree:.2f} = {final_degree:.2f}", 
                       ha='center', va='bottom')
            else:
                final_degree = membership_degree  # Default case
            
            antecedent_values.append(final_degree)
            
            # Plot vertical line for input value
            ax.axvline(x=input_value, color='r', linestyle='-', alpha=0.3)
            
            # Fill the area under the curve up to the membership degree
            if membership_degree > 0:
                # Avoid using where parameter - split the data manually
                x_before = np.array([x_val for x_val in x if x_val <= input_value], dtype=float)
                y_before = np.array([mem_fn.calculateMembershipDegree(x_val) for x_val in x_before], dtype=float)
                
                x_after = np.array([x_val for x_val in x if x_val > input_value], dtype=float)
                y_after = np.array([mem_fn.calculateMembershipDegree(x_val) for x_val in x_after], dtype=float)
                
                if len(x_before) > 0:
                    ax.fill_between(x_before, 0, y_before, alpha=0.3, color='green')
                
                if len(x_after) > 0:
                    ax.fill_between(x_after, 0, y_after, alpha=0.3, color='blue')
                
                # Plot the membership degree
                ax.plot([input_value, input_value], [0, membership_degree], 'r--')
                ax.plot([x_min, input_value], [membership_degree, membership_degree], 'r--')
                ax.scatter(input_value, membership_degree, color='red')
                
                # Show the value
                ax.text(input_value, 0.05, f'{input_value}', ha='center', va='bottom', color='red')
                ax.text(input_value, membership_degree + 0.05, f'{membership_degree:.2f}', 
                       ha='center', va='bottom')
            
            ax.set_title(f"{var_name} is {label}")
            ax.set_ylim(0, 1.1)
            ax.grid(True)
        
        # Create a subplot for the AND/OR operation
        ax = fig.add_subplot(gs[rule_idx, len(rule.antecedents)])
        
        # Calculate the final activation by applying AND/OR operators
        current_activation = antecedent_values[0]
        current_connector = rule.antecedents[0][3] if len(rule.antecedents) > 1 else None
        
        # Create a visual representation of the AND/OR operation
        bar_width = 0.3
        bars = ax.bar([0], [antecedent_values[0]], width=bar_width, label=f"Ant. 1: {antecedent_values[0]:.2f}")
        
        for i in range(1, len(antecedent_values)):
            prev_activation = current_activation
            
            if current_connector == "AND":
                current_activation = min(current_activation, antecedent_values[i])
                operation = "min"
            elif current_connector == "OR":
                current_activation = max(current_activation, antecedent_values[i])
                operation = "max"
            else:
                current_activation = antecedent_values[i]
                operation = "="
            
            bars = ax.bar([i], [antecedent_values[i]], width=bar_width, 
                         label=f"Ant. {i+1}: {antecedent_values[i]:.2f}")
            
            # Update connector for next iteration
            current_connector = rule.antecedents[i][3] if i < len(rule.antecedents) - 1 else None
        
        # Add the final activation bar
        bars = ax.bar([len(antecedent_values)], [current_activation], width=bar_width, color='red',
                     label=f"Final: {current_activation:.2f}")
        
        # Add operation labels
        for i in range(len(rule.antecedents)-1):
            connector = rule.antecedents[i][3]
            ax.text(i + 0.5, 0.5, connector, ha='center', va='center', fontsize=12, fontweight='bold')
        
        ax.set_xticks(range(len(antecedent_values) + 1))
        ax.set_xticklabels([f"Ant {i+1}" for i in range(len(antecedent_values))] + ["Final"])
        ax.set_ylim(0, 1.1)
        ax.set_title("Rule Activation")
        ax.grid(True)
        
        # Create a subplot for the consequent
        ax = fig.add_subplot(gs[rule_idx, len(rule.antecedents) + 1])
        
        # Get the consequent variable, label, and operator
        var_name, label, operator = rule.consequent
        var = fis.output_variables[var_name]
        mem_fn = var.membership_functions[label]
        
        # Plot the original membership function
        x_min, x_max = var.range
        x = np.linspace(x_min, x_max, 1000)
        y = np.array([mem_fn.calculateMembershipDegree(val) for val in x], dtype=float)
        ax.plot(x, y, '--', label=f'{label} (original)', alpha=0.5)
        
        # Plot the activated membership function
        if current_activation > 0:
            try:
                portion_points = mem_fn.generatePortionPoints(current_activation)
                if portion_points:
                    xy = np.array([(float(p.x), float(p.y)) for p in portion_points], dtype=float)
                    ax.fill(xy[:, 0], xy[:, 1], alpha=0.5, color='red', label=f'{label} (activated)')
            except:
                # If there's an error with the portion points, skip this part
                pass
            
            # Draw a horizontal line at the activation level
            ax.axhline(y=current_activation, color='r', linestyle='--', alpha=0.8)
            ax.text(x_min + 5, current_activation + 0.05, f'{current_activation:.2f}', 
                   ha='left', va='bottom', color='red')
        
        ax.set_title(f"{var_name} is {label}")
        ax.set_ylim(0, 1.1)
        ax.grid(True)
        ax.legend()
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.95)
    
    return fig
