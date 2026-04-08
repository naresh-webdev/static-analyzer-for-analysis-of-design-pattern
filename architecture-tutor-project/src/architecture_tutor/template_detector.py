import ast
import numpy as np

def map_ecosystem(tree):
    """Pass 1: Map all Abstract Base Classes and track class inheritance."""
    abcs = {} 
    subclasses = {} 
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            
            bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
            for base in bases:
                if base not in subclasses:
                    subclasses[base] = []
                subclasses[base].append(node.name)

            is_abc = 'ABC' in bases
            
            abstract_methods = []
            concrete_methods = []
            
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if any(isinstance(d, ast.Name) and d.id == 'abstractmethod' for d in item.decorator_list):
                        abstract_methods.append(item.name)
                    else:
                        if item.name != "__init__":
                            concrete_methods.append(item.name)
            
            if is_abc or abstract_methods:
                abcs[node.name] = {
                    "abstract_methods": abstract_methods,
                    "concrete_methods": concrete_methods,
                    "node": node
                }
                
    return abcs, subclasses

def extract_features(abc_name, template_method, called_abstracts, subclasses):
    """Pass 3: Build the Template Feature Vector."""
    
    # Base Vector: [Skeleton, Has_1_Subclass, Has_Multiple_Subclasses]
    features = [1, 0, 0] 
    
    evidence = [f"✅ Skeleton: '{template_method}()' orchestrates abstract steps: {called_abstracts}"]
    suggestions = []
    
    children = subclasses.get(abc_name, [])
    
    if len(children) >= 1:
        features[1] = 1
        evidence.append(f"✅ Implementation: Subclass '{children[0]}' implements the template.")
    else:
        suggestions.append(f"💡 Usage: You built the Template Class '{abc_name}', but no subclasses exist to implement the blanks.")

    if len(children) >= 2:
        features[2] = 1
        evidence.append(f"✅ Polymorphism: {len(children)} subclasses ({children}) share this master workflow.")
    elif len(children) == 1:
        suggestions.append("💡 Architecture: A template is best utilized when multiple subclasses share the workflow.")

    return features, evidence, suggestions

def detect_template_method(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        return []

    tree = ast.parse(source)
    abcs, subclasses = map_ecosystem(tree)
    results = []

    for abc_name, data in abcs.items():
        if not data["abstract_methods"] or not data["concrete_methods"]:
            continue 
            
        for item in data["node"].body:
            if isinstance(item, ast.FunctionDef) and item.name in data["concrete_methods"]:
                
                called_abstracts = set()
                for stmt in ast.walk(item):
                    if isinstance(stmt, ast.Call):
                        func = stmt.func
                        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == "self":
                            if func.attr in data["abstract_methods"]:
                                called_abstracts.add(func.attr)
                
                # ---> THE GATEWAY <---
                if called_abstracts:
                    feature_list, evidence, suggestions = extract_features(
                        abc_name, item.name, list(called_abstracts), subclasses
                    )
                    
                    # Convert to a Numpy Column Matrix
                    feature_column_matrix = np.array(feature_list).reshape(-1, 1)
                    
                    results.append({
                        "class": abc_name,
                        "template_method": item.name,
                        "feature_matrix": feature_column_matrix,
                        "evidence": evidence,
                        "suggestions": suggestions
                    })

    return results

if __name__ == "__main__":
    for i in range(1, 5):
        print(f"--- Analyzing test_cases-template/test{i}.py ---")
        results = detect_template_method(f"test_cases-template/test{i}.py")
        for res in results:
            print(f"Class: {res['class']}")
            print(f"Template Method: {res['template_method']}")
            print("Feature Matrix:")
            print(res["feature_matrix"])
            print("Evidence:")
            for ev in res["evidence"]:
                print(f"  - {ev}")
            if res["suggestions"]:
                print("Suggestions:")
                for sug in res["suggestions"]:
                    print(f"  - {sug}")
            print("\n")