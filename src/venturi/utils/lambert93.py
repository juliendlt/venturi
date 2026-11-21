"""Conversion de coordonnées Lambert-93 (EPSG:2154) en longitude / latitude.

Projection conique conforme de Lambert sur l'ellipsoïde GRS80, inversée selon
l'algorithme ALG0004 de l'IGN. Le résultat est en RGF93, confondu avec le WGS84 à
moins d'un mètre : suffisant pour placer un aérogénérateur sur une carte.

Les fonctions travaillent sur des colonnes Spark, sans UDF ni dépendance.
"""

from __future__ import annotations

import math

from pyspark.sql import Column
from pyspark.sql import functions as F

# Constantes de la projection Lambert-93.
_N = 0.7256077650532670  # exposant de la projection
_C = 11754255.426096  # constante de la projection (m)
_XS = 700000.0  # abscisse du pôle (m)
_YS = 12655612.049876  # ordonnée du pôle (m)
_LONGITUDE_ORIGIN_DEG = 3.0  # méridien central : 3° Est de Greenwich
_E = 0.0818191910428158  # première excentricité de GRS80

# La latitude s'obtient par approximations successives : chaque itération gagne un
# facteur e² (environ 150). Cinq itérations donnent une précision bien inférieure
# au millimètre.
_LATITUDE_ITERATIONS = 5


def lambert93_to_longitude(x: Column, y: Column) -> Column:
    """Longitude en degrés décimaux, à partir de x / y en mètres."""
    gamma = F.atan((x - F.lit(_XS)) / (F.lit(_YS) - y))
    return F.lit(_LONGITUDE_ORIGIN_DEG) + F.degrees(gamma / F.lit(_N))


def lambert93_to_latitude(x: Column, y: Column) -> Column:
    """Latitude en degrés décimaux, à partir de x / y en mètres."""
    radius = F.sqrt(F.pow(x - F.lit(_XS), 2) + F.pow(y - F.lit(_YS), 2))
    # exp(latitude isométrique)
    exp_isometric = F.pow(radius / F.lit(_C), -1.0 / _N)

    latitude = F.lit(2.0) * F.atan(exp_isometric) - F.lit(math.pi / 2)
    for _ in range(_LATITUDE_ITERATIONS):
        e_sin = F.lit(_E) * F.sin(latitude)
        correction = F.pow((F.lit(1.0) + e_sin) / (F.lit(1.0) - e_sin), _E / 2)
        latitude = F.lit(2.0) * F.atan(correction * exp_isometric) - F.lit(math.pi / 2)
    return F.degrees(latitude)
