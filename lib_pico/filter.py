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
        self._X = [0]*self._size_in
        self._size_out = len(coef_out)
        self._Y = [0]*self._size_out
        self._A = coef_in
        self._B = coef_out
        
    def __repr__(self):
        return f"A[i]:{self._A}, B[i]:{self._B}"

    def _push(self, fifo, data):
        del fifo[-1]
        fifo.insert(0, data)

    def filter(self, x_in):
        self._push(self._X, x_in) # init X[0]
        self._push(self._Y, 0) # init Y[0]
        
        for i in range(self._size_in):
            self._Y[0] += self._A[i]*self._X[i]
            
        for j in range(1,self._size_out):
            self._Y[0] += self._B[j]*self._Y[j]
            
        self._Y[0] = self._Y[0]/self._B[0]
        return self._Y[0]
    
    def get_output(self):
        return self._Y[0]
    
    
    
class PID(Filter):
    def __init__(self, Ts, G, Ti, Td):
        A = [0]*3
        A[0] = G + Ts/Ti + Td/Ts
        A[1] = - (G + 2*Td/Ts)
        A[2] = Td/Ts
        B = [0]*2
        B[0] = 1
        B[1] = 1
        super().__init__(A,B)
        
    def __repr__(self):
        return f"A[i]:{self._A}, B[i]:{self._B}"

class FilteredPID(Filter):
    def __init__(self, Ts, G, Ti, Td, N):
        a = Ti/Ts
        b = Td/Ts
        c = b/N
        D = a*G + c
        E = a*c*G + a*b
                
        A = [0]*3
        A[0] = 1 + D + E
        A[1] = - (D + 2*E)
        A[2] = E
        
        B = [0]*3
        B[0] = 1/(a+a*c)
        B[1] = a + 2*a*c
        B[2] = -a*c
        
        super().__init__(A,B)

        
        


class Means(Filter):
    def __init__(self,size):        
        A = [0]*size
        A[-1] = 1/size
        B = [0]*2
        B[0] = 1
        B[1] = 1
        super().__init__(A,B)
         

    
if __name__ == "__main__":
    def test_PID():
        pid = PID(Ts=1000, Td=0, Ti=3000, G=.5)
        setpoint = 1000
        for _ in range(50):
            delta = setpoint - pid.get_output()
            print( pid.filter(delta))
    def test_FileteredPID():    
        fpid = FilteredPID(Ts=1000, Td=0, Ti=3000, G=.5, N=10)
        setpoint = 1000
        for _ in range(50):
            delta = setpoint - fpid.get_output()
            print( fpid.filter(delta))
    def test_Means():     
        m = Means(5)
        setpoint = 1000
        for _ in range(50):
            delta = setpoint - m.get_output()
            print( m.filter(delta))
            

    test_PID()
    test_FileteredPID()
    test_Means()

        
        
    
    
    
        
        
        