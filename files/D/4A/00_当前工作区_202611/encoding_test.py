raw = b'00_Codex\xe4\xba\xa4\xe6\x8e\xa5\xe7\xbb\x99Gemini_20261101'
print("Decoded with GBK:", repr(raw.decode('gbk', errors='replace')))
print("Decoded with UTF-8:", repr(raw.decode('utf-8', errors='replace')))
s = '00_Codex交接给Gemini_20261101'
print("s encoded in GBK:", repr(s.encode('gbk')))
print("s encoded in UTF-8:", repr(s.encode('utf-8')))
