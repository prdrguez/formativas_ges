import chardet
import pandas as pd

def leer_csv_con_encoding_detectado(path, sep):
    with open(path, 'rb') as file:
        result = chardet.detect(file.read())
    return pd.read_csv(path, encoding=result['encoding'], sep=sep)