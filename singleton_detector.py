import ast
from scalpel.cfg import CFGBuilder

def build_cfg(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source)
    builder = CFGBuilder()
    cfg = builder.build_from_src("module", source)

    # print("FULL AST DUMP: ", ast.dump(tree, indent=2))  # --- undo for testing (0)
    return tree, cfg

def find_class_level_none_vars(classnode):
    """Rule 1: Find all class level variables initialized to None"""
    none_vars = []
    for item in classnode.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name):
                    if isinstance(item.value, ast.Constant) and item.value.value is None:
                        none_vars.append(target.id)

    # print("TESTING: Found class level None variables:", none_vars)             ----        undo for testing (1)
    return none_vars

def find_control_method(classnode, none_vars):
    candidates = []
    
    for item in classnode.body:
        if isinstance(item, ast.FunctionDef):
            if item.name == "__new__":
                candidates.append(item)
                continue
            for decorator in item.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == "classmethod":
                    candidates.append(item)
    
    for method in candidates:
        found, var = check_condition_and_assignment(method, none_vars)
        if found:
            return method, var  # ← return both
    
    return None, None  # ← both None if not found

def check_condition_and_assignment(method, none_vars):
    """Rule 3+4: Check if none_var is used in condition AND reassigned inside"""
    for stmt in ast.walk(method):
        if isinstance(stmt, ast.If):
            # Check if any of our tracked variables appear in the condition
            condition_src = ast.dump(stmt.test)
            for var in none_vars:
                if var in condition_src:
                    # Now check if that var is assigned inside the if body
                    for body_stmt in stmt.body:
                        if isinstance(body_stmt, ast.Assign):
                            for target in body_stmt.targets:
                                if isinstance(target, ast.Attribute):
                                    if target.attr == var:
                                        # Check if the value being assigned is a class instantiation
                                        if isinstance(body_stmt.value, ast.Call):
                                            # The call should reference cls or the class itself
                                            call_func = body_stmt.value.func
                                            if isinstance(call_func, ast.Name) and call_func.id == "cls":
                                                return True, var
                                            if isinstance(call_func, ast.Attribute) and call_func.attr == "__new__":
                                                return True, var
                                        return False, None  # assigned but not a class instance
    return False, None

def check_return(method, var):
    """Rule 4: Check if the tracked variable is returned"""
    for stmt in ast.walk(method):
        if isinstance(stmt, ast.Return):
            return_src = ast.dump(stmt.value)
            if var in return_src:
                return True
    return False

def calculate_strength(control_method):
    if control_method.name == "__new__":
        return 30, "Strong - direct instantiation protected via __new__"
    else:
        return 0, "Weak - direct instantiation not protected, use __new__"

def detect_singleton(filepath):
    tree, cfg = build_cfg(filepath)
    
    results = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            score = 0
            evidence = []
            
            # Rule 1
            none_vars = find_class_level_none_vars(node)
            if none_vars:
                score += 20
                evidence.append(f"✅ Rule 1: Found class level None variable(s): {none_vars}")
            else:
                evidence.append("❌ Rule 1: No class level None variable found")
            
            # Rule 2 + 3 combined
            control_method, tracked_var = find_control_method(node, none_vars)
            if control_method:
                score += 15
                evidence.append(f"✅ Rule 2: Found control method: {control_method.name}")
                score += 15
                evidence.append(f"✅ Rule 3: Condition + assignment found for: {tracked_var}")
                
                # Rule 4 only runs if Rule 2+3 passed
                if check_return(control_method, tracked_var):
                    score += 20
                    evidence.append(f"✅ Rule 4: Tracked variable '{tracked_var}' is returned")
                else:
                    evidence.append(f"❌ Rule 4: Control method found but returns wrong variable")

                # Strength calculation based on control method type
                strength_score, strength_evidence = calculate_strength(control_method)
                score += strength_score
                evidence.append(f"📝 Strength: {strength_evidence}")
            else:
                evidence.append("❌ Rule 2+3: No singleton control method found")
                evidence.append("⏭️ Rule 4: Skipped")

    
            results.append({
                "class": node.name,
                "score": score,
                "evidence": evidence
            })
    
    # Print results
    for result in results:
        print(f"\nClass: {result['class']}")
        print(f"Singleton Confidence Score: {result['score']}%")
        print("Evidence:")
        for e in result['evidence']:
            print(f"  {e}")

detect_singleton("test_singleton.py")