"""
src/fis.py

Main fuzzy inference system implementation
"""
from typing import Dict, List
from utils.polygon import Polygon, combinePolygons
from utils.centroid import get_centroid
from src.rule import FuzzyRule, RuleParser

class FuzzyInferenceSystem:
    def __init__(self):
        self.input_variables: Dict[str, object] = {}
        self.output_variables: Dict[str, object] = {}
        self.rules: List[FuzzyRule] = []
        self.rule_parser = RuleParser()
    
    def add_input_variable(self, variable):
        """Add an input linguistic variable"""
        self.input_variables[variable.name] = variable
    
    def add_output_variable(self, variable):
        """Add an output linguistic variable"""
        self.output_variables[variable.name] = variable
    
    def add_rule(self, rule: FuzzyRule):
        """Add a single rule"""
        self.rules.append(rule)
    
    def add_rules_from_string(self, rules_str: str):
        """Parse and add multiple rules from a string"""
        parsed_rules = self.rule_parser.parse_rules(rules_str)
        self.rules.extend(parsed_rules)
    
    def infer(self, inputs: Dict[str, float]) -> Dict[str, float]:
        """
        Perform fuzzy inference and return defuzzified outputs
        """
        # Validate inputs
        for var_name in inputs:
            if var_name not in self.input_variables:
                raise ValueError(f"Input variable '{var_name}' not defined")
        
        # Initialize output aggregation
        output_aggregations = {}
        for var_name, variable in self.output_variables.items():
            output_aggregations[var_name] = {}
        
        # Evaluate rules
        for rule in self.rules:
            # Calculate rule activation
            activation = rule.evaluate(inputs, self.input_variables)
            
            # Apply activation to consequent
            var_name, label, operator = rule.consequent
            
            if var_name not in self.output_variables:
                raise ValueError(f"Output variable '{var_name}' not defined")
            
            if operator == "is":
                mem_fn = self.output_variables[var_name].membership_functions[label]
                portion_points = mem_fn.generatePortionPoints(activation)
                
                # Store points for aggregation
                if label not in output_aggregations[var_name]:
                    output_aggregations[var_name][label] = portion_points
                else:
                    # Aggregate using max (already implemented in combinePolygons)
                    current_polygon = Polygon(output_aggregations[var_name][label])
                    new_polygon = Polygon(portion_points)
                    combined = combinePolygons(current_polygon, new_polygon)
                    output_aggregations[var_name][label] = combined.points
            elif operator == "is not":
                # Handling negation is more complex and not implemented here
                raise ValueError("Negation in consequent not supported")
        
        # Defuzzify using centroid method
        defuzzified = {}
        for var_name, aggregation in output_aggregations.items():
            if not aggregation:
                # No rules fired for this variable
                defuzzified[var_name] = 0.0
                continue
            
            # Combine all labels for the variable
            combined_polygon = None
            for label, points in aggregation.items():
                polygon = Polygon(points)
                if combined_polygon is None:
                    combined_polygon = polygon
                else:
                    combined_polygon = combinePolygons(combined_polygon, polygon)
            
            # Calculate centroid
            centroid = get_centroid(combined_polygon)
            defuzzified[var_name] = centroid.x
        
        return defuzzified