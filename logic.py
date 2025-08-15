import pandas as pd
import re

def extract_floor_from_sheet(sheet_name):
    name = str(sheet_name).strip()
    if re.match(r'^00(\D|$)', name):
        return '00'
    if re.match(r'^0(\D|$)', name):
        return '0'
    m = re.match(r'^(\d+)', name)
    if m:
        return m.group(1)
    return None

def normalize_key(s):
    s = str(s).strip().lower()
    s = re.sub(r'[\u2013\u2014\u2212]', '-', s)
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', s)
    return s

def clean_and_aggregate(xl):
    floors = {}
    for sheet in xl.sheet_names:
        floor = extract_floor_from_sheet(sheet)
        if floor is None:
            continue
        df = xl.parse(sheet, header=None)
        df = df.dropna(how='all')
        if df.shape[0] == 0:
            continue
        # Проверяем первые две строки на наличие заголовков
        header_row = None
        for i in range(min(2, df.shape[0])):
            cols = [str(x).lower() for x in df.iloc[i]]
            if any('марка' in c for c in cols) and (any('наимен' in c for c in cols) or any('опис' in c for c in cols)):
                header_row = i
                break
        if header_row is not None:
            # Если нашли заголовки — используем их
            df.columns = df.iloc[header_row].astype(str)
            df = df.iloc[header_row+1:]
            cols = list(df.columns)
            mark_col = next((c for c in cols if re.search(r'марка', c, re.I)), cols[0])
            name_col = next((c for c in cols if re.search(r'наимен|опис', c, re.I)), cols[1])
            name_idx = cols.index(name_col)
            qty_col = cols[name_idx+1] if name_idx+1 < len(cols) else cols[-1]
            df = df[[mark_col, name_col, qty_col]].copy()
            df.columns = ['Марка', 'Наименование', 'Количество']
        else:
            # Если не нашли заголовки — просто берём первые 3 столбца и присваиваем имена
            cols = list(df.columns)[:3]
            df = df[cols].copy()
            df.columns = ['Марка', 'Наименование', 'Количество']
        # Привести количество к числу
        df['Количество'] = pd.to_numeric(df['Количество'], errors='coerce').fillna(0)
        # Нормализовать ключи
        df['Марка_norm'] = df['Марка'].apply(normalize_key)
        df['Наименование_norm'] = df['Наименование'].apply(normalize_key)
        df = df.groupby(['Марка_norm', 'Наименование_norm'], as_index=False).agg({'Марка':'first', 'Наименование':'first', 'Количество':'sum'})
        if floor not in floors:
            floors[floor] = []
        floors[floor].append(df)
    # Объединить по этажам
    for floor in floors:
        floors[floor] = pd.concat(floors[floor], ignore_index=True).groupby(['Марка_norm', 'Наименование_norm'], as_index=False).agg({'Марка':'first', 'Наименование':'first', 'Количество':'sum'})
    return floors

def build_final_table_multi(floors, multipliers):
    all_keys = set()
    for df in floors.values():
        for _, row in df.iterrows():
            all_keys.add((row['Марка_norm'], row['Наименование_norm']))
    df0 = floors.get('0', None)
    if df0 is not None:
        for _, row in df0.iterrows():
            all_keys.add((row['Марка_norm'], row['Наименование_norm']))
    all_keys = sorted(all_keys)
    floor_nums = sorted([f for f in floors if not (str(f).startswith('0') and str(f) != '0') and str(f) != '0'], key=lambda x: (len(str(x)), str(x)))
    podval_nums = [f for f in floors if str(f).startswith('0') and str(f) != '0']
    print('DEBUG: multipliers:', multipliers)
    print('DEBUG: floor_nums:', floor_nums)
    print('DEBUG: podval_nums:', podval_nums)
    data = []
    for key in all_keys:
        row = {}
        for df in floors.values():
            found = df[(df['Марка_norm'] == key[0]) & (df['Наименование_norm'] == key[1])]
            if not found.empty:
                row['Марка'] = found.iloc[0]['Марка']
                row['Наименование'] = found.iloc[0]['Наименование']
                break
        df0 = floors.get('0', None)
        if df0 is None:
            row['Сводная'] = 0
        else:
            found = df0[(df0['Марка_norm'] == key[0]) & (df0['Наименование_norm'] == key[1])]
            row['Сводная'] = float(found['Количество'].iloc[0]) if not found.empty else 0
        podval_val = 0.0
        for f in podval_nums:
            dfp = floors[f]
            found = dfp[(dfp['Марка_norm'] == key[0]) & (dfp['Наименование_norm'] == key[1])]
            val = float(found['Количество'].iloc[0]) * multipliers.get(f, 1) if not found.empty else 0
            podval_val += val
            print(f'DEBUG: key={key}, podval floor={f}, val={val}, multiplier={multipliers.get(f, 1)}')
        if podval_nums:
            row['Подвал'] = podval_val
        sum_etazhi = 0
        for f in floor_nums:
            dff = floors[f]
            found = dff[(dff['Марка_norm'] == key[0]) & (dff['Наименование_norm'] == key[1])]
            val = float(found['Количество'].iloc[0]) * multipliers.get(f, 1) if not found.empty else 0
            row[f] = val
            sum_etazhi += val
            print(f'DEBUG: key={key}, floor={f}, val={val}, multiplier={multipliers.get(f, 1)}')
        row['Сумма этажей'] = sum_etazhi
        row['Проверка'] = row.get('Сводная', 0) - (sum_etazhi + row.get('Подвал', 0))
        print(f'DEBUG: key={key}, Сводная={row.get("Сводная", 0)}, Сумма этажей={sum_etazhi}, Подвал={row.get("Подвал", 0)}, Проверка={row["Проверка"]}')
        data.append(row)
    columns = ['Марка', 'Наименование', 'Сводная']
    if podval_nums:
        columns.append('Подвал')
    columns += floor_nums
    columns += ['Сумма этажей', 'Проверка']
    df_final = pd.DataFrame(data, columns=columns)
    return df_final
