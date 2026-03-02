import pandas as pd
import os


def save_table(data, output_dir, name):

    df = pd.DataFrame(data)

    csv_path = os.path.join(output_dir, name + ".csv")
    xlsx_path = os.path.join(output_dir, name + ".xlsx")

    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False)

    return csv_path, xlsx_path
