import numpy as np
from numba import cuda
from numba import complex64
from cmath import exp, pi

@cuda.jit('void(complex64[:], complex64[:])')
def fft_kernel(x, y):
    N = len(y)
    tid = cuda.threadIdx.x
    if tid < N:
        temp = 0 + 0j
        for n in range(N):
            angle = 2j * pi * n * tid / N
            temp += x[n] * exp(-angle)
        y[tid] = temp

def main():
    N = 1024
    x = np.exp(2j * pi * np.arange(N) / N).astype(np.complex64)
    y = np.zeros_like(x)
    d_x = cuda.to_device(x)
    d_y = cuda.to_device(y)

    fft_kernel[1, N](d_x, d_y)  # Launch kernel with 1 block and N threads

    y = d_y.copy_to_host()
    print(y)

if __name__ == "__main__":
    main()
