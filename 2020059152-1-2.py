import numpy as np

#A
M=np.arange(2,27)
print(M)
#B
M.shape=(5,5)
print(M)
#C
M[:,0]=0
print(M)
#D
M=M@M
print(M)
#E
sum=0
for i in range(5):
    sum+=(np.square(M[0,i]))
print(np.sqrt(sum))