## Práctica Formativa Integradora

## Sección 1. Integridad del dato (Módulo 5075)
### Comparativa de hashes
 
 `telemetria_envios.csv` (original): 4471c18a0284b3aa5b32a0713e691e3c7fcadae402f105e901c7c57f49474911
 `telemetria_limpia.csv` (saneado): fd4e27a6a9331718e2c6d795cadbcf34ef285b366a8ff16e000dfc26505bf91b

El hash del original coincide con el de referencia del enunciado
(`4471c...911`). El hash del limpio es distinto, lo que confirma que el contenido
cambió tras la depuración.

## 2. Despliegue y HDFS (Módulo 5074)

Se despliega un clúster Hadoop 3.4.0 con Docker Compose, con un contenedor por demonio:

| Contenedor | Demonio | Puertos |
|---|---|---|
| `lab-namenode` | NameNode | 9870 (Web UI), 8020 |
| `lab-datanode` | DataNode | – |
| `lab-resourcemanager` | ResourceManager | 8088 (Web UI) |
| `lab-nodemanager` | NodeManager | – |

El volumen `./datos` se monta en `/workspace` del NameNode. La replicación está en 1 porque solo hay un DataNode.

**Despliegue y verificación:**

```bash
docker compose up -d
docker exec lab-namenode jps
docker exec lab-datanode jps
docker exec lab-resourcemanager jps
docker exec lab-nodemanager jps
```

**Comandos HDFS** (dentro de `docker exec -it lab-namenode bash`):

```bash
hdfs dfs -mkdir -p /empresa/logistica/input
hdfs dfs -put /workspace/telemetria_limpia.csv /empresa/logistica/input/
hdfs dfs -ls /empresa/logistica/input/
hdfs dfs -head /empresa/logistica/input/telemetria_limpia.csv
hdfs fsck /empresa/logistica/input/telemetria_limpia.csv -files -blocks -locations
```

**Resultado de `fsck`:** bloque `<blk_...>`, 1 réplica, almacenado en el DataNode `<IP:9866>`, estado `<HEALTHY>`.


## 3. Análisis crítico

**¿Por qué un fichero en HDFS no se corrompe ni se pierde aunque falle o se apague un DataNode en un clúster de producción?**

HDFS no confía en la fiabilidad de un único disco o servidor, sino en la
**redundancia**. Los ficheros se dividen en bloques (128 MB por defecto) y
cada bloque se replica en varios DataNodes, normalmente con un factor de
replicación de 3. La política de colocación tiene en cuenta los racks: una
réplica en el nodo de escritura y otras dos en un rack distinto. Así, la
caída de un disco, un nodo o incluso un rack completo no elimina todas las
copias de un bloque. Los DataNodes envían *heartbeats* periódicos al
NameNode; si uno deja de responder, se marca como muerto y el NameNode
detecta qué bloques han quedado *under-replicated*. Entonces ordena copiar
esos bloques desde las réplicas supervivientes a otros nodos hasta recuperar
el factor de replicación, sin intervención humana y de forma transparente
para las aplicaciones, que leen de cualquier réplica disponible.

Frente a la **corrupción silenciosa**, HDFS calcula checksums (CRC32C) por
cada pequeño tramo de datos (512 bytes por defecto), que se guardan junto al
bloque. Se verifican al leer, y además cada DataNode ejecuta un escáner de
bloques en segundo plano. Si se detecta una réplica corrupta, el cliente
lee otra réplica sana, y el NameNode marca la dañada y la sustituye por una
copia correcta. Es el mismo principio de integridad que aplicamos en el
Bloque A con SHA-256, pero aplicado de forma continua y automática a cada
bloque.

Por último, la disponibilidad de los **metadatos** (qué bloques forman cada
fichero y dónde están) se protege con una arquitectura de alta
disponibilidad: un NameNode activo y otro en espera, sincronizados mediante
JournalNodes y coordinados con ZooKeeper, que permiten un *failover*
automático. Hay que subrayar que nuestro laboratorio, con un único DataNode
y `dfs.replication=1`, **no** tiene esta protección: si ese DataNode se
apagara, el bloque quedaría inaccesible. La tolerancia a fallos es una
propiedad del clúster de producción (varios DataNodes y réplicas), no de HDFS
como software aislado.