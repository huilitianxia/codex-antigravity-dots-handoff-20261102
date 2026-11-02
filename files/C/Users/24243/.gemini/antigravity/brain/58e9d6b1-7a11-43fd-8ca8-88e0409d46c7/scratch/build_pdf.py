import os
import shutil
import subprocess

base = r"C:\Users\24243\.gemini\antigravity\brain\58e9d6b1-7a11-43fd-8ca8-88e0409d46c7"
scratch = os.path.join(base, "scratch")
html_path = os.path.join(scratch, "report.html")
pdf_ascii = os.path.join(scratch, "report.pdf")
profile_dir = os.path.join(scratch, "browser_profile")
os.makedirs(profile_dir, exist_ok=True)

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
browser = chrome_path if os.path.exists(chrome_path) else edge_path

cmd = [
    browser,
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    f"--user-data-dir={profile_dir}",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_ascii}",
    html_path,
]

print("Running:", " ".join(cmd))
res = subprocess.run(cmd, capture_output=True, text=True)
print("Return code:", res.returncode)
if res.stderr:
    print("Stderr:", res.stderr[:500])

if os.path.exists(pdf_ascii):
    cn_name = "周慧天_生涯发展报告_成长赛道.pdf"
    dst1 = os.path.join(base, cn_name)
    dst2 = os.path.join(r"C:\Users\24243\.gemini\antigravity\scratch", cn_name)
    os.makedirs(os.path.dirname(dst2), exist_ok=True)
    shutil.copy2(pdf_ascii, dst1)
    shutil.copy2(pdf_ascii, dst2)
    subprocess.Popen(["explorer.exe", f"/select,{dst2}"])
    print("SUCCESS! PDF size:", os.path.getsize(dst1), "bytes")
    print("Saved to:", dst1)
    print("Saved to:", dst2)
else:
    print("FAILED: report.pdf was not created")
