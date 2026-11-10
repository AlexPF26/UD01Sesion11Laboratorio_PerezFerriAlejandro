import hashlib
from pathlib import Path

import pandas as pd

# --- Rutas (relativas a la raíz del repo, independientes del directorio de ejecución) ---
RAIZ = Path(__file__).resolve().parent.parent
DIR_DATOS = RAIZ / "datos"
RUTA_ORIGINAL = DIR_DATOS / "telemetria_envios.csv"
RUTA_LIMPIO = DIR_DATOS / "telemetria_limpia.csv"

# --- Criterios de calidad ---
CAMPOS_CLAVE = ["temp_celsius", "peso_kg", "destino"]
TEMP_MIN, TEMP_MAX = -30, 50
ESTADOS_VALIDOS = {"ENTREGADO", "EN_TRANSITO", "EN_REPARTO"}  # ajústalo tras describir_csv


def obtener_sha256(ruta_fichero):
    """Calcula el SHA-256 de un fichero leyéndolo por bloques."""
    sha = hashlib.sha256()
    with open(ruta_fichero, "rb") as f:
        for bloque in iter(lambda: f.read(4096), b""):
            sha.update(bloque)
    return sha.hexdigest()


def _detectar_anomalias(df):
    """Devuelve {descripción: máscara booleana} con las filas problemáticas."""
    return {
        "Nulos en campos clave": df[CAMPOS_CLAVE].isna().any(axis=1),
        "Peso <= 0": df["peso_kg"] <= 0,
        f"Temperatura fuera de [{TEMP_MIN}, {TEMP_MAX}] °C":
            df["temp_celsius"].notna() & ~df["temp_celsius"].between(TEMP_MIN, TEMP_MAX),
        "Estado no catalogado":
            df["estado_envio"].notna() & ~df["estado_envio"].isin(ESTADOS_VALIDOS),
    }


def describir_csv(ruta_fichero):
    """Muestra estructura, nulos, duplicados y valores erróneos del CSV."""
    df = pd.read_csv(ruta_fichero)

    print(f"=== ESTRUCTURA: {ruta_fichero} ===")
    print(f"Filas: {df.shape[0]} | Columnas: {df.shape[1]}")
    print(df.dtypes, "\n")

    print("=== NULOS POR COLUMNA ===")
    print(df.isna().sum(), "\n")

    print("=== DUPLICADOS (filas completas repetidas) ===")
    print(f"{df.duplicated().sum()} filas duplicadas\n")
    print(f"Filas duplicadas:\n{df[df.duplicated(keep=False)]}") #Mostrar las filas duplicadas

    print("=== VALORES ERRÓNEOS ===")
    for nombre, mascara in _detectar_anomalias(df).items():
        print(f"{nombre}: {mascara.sum()} filas")
        if mascara.any():
            print(df[mascara].head(5).to_string(), "\n")

    print("=== ESTADOS PRESENTES ===")
    print(df["estado_envio"].value_counts(dropna=False), "\n")

    print("=== ESTADÍSTICAS NUMÉRICAS ===")
    print(df.describe())


def limpiar_csv(ruta_fichero, ruta_salida=RUTA_LIMPIO):
    """Elimina duplicados y filas inválidas; guarda telemetria_limpia.csv en datos/."""
    df = pd.read_csv(ruta_fichero)
    print(f"Filas iniciales: {len(df)}")

    # 1. Duplicados
    antes = len(df)
    df = df.drop_duplicates()
    print(f"- Duplicados eliminados: {antes - len(df)}")

    # 2. Resto de anomalías, paso a paso
    for nombre, mascara in _detectar_anomalias(df).items():
        antes = len(df)
        df = df[~mascara.loc[df.index]]
        print(f"- {nombre}: {antes - len(df)} eliminadas")

    Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta_salida, index=False, encoding="utf-8")
    print(f"Filas finales: {len(df)} -> {ruta_salida}")
    return df


def main():
    hash_original = obtener_sha256(RUTA_ORIGINAL)
    print(f"SHA-256 original: {hash_original}\n")

    describir_csv(RUTA_ORIGINAL)

    print("\n=== LIMPIEZA ===")
    limpiar_csv(RUTA_ORIGINAL)

    hash_limpio = obtener_sha256(RUTA_LIMPIO)
    print("\n=== COMPARATIVA DE HASHES ===")
    print(f"SHA-256 original: {hash_original}")
    print(f"SHA-256 limpio:   {hash_limpio}")
    print(f"¿Han cambiado?    {hash_original != hash_limpio}")


if __name__ == "__main__":
    main()