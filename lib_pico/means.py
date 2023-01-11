from lib_pico.FIFO import FIFO

class Means():
    def __init__(self,size):
        self._size = size
        self._fifo = FIFO(self._size + 1)
        self.last_output = 0
    def __repr__(self):
        return self._fifo.register
         
    def compute_sliding_means(self, input_data):
        self._fifo.push(input_data)
        output_data = self.last_output + (input_data-self._fifo.register[-1])/self._size
        self.last_output = output_data
        return output_data
    
   
if __name__ == "__main__":
    import random
    shift_reg = Means(10)
    target = 1000
    max_noise = 10
    for i in range(100):
        x = target + max_noise*( -0.5 + random.random())
        print(shift_reg.compute_sliding_means(x))
        
    