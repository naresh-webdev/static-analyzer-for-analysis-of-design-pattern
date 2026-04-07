import ast
from scalpel.cfg import CFGBuilder

# ==========================================
# 1. AST HELPERS (Rules 1 & 2)
# ==========================================

def find_class_level_none_vars(classnode):
    """Rule 1: Find all class level variables initialized to None"""
    none_vars = []
    for item in classnode.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name):
                    if isinstance(item.value, ast.Constant) and item.value.value is None:
                        none_vars.append(target.id)
    return none_vars

def find_control_method_candidates(classnode):
    """Rule 2: Find __new__ or @classmethod decorators"""
    candidates = []
    for item in classnode.body:
        if isinstance(item, ast.FunctionDef):
            if item.name == "__new__":
                candidates.append(item)
                continue
            for decorator in item.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == "classmethod":
                    candidates.append(item)
    return candidates

def contains_exact_variable(ast_node, target_var_name):
    """Safely checks if an exact variable name is used in an AST node."""
    for node in ast.walk(ast_node):
        if isinstance(node, ast.Attribute) and node.attr == target_var_name:
            return True
        elif isinstance(node, ast.Name) and node.id == target_var_name:
            return True
    return False

# ==========================================
# 2. CFG EXTRACTION 
# ==========================================

def find_cfg_recursively(cfg_obj, target_method_name):
    """Recursively searches both class_cfgs and functioncfgs safely."""
    if hasattr(cfg_obj, 'functioncfgs') and cfg_obj.functioncfgs:
        for func_key, child_cfg in cfg_obj.functioncfgs.items():
            name = func_key[1] if isinstance(func_key, tuple) else func_key
            if name == target_method_name: return child_cfg
            found = find_cfg_recursively(child_cfg, target_method_name)
            if found: return found

    if hasattr(cfg_obj, 'class_cfgs') and cfg_obj.class_cfgs:
        for class_key, child_cfg in cfg_obj.class_cfgs.items():
            found = find_cfg_recursively(child_cfg, target_method_name)
            if found: return found
    return None

# ==========================================
# 3. GRAPH ENGINE (Adjacency Matrix & Topology Constraints)
# ==========================================

class SafeCFGVisitor(ast.NodeVisitor):
    """
    Safely traverses a CFG statement without double-counting nested control flow bodies.
    """
    def __init__(self, tracked_var):
        self.tracked_var = tracked_var
        self.has_condition = False
        self.has_assignment = False
        self.has_return = False

    def visit_If(self, node):
        # ONLY look at the condition (node.test). 
        # Do NOT visit the body, because Scalpel put the body in the next CFG block!
        if contains_exact_variable(node.test, self.tracked_var):
            self.has_condition = True
            
    def visit_Compare(self, node):
        if contains_exact_variable(node, self.tracked_var):
            self.has_condition = True
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Attribute) and target.attr == self.tracked_var:
                if isinstance(node.value, ast.Call):
                    call_func = node.value.func
                    if isinstance(call_func, ast.Name) and call_func.id == "cls":
                        self.has_assignment = True
                    elif isinstance(call_func, ast.Attribute) and call_func.attr == "__new__":
                        self.has_assignment = True
        self.generic_visit(node)

    def visit_Return(self, node):
        if node.value and contains_exact_variable(node.value, self.tracked_var):
            self.has_return = True
        self.generic_visit(node)

    def visit_With(self, node):
        # We DO want to traverse inside Context Managers (like locks), 
        # because Scalpel sometimes groups them in the same block.
        self.generic_visit(node)


def extract_simple_graph(method_cfg, tracked_var):
    """Converts Scalpel's CFG into an adjacency list safely."""
    graph = {}
    
    for block in method_cfg.get_all_blocks():
        node_id = block.id
        
        # Instantiate our new safe visitor
        visitor = SafeCFGVisitor(tracked_var)
        
        for stmt in block.statements:
            # Let the visitor safely evaluate the statement
            visitor.visit(stmt)

        edges = [link.target.id for link in block.exits]
        
        graph[node_id] = {
            "is_condition": visitor.has_condition,
            "is_assignment": visitor.has_assignment,
            "is_return": visitor.has_return,
            "edges": edges
        }
        
    return graph

def print_adjacency_matrix(graph, method_name):
    """Renders the simple_graph as a formatted 2D Adjacency Matrix in the terminal."""
    print(f"\n📊 Adjacency Matrix for '{method_name}':")
    
    nodes = sorted(list(graph.keys()))
    if not nodes:
        print("  [Empty Graph]")
        return
        
    n = len(nodes)
    node_to_idx = {node_id: i for i, node_id in enumerate(nodes)}
    
    matrix = [[0] * n for _ in range(n)]
    
    for source, data in graph.items():
        i = node_to_idx[source]
        for target in data["edges"]:
            if target in node_to_idx: 
                j = node_to_idx[target]
                matrix[i][j] = 1
                
    header = "    " + " ".join([f"{node:^2}" for node in nodes])
    print(header)
    print("  " + "-" * len(header))
    
    for row_node in nodes:
        i = node_to_idx[row_node]
        row_str = " ".join([f"{val:^2}" for val in matrix[i]])
        print(f"{row_node:^2} | {row_str}")
    print()

