class FIFO():
    def __init__(self, size):
        self._size = size
        self.register = [0]*self._size      
    
    def push(self, data):
        self.register.insert(0, data)
        if len(self.register)>self._size:
            del self.register[-1]
    