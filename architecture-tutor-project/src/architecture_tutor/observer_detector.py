import ast
import importlib
import numpy as np

# ============================================================
# CORE UTILITY (Unchanged)
# ============================================================

def build_cfg(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source)

    cfg = None
    try:
        cfg_module = importlib.import_module("scalpel.cfg")
        cfg_builder_cls = getattr(cfg_module, "CFGBuilder")
        cfg = cfg_builder_cls().build_from_src("observer", source)
    except (ImportError, AttributeError):
        # Scalpel is optional; Rule 5 will be skipped if CFG cannot be built.
        cfg = None

    return tree, cfg

def find_cfg_recursively(cfg_obj, target_class_name):
    """Safely extracts a class CFG from Scalpel's nested dictionary."""
    if hasattr(cfg_obj, 'class_cfgs') and cfg_obj.class_cfgs:
        if target_class_name in cfg_obj.class_cfgs:
            return cfg_obj.class_cfgs[target_class_name]
        for _, child_cfg in cfg_obj.class_cfgs.items():
            found = find_cfg_recursively(child_cfg, target_class_name)
            if found: return found
    return None

# ============================================================
# DYNAMIC RULES ENGINE (Unchanged)
# ============================================================

def check_rule1(classnode):
    """Rule 1: Dynamically find ANY list or set initialized to track state."""
    for item in classnode.body:
        if isinstance(item, ast.FunctionDef) and item.name == "__init__":
            for stmt in ast.walk(item):
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Attribute) and getattr(target.value, 'id', '') == 'self':
                            # Check for [] or set() or list()
                            if isinstance(stmt.value, ast.List) or \
                               (isinstance(stmt.value, ast.Call) and getattr(stmt.value.func, 'id', '') in ('set', 'list')):
                                return True, target.attr 
    return False, None

def check_rule2(classnode, list_name):
    """Rule 2: Find ANY method that appends/adds to the tracked collection."""
    registration_methods = []
    for item in classnode.body:
        if isinstance(item, ast.FunctionDef) and item.name != "__init__":
            for stmt in ast.walk(item):
                if isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Attribute):
                    # Support both list.append() and set.add()
                    if stmt.func.attr in ("append", "add"):
                        if isinstance(stmt.func.value, ast.Attribute) and stmt.func.value.attr == list_name:
                            registration_methods.append(item.name)
                            
    return len(registration_methods) > 0, registration_methods

def check_rule3(classnode, list_name):
    """
    Rule 3: Find ANY method that loops over the collection and calls a method.
    Returns the discovered notification method and the target observer method.
    """
    for item in classnode.body:
        if isinstance(item, ast.FunctionDef):
            for stmt in ast.walk(item):
                if isinstance(stmt, ast.For):
                    # Check if the loop iterates over our tracked list
                    if isinstance(stmt.iter, ast.Attribute) and stmt.iter.attr == list_name:
                        loop_var = stmt.target.id if isinstance(stmt.target, ast.Name) else None
                        
                        if loop_var:
                            # Look inside the loop for: loop_var.method()
                            for sub_stmt in ast.walk(stmt):
                                if isinstance(sub_stmt, ast.Call) and isinstance(sub_stmt.func, ast.Attribute):
                                    if getattr(sub_stmt.func.value, 'id', '') == loop_var:
                                        # We dynamically discovered the target method (e.g. 'update')!
                                        target_method = sub_stmt.func.attr
                                        return True, item.name, target_method
    return False, None, None

def check_rule4(tree, subject_name, target_method_name):
    """Rule 4: Check if other classes actually implement the discovered target method."""
    observers = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name != subject_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == target_method_name:
                    observers.append(node.name)
    return len(observers) > 0, observers

