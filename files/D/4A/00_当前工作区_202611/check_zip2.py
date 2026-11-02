import zipfile
import sys

sys.stdout.reconfigure(encoding='utf-8')

zip_path = r"D:\4A\01_便签店运营_2026-10\4A便签店运营归档_终版_20261101.zip"
with zipfile.ZipFile(zip_path, 'r') as z:
    for name in z.namelist():
        if any(k in name for k in ['库存', '订单', '10-31', '11-01', 'FBA', 'Order', 'Inventory']):
            print(name)
