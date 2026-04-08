import time
from tutor_module import ArchitectureTutor

def run_tests():
    print(f"\n{'='*70}")
    print("🚀 STARTING ENTERPRISE ARCHITECTURE TEST SUITE")
    print(f"{'='*70}")
    
    # 1. Test the E-Commerce File
    tutor1 = ArchitectureTutor("./mixed_testcases/test3.py")
    tutor1.analyze()
    
    # # 2. Test the Payments File
    # tutor2 = ArchitectureTutor("./mixed_testcases/test2.py")
    # tutor2.analyze()
    
    # # 3. Test the Data Pipeline File
    # tutor3 = ArchitectureTutor("./mixed_testcases/test3.py")
    # tutor3.analyze()

    # ==========================================
    # INTERACTIVE RECHECK DEMO
    # ==========================================
    print("\n" + "#"*70)
    print("🛑 INTERACTIVE RECHECK TEST INITIATED")
    print("#"*70)
    print("\nTry modifying 'test1.py' right now!")
    print("Examples:")
    print("  - Change 'PaymentStrategy(ABC)' to just 'PaymentStrategy' (Degrade Strategy)")
    print("  - Delete the 'registry = {}' dictionary in the Factory (Break Factory)")
    print("  - Change nothing (Stable)")
    
    input("\nPress [ENTER] when you are done modifying the file to run the recheck...")
    
    # This will generate the Cosine Similarity and Score Change metrics!
    tutor1.recheck()

if __name__ == "__main__":
    run_tests()