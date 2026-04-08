import sys
import numpy as np

try:
    from . import singleton_detector
    from . import factory_detector
    from . import strategy_detector
    from . import template_detector
    from . import observer_detector
except ImportError as e:
    print(f"❌ Failed to load detector modules: {e}")
    sys.exit(1)

class ArchitectureTutor:
    def __init__(self, filepath):
        self.filepath = filepath
        self.history = []  
        
        # Row Matrices for Scoring
        self.weights = {
            "Strategy": np.array([30, 20, 30, 20]),
            "Template Method": np.array([50, 20, 30]),
            "Singleton": np.array([30, 25, 25, 20]),
            "Observer": np.array([20, 20, 20, 20, 20]),
            "Factory": np.array([25, 25, 50, 75]) 
        }

    def _calculate_score(self, pattern_name, feature_matrix):
        """Dot product W * F"""
        weight_vector = self.weights[pattern_name]
        flat_features = feature_matrix.flatten()
        return int(np.dot(weight_vector, flat_features))

    def _calculate_cosine_similarity(self, vec1, vec2):
        """Calculates the angle between two feature matrices."""
        flat1, flat2 = vec1.flatten(), vec2.flatten()
        dot_prod = np.dot(flat1, flat2)
        norm1 = np.linalg.norm(flat1)
        norm2 = np.linalg.norm(flat2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_prod / (norm1 * norm2)

    def _run_detectors(self):
        """Runs sensors and calculates matrix math."""
        report = {"Singleton": [], "Factory": [], "Strategy": [], "Template Method": [], "Observer": []}
        detectors = {
            "Singleton": singleton_detector.detect_singleton,
            "Factory": factory_detector.detect_factory,
            "Strategy": strategy_detector.detect_strategy,
            "Template Method": template_detector.detect_template_method,
            "Observer": observer_detector.detect_observer
        }

        for pattern_name, func in detectors.items():
            try:
                results = func(self.filepath)
                for res in results:
                    if "feature_matrix" in res:
                        res["score"] = self._calculate_score(pattern_name, res["feature_matrix"])
                if results:
                    report[pattern_name].extend(results)
            except Exception:
                pass

        return report

    def _flatten_report(self, report):
        flat = {}
        for pattern, instances in report.items():
            for inst in instances:
                class_name = inst.get("class", "Unknown")
                flat[f"{pattern}::{class_name}"] = inst
        return flat
    
    
    def _get_normalized_score(self, flat_report):
        """Calculates the overall file score (average of all patterns)."""
        if not flat_report: return 0
        total_score = sum(data.get("score", 0) for data in flat_report.values())
        return int(total_score / len(flat_report))

    
    def analyze(self):
        print(f"\n{'='*70}")
        print(f"📘 INITIALIZING TUTOR FOR: {self.filepath}")
        print(f"{'='*70}")
        
        current_report = self._run_detectors()
        self.history.append(current_report)
        flat_report = self._flatten_report(current_report)
        
        # ---> CALCULATING THE OVERALL SCORE <---
        normalized_score = self._get_normalized_score(flat_report)

        if not flat_report:
            print("\n  ❌ Baseline: No standard enterprise patterns detected.")
            print(f"  📊 OVERALL FILE SCORE: 0 / 100")
        else:
            print(f"\n  🎯 Baseline: {len(flat_report)} patterns detected.")
            print(f"  📊 OVERALL FILE SCORE: {normalized_score} / 100\n")
            
            for key, data in flat_report.items():
                pattern, cls = key.split("::")
                print(f"      - {cls} [{pattern}]: {data.get('score', 0)}/100")
        print("-" * 70)

   
    def recheck(self):
        if not self.history:
            print("⚠️ No history found! Run .analyze() first.")
            return

        print(f"\n{'='*70}")
        print(f"🔄 RE-CHECKING: {self.filepath}")
        print(f"{'='*70}")

        old_report = self.history[-1]
        new_report = self._run_detectors()
        self.history.append(new_report)

        old_flat = self._flatten_report(old_report)
        new_flat = self._flatten_report(new_report)

        # ---> COMPARING THE OVERALL SCORES <---
        old_norm = self._get_normalized_score(old_flat)
        new_norm = self._get_normalized_score(new_flat)
        
        print(f"\n  📊 OVERALL FILE SCORE: {new_norm} / 100", end="")
        if new_norm > old_norm: print(f" (📈 +{new_norm - old_norm} pts)")
        elif new_norm < old_norm: print(f" (📉 {new_norm - old_norm} pts)")
        else: print(" (➖ Unchanged)")
        
        print("\n  📝 INDIVIDUAL FEEDBACK REPORT:")

        for key, new_data in new_flat.items():
            pattern, cls = key.split("::")
            new_score = new_data.get("score", 0)
            
            if key not in old_flat:
                print(f"      🎉 NEW: Implemented {pattern} in '{cls}'! ({new_score}/100)")
            else:
                old_score = old_flat[key].get("score", 0)
                score_diff = new_score - old_score
                
                if score_diff > 0:
                    print(f"      📈 IMPROVED: '{cls}' {pattern} (+{score_diff} pts)")
                elif score_diff < 0:
                    print(f"      📉 DEGRADED: '{cls}' {pattern} ({score_diff} pts)")
                    for suggestion in new_data.get("suggestions", []):
                        print(f"         -> Fix: {suggestion}")
                else:
                    print(f"      ✅ STABLE: '{cls}' {pattern} score maintained ({new_score}/100).")

        for key in old_flat:
            if key not in new_flat:
                pattern, cls = key.split("::")
                print(f"      ⚠️ BROKEN: '{cls}' {pattern} was destroyed or removed.")

        print("-" * 70)