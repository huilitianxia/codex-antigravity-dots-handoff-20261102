import hashlib, json, zipfile
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime

ROOT = Path('D:/4A/01_便签店运营_2026-10')
OUT = Path(__file__).parent / 'D盘只读审计_20261101.json'

def digest(stream):
    h = hashlib.sha256()
    while chunk := stream.read(1024 * 1024):
        h.update(chunk)
    return h.hexdigest()

files = []
by_hash = defaultdict(list)
groups = defaultdict(lambda: {'files': 0, 'bytes': 0})
for p in sorted(ROOT.rglob('*')):
    if not p.is_file():
        continue
    rel = p.relative_to(ROOT).as_posix()
    size = p.stat().st_size
    with p.open('rb') as f:
        sha = digest(f)
    entry = {'path': rel, 'bytes': size, 'sha256': sha}
    files.append(entry)
    if p.parent != ROOT or p.suffix.lower() != '.zip':
        by_hash[sha].append(rel)
    group = rel.split('/')[0]
    groups[group]['files'] += 1
    groups[group]['bytes'] += size

zip_path = next(ROOT.glob('*.zip'))
zip_entries, zip_errors = [], []
with zipfile.ZipFile(zip_path) as z:
    for item in z.infolist():
        if item.is_dir():
            continue
        try:
            with z.open(item) as stream:
                sha = digest(stream)
            zip_entries.append({'archive_path': item.filename, 'bytes': item.file_size,
                                'sha256': sha, 'matching_current_paths': by_hash.get(sha, [])})
        except Exception as e:
            zip_errors.append({'archive_path': item.filename, 'error': str(e)})

bucket_names = ['原图参考', '生成源图', '_核验依据', '_核心依据', '交付候选_2000px',
                '交付终选_2000px', '可交付_已批准', '审稿待核_2000px']
buckets = {}
for name in bucket_names:
    subset = [f for f in files if name in Path(f['path']).parts]
    buckets[name] = {'files': len(subset), 'bytes': sum(f['bytes'] for f in subset),
                     'suffix_counts': dict(Counter(Path(f['path']).suffix.lower() for f in subset))}
missing = [e for e in zip_entries if not e['matching_current_paths']]
duplicate_groups = [{'sha256': sha, 'paths': paths} for sha, paths in by_hash.items() if len(paths) > 1]
summary = {
    'audited_at': datetime.now().astimezone().isoformat(), 'root': str(ROOT),
    'read_only_source': True, 'file_count': len(files), 'bytes': sum(f['bytes'] for f in files),
    'top_level': dict(groups), 'image_buckets': buckets,
    'zip': {'path': str(zip_path), 'archive_bytes': zip_path.stat().st_size,
            'file_entries': len(zip_entries), 'uncompressed_bytes': sum(e['bytes'] for e in zip_entries),
            'entries_matching_current_content': len(zip_entries)-len(missing),
            'unmatched_entries': len(missing), 'unmatched_bytes': sum(e['bytes'] for e in missing),
            'read_crc_errors': zip_errors, 'unmatched_details': missing},
    'exact_duplicate_groups': duplicate_groups,
    'files': files, 'zip_entries': zip_entries,
    'limitations': ['Hashes establish identical file content, not correctness, upload status, project dependency safety, or independent backup sufficiency.',
                   'Only the named D-drive tree was compared; an unmatched archive file may exist elsewhere. No files were removed or extracted.']
}
OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k not in ('files','zip_entries','exact_duplicate_groups')}, ensure_ascii=False, indent=2))
