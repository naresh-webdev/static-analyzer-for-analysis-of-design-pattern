import ast
from scalpel.cfg import CFGBuilder

# ============================================================
# CORE UTILITY
# ============================================================

def build_cfg(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source)
    cfg = CFGBuilder().build_from_src("observer", source)
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
# DYNAMIC RULES ENGINE
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
# MAIN DETECTOR
# ============================================================

def detect_observer(filepath):
    print(f"\n{'='*60}")
    print(f"🚀 RUNNING DYNAMIC OBSERVER ANALYZER: {filepath}")
    print(f"{'='*60}")
    
    try:
        tree, module_cfg = build_cfg(filepath)
    except FileNotFoundError:
        print(f"❌ Error: Could not find {filepath}")
        return

    evidence = []
    passed = True
    subject_class = None
    list_name = None

    # Rule 1
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            r1, lst = check_rule1(node)
            if r1:
                subject_class = node
                list_name = lst
                evidence.append(f"✅ Rule 1 (State): Subject '{node.name}' initializes tracking collection: 'self.{list_name}'")
                break
    
    if not subject_class:
        passed = False
        evidence.append("❌ Rule 1: No subject class with tracking collection found.")

    # Rule 2
    if passed:
        r2, reg_methods = check_rule2(subject_class, list_name)
        if r2:
            evidence.append(f"✅ Rule 2 (Registration): Found methods appending to collection: {reg_methods}")
        else:
            passed = False
            evidence.append(f"❌ Rule 2: Nothing adds items to 'self.{list_name}'.")

    # Rule 3
    if passed:
        r3, notify_method, target_method = check_rule3(subject_class, list_name)
        if r3:
            evidence.append(f"✅ Rule 3 (Broadcast): Method '{notify_method}()' loops over collection and delegates to '.{target_method}()'")
        else:
            passed = False
            evidence.append(f"❌ Rule 3: No method broadcasts a loop over 'self.{list_name}'.")

    # Rule 4
    if passed:
        r4, observers = check_rule4(tree, subject_class.name, target_method)
        if r4:
            evidence.append(f"✅ Rule 4 (Listeners): Found {len(observers)} classes implementing '{target_method}()': {observers}")
        else:
            passed = False
            evidence.append(f"❌ Rule 4: No other classes implement the expected listener method '{target_method}()'.")

    # Rule 5
    if passed:
        r5 = check_rule5_cfg(module_cfg, subject_class.name, target_method)
        if r5:
            evidence.append(f"✅ Rule 5 (CFG Verification): Graph mathematically confirms '.{target_method}()' execution path exists.")
        else:
            passed = False
            evidence.append(f"❌ Rule 5: CFG could not verify an execution path for '.{target_method}()'.")

    # Results
    print(f"\n📊 DETECTOR VERDICT:")
    if passed:
        print(f"✅ PASSED - Observer Pattern verified dynamically.")
    else:
        print(f"❌ FAILED - Observer Pattern incomplete.")
        
    print("\n🔍 ARCHITECTURAL EVIDENCE:")
    for e in evidence:
        print(f"  {e}")

if __name__ == "__main__":
    detect_observer("test_observer1.py")