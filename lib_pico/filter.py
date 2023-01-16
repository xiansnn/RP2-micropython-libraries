def clamp(min_value, max_value, value):
    return max(min_value ,min(value,max_value))

class Coef_Exception(BaseException):
    pass

class Filter():
    '''
coef_in : the list of n coef values in [0 ... n-1] for the n input values including present value (x[0])
coef_out : the list of m coef values in [0 ... m] for the output values in [0 ... m] with always coef_out[0]=1.
By definition,the coeficient of computed present output Y[0] is 1.
note : size of input vector is n+1,  size of output vector is m
'''
    def __init__(self, coef_in, coef_out):
        self._A = coef_in
        self._B = coef_out
        if (self._B[0]!=1): raise Coef_Exception("warning : coef_out[0]!=1")
        self._X = [0]*len(self._A)
        self._Y = [0]*len(self._B)
        
    def __repr__(self):
        return f"A[i]:{self._A}, B[i]:{self._B}"

    def _push(self, fifo, data):
        del fifo[-1]
        fifo.insert(0, data)

    def filter(self, x_in):
        self._push(self._X, x_in) # init X[0]
        self._push(self._Y, 0) # init Y[0]
        
        for i in range(len(self._A)):
            self._Y[0] += self._A[i]*self._X[i]
            
        for j in range(1,len(self._B)):
            self._Y[0] += self._B[j]*self._Y[j]
            
        return self._Y[0]
    
    def get_output(self):
        return self._Y[0]
    
    
    
class PID(Filter):
    def __init__(self, Ts, G, Ti, Td):
        A = [0]*3
        A[0] = G*(1 + Ts/Ti + Td/Ts)
        A[1] = - G*(1 + 2*Td/Ts)
        A[2] = G*Td/Ts
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
        d = a + c
        e = a*c + a*b
        f = a+a*c
                
        A = [0]*3
        A[0] = G*(1 + d + e)/f
        A[1] = - G*(d + 2*e)/f
        A[2] = G*e/f
        
        B = [0]*3
        B[0] = 1
        B[1] = (a + 2*a*c)/f
        B[2] = -a*c/f
        
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
    nb_point =30
    def test_PID():
        pid = PID(Ts=1000, Td=10, Ti=1500, G=.6)
#         print(pid)
        setpoint = 1000
        for _ in range(nb_point):
            delta = setpoint - pid.get_output()
            print( pid.filter(delta))
    def test_FileteredPID():    
        fpid = FilteredPID(Ts=1000, Td=1, Ti=1500, G=.6, N=1)
#         print(fpid)
        setpoint = 1000
        for _ in range(nb_point):
            delta = setpoint - fpid.get_output()
            print( fpid.filter(delta))
    def test_Means():     
        m = Means(5)
#         print(m)
        setpoint = 1000
        for _ in range(nb_point):
            delta = setpoint - m.get_output()
            print( m.filter(delta))
            

#     test_PID()
    test_FileteredPID()
#     test_Means()

        
        
    
    
    
        
        
        