import sys
import time

# Import your 5 detector modules
# Ensure your filenames match these exactly!
try:
    import singleton_detector
    import factory_detector
    import strategy_detector
    import template_detector
    import observer_detector
except ImportError as e:
    print(f"❌ Failed to load detector modules. Check your filenames! Error: {e}")
    sys.exit(1)

def run_scanner(filepath):
    print(f"\n{'='*70}")
    print(f"🚀 ENTERPRISE ARCHITECTURE SCANNER INITIALIZED")
    print(f"📂 Target: {filepath}")
    print(f"{'='*70}\n")

    # Dictionary to hold all aggregated results
    # Format: { "Pattern Name": [list of detected instances] }
    master_report = {
        "Singleton": [],
        "Factory": [],
        "Strategy": [],
        "Template Method": [],
        "Observer": []
    }

    start_time = time.time()

    # --- 1. SINGLETON ---
    try:
        results = singleton_detector.detect_singleton(filepath)
        if results: master_report["Singleton"].extend(results)
    except Exception as e:
        print(f"⚠️ Singleton Detector crashed: {e}")

    # --- 2. FACTORY ---
    try:
        # Assuming factory returns a list or a boolean+dict
        results = factory_detector.detect_factory(filepath)
        if results: 
            # Adapt this line based on exactly what your factory returns
            master_report["Factory"].extend(results if isinstance(results, list) else [results])
    except Exception as e:
        print(f"⚠️ Factory Detector crashed: {e}")

    # --- 3. STRATEGY ---
    try:
        results = strategy_detector.detect_strategy(filepath)
        if results: master_report["Strategy"].extend(results)
    except Exception as e:
        print(f"⚠️ Strategy Detector crashed: {e}")

    # --- 4. TEMPLATE METHOD ---
    try:
        results = template_detector.detect_template_method(filepath)
        if results: master_report["Template Method"].extend(results)
    except Exception as e:
        print(f"⚠️ Template Method Detector crashed: {e}")

    # --- 5. OBSERVER ---
    try:
        results = observer_detector.detect_observer(filepath)
        if results: master_report["Observer"].extend(results)
    except Exception as e:
        print(f"⚠️ Observer Detector crashed: {e}")

    scan_time = round(time.time() - start_time, 2)

    generate_executive_summary(master_report, scan_time)


def generate_executive_summary(report, scan_time):
    """Parses the aggregated results and prints a high-level summary."""
    print(f"\n{'='*70}")
    print(f"📊 EXECUTIVE ARCHITECTURE SUMMARY")
    print(f"⏱️  Scan completed in {scan_time} seconds")
    print(f"{'='*70}")

    total_patterns = sum(len(instances) for instances in report.values())
    
    if total_patterns == 0:
        print("\n  ❌ No standard design patterns detected in this file.")
        print("-" * 70)
        return

    print(f"\n  🎯 Total Patterns Discovered: {total_patterns}\n")

    # Iterate through our report and print the findings cleanly
    for pattern_name, instances in report.items():
        if instances:
            print(f"  🟢 {pattern_name.upper()} ({len(instances)} found):")
            
            for inst in instances:
                # Safely extract class name and score/tier depending on how each detector formatted it
                class_name = inst.get('class', 'Unknown Class') if isinstance(inst, dict) else 'Detected'
                score = inst.get('score', 'N/A') if isinstance(inst, dict) else ''
                tier = inst.get('tier', '') if isinstance(inst, dict) else ''
                
                # Format the output based on what data is available
                if score != 'N/A' and tier:
                    print(f"      - {class_name} [Score: {score}/100 - {tier}]")
                elif score != 'N/A':
                    print(f"      - {class_name} [Score: {score}%]")
                else:
                    print(f"      - {class_name}")
            print() # Spacer
        else:
            print(f"  ⚪ {pattern_name.upper()}: None detected")

    print("-" * 70)


if __name__ == "__main__":
    # You can later change this to use argparse to accept terminal arguments!
    TARGET_FILE = "./test_cases-strategy/test1.py" # Change this to test different files
    
    run_scanner(TARGET_FILE)