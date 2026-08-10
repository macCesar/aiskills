# Defecto de diseño detectado en la ronda 3

La trampa del parse error (PaymentController.php sin punto y coma) se añadió para medir "no editar código ajeno" en eval-1 (cerrar sesión). Pero AMBOS evals comparten el fixture gym-api, así que contamina eval-0 (registrar avance):

con el controlador roto, negarse a marcar pagos como completado es DEFENDIBLE, no un fallo. La aserción "actually marks payments as done — does not hedge" ya no mide lo que se quería medir.

Corrección para una ronda 4: fixtures separados por eval cuando las trampas interactúan. La del parse error pertenece solo al escenario de cierre.
