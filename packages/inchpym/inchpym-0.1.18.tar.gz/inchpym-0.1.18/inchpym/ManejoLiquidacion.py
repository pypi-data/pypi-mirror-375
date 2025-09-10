import numpy as np

def corregirSiAplicaExcp(df,ResultadoSinExp,ColumnaExcepcion,ColumnaAfectaRanking):
    df[ColumnaExcepcion] = np.where((df[ResultadoSinExp]==True),False,df[ColumnaExcepcion])
    df[ColumnaAfectaRanking] = np.where((df[ResultadoSinExp]==True),False,df[ColumnaAfectaRanking])
