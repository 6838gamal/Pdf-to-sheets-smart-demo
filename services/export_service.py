import pandas as pd

def save_csv(data, path):
    """
    يحفظ البيانات في CSV
    """
    df = pd.DataFrame(data)
    df.to_csv(path, index=False)
    return path

def save_xlsx(data, path):
    """
    يحفظ البيانات في XLSX
    """
    df = pd.DataFrame(data)
    df.to_excel(path, index=False)
    return path
