def clamp(min_value, max_value, value):
    return max(min_value ,min(value,max_value))

class Filter():
    '''
coef_in : the list of n coef values in [0 ... n-1] for the n input values including present value (x[0])
coef_out : the list of m coef values in [1 ... m] for the output values in [1 ... m].
By definition,the coeficient of computed present output Y[0] is 1.
note : size of input vector is n+1,  size of output vector is m
'''
    def __init__(self, coef_in, coef_out):
        self._size_in = len(coef_in)
        self._size_out = len(coef_out)
        self._A = coef_in
        self._B = coef_out
        self._X = [0]*self._size_in
        self._Y = [0]*self._size_out
        
    def __repr__(self):
        return f"coef_in:{self._A}, coef_out:{self._B}"

    def _push(self, fifo, data):
        del fifo[-1]
        fifo.insert(0, data)

    def filter(self, x_in):
        self._push(self._X, x_in)
        sum_y = 0
        for i in range(self._size_in):
            sum_y += self._A[i]*self._X[i]
        for j in range(self._size_out):
            sum_y += self._B[j]*self._Y[j]
        self._push(self._Y, sum_y)
        return sum_y
    
class PID(Filter):
    def __init__(self, Ts, G, Ti, Td):
#         print(f"Ts:{Ts}, G:{G}, Td:{Td}, Ti:{Ti}")
        self._size_in = 3
        self._A = [0]*self._size_in
        self._A[0] = G + Ts/Ti + Td/Ts
        self._A[1] = - (G + 2*Td/Ts)
        self._A[2] = Td/Ts
        self._X = [0]*self._size_in   
        self._size_out = 1
        self._B = [1]
        self._Y = [0]*self._size_out

        
    
if __name__ == "__main__":
    pid = PID(Ts=1000, Td=0, Ti=2500, G=.3)
#     print(pid)
    setpoint = 1000
    for n in range(30):
        delta = setpoint - pid._Y[0]
        print( pid.filter(delta))
    
    
        
        
        