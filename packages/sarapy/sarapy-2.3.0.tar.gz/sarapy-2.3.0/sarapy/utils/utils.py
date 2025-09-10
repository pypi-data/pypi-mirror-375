from typing import List, Tuple

import numpy as np
import pandas as pd
from pathlib import Path
from sarapy.analysis.FeaturesResume import FeaturesResume

def dataMerging(historical_data, post_processing_data, raw_data, nodoName = None, newColumns = False, asDF = False):
    """
    Función para tomar historical_data y post_processing_data y formar una 
    sóla lista de diccionarios (json)

    Si newColumns es False la función reemplaza los valores de tag_seedling y tag_fertilizer de historical_data,
    sino genera dos nuevos campos llamados tag_seedling_classified y tag_fertilizer_estimated en historical_data.

    Args:
        - historical_data (list): Lista de diccionarios con datos históricos (tipo json)
        - post_processing_data (list): Lista de diccionarios con datos de post-procesamiento (tipo json)
        - nodoName (str|None): Nombre del nodo al que pertenecen los datos. Por defecto es None
        - newColumns (bool): Indica si se deben crear nuevas columnas en lugar de reemplazar las existentes.
        - asDF (bool): Indica si se debe retornar como un dataframe o no
    """
    #chequeo que historical_data y post_processing_data sean del mismo tamaño, sino rais
    if len(historical_data) != len(post_processing_data):
        raise ValueError("Las listas de datos históricos y de post-procesamiento no son del mismo tamaño.")

    final_data = pd.DataFrame(historical_data)
    post_data = pd.DataFrame(post_processing_data)
    raw_data = pd.DataFrame(raw_data)

    final_data['raw_tag_seedling'] = raw_data['raw_tag_seedling']
    final_data['raw_tag_fertilizer'] = raw_data['raw_tag_fertilizer']

    if not newColumns:
        final_data['tag_seedling'] = post_data['tag_seedling']
        final_data['tag_fertilizer'] = post_data['tag_fertilizer']
    else:
        final_data['tag_seedling_classified'] = post_data['tag_seedling']
        final_data['tag_fertilizer_estimated'] = post_data['tag_fertilizer']

    if nodoName:
        final_data['nodo'] = nodoName

    #retorno como lista de diccionarios (json)
    if not asDF:
        return final_data.to_dict(orient='records')
    else:
        return final_data

def getOutliersThresholds(data, q1 = 0.25, q3 = 0.75, k = 1.5):
    """Cálculo de los límites para detectar outliers a partir del rango intercuartil
    
    data: array con los datos
    q1: primer cuartil
    q3: tercer cuartil
    k: factor de escala
    """
    # Calculo del rango intercuartil
    q1 = np.quantile(data, q1)
    q3 = np.quantile(data, q3)
    iqr = q3 - q1

    # Cálculo de los límites
    lower = q1 - k * iqr
    upper = q3 + k * iqr

    return lower, upper


def countingZeros(array: List[int], minimos_seguidos: int = 3) -> List[Tuple[int, int]]:
    """
    Cuenta ceros consecutivos en un array binario (0s y 1s), retornando una lista de tuplas.
    Cada tupla (n, k) indica que se encontraron 'n' secuencias de 'k' ceros consecutivos,
    siempre que k >= minimos_seguidos.
    
    Parameters:
        array (List[int]): Lista binaria de 0s y 1s.
        minimos_seguidos (int): Mínimo de ceros consecutivos a considerar.
        
    Returns:
        List[Tuple[int, int]]: Lista de tuplas (n, k), ordenadas por k.
    """
    contador = 0
    resultados = {}
    indexes = []
    for i, val in enumerate(array):
        if val == 0:
            contador += 1
            indexes.append(i)
        else:
            if contador >= minimos_seguidos:
                if contador in resultados.keys():
                    resultados[contador][0] += 1
                    resultados[contador][1] += (indexes,)
                    indexes = []
                else:
                    resultados[contador] = [1, (indexes,)]
                    indexes = []
            contador = 0

    # Por si la secuencia termina en ceros
    if contador >= minimos_seguidos:
        if contador in resultados.keys():
            resultados[contador][0] += 1
            resultados[contador][1] += (indexes,)
            indexes = []
        else:
            resultados[contador] = [1, (indexes,)]

    # retorna [cantidad de ocurrencias, longitud de ceros, indices de ocurrencias]
    return sorted([(v[0], k, v[1]) for k, v in resultados.items()])

def get_lat_long_from_indices(df: pd.DataFrame, indices: List[List[int]]) -> Tuple[float, float]:
    """
    Obtiene la latitud y longitud a partir de una lista de índices en un DataFrame.
    
    Parameters:
        df (pd.DataFrame): DataFrame que contiene las columnas 'latitude' y 'longitude'.
        indices (List[int]): Lista de listas de índices para buscar las coordenadas.
        
    Returns:
        Tuple[float, float]: Tupla con la latitud y longitud correspondientes.
    """
    latitudes = []
    longitudes = []
    nodos = []
    for index_list in indices:
        for index in index_list:
            latitudes.append(df.iloc[index]["latitude"])
            longitudes.append(df.iloc[index]["longitude"])
            nodos.append(df.iloc[index]["nodo"])
    return [nodos, latitudes, longitudes]


def readingFolders(raiz: str | Path, ignorar_ocultas: bool = True, ordenar: bool = True) -> list[str]:
    raiz = Path(raiz)
    if not raiz.is_dir():
        raise NotADirectoryError(f"La ruta no es una carpeta: {raiz}")

    nombres = [p.name for p in raiz.iterdir() if p.is_dir()]
    if ignorar_ocultas:
        nombres = [n for n in nombres if not n.startswith(".")]
    if ordenar:
        nombres.sort()
    return nombres

def computar_resumenes_por_filtro(nodos_ok, merged_cache, filtro, outliers):
        """
        Función para computar resúmenes filtrados por un criterio específico.
        """
        conteos, resumenes, dstp_ptmas, delta_dcdp, time_ac = {}, {}, {}, {}, {}
        for nodo in nodos_ok:
            fr = FeaturesResume(merged_cache[nodo], info=nodo, filtrar=filtro)
            fr.removeOutliers(outliers)
            conteos[nodo] = fr.data["tag_seedling"].value_counts(normalize=True)
            resumenes[nodo] = fr.getResume(to="all")
            dstp_ptmas[nodo] = fr.getSensorMA()
            delta_dcdp[nodo] = fr.data["ratio_dCdP"]
            time_ac[nodo] = fr.data["time_ac"]
        return conteos, resumenes

def metricas_desde_resumenes(nodos_ok, resumenes, stats):
    """Devuelve dict nombre_metrica -> vector numpy en el orden de nodos_ok."""
    return {
        "nodo": [n for n in nodos_ok],
        "time_ac":   np.array([resumenes[n]["time_ac"][stats]   for n in nodos_ok]),
        "deltaO":    np.array([resumenes[n]["deltaO"][stats]    for n in nodos_ok]),
        "ratio_dCdP":np.array([resumenes[n]["ratio_dCdP"][stats]for n in nodos_ok]),
        "precision": np.array([resumenes[n]["precision"][stats] for n in nodos_ok]),
        "distances": np.array([resumenes[n]["distances"][stats] for n in nodos_ok]),
        "dst_pt":    np.array([resumenes[n]["dst_pt"][stats]    for n in nodos_ok]),
    }