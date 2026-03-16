class Store:
    def __init__(self):
        self._subscribers = []
    
    def attach(self, observer):
        self._subscribers.append(observer)
    
    def detach(self, observer):
        self._subscribers.remove(observer)
    
    def notify(self):
        for observer in self._subscribers:
            observer.update()

class Client:
    def update(self):
        print("Store has changed!")