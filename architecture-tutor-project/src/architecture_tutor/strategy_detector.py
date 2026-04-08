import ast

def map_ecosystem(tree):
    """Pass 1: Scan the file to map out classes, methods, and ABCs."""
    abcs = {} 
    concrete_methods = {} 
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            is_abc = any(isinstance(b, ast.Name) and b.id == 'ABC' for b in node.bases)
            abstract_methods = []
            
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_name = item.name
                    if any(isinstance(d, ast.Name) and d.id == 'abstractmethod' for d in item.decorator_list):
                        abstract_methods.append(method_name)
                    else:
                        if method_name not in concrete_methods:
                            concrete_methods[method_name] = []
                        concrete_methods[method_name].append(node.name)
            
            if is_abc and abstract_methods:
                abcs[node.name] = abstract_methods
                
    return abcs, concrete_methods

def extract_features(context_name, injected_var, delegated_method, abcs, concrete_methods):
    """
    Pass 3: Instead of calculating a score, this builds our Feature Vector.
    Index 0: Basic Structure (Always 1 if this function is called)
    Index 1: Multiple Implementations
    Index 2: ABC Interface Used
    Index 3: Properly Type Hinted
    """
    # Start with a base vector of zeros. 
    # Index 0 is automatically 1 because composition/delegation was proven to reach this function.
    features = [1, 0, 0, 0] 
    
    evidence = [f"✅ Structural: '{context_name}' successfully injects state and delegates to '.{delegated_method}()'"]
    suggestions = []
    
    # Check 1: Multiple Implementations (Interchangeability)
    implementations = concrete_methods.get(delegated_method, [])
    if len(implementations) >= 2:
        features[1] = 1
        evidence.append(f"✅ Interchangeability: Found {len(implementations)} classes implementing '{delegated_method}()'")
    else:
        suggestions.append(f"💡 Architecture: Found fewer than 2 classes implementing '{delegated_method}()'.")

    # Check 2: Formal ABC Interface
    matching_abc = None
    for abc_name, abs_methods in abcs.items():
        if delegated_method in abs_methods:
            matching_abc = abc_name
            break

    if matching_abc:
        features[2] = 1
        evidence.append(f"✅ Contract: Strategies are governed by the formal ABC '{matching_abc}'")
        
        # Check 3: Type Hinting
        if injected_var["type_hint"] == matching_abc:
            features[3] = 1
            evidence.append(f"✅ Type Safety: Context explicitly type-hints the '{matching_abc}' interface")
        else:
            if injected_var["type_hint"]:
                suggestions.append(f"💡 Typing: Context is type-hinted as '{injected_var['type_hint']}', but interface is '{matching_abc}'.")
            else:
                suggestions.append(f"💡 Typing: Add type hinting to enforce the '{matching_abc}' contract.")
    else:
        suggestions.append(f"💡 Contract: You are relying on Duck-Typing. Create an `abc.ABC` interface to enforce a contract.")

    return features, evidence, suggestions

def detect_strategy(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        return []

    tree = ast.parse(source)
    abcs, concrete_methods = map_ecosystem(tree)
    results = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            injected_vars = {} 
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    for arg in item.args.args:
                        if arg.arg != 'self':
                            type_hint = arg.annotation.id if hasattr(arg, 'annotation') and isinstance(arg.annotation, ast.Name) else None
                            for stmt in ast.walk(item):
                                if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Name) and stmt.value.id == arg.arg:
                                    for target in stmt.targets:
                                        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                                            injected_vars[target.attr] = {"arg_name": arg.arg, "type_hint": type_hint}

            if injected_vars:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        for stmt in ast.walk(item):
                            if isinstance(stmt, ast.Call):
                                func = stmt.func
                                if isinstance(func, ast.Attribute):
                                    caller = func.value
                                    if isinstance(caller, ast.Attribute) and isinstance(caller.value, ast.Name) and caller.value.id == "self":
                                        if caller.attr in injected_vars:
                                            delegated_method = func.attr
                                            
                                            # ---> BUILD THE MATRIX HERE <---
                                            feature_list, evidence, suggestions = extract_features(
                                                node.name, injected_vars[caller.attr], delegated_method, abcs, concrete_methods
                                            )
                                            
                                            # Convert the feature list to a column-style list
                                            feature_column_matrix = [[value] for value in feature_list]
                                            
                                            results.append({
                                                "class": node.name,
                                                "feature_matrix": feature_column_matrix, # Return the math, not the score!
                                                "evidence": evidence,
                                                "suggestions": suggestions
                                            })
                                            break 

    return results

if __name__ == "__main__":
    for i in range(1, 8): 
        print(f"\n--- Testing File: ./test_cases-strategy/test{i}.py ---")
        res = detect_strategy(f"./test_cases-strategy/test{i}.py")
        for r in res:
            print(f"Detected Strategy in: {r['class']}")
            print(f"Feature Matrix (Column):\n{r['feature_matrix']}")
            print("Evidence:")
            for e in r['evidence']:
                print(f"  {e}")
            print("Suggestions:")
            for s in r['suggestions']:
                print(f"  {s}")