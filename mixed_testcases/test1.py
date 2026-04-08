import threading

# ==========================================
# 1. SINGLETON: Enterprise System Logger
# ==========================================
class SystemLogger:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SystemLogger, cls).__new__(cls)
        return cls._instance

    def log(self, message):
        print(f"[LOG] {message}")


# ==========================================
# 2. OBSERVER: Order Event System
# ==========================================
class OrderManager:
    def __init__(self):
        # Rule 1: State tracking collection
        self.subscribers = []

    def attach(self, observer):
        # Rule 2: Registration
        self.subscribers.append(observer)

    def update_shipping_status(self, new_status):
        SystemLogger().log(f"Status changed to {new_status}")
        # Rule 3: Broadcast loop
        for sub in self.subscribers:
            sub.on_order_update(new_status)

# Rule 4 & 5: Listeners implementing the target method
class EmailNotifier:
    def on_order_update(self, new_status):
        pass

class SMSNotifier:
    def on_order_update(self, new_status):
        pass