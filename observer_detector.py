import ast
from scalpel.cfg import CFGBuilder

# ============================================================
# CORE UTILITY: Build AST tree and CFG from a Python file
# ============================================================

def build_cfg(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source)
    # build_from_file gives us class_cfgs which contains per-method CFGs
    cfg = CFGBuilder().build_from_file("observer", filepath)
    return tree, cfg

# ============================================================
# RULE 1: Subject class must have a list in __init__
# This list will store observer objects
# e.g. self._subscribers = []
# ============================================================

def check_rule1(classnode):
    for item in classnode.body:
        if isinstance(item, ast.FunctionDef) and item.name == "__init__":
            for stmt in ast.walk(item):
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        # Must be self.something = []
                        if isinstance(target, ast.Attribute):
                            if isinstance(stmt.value, ast.List):
                                return True, target.attr  # return list name e.g. '_subscribers'
    return False, None

# ============================================================
# RULE 2: Subject must have attach() that appends to the list
# This is how observers register themselves
# e.g. self._subscribers.append(observer)
# ============================================================

def check_rule2(classnode, list_name):
    for item in classnode.body:
        if isinstance(item, ast.FunctionDef) and item.name == "attach":
            for stmt in ast.walk(item):
                if isinstance(stmt, ast.Call):
                    if isinstance(stmt.func, ast.Attribute):
                        # Must be calling .append()
                        if stmt.func.attr == "append":
                            if isinstance(stmt.func.value, ast.Attribute):
                                # Must be appending to our tracked list
                                if stmt.func.value.attr == list_name:
                                    return True
    return False

# ============================================================
# RULE 3: notify() must loop over the observer list
# Either directly or via a helper method (one level deep)
# e.g. for observer in self._subscribers: ...
# ============================================================

def check_rule3(classnode, list_name):
    notify_method = None
    helper_methods = []
    
    # Collect notify() and all other methods as potential helpers
    for item in classnode.body:
        if isinstance(item, ast.FunctionDef):
            if item.name == "notify":
                notify_method = item
            else:
                helper_methods.append(item)
    
    if not notify_method:
        return False
    
    # Case 1: notify() directly loops over the list
    for stmt in ast.walk(notify_method):
        if isinstance(stmt, ast.For):
            if isinstance(stmt.iter, ast.Attribute):
                if stmt.iter.attr == list_name:
                    return True
    
    # Case 2: notify() calls a helper method that loops
    # e.g. notify() calls self.__update_all() which has the loop
    for stmt in ast.walk(notify_method):
        if isinstance(stmt, ast.Call):
            if isinstance(stmt.func, ast.Attribute):
                called_method = stmt.func.attr
                for helper in helper_methods:
                    if helper.name == called_method:
                        for s in ast.walk(helper):
                            if isinstance(s, ast.For):
                                if isinstance(s.iter, ast.Attribute):
                                    if s.iter.attr == list_name:
                                        return True
    return False

# ============================================================
# RULE 4: At least one other class must have an update() method
# This is the Observer class that reacts to notifications
# e.g. class Client: def update(self): ...
# ============================================================

def check_rule4(tree, subject_name):
    observers = []
    for node in ast.walk(tree):
        # Skip the subject class itself
        if isinstance(node, ast.ClassDef) and node.name != subject_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "update":
                    observers.append(node.name)
    return len(observers) > 0, observers

# ============================================================
# RULE 5: CFG analysis confirms update() is actually called
# somewhere in the subject class (directly or via helper)
# This uses Scalpel's CFG block analysis - stronger than pure AST
# because it verifies actual execution paths, not just structure
#
# LIMITATION: Currently checks all methods in subject class.
# A stricter version would trace only from notify() forward.
# Full interprocedural analysis via call graph is a future enhancement.
# ============================================================

def check_rule5_cfg(cfg, subject_name):
    if subject_name in cfg.class_cfgs:
        class_cfg = cfg.class_cfgs[subject_name]
        # Iterate through all method CFGs in the subject class
        for (block_id, fun_name), fun_cfg in class_cfg.functioncfgs.items():
            # Get all CFG blocks including nested ones (e.g. inside for loops)
            for block in fun_cfg.get_all_blocks():
                for stmt in block.statements:
                    # Look for expression statements that are calls
                    if isinstance(stmt, ast.Expr):
                        if isinstance(stmt.value, ast.Call):
                            if isinstance(stmt.value.func, ast.Attribute):
                                # Check if the call is to update()
                                if stmt.value.func.attr == "update":
                                    return True
    return False

# ============================================================
# MAIN DETECTOR: Runs all 5 rules and reports result
# All 5 rules must pass for Observer pattern to be confirmed
# ============================================================

def detect_observer(filepath):
    tree, cfg = build_cfg(filepath)
    
    evidence = []
    passed = True
    subject_class = None
    list_name = None

    # Rule 1: Find subject class with observer list
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            r1, lst = check_rule1(node)
            if r1:
                subject_class = node
                list_name = lst
                evidence.append(f"✅ Rule 1: Subject '{node.name}' has observer list: '{list_name}'")
                break
    
    if not subject_class:
        passed = False
        evidence.append("❌ Rule 1: No subject class with observer list found")

    # Rule 2: attach() must append to observer list
    if passed:
        r2 = check_rule2(subject_class, list_name)
        if r2:
            evidence.append(f"✅ Rule 2: attach() appends to '{list_name}'")
        else:
            passed = False
            evidence.append("❌ Rule 2: No valid attach() method found")

    # Rule 3: notify() must loop over observer list
    if passed:
        r3 = check_rule3(subject_class, list_name)
        if r3:
            evidence.append(f"✅ Rule 3: notify() loops over '{list_name}'")
        else:
            passed = False
            evidence.append("❌ Rule 3: notify() does not loop over observer list")

    # Rule 4: At least one observer class with update() must exist
    if passed:
        r4, observers = check_rule4(tree, subject_class.name)
        if r4:
            evidence.append(f"✅ Rule 4: Observer class(es) with update(): {observers}")
        else:
            passed = False
            evidence.append("❌ Rule 4: No observer class with update() found")

    # Rule 5: CFG confirms update() is actually called in subject
    if passed:
        r5 = check_rule5_cfg(cfg, subject_class.name)
        if r5:
            evidence.append("✅ Rule 5: CFG confirms notify() calls update()")
        else:
            passed = False
            evidence.append("❌ Rule 5: CFG could not confirm notify() calls update()")

    # Print final results
    print(f"\n{'='*50}")
    if passed:
        print("OBSERVER PATTERN DETECTED ✅")
    else:
        print("NO OBSERVER PATTERN DETECTED ❌")
    print("Evidence:")
    for e in evidence:
        print(f"  {e}")

detect_observer("test_observer1.py")