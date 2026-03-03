def normalize_table(data):
    """
    يجعل كل الصفوف بنفس عدد الأعمدة
    """

    if not data:
        return data

    max_cols = max(len(row) for row in data)

    new_data = []

    for row in data:

        row = list(row)

        if len(row) < max_cols:
            row += [""] * (max_cols - len(row))

        new_data.append(row)

    return new_data


def json_to_rows(json_data):
    """
    يحول JSON إلى صفوف
    """

    if isinstance(json_data, dict):

        keys = list(json_data.keys())

        values = list(json_data.values())

        return [keys, values]

    if isinstance(json_data, list):

        rows = []

        for item in json_data:

            if isinstance(item, dict):

                rows.append(list(item.values()))

            else:

                rows.append(item)

        return rows

    return []
