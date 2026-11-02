import os

items = os.listdir(r"D:\4A")
for it in items:
    print(repr(it), os.path.isdir(os.path.join(r"D:\4A", it)))
