import xlrd
import json

path = r'C:\Users\Admin\Documents\카카오톡 받은 파일\666.xls'
wb = xlrd.open_workbook(path)
ws = wb.sheet_by_name('Sheet')

from collections import defaultdict
monthly = defaultdict(lambda: {'pe_cn':[], 'pp_cn':[], 'pe_sea':[], 'pp_sea':[]})

for r in range(1, ws.nrows):
    ym_raw = ws.cell_value(r, 1)
    if not ym_raw:
        continue
    ym = str(int(float(ym_raw)))
    for col, key in [(2,'pe_cn'),(3,'pp_cn'),(4,'pe_sea'),(5,'pp_sea')]:
        v = ws.cell_value(r, col)
        if v and float(v) > 0:
            monthly[ym][key].append(float(v))

result = {}
for ym in sorted(monthly.keys()):
    d = monthly[ym]
    result[ym] = {
        'pe_cn':  round(sum(d['pe_cn'])/len(d['pe_cn']),1)  if d['pe_cn']  else None,
        'pp_cn':  round(sum(d['pp_cn'])/len(d['pp_cn']),1)  if d['pp_cn']  else None,
        'pe_sea': round(sum(d['pe_sea'])/len(d['pe_sea']),1) if d['pe_sea'] else None,
        'pp_sea': round(sum(d['pp_sea'])/len(d['pp_sea']),1) if d['pp_sea'] else None,
    }

print(json.dumps(result, ensure_ascii=False, indent=2))
