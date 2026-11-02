import os

items = os.listdir(b"D:\\4A")
for it in items:
    print("bytes:", repr(it))
    try:
        print("gbk:", repr(it.decode("gbk")))
    except:
        pass
    try:
        print("utf-8:", repr(it.decode("utf-8")))
    except:
        pass
