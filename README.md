## Práctica Formativa Integradora

## Sección 1. Integridad del dato (Módulo 5075)

### 1.1 ¿Qué hace el código?

El script `saneamiento.py` automatiza el control de calidad del dataset de telemetría logística.
Contiene tres funciones principales:

- **`obtener_sha256(ruta_fichero)`**: calcula la huella SHA-256 de un
  fichero leyéndolo por bloques de 4 KB, de modo que funciona igual con
  ficheros pequeños o grandes.
- **`describir_csv(ruta_fichero)`**: diagnostica el fichero sin modificarlo.
  Muestra su estructura (filas, columnas y tipos), los nulos por columna,
  las filas duplicadas, los valores erróneos (pesos no positivos,
  temperaturas fuera de rango, estados no catalogados) y las estadísticas
  numéricas.
- **`limpiar_csv(ruta_fichero)`**: aplica los filtros de calidad, indica
  cuántas filas elimina en cada paso y genera
  `datos/telemetria_limpia.csv`.

### 1.2 ¿Para qué sirve hashear?

SHA-256 es una función resumen criptográfica que convierte cualquier
fichero en una cadena de 64 caracteres hexadecimales. Es determinista,
unidireccional (no se puede reconstruir el dato a partir del hash).
(efecto avalancha: modificar un solo carácter altera el hash por completo).
En esta práctica se usa para:

- **Verificar la integridad** del fichero recibido, comparándolo con el
   hash de referencia del enunciado.
- **Garantizar la trazabilidad**: el hash identifica una versión concreta
   del dato.
- **Demostrar que la depuración modificó el fichero**: el hash del limpio
   debe ser distinto del original.

### 1.3 Comparativa de hashes
 
 `telemetria_envios.csv` (original): 4471c18a0284b3aa5b32a0713e691e3c7fcadae402f105e901c7c57f49474911
 `telemetria_limpia.csv` (saneado): fd4e27a6a9331718e2c6d795cadbcf34ef285b366a8ff16e000dfc26505bf91b

El hash del original coincide con el de referencia del enunciado
(`4471c...911`). El hash del limpio es distinto, lo que confirma que el contenido
cambió tras la depuración.


