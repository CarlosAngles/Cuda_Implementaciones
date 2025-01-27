import numpy as np
from numba import cuda
import math

@cuda.jit
def monte_carlo_pi_kernel(counts, num_points_per_thread):
    """
    Kernel CUDA para ejecutar el método de Monte Carlo para la estimación de Pi.
    Cada hilo generará 'num_points_per_thread' puntos aleatorios.
    """
    thread_id = cuda.grid(1)  # Identificación del hilo
    inside = 0
    
    # Parámetros del generador congruente lineal
    a = 1664525
    c = 1013904223
    m = 4294967296  # 2^32

    # Generar un valor aleatorio basado en el hilo
    state = thread_id  # Usar thread_id como semilla inicial

    for i in range(num_points_per_thread):
        # Generación de números pseudoaleatorios para x y y
        state = (a * state + c) % m  # Actualizar el estado
        x = state / float(m)  # Normalizar a [0, 1)
        state = (a * state + c) % m  # Actualizar el estado para y
        y = state / float(m)  # Normalizar a [0, 1)
        # Verificamos si el punto (x, y) cae dentro del círculo unitario
        if x * x + y * y <= 1.0:
            inside += 1
    
    counts[thread_id] = inside  # Guardamos el número de puntos dentro del círculo

def estimate_pi(num_threads, num_points):
    """
    Función para estimar Pi usando el método de Monte Carlo en CUDA.
    """
    threads_per_block = 256
    blocks_per_grid = (num_threads + threads_per_block - 1) // threads_per_block
    
    # Calcula el número de puntos por hilo
    num_points_per_thread = math.ceil(num_points / num_threads)  
    # Reserva espacio para los resultados de cada hilo
    d_counts = cuda.device_array(num_threads, dtype=np.int32)  
    # Ejecuta el kernel
    monte_carlo_pi_kernel[blocks_per_grid, threads_per_block](d_counts, num_points_per_thread)
    
    # Copia los resultados de vuelta al host
    counts = d_counts.copy_to_host()
    
    # Calcula el número total de puntos dentro del círculo
    total_inside = np.sum(counts)
    
    # Estima Pi
    estimated_pi = 4 * total_inside / num_points
    
    return estimated_pi
def main():
    num_points = 10000000  # Número total de puntos lanzados
    num_threads = 1024     # Número de hilos en la GPU
    pi_estimate = estimate_pi(num_threads, num_points)
    print(f"Estimación de Pi: {pi_estimate}")

if __name__ == "__main__":
    main()
