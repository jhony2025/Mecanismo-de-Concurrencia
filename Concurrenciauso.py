import threading
import time

# =========================
# Variables globales y mutex
# =========================
contador_global = 0               # variable compartida entre hilos
mutex = threading.Lock()          # objeto Lock (mutex) para exclusión mutua

# =========================
# FUNCIONES DE INCREMENTO
# =========================
def incrementar_con_lock():
    """
    Incrementa el contador_global de forma segura.
    Uso recomendado: 'with mutex' (context manager) que adquiere y libera automáticamente el lock.
    """
    global contador_global
    with mutex:                    # equivale a mutex.acquire()/try:... finally: mutex.release()
        contador_global += 1      # sección crítica: leer-modificar-escribir

def incrementar_sin_lock():
    """
    Incrementa el contador_global sin protección.
    Esto puede provocar condiciones de carrera cuando varios hilos acceden simultáneamente.
    """
    global contador_global
    contador_global += 1          # NO es atómico en Python (operación compuesta)

# =========================
# TAREAS (trabajadores)
# =========================
def tarea(n_incrementos, use_lock=True):
    """
    Ejecuta n_incrementos veces la operación de incremento.
    Si use_lock=True usa incrementar_con_lock(), si no usa incrementar_sin_lock().
    """
    if use_lock:
        for _ in range(n_incrementos):
            incrementar_con_lock()
    else:
        for _ in range(n_incrementos):
            incrementar_sin_lock()

# Variante mejorada: acumular localmente y sumar una sola vez con lock
def tarea_mejorada(n_incrementos):
    """
    Reduce la contención: cada hilo acumula en una variable local y
    sólo adquiere el mutex una vez para añadir el total al contador global.
    """
    local = 0
    for _ in range(n_incrementos):
        local += 1
    # Sumar el total local al global con una sola adquisición del lock
    global contador_global
    with mutex:
        contador_global += local

# =========================
# FUNCIÓN DE PRUEBA / BENCHMARK
# =========================
def run_test(n_threads=2, n_incrementos=100000, mode="with_lock"):
    """
    mode: "with_lock", "without_lock", "improved"
    Reinicia contador_global, lanza n_threads hilos que ejecutan n_incrementos cada uno,
    espera a que terminen y devuelve (valor_final, tiempo_ejecucion).
    """
    global contador_global
    contador_global = 0
    threads = []
    start = time.perf_counter()

    for _ in range(n_threads):
        if mode == "with_lock":
            t = threading.Thread(target=tarea, args=(n_incrementos, True))
        elif mode == "without_lock":
            t = threading.Thread(target=tarea, args=(n_incrementos, False))
        elif mode == "improved":
            t = threading.Thread(target=tarea_mejorada, args=(n_incrementos,))
        else:
            raise ValueError("mode debe ser 'with_lock', 'without_lock' o 'improved'")
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    elapsed = time.perf_counter() - start
    return contador_global, elapsed

# =========================
# EJECUCIÓN DE EJEMPLOS
# =========================
if __name__ == "__main__":
    n_threads = 2
    n_incrementos = 100000

    # 1) Sin lock
    val_nolock, t_nolock = run_test(n_threads, n_incrementos, mode="without_lock")
    print(f"[SIN LOCK]    contador_final = {val_nolock} (esperado {n_threads * n_incrementos}), tiempo {t_nolock:.3f}s")

    # 2) Con lock
    val_lock, t_lock = run_test(n_threads, n_incrementos, mode="with_lock")
    print(f"[CON LOCK]    contador_final = {val_lock} (esperado {n_threads * n_incrementos}), tiempo {t_lock:.3f}s")

    # 3) Mejorado (acumular local y sumar una vez)
    val_improved, t_improved = run_test(n_threads, n_incrementos, mode="improved")
    print(f"[MEJORADO]    contador_final = {val_improved} (esperado {n_threads * n_incrementos}), tiempo {t_improved:.3f}s")
