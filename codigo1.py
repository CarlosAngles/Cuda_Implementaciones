import numpy as np
from numba import cuda

@cuda.jit
def add_vectors(a, b, c):
    idx = cuda.grid(1)
    if idx < a.size:
        c[idx] = a[idx] + b[idx]

def main():
    N = 1000000
    a = np.ones(N, dtype=np.float32)
    b = np.ones(N, dtype=np.float32)
    c = np.zeros(N, dtype=np.float32)
    
    d_a = cuda.to_device(a)
    d_b = cuda.to_device(b)
    d_c = cuda.device_array(N, dtype=np.float32)
    
    threads_per_block = 256
    blocks_per_grid = (N + threads_per_block - 1) // threads_per_block
    
    add_vectors[blocks_per_grid, threads_per_block](d_a, d_b, d_c)
    
    c = d_c.copy_to_host()
    print(c)

if __name__ == "__main__":
    main()
