# Mecanismo-de-Concurrencia
Explicacion del uso de concurrencia 


# Ejemplo: sincronización con `threading.Event` en Python

## Descripción
Este repositorio contiene un ejemplo didáctico que muestra cómo usar `threading.Event` para coordinar la ejecución de hilos en Python.  
`Event` actúa como una señal compartida (flag booleano) que permite que uno o varios hilos esperen hasta que otro hilo active la señal.

---

## Estructura sugerida del repositorio


.
├─ README.md
└─ src/
└─ event_example.py


---

## Requisitos
- Python 3.8+ (funciona en 3.8, 3.9, 3.10, 3.11, etc.)
- Módulo estándar `threading` (incluido en la distribución estándar de Python)

---

## Cómo ejecutar
```bash
python src/event_example.py

Código (archivo: src/event_example.py)
import threading
import time

# Creamos un evento (inicialmente no está activado: evento.is_set() == False)
evento = threading.Event()

def esperar_evento():
    """
    Hilo que espera a que el evento sea activado.
    Queda bloqueado en evento.wait() hasta que otro hilo llame evento.set().
    """
    print(f"[{threading.current_thread().name}] Esperando al evento...")
    # Espera indefinidamente hasta que el evento esté activado
    evento.wait()
    # Cuando wait() retorna, el evento fue activado
    print(f"[{threading.current_thread().name}] ¡El evento ha sido activado!")

def activar_evento():
    """
    Hilo que simula trabajo/espera y luego activa el evento con evento.set().
    """
    print(f"[{threading.current_thread().name}] Esperando 5 segundos antes de activar el evento...")
    time.sleep(5)
    # Activa el evento: libera a todos los hilos que están en wait()
    evento.set()
    print(f"[{threading.current_thread().name}] El evento ha sido activado después de 5 segundos")

if __name__ == "__main__":
    hilo1 = threading.Thread(target=esperar_evento, name="Espera-1")
    hilo2 = threading.Thread(target=activar_evento, name="Activador")

    hilo1.start()
    hilo2.start()

    hilo1.join()
    hilo2.join()

    print("Programa terminado")

# Explicación detallada (línea por línea / por bloques)
evento = threading.Event()

Qué hace: Crea un objeto Event.

Internamente: es un flag booleano compartido entre hilos.

Estado inicial: no activado. evento.is_set() devuelve False.

def esperar_evento():

print(...) → indica que el hilo comenzó y va a esperar la señal.

evento.wait() → bloquea el hilo hasta que el flag del evento sea True.

Sin argumento: espera indefinidamente.

Si se pasa timeout devuelve True si la señal llegó antes del timeout, False si expiró.

Después de wait() el hilo continúa y puede ejecutar código dependiente de la señal (en el ejemplo, imprime que el evento fue activado).

def activar_evento():

print(...) → indica que el hilo activador empezó su preparación.

time.sleep(5) → simula trabajo o retardo (5 segundos).

evento.set() → pone el flag en True y libera simultáneamente a todos los hilos bloqueados en wait().

print(...) → confirma que la activación se realizó.

Creación y arranque de hilos / join

hilo1 = threading.Thread(target=esperar_evento, name="Espera-1")
hilo2 = threading.Thread(target=activar_evento, name="Activador")
→ se crean dos hilos: uno espera la señal y otro la produce.

start() ejecuta los hilos de forma concurrente.

join() en el hilo principal espera la finalización de cada hilo antes de continuar.

# Comportamiento y análisis del resultado
Flujo típico de ejecución

Espera-1 imprime: Esperando al evento... y queda bloqueado en evento.wait().

Activador imprime: Esperando 5 segundos antes de activar el evento... y duerme 5 s.

Tras 5 segundos, Activador llama evento.set() → esto desbloquea inmediatamente a Espera-1.

Espera-1 continúa e imprime: ¡El evento ha sido activado!.

Ambos hilos terminan; el programa imprime Programa terminado.

Salida de ejemplo (el orden de las primeras impresiones puede variar):
[Espera-1] Esperando al evento...
[Activador] Esperando 5 segundos antes de activar el evento...
[Activador] El evento ha sido activado después de 5 segundos
[Espera-1] ¡El evento ha sido activado!
Programa terminado


Nota: el scheduler del sistema decide el orden de ejecución entre hilos; lo importante es que la impresión “¡El evento ha sido activado!” sólo aparece después de evento.set().

Puntos importantes (resumen rápido)

evento.set() libera a todos los hilos esperando. Es ideal para señalizar una condición global.

Si un hilo llama evento.wait() después de que set() ya fue ejecutado, no quedará bloqueado: wait() retorna inmediatamente.

Para reutilizar el Event en varias rondas (señal → consumo → nueva señal), usar evento.clear() para volver a False.

# Variantes y casos prácticos (útiles para tu informe)
1) wait(timeout=segundos) — evitar esperas indefinidas
if evento.wait(timeout=10):
    print("Evento recibido dentro de 10s")
else:
    print("Timeout: no se recibió la señal en 10s")


wait devuelve True si el evento fue activado antes del timeout; False si expiró.

2) Reutilizar el evento (set → clear)
evento.set()    # libera a los waiters
# ... después de algún control ...
evento.clear()  # vuelve a estado no activado para la próxima ronda


Cuidado: limpiar demasiado pronto puede hacer que hilos que todavía no llamaron wait() pierdan la señal.

3) Muchos hilos esperando (broadcast)

Si 5 hilos ejecutan evento.wait(), un solo evento.set() liberará a los 5 a la vez.

Útil para despertar múltiples consumidores simultáneamente.

4) Comparación con otras primitivas

Event vs Barrier:

Event: señal ON/OFF que despierta a todos los waiters cuando se activa.

Barrier: espera a que un conjunto fijo de hilos llegue a un punto y los libera juntos.

Event vs Condition / Lock:

Condition y Lock permiten patrones más finos (notify/notify_all, protección de datos).

Event es más sencillo cuando sólo se necesita una señal global.

## Errores comunes y buenas prácticas

Pensar que Event garantiza orden: no lo hace; solo libera a los hilos.

Olvidar clear() si se planea reutilizarlo: recuerda volver a False.

Limpiar (clear()) en mal momento: planifica para no perder señales.

Para paso de datos entre hilos: usar queue.Queue es más seguro y adecuado (productor/consumidor).

Para sincronización fina: Condition con un Lock puede ser más apropiado.

Texto listo para el informe (Desarrollo / Resultados / Análisis)

Desarrollo: Se implementó un ejemplo usando threading.Event donde un hilo (Espera-1) llama evento.wait() y permanece bloqueado hasta que otro hilo (Activador) ejecuta evento.set() tras 5 s. Event funciona como un flag compartido; set() lo pone a True y libera a todos los hilos en espera.

Resultados esperados: El hilo que espera no continúa hasta que se llame set(). Tras 5 segundos, el activador llama set() y los hilos esperando continúan inmediatamente. Si hay múltiples hilos esperando, todos serán liberados por el mismo set().

Análisis: El patrón demuestra coordinación simple entre hilos: control del inicio de ejecución condicionado por una señal. Es recomendable para escenarios donde una condición global debe desbloquear múltiples tareas a la vez.
Referencias

Documentación oficial de Python: módulo threading (Event, Barrier, Lock, Condition).
(Incluye ejemplos y notas sobre wait(), set(), clear() y excepciones relacionadas.)

Licencia y autor

Autor: Johnny Vera
Estudiante de la universidad ESTATAL AMAZONICA UEA 
