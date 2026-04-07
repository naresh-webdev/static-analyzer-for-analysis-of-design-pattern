import ast

def map_ecosystem(tree):
    """
    Pass 1: Scan the entire file to map out the classes, their methods, 
    and identify any Abstract Base Classes (Interfaces).
    """
    abcs = {} # { ClassName: [abstract_methods] }
    concrete_methods = {} # { method_name: [ClassNames that implement it] }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            is_abc = any(isinstance(b, ast.Name) and b.id == 'ABC' for b in node.bases)
            abstract_methods = []
            
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_name = item.name
                    
                    # Track abstract methods
                    if any(isinstance(d, ast.Name) and d.id == 'abstractmethod' for d in item.decorator_list):
                        abstract_methods.append(method_name)
                    else:
                        # Track concrete methods for duck-typing analysis
                        if method_name not in concrete_methods:
                            concrete_methods[method_name] = []
                        concrete_methods[method_name].append(node.name)
            
            if is_abc and abstract_methods:
                abcs[node.name] = abstract_methods
                
    return abcs, concrete_methods

def analyze_strategy_strength(context_name, injected_var, delegated_method, abcs, concrete_methods):
    """
    Pass 3: We found a Context. Now we audit how strongly the Strategy is implemented
    and generate actionable feedback.
    """
    score = 30 # Base score for basic composition/delegation
    strength_tier = "Loose (Duck-Typed)"
    evidence = [f"✅ Structural: '{context_name}' successfully injects state and delegates to '.{delegated_method}()'"]
    suggestions = []
    
    # Check 1: Are there actually multiple strategies available in this file?
    implementations = concrete_methods.get(delegated_method, [])
    if len(implementations) >= 2:
        score += 20
        evidence.append(f"✅ Interchangeability: Found {len(implementations)} classes implementing '{delegated_method}()' {implementations}")
    else:
        suggestions.append(f"💡 Architecture: Found fewer than 2 classes implementing '{delegated_method}()'. A Strategy pattern usually requires multiple interchangeable algorithms.")

    # Check 2: Is there a formal ABC Interface governing this method?
    matching_abc = None
    for abc_name, abs_methods in abcs.items():
        if delegated_method in abs_methods:
            matching_abc = abc_name
            break

    if matching_abc:
        score += 30
        strength_tier = "Moderate (Formal Interface)"
        evidence.append(f"✅ Contract: Strategies are governed by the formal ABC interface '{matching_abc}'")
        
        # Check 3: Did the Context explicitly Type-Hint the injection?
        if injected_var["type_hint"] == matching_abc:
            score += 20
            strength_tier = "Enterprise Grade (Strictly Typed)"
            evidence.append(f"✅ Type Safety: Context explicitly type-hints the '{matching_abc}' interface in its arguments")
        else:
            if injected_var["type_hint"]:
                suggestions.append(f"💡 Typing: Context is type-hinted as '{injected_var['type_hint']}', but the formal interface is '{matching_abc}'. Consider updating the hint.")
            else:
                suggestions.append(f"💡 Typing: Add type hinting to your Context (e.g., `def __init__(self, strategy: {matching_abc}):`) to enforce the contract.")
    else:
        suggestions.append(f"💡 Contract: You are relying on Duck-Typing. Create an `abc.ABC` interface that defines `@abstractmethod def {delegated_method}(self):` to enforce a strict contract.")

    return score, strength_tier, evidence, suggestions

def detect_strategy(filepath):
    print(f"\n{'='*60}")
    print(f"🚀 RUNNING ENTERPRISE STRATEGY ANALYZER: {filepath}")
    print(f"{'='*60}")
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"❌ Error: Could not find {filepath}")
        return

    tree = ast.parse(source)
    
    # 1. Map the ecosystem
    abcs, concrete_methods = map_ecosystem(tree)
    print("TESTING 1 : ", abcs, concrete_methods)
    results = []

    # 2. Search for the Context
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            
            # Step A: Find Injected Attributes
            injected_vars = {} # { attr_name: {"arg_name": name, "type_hint": type} }
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    for arg in item.args.args:
                        if arg.arg != 'self':
                            # Extract type hint if it exists
                            type_hint = arg.annotation.id if hasattr(arg, 'annotation') and isinstance(arg.annotation, ast.Name) else None
                            
                            for stmt in ast.walk(item):
                                if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Name) and stmt.value.id == arg.arg:
                                    for target in stmt.targets:
                                        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                                            injected_vars[target.attr] = {"arg_name": arg.arg, "type_hint": type_hint}

            # Step B: Check for Delegation
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
                                            
                                            # Step C: Audit the Architecture
                                            score, tier, evidence, suggestions = analyze_strategy_strength(
                                                node.name, injected_vars[caller.attr], delegated_method, abcs, concrete_methods
                                            )
                                            
                                            results.append({
                                                "class": node.name,
                                                "score": score,
                                                "tier": tier,
                                                "evidence": evidence,
                                                "suggestions": suggestions
                                            })
                                            break # Move to next class

    # 3. Print the comprehensive report
    if not results:
        print("❌ No Strategy Pattern detected.")
    else:
        for result in results:
            print(f"\n🏛️  CONTEXT CLASS : {result['class']}")
            print(f"📊 ARCH SCORE    : [{result['score']}/100] - {result['tier']}")
            
            print("\n  🔍 EVIDENCE:")
            for e in result['evidence']:
                print(f"      {e}")
                
            if result['suggestions']:
                print("\n  🛠️  ACTIONABLE IMPROVEMENTS:")
                for s in result['suggestions']:
                    print(f"      {s}")
            print("-" * 60)

if __name__ == "__main__":
    for i in range(1, 8):
        print(f"\n{'='*60}")
        print(f"🔎 TEST CASE {i}:")
        TEST_FILE = f"./test_cases-strategy/test{i}.py" 
        detect_strategy(TEST_FILE)