def check_rule5_cfg(module_cfg, subject_name, target_method_name):
    """Rule 5: Use CFG to mathematically prove the target method is called."""
    class_cfg = find_cfg_recursively(module_cfg, subject_name)
    if not class_cfg:
        return False
        
    for (block_id, fun_name), fun_cfg in class_cfg.functioncfgs.items():
        for block in fun_cfg.get_all_blocks():
            for stmt in block.statements:
                for node in ast.walk(stmt):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                        if node.func.attr == target_method_name:
                            return True
    return False

# ============================================================
# MATRIX EXTRACTION (Updated)
# ============================================================

def detect_observer(filepath):
    # Suppressing prints here so it is silent for the Master Tutor
    try:
        tree, module_cfg = build_cfg(filepath)
    except Exception: # Broad catch in case of parse/file errors
        return []

    results = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            
            # ---> THE GATEWAY <---
            r1, list_name = check_rule1(node)
            
            if r1:
                # We passed the gateway! Initialize the base vector
                # [Gateway, Registration, Broadcast, Listeners, CFG]
                features = [1, 0, 0, 0, 0]
                evidence = [f"✅ Gateway: Subject '{node.name}' initializes tracking collection 'self.{list_name}'"]
                suggestions = []

                # Rule 2
                r2, reg_methods = check_rule2(node, list_name)
                if r2:
                    features[1] = 1
                    evidence.append(f"✅ Registration: Found methods appending to collection: {reg_methods}")
                else:
                    suggestions.append(f"💡 Logic: No methods found that add items to 'self.{list_name}'.")

                # Rule 3
                r3, notify_method, target_method = check_rule3(node, list_name)
                if r3:
                    features[2] = 1
                    evidence.append(f"✅ Broadcast: '{notify_method}()' loops over collection and delegates to '.{target_method}()'")
                    
                    # Rule 4 & 5 ONLY make sense to check if Rule 3 found the target method
                    r4, observers = check_rule4(tree, node.name, target_method)
                    if r4:
                        features[3] = 1
                        evidence.append(f"✅ Listeners: Found {len(observers)} classes implementing '{target_method}()': {observers}")
                    else:
                        suggestions.append(f"💡 Ecosystem: No other classes implement the expected listener method '{target_method}()'.")

                    r5 = check_rule5_cfg(module_cfg, node.name, target_method)
                    if r5:
                        features[4] = 1
                        evidence.append(f"✅ Execution: CFG mathematically confirms '.{target_method}()' execution path exists.")
                    else:
                        suggestions.append(f"💡 Execution: CFG could not verify a guaranteed execution path for '.{target_method}()'.")
                else:
                    suggestions.append(f"💡 Logic: No method broadcasts a loop over 'self.{list_name}'.")

                # Convert to a Numpy Column Matrix
                feature_column_matrix = np.array(features).reshape(-1, 1)

                results.append({
                    "class": node.name,
                    "feature_matrix": feature_column_matrix,
                    "evidence": evidence,
                    "suggestions": suggestions
                })

    return results

if __name__ == "__main__":
    for i in range(1, 8):
        print(f"\n{'#'*80}")
        print("" + f"TEST CASE {i}".center(78) + " ")
        res = detect_observer(f"test_cases-observer/test{i}.py")  
        print("result : ", res)
        for r in res:
            print(f"Detected Observer in: {r['class']}")
            print(f"Feature Matrix:\n{r['feature_matrix']}")


'''
features[0] — Gateway (State Tracking): 1 if the subject initializes a list or set to track observers (e.g., self.listeners = []). If this is 0, the matrix returns empty.

features[1] — Registration: 1 if there is a method that actively appends or adds objects to that tracking collection (e.g., self.listeners.append(obj)).

features[2] — Broadcast (The Loop): 1 if a method iterates over the collection and invokes a specific target method on the items (e.g., for obs in self.listeners: obs.update()).

features[3] — Listeners (Ecosystem): 1 if at least one other class in the file actually implements that dynamically discovered target method (e.g., def update(self):).

features[4] — Execution (CFG Proof): 1 if the Control Flow Graph mathematically verifies that a valid execution path exists to trigger that target method.
'''