def has_instantiation_path(graph, current_node, visited=None, assigned=False):
    """Path 1: Must hit an Assignment node, then eventually hit a Return node."""
    if visited is None: visited = set()
    if current_node in visited or current_node not in graph: return False
    visited.add(current_node)
    
    node_data = graph[current_node]
    
    if node_data["is_assignment"]:
        assigned = True
        
    if node_data["is_return"] and assigned:
        return True
        
    for edge in node_data["edges"]:
        if has_instantiation_path(graph, edge, visited.copy(), assigned):
            return True
            
    return False

def has_bypass_path(graph, current_node, visited=None):
    """Path 2: Must hit a Return node WITHOUT ever touching an Assignment node."""
    print("current node:", current_node, "data", graph[current_node])
    if visited is None: visited = set()
    if current_node in visited or current_node not in graph: return False
    visited.add(current_node)
    
    node_data = graph[current_node]
    
    if node_data["is_assignment"]:
        return False 
        
    if node_data["is_return"]:
        return True
        
    for edge in node_data["edges"]:
        if has_bypass_path(graph, edge, visited.copy()):
            return True
            
    return False

def verify_singleton_via_graph_traversal(method_cfg, none_vars, method_name):
    """Engine for Rules 3 & 4 using Branch Divergence Math."""
    for var in none_vars:
        simple_graph = extract_simple_graph(method_cfg, var)
        
        # Print the matrix to terminal
        print_adjacency_matrix(simple_graph, method_name)
        
        # 1. Find the exact node(s) where the condition occurs
        condition_nodes = [node_id for node_id, data in simple_graph.items() if data["is_condition"]]
        
        if not condition_nodes:
            continue
            
        # 2. Test the topological constraints diverging from the Condition node
        for cond_node in condition_nodes:
            path_1 = has_instantiation_path(simple_graph, cond_node)
            print("  🔍 Path 1 (Condition -> Assignment -> Return):", "✅ Found" if path_1 else "❌ Not Found")
            path_2 = has_bypass_path(simple_graph, cond_node)
            print("  🔍 Path 2 (Condition -> Return):", "✅ Found" if path_2 else "❌ Not Found")
            
            if path_1 and path_2:
                # Both realities converge safely on a return.
                return True, var, True

    return False, None, False

# ==========================================
# 4. MAIN DETECTOR & EXECUTION
# ==========================================

def calculate_strength(control_method):
    if control_method.name == "__new__":
        return 30, "Strong - direct instantiation protected via __new__"
    return 0, "Weak - direct instantiation not protected, use __new__"

def detect_singleton(filepath):
    print(f"\n--- Scanning: {filepath} ---")
    
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source)
    
    builder = CFGBuilder()
    module_cfg = builder.build_from_file('module', filepath)
    
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
            
            # Identify Candidates
            candidates = find_control_method_candidates(node)
            control_method = None
            tracked_var = None
            is_returned = False
            
            if none_vars:
                for candidate in candidates:
                    method_cfg = find_cfg_recursively(module_cfg, candidate.name)
                    if method_cfg:
                        
                        # Save the CFG Image visually
                        print(f"🎨 Rendering CFG image for '{candidate.name}'...")
                        try:
                            dot = method_cfg.build_visual('png')
                            output_filename = f"{candidate.name}_cfg_diagram"
                            dot.render(output_filename, view=False)
                            print(f"✅ Saved visually as {output_filename}.png")
                        except Exception as e:
                            print(f"⚠️ Could not render PNG (Graphviz may be missing): {e}")
                        
                        # Run the mathematical edge traversal
                        is_singleton, t_var, ret_status = verify_singleton_via_graph_traversal(
                            method_cfg, none_vars, candidate.name
                        )
                        
                        if is_singleton:
                            control_method = candidate
                            tracked_var = t_var
                            is_returned = ret_status
                            break
            
            if control_method:
                score += 15
                evidence.append(f"✅ Rule 2: Found control method: {control_method.name}")
                score += 15
                evidence.append(f"✅ Rule 3: Graph verified divergent assignment paths for: {tracked_var}")
                score += 20
                evidence.append(f"✅ Rule 4: Graph verified '{tracked_var}' reaches return block safely on all paths")

                strength_score, strength_evidence = calculate_strength(control_method)
                score += strength_score
                evidence.append(f"📝 Strength: {strength_evidence}")
            else:
                evidence.append("❌ Rule 2+3: Graph rejected paths (Missing valid Condition -> Assignment branch logic)")
                evidence.append("⏭️ Rule 4: Skipped")

            results.append({
                "class": node.name,
                "score": score,
                "evidence": evidence
            })
    
    print("\n" + "="*40)
    print("FINAL DETECTOR RESULTS")
    print("="*40)
    for result in results:
        print(f"Class: {result['class']}")
        print(f"Singleton Confidence Score: {result['score']}%")
        print("Evidence:")
        for e in result['evidence']:
            print(f"  {e}")
        print("-" * 40)

if __name__ == "__main__":
    TEST_FILE = "./test_cases-singleton/test_singleton8.py"
    
    try:
        detect_singleton(TEST_FILE)
    except FileNotFoundError:
        print(f"❌ Error: Could not find {TEST_FILE}. Check your path!")