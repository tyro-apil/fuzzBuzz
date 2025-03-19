"""
src/rule.py

Enhanced Rule representation and parsing with support for both AND and OR operations
"""
from typing import Dict, List, Tuple
import re

class FuzzyRule:
    def __init__(self, antecedents: List[Tuple[str, str, str, str]], consequent: Tuple[str, str, str]):
        """
        Initialize rule with antecedents and consequent
        Each antecedent is a tuple of (variable_name, label, operator, connector)
        where connector is either "AND", "OR", or None for the last antecedent
        Operator can be "is", "is not", etc.
        """
        self.antecedents = antecedents
        self.consequent = consequent
    
    def evaluate(self, input_values: Dict[str, float], linguistic_variables: Dict[str, object]) -> float:
        """
        Evaluate the rule for given input values and return activation degree
        Supports both AND and OR operations between antecedents
        """
        if not self.antecedents:
            return 1.0  # Empty rule always fires at maximum activation
        
        current_activation = None
        current_connector = None
        
        for i, (var_name, label, operator, connector) in enumerate(self.antecedents):
            if var_name not in input_values:
                raise ValueError(f"Input value for '{var_name}' not provided")
            
            if var_name not in linguistic_variables:
                raise ValueError(f"Linguistic variable '{var_name}' not found")
            
            value = input_values[var_name]
            membership = linguistic_variables[var_name].get_membership_degree(value, label)
            
            # Apply operator
            if operator == "is":
                condition_activation = membership
            elif operator == "is not":
                condition_activation = 1.0 - membership
            else:
                raise ValueError(f"Unsupported operator: {operator}")
            
            # First condition or apply connector
            if current_activation is None:
                current_activation = condition_activation
            elif current_connector == "AND":
                current_activation = min(current_activation, condition_activation)
            elif current_connector == "OR":
                current_activation = max(current_activation, condition_activation)
            else:
                raise ValueError(f"Unsupported connector: {current_connector}")
            
            # Update connector for next iteration
            current_connector = connector
        
        return current_activation


class RuleParser:
    def __init__(self):
        # Define regex patterns for rule components
        self.antecedent_pattern = r'([\w_]+)\s+(is|is not)\s+([\w_]+)'
    
    def parse_rule(self, rule_str: str) -> FuzzyRule:
        """
        Parse a rule string like "IF temperature IS hot AND humidity IS high THEN fan_speed IS fast"
        Also supports OR operator: "IF temperature IS hot OR humidity IS high THEN fan_speed IS fast"
        """
        # Split into antecedent and consequent parts
        parts = rule_str.split("THEN")
        if len(parts) != 2:
            raise ValueError("Rule must have exactly one THEN clause")
        
        antecedent_str = parts[0].strip()
        consequent_str = parts[1].strip()
        
        # Remove the "IF" keyword
        if antecedent_str.startswith("IF"):
            antecedent_str = antecedent_str[2:].strip()
        
        # Parse antecedents with connectors (AND/OR)
        antecedent_clauses = []
        remaining = antecedent_str
        
        while remaining:
            # Look for the next AND or OR
            and_pos = remaining.find(" AND ")
            or_pos = remaining.find(" OR ")
            
            if and_pos == -1 and or_pos == -1:
                # Last condition
                match = re.match(self.antecedent_pattern, remaining)
                if not match:
                    raise ValueError(f"Invalid antecedent clause: {remaining}")
                var_name, operator, label = match.groups()
                antecedent_clauses.append((var_name, label, operator, None))
                break
            elif (and_pos != -1 and or_pos == -1) or (and_pos != -1 and and_pos < or_pos):
                # AND connector
                clause = remaining[:and_pos]
                remaining = remaining[and_pos + 5:]  # Skip " AND "
                match = re.match(self.antecedent_pattern, clause)
                if not match:
                    raise ValueError(f"Invalid antecedent clause: {clause}")
                var_name, operator, label = match.groups()
                antecedent_clauses.append((var_name, label, operator, "AND"))
            else:
                # OR connector
                clause = remaining[:or_pos]
                remaining = remaining[or_pos + 4:]  # Skip " OR "
                match = re.match(self.antecedent_pattern, clause)
                if not match:
                    raise ValueError(f"Invalid antecedent clause: {clause}")
                var_name, operator, label = match.groups()
                antecedent_clauses.append((var_name, label, operator, "OR"))
        
        # Parse consequent
        match = re.match(self.antecedent_pattern, consequent_str)
        if not match:
            raise ValueError(f"Invalid consequent: {consequent_str}")
        
        var_name, operator, label = match.groups()
        consequent = (var_name, label, operator)
        
        return FuzzyRule(antecedent_clauses, consequent)
    
    def parse_rules(self, rules_str: str) -> List[FuzzyRule]:
        """Parse multiple rules separated by semicolons or newlines"""
        rules = []
        rule_strings = re.split(r'[;\n]+', rules_str)
        
        for rule_str in rule_strings:
            rule_str = rule_str.strip()
            if rule_str:  # Skip empty strings
                rules.append(self.parse_rule(rule_str))
        
        return rules