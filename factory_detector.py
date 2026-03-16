import ast
from scalpel.cfg import CFGBuilder

# ============================================================
# CORE UTILITIES
# ============================================================

def build_cfg(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source)
    builder = CFGBuilder()
    cfg = builder.build_from_src("module", source)
    return tree, cfg

# ============================================================
# VARIANT 1: SIMPLE FACTORY (if/elif branching)
# ============================================================

def check_simple_factory(classnode):
    """Detect simple factory - if/elif branching returning different types"""
    for item in classnode.body:
        if isinstance(item, ast.FunctionDef):
            # Rule 1: method has parameter besides self/cls
            args = [a.arg for a in item.args.args if a.arg not in ('self', 'cls')]
            if not args:
                continue
            
            # Rule 2: has if/elif branching
            has_branch = any(isinstance(s, ast.If) for s in ast.walk(item))
            if not has_branch:
                continue
            
            # Rule 3+4: returns multiple different object types
            returned_types = []
            for stmt in ast.walk(item):
                if isinstance(stmt, ast.Return):
                    if stmt.value and isinstance(stmt.value, ast.Call):
                        if isinstance(stmt.value.func, ast.Name):
                            returned_types.append(stmt.value.func.id)
            
            if len(returned_types) >= 2 and len(returned_types) == len(set(returned_types)):
                return True, {
                    "method": item.name,
                    "params": args,
                    "returns": returned_types
                }
    
    return False, None

# ============================================================
# VARIANT 2: REGISTRY FACTORY (dictionary based)
# ============================================================

def check_registry_factory(classnode):
    """Detect registry factory - dictionary mapping to class references"""
    # Rule 1+2: find class level dictionary with class references as values
    registry_name = None
    for item in classnode.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name):
                    if isinstance(item.value, ast.Dict):
                        if all(isinstance(v, ast.Name) for v in item.value.values):
                            registry_name = target.id
    
    if not registry_name:
        return False, None
    
    # Rule 3+4: method does dictionary lookup and calls the result
    for item in classnode.body:
        if isinstance(item, ast.FunctionDef):
            for stmt in ast.walk(item):
                if isinstance(stmt, ast.Return):
                    if stmt.value and isinstance(stmt.value, ast.Call):
                        func = stmt.value.func
                        if isinstance(func, ast.Subscript):
                            if isinstance(func.value, ast.Attribute):
                                if func.value.attr == registry_name:
                                    return True, {
                                        "method": item.name,
                                        "registry": registry_name
                                    }
    
    return False, None

# ============================================================
# VARIANT 3: TRUE FACTORY METHOD (abstract + inheritance)
# ============================================================

def check_true_factory(tree):
    """Detect true factory method - abstract class + subclass overrides"""
    # Rule 1+2: find abstract base class with abstract method
    abstract_classes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
            if 'ABC' in bases:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        for decorator in item.decorator_list:
                            if isinstance(decorator, ast.Name) and decorator.id == 'abstractmethod':
                                abstract_classes[node.name] = item.name
    
    if not abstract_classes:
        return False, None
    
    # Rule 3+4: find subclasses that override abstract method and return instance
    subclasses = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
            for abstract_class, abstract_method in abstract_classes.items():
                if abstract_class in bases:
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == abstract_method:
                            for stmt in ast.walk(item):
                                if isinstance(stmt, ast.Return):
                                    if stmt.value and isinstance(stmt.value, ast.Call):
                                        subclasses.append(node.name)
    
    if len(subclasses) >= 2:
        return True, {
            "abstract_classes": abstract_classes,
            "concrete_classes": subclasses
        }
    
    return False, None

# ============================================================
# MAIN DETECTOR
# ============================================================

def detect_factory(filepath):
    tree, cfg = build_cfg(filepath)
    
    detected = False
    
    # Check Variant 3 first (strongest)
    r3, info3 = check_true_factory(tree)
    if r3:
        detected = True
        print(f"\n{'='*50}")
        print(f"FACTORY PATTERN DETECTED")
        print(f"Variant: True Factory Method (Strongest)")
        print(f"Strength Score: 100%")
        print(f"Evidence:")
        print(f"  ✅ Abstract creator(s): {info3['abstract_classes']}")
        print(f"  ✅ Concrete creators: {info3['concrete_classes']}")
    
    # Check Variant 2
    if not detected:
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                r2, info2 = check_registry_factory(node)
                if r2:
                    detected = True
                    print(f"\n{'='*50}")
                    print(f"FACTORY PATTERN DETECTED")
                    print(f"Class: {node.name}")
                    print(f"Variant: Registry Based (Medium)")
                    print(f"Strength Score: 75%")
                    print(f"Evidence:")
                    print(f"  ✅ Registry dictionary: '{info2['registry']}'")
                    print(f"  ✅ Factory method: '{info2['method']}'")
                    break
    
    # Check Variant 1
    if not detected:
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                r1, info1 = check_simple_factory(node)
                if r1:
                    detected = True
                    print(f"\n{'='*50}")
                    print(f"FACTORY PATTERN DETECTED")
                    print(f"Class: {node.name}")
                    print(f"Variant: Simple Factory (Weakest)")
                    print(f"Strength Score: 50%")
                    print(f"Evidence:")
                    print(f"  ✅ Factory method: '{info1['method']}'")
                    print(f"  ✅ Parameters: {info1['params']}")
                    print(f"  ✅ Returns: {info1['returns']}")
                    break
    
    if not detected:
        print("\nNo Factory pattern detected")

detect_factory("test_factory7.py")