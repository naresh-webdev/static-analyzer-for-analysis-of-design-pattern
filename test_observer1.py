class Store:
    def __init__(self):
        self._subscribers = []
    
    def attach(self, observer):
        self._subscribers.append(observer)
    
    def detach(self, observer):
        self._subscribers.remove(observer)
    
    def notify(self):
        self.__update_all()  # ← calls helper, not update() directly
    
    def __update_all(self):
        for observer in self._subscribers:
            observer.update()  # ← update() is here, one level deeper

class Client:
    def update(self):
        print("Store has changed!")