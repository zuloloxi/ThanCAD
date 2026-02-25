from math import pi, fabs, cos

def lgaus(N):
      "CALCULATION OF GAUSSIAN INTEGRATION POINTS AND WEIGHTS."
      EPS=3e-14
      X = [0.0]*N; W = [0.0]*N
      M=(N+1)//2
      for I in range(1, M+1):  #OK for python2,3
          Z=cos(pi*(I-0.25)/(N+0.50)); Z1=Z-1
          while fabs(Z-Z1) > EPS:
              P1=1.0; P2=0.0
              for J in range(1, N+1):  #OK for python2,3
                  P3=P2
                  P2=P1
                  P1=((2.0*J-1.0)*Z*P2-(J-1.0)*P3)/J
              PP=N*(Z*P1-P2)/(Z*Z-1.0)
              Z1=Z
              Z=Z1-P1/PP

          X[I-1]=-Z
          X[N-I]=Z
          W[I-1]=2.0/((1.0-Z*Z)*PP*PP)
          W[N-I]=W[I-1]
      return X, W

def test():
      n = 10
      x, w = lgaus(n)
      for x1,w1 in zip(x,w): print("%20.10f%20.10f" % (x1, w1))

if __name__ == "__main__": test()
