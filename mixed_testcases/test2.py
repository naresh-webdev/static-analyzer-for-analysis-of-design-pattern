from abc import ABC, abstractmethod

# ==========================================
# 1. STRATEGY: Interchangeable Payment Algorithms
# ==========================================
class PaymentStrategy(ABC):
    @abstractmethod
    def process_payment(self, amount: float):
        pass

class StripePayment(PaymentStrategy):
    def process_payment(self, amount: float):
        print(f"Charging ${amount} via Stripe API...")

class PayPalPayment(PaymentStrategy):
    def process_payment(self, amount: float):
        print(f"Charging ${amount} via PayPal OAuth...")

class CheckoutContext:
    def __init__(self, strategy: PaymentStrategy):
        # Injecting the strategy with type hinting
        self.strategy = strategy

    def execute_checkout(self, amount: float):
        # Delegating the behavior
        self.strategy.process_payment(amount)


# ==========================================
# 2. FACTORY: Registry-based creation
# ==========================================
class PaymentFactory:
    def __init__(self):
        # Registry dictionary
        self.registry = {
            "stripe": StripePayment,
            "paypal": PayPalPayment
        }

    def create_payment_method(self, method_name: str):
        # Dynamic instantiation
        return self.registry[method_name]()