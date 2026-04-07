import ast

def map_ecosystem(tree):
    """Pass 1: Map all Abstract Base Classes and track class inheritance."""
    abcs = {} # { class_name: {"abstract_methods": [], "concrete_methods": [], "node": ast.ClassDef} }
    subclasses = {} # { parent_name: [list of child class names] }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            
            # Map inheritance (who inherits from whom)
            bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
            for base in bases:
                if base not in subclasses:
                    subclasses[base] = []
                subclasses[base].append(node.name)

            # Map Abstract Classes and their methods
            is_abc = 'ABC' in bases
            
            abstract_methods = []
            concrete_methods = []
            
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if any(isinstance(d, ast.Name) and d.id == 'abstractmethod' for d in item.decorator_list):
                        abstract_methods.append(item.name)
                    else:
                        # Exclude __init__ from being considered a template method
                        if item.name != "__init__":
                            concrete_methods.append(item.name)
            
            # Even if it doesn't inherit from ABC, if it has abstractmethods, we track it
            if is_abc or abstract_methods:
                abcs[node.name] = {
                    "abstract_methods": abstract_methods,
                    "concrete_methods": concrete_methods,
                    "node": node
                }
                
    return abcs, subclasses

def analyze_template_strength(abc_name, template_method, called_abstracts, subclasses):
    """Pass 3: Grade the architectural strength of the detected pattern."""
    score = 50 # Base score: The structural skeleton exists!
    strength_tier = "Structural (Skeleton Only)"
    evidence = [f"✅ Skeleton: Concrete method '{template_method}()' orchestrates abstract steps: {called_abstracts}"]
    suggestions = []
    
    children = subclasses.get(abc_name, [])
    
    if len(children) == 0:
        suggestions.append(f"💡 Usage: You built the Template Class '{abc_name}', but no subclasses exist to implement the blanks. Create a concrete child class.")
    elif len(children) == 1:
        score += 30
        strength_tier = "Functional (Single Use)"
        evidence.append(f"✅ Implementation: Subclass '{children[0]}' implements the template.")
        suggestions.append("💡 Architecture: A template is best utilized when multiple subclasses share the workflow. Consider if this over-engineers a single use-case.")
    else:
        score += 50
        strength_tier = "Enterprise Grade (Polymorphic)"
        evidence.append(f"✅ Polymorphism: {len(children)} subclasses ({children}) share this master workflow.")

    return score, strength_tier, evidence, suggestions

def detect_template_method(filepath):
    print(f"\n{'='*60}")
    print(f"🚀 RUNNING ENTERPRISE TEMPLATE ANALYZER: {filepath}")
    print(f"{'='*60}")
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"❌ Error: Could not find {filepath}")
        return

    tree = ast.parse(source)
    
    # 1. Map the ecosystem
    abcs, subclasses = map_ecosystem(tree)
    results = []

    # 2. Search for the Template Method Signature inside the ABCs
    for abc_name, data in abcs.items():
        if not data["abstract_methods"] or not data["concrete_methods"]:
            continue # A template MUST have both concrete and abstract methods
            
        for item in data["node"].body:
            if isinstance(item, ast.FunctionDef) and item.name in data["concrete_methods"]:
                
                # Look inside the concrete method to see what it calls
                called_abstracts = set()
                for stmt in ast.walk(item):
                    if isinstance(stmt, ast.Call):
                        func = stmt.func
                        # Looking for: self.<method_name>()
                        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == "self":
                            if func.attr in data["abstract_methods"]:
                                called_abstracts.add(func.attr)
                
                # If a concrete method calls its own abstract siblings, it is mathematically a Template Method
                if called_abstracts:
                    score, tier, evidence, suggestions = analyze_template_strength(
                        abc_name, item.name, list(called_abstracts), subclasses
                    )
                    
                    results.append({
                        "class": abc_name,
                        "template_method": item.name,
                        "score": score,
                        "tier": tier,
                        "evidence": evidence,
                        "suggestions": suggestions
                    })

    # 3. Print the comprehensive report
    if not results:
        print("❌ No Template Method Pattern detected.")
    else:
        for result in results:
            print(f"\n🏛️  TEMPLATE BASE : {result['class']}")
            print(f"⚙️  MASTER METHOD : {result['template_method']}()")
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
    for i in range(1, 5):
        print(f"\n{'='*60}" + f"\n🚀 RUNNING TEST CASE {i}" + f"\n{'='*60}")
        
        TEST_FILE = f"./test_cases-template/test{i}.py" 
        detect_template_method(TEST_FILE)