# 1. The Factory handles the CREATION (The "Who")
class PaymentFactory:
    def create_payment(method_string):
        if method_string == "credit":
            return CreditCardPayment()
        elif method_string == "paypal":
            return PayPalPayment()

# 2. The Context handles the EXECUTION (The "How")
class ShoppingCart:
    def __init__(self, strategy):
        self._strategy = strategy
        
    def checkout(self, amount):
        self._strategy.pay(amount) 

# --- The Perfect Marriage ---
# Factory builds it, Cart executes it.
selected_strategy = PaymentFactory.create_payment("paypal")
cart = ShoppingCart(selected_strategy)
cart.checkout(50.0)