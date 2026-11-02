import json,re,collections,html
from pathlib import Path
import scan_text_batch as scan
P=Path(__file__).parent
raw=scan.rows
current=scan.current
key=lambda prefix:next(k for _,k in scan.raw['headers'] if k and k.startswith(prefix))
TITLE=key('item_name[');HIGH=key('title_differentiation[');DESC=key('product_description[')
BUL=[k for _,k in scan.raw['headers'] if k and k.startswith('bullet_point[')]
plan=json.loads((P/'v4-receipt-repair-plan.json').read_text(encoding='utf8'))
identity_hold={r['sku']:sorted({i['code'] for i in r['issues'] if i['code'] in ['8541','13013','100390','100477','100720']}) for r in plan['records']}
identity_hold={k:v for k,v in identity_hold.items() if v}
identity_hold.update({'4A 189':['pack_identity_conflict'],'4A001':['pack_identity_conflict']})
pending_bullets={x['sku'] for x in scan.sent if x['file'][:2] in ['06','11']}
previous_live_bullet_asins={'B07FKJNNHP','B07FK8ML41','B01N6J0VZO','B07F2FCHLK','B07F2CWVQ7','B07FKL115P','B07RQ6HLK3','B07RP8FX7N','B07RP95GGF'}
manual_pairs={
 '4A 6032':('4A File Tabs, 24 Tabs/Set','Transparent writable dividers and page markers; repositionable labels for folders and documents'),
 '4A 303-Holder+Flag':('4A Sticky Note and Pen Holder with 3 x 3 in Notes','Bright colored sticky notes with page marker tabs and flags for desk organization'),
 '4A GM303-AC-holder':('4A Sticky Note and Pen Holder with 3 x 3 in Notes','8 bright note colors, sticky tabs and Sign Here flags for desk organization'),
 '4A Meeting-51':('4A Tabletop Easel Pad and Dry Erase Board, 20 x 23 in','2-in-1 design with a built-in easel stand and 20 self-stick sheets'),
}

def norm(s):
 s=re.sub(r'\s+',' ',str(s)).strip(' ,.;')
 s=re.sub(r'^AAAA\s+4A\b','4A',s)
 s=re.sub(r'\bInches\b','in',s,flags=re.I)
 s=re.sub(r'(\d)\s*[xX]\s*(\d)',r'\1 x \2',s)
 s=re.sub(r'\b(?:Premium|High Quality|Super)\s+','',s,flags=re.I)
 s=re.sub(r'\bReuseable\b','Reusable',s,flags=re.I)
 s=re.sub(r'\bBoarder\b','Border',s,flags=re.I)
 s=re.sub(r'\bPage Maker\b','Page Marker',s,flags=re.I)
 s=re.sub(r'\s*,\s*',', ',s)
 return s

def pair(title):
 t=norm(title)
 if re.match(r'^4A Self-Stick Notes,',t):return None,'generic_source_title_identity_insufficient'
 t=re.sub(r',\s*/Pack', '/Pack',t,flags=re.I)
 t=re.sub(r'^(\d+ Packs?)\s+4A\s+',r'4A \1 ',t,flags=re.I)
 t=re.sub(r'\b3D Shape Printed Sticky Notes(?: Memo Pad)?\b','3D Printed Sticky Notes',t,flags=re.I)
 parts=[p.strip(' ,.;') for p in re.split(r',|\s*;\s*',t) if p.strip(' ,.;')]
 if not parts:return None,'missing_title'
 colorwords=r'(?:Neon |Pastel |Light |Dark )?(?:Yellow|Orange|Red|Pink|Blue|Green|Purple|Black|White)(?: and (?:Yellow|Orange|Red|Pink|Blue|Green|Purple|Black|White))?'
 grouped=[]
 for p in parts:
  if grouped and re.fullmatch(colorwords,p,re.I) and all(re.fullmatch(colorwords,q.strip(),re.I) for q in grouped[-1].split(',')):
   grouped[-1]+=', '+p
  else:grouped.append(p)
 parts=grouped
 # Keep the product identity intact. Split only at complete purpose/feature clauses.
 if len(parts[0])>75:
  head=re.split(r'\s+(?=for |with |Includes |Including )',parts[0],maxsplit=1,flags=re.I)
  if len(head)<2:return None,'identity_clause_over75'
  parts=head+parts[1:]
 base=parts[0]
 if not re.search(r'\b4A\b',base):base='4A '+base
 if len(base)>75:return None,'identity_clause_over75'
 # Redundant product-name phrases and promotional use cases do not need repetition.
 rest=[];removed=[]
 for p in parts[1:]:
  if re.match(r'^(?:AAAA\s+)?4A\s*[A-Z0-9]',p,re.I):removed.append(p);continue
  if re.match(r'^(?:Great for |More Sticky|Large Size$)',p,re.I):removed.append(p);continue
  if re.fullmatch(r'(?:Self[- ]Stick Notes|Sticky Notes|Sticky Note Pads|Sticky Note|Sticky|Note Pads)',p,re.I):removed.append(p);continue
  if re.fullmatch(r'(?:Home|Office|School|School Supplies|Notebooks?|Gift|Back to School Supplies)',p,re.I):removed.append(p);continue
  if re.match(r'^(?:Colorful |Cute |Small |Full Sticky Back |Non Sticky Memo Padsfor |Fun |Sticky Notes with Lines |Self-Stick Notes for Reminder)',p,re.I) and not re.search(r'\d',p):
   # These repeat the product name and generic usage, not variant specifications.
   if re.search(r'Index Tabs|Flags',p,re.I) and not re.search(r'Index|Tabs|Flags',base,re.I):p='Index tabs and flags'
   elif re.search(r'Lined|with Lines',p,re.I) and not re.search(r'Lined|with Lines',base,re.I):p='Lined note paper'
   elif re.search(r'Full Sticky Back',p,re.I) and not re.search(r'Full Adhesive|Full Sticky',base,re.I):p='Full adhesive backing'
   else:removed.append(p);continue
  if p.lower().startswith('neon color page marker'):p='Neon colors'
  if p.lower().startswith('color page marker fluorescent'):p='Color page markers'
  if p.lower().startswith('writable and repositionable arrow sticky flags annotation'):p='Writable, repositionable arrow flags for annotating books'
  if p.lower().startswith('writable sticky flags annotation'):p='Writable flags for annotating books'
  if p.lower().startswith('text highlighter strips writable'):
   size=re.search(r'\d+(?:\.\d+)?\s*x\s*\d+(?:\.\d+)?\s*mm',p,re.I)
   p='Writable labels and page markers'+(', '+size[0] if size else '')
  if p.lower() in ['page marker index label flags','transparent tabs flags stickers','transparent tabs stickers','transparent tabs flags']:p='Transparent page markers' if p.lower().startswith('transparent') else 'Page markers'
  p=re.sub(r'\bFlaging\b','Flagging',p,flags=re.I)
  p=re.sub(r'\bClose Size\s*:','Closed size:',p,flags=re.I)
  if p.casefold() in base.casefold() or p.casefold() in [x.casefold() for x in rest]:removed.append(p);continue
  rest.append(p)
 # Move full model names into the title before a generic colour-only highlight.
 if len(rest)==1 and re.search(r'\b(?:4A|[A-Z]{2,}|\d{3,})',rest[0]) and not re.search(r'\b(?:in|Sheets|Pads|Colors|Pack|Rolls)\b',rest[0],re.I):
  return None,'insufficient_highlight_facts'
 # Select whole attributes by importance: size/pack first, colour second, features next.
 def rank(x):
  if re.search(r'\d.*(?:\bin\b|\"|Round)',x,re.I):return 0
  if re.search(r'Yellow|Neon|Assorted|Black|White|Red|Blue|Green|Purple|Pink|Pastel|Lined|Blank|Print|Pattern|Colors',x,re.I):return 1
  if re.search(r'\d.*(?:Pads|Pad/Pack|Packs|Rolls|Pcs|Labels|Dispensers|Flags)',x,re.I):return 1
  if re.search(r'\d.*Sheets',x,re.I):return 2
  return 3
 selected=[]
 for i,p in sorted(enumerate(rest),key=lambda ip:(rank(ip[1]),ip[0])):
  candidate=', '.join([base]+[rest[j] for j in sorted(selected+[i])])
  # Keep at least one factual attribute in highlights.
  if rank(p)<3 and len(candidate)<=75 and len(selected)<len(rest)-1:selected.append(i)
 name=', '.join([base]+[rest[i] for i in sorted(selected)])
 highlights=', '.join(p for i,p in enumerate(rest) if i not in selected)
 if not highlights:return None,'no_highlight_facts'
 if len(highlights)>125:return None,'highlight_over125'
 if re.fullmatch(r'[A-Z0-9 x-]+',highlights) and not re.search(r'\b(?:Pads|Sheets|Pack|Rolls)\b',highlights,re.I):return None,'model_only_highlight'
 # Catalog indexing policy disallows repeated meaningful title words more than twice.
 words=[w.lower() for w in re.findall(r'[A-Za-z]+',name) if w.lower() not in ['and','or','the','a','an','for','with','in','x','of','to']]
 if any(n>2 for n in collections.Counter(words).values()):
  # Move a complete sheet-count clause out of the name when Pad/Cube repeats.
  for i in list(selected):
   if re.search(r'Sheets/(?:Pad|Cube)',rest[i],re.I):selected.remove(i)
  name=', '.join([base]+[rest[i] for i in sorted(selected)])
  highlights=', '.join(p for i,p in enumerate(rest) if i not in selected)
  if len(highlights)>125:return None,'highlight_over125'
  words=[w.lower() for w in re.findall(r'[A-Za-z]+',name) if w.lower() not in ['and','or','the','a','an','for','with','in','x','of','to']]
  if any(n>2 for n in collections.Counter(words).values()):return None,'repeated_title_words'
 return {'title':name,'highlight':highlights,'removed_redundancy':removed},None

def clean_bullet(v,index):
 if re.search(r'^\[?Recyclable\]?|^The paper .*certified',v,re.I):
  return 'Use the notes for written reminders and everyday lists.'
 if re.search(r'longer\s*and\s*stronger',v,re.I):
  return 'Self-stick backing for placing notes on smooth surfaces.'
 if re.search(r'good\s*price|free\s*shipping|^\[4A brand\]',v,re.I):
  return 'Keep written reminders together at home, school or the office.'
 if re.search(r'Christmas Gifts',v,re.I):return re.sub(r',?\s*Christmas Gifts','',v,flags=re.I).strip(' .')+'.'
 if re.search(r'\[Features\].*High quality paper',v,re.I):return 'Writable paper notes that are easy to peel from the pad.'
 if re.search(r'^No More Damaged Pages|^Durable & Reusable|^Write and Re-stick',v,re.I):return 'Writable paper for notes, reminders and page marking.'
 sheet_cube=re.search(r'\b(\d+) sheets high quality notes in one cube',v,re.I)
 if sheet_cube:return f'The memo cube contains {sheet_cube[1]} sheets for written notes and reminders.'
 # Retain existing sizes, quantities, materials and product terms; remove only unsupported claims.
 x=v
 x=re.sub(r'\bhigh quality\s*','',x,flags=re.I)
 x=re.sub(r'\bthick and recyclable\s+','',x,flags=re.I)
 x=re.sub(r'\brecyclable\s+','',x,flags=re.I)
 x=re.sub(r'\bEco-Friendly\s*:?\s*','',x,flags=re.I)
 x=re.sub(r'\b(?:Reliable\s*&\s*Durable|Durable\s*&\s*Reliable|High Quality|Reliable(?: Large| White)?(?: Self-Stick)?(?: Sticky Note Pads| Sticky Note Set| Book Tabs)|Durable\s*&\s*Reusable)\s*:\s*','',x,flags=re.I)
 # Universal no-residue/no-damage promises are not supported by material test evidence.
 x=re.sub(r'\s*(?:The strong adhesive|Sticks securely|The strong adhesive on top)\b.*','',x,flags=re.I)
 x=re.sub(r'\s+and removes? cleanly.*','',x,flags=re.I)
 x=re.sub(r',?\s*(?:yet removes? cleanly|no residue|no smudging or bleed-through).*','',x,flags=re.I)
 x=re.sub(r'\s+without (?:leaving |damaging |tearing ).*','',x,flags=re.I)
 x=re.sub(r'\s+ensuring .*','',x,flags=re.I)
 x=re.sub(r'\s*,\s*',', ',x)
 x=re.sub(r'\s+',' ',x).strip(' ,.;!:')
 if re.search(r'Eco-Friendly|Residue-Free|No Damage|Write and Re-stick|\bcertified\b',x,re.I):
  return 'Writable paper for notes, reminders and lists.'
 if len(x)<12:return 'Writable notes for reminders and everyday organization.'
 return x+'.'

def factual_description(r,bullets):
 title=r.get(TITLE,'')
 # Build from the existing product-specific facts, excluding unverified generic promotion.
 candidates=[]
 for b in bullets:
  if not b:continue
  b=re.sub(r'^\[[^]]+\]\s*','',b).strip()
  if re.search(r'\b(?:recycl|certif|best |FREE |High quality|good price|longer and stronger)',b,re.I):continue
  if re.search(r'\d|lined|roll|dispenser|tab|cube|planner|flags',b,re.I):candidates.append(b.rstrip(' .')+'.')
 if candidates:
  fact=re.sub(r'\s*,\s*',', ',candidates[0])
  if re.search(r'easel|meeting|dry erase',title,re.I):use='For written notes, meeting plans and presentations.'
  elif re.search(r'flags|tabs|marker',title,re.I):use='For marking pages and organizing documents.'
  elif re.search(r'holder|dispenser',title,re.I):use='For keeping notes organized at a desk.'
  else:use='For written reminders, lists and everyday note taking.'
  return fact+' '+use
 if re.search(r'roll',title,re.I):return 'Self-stick note paper in a roll format for written notes and reminders.'
 if re.search(r'flags|tabs|marker',title,re.I):return 'Page markers for organizing documents, notebooks and reading notes.'
 if re.search(r'sticky|self-stick',title,re.I):return 'Self-stick note pads for written reminders, lists and everyday note taking.'
 return None

ops=[];holds=[];pairs=[]
issue_map=collections.defaultdict(list)
for i in json.loads((P/'12-text-scan.json').read_text(encoding='utf8'))['issues']:issue_map[i['sku']].append(i)
for sku,r in raw.items():
 issues=issue_map.get(sku,[])
 if not issues:continue
 reason=None
 if sku not in current:reason='exact_sku_missing_latest_report'
 elif str(r.get('parentage_level[marketplace_id=ATVPDKIKX0DER]#1.value','')).lower()=='parent':reason='parent_family_deferred'
 elif current[sku].get('asin1')!=r.get('amzn1.volt.ca.product_id_value'):reason='latest_report_asin_differs_from_source'
 elif sku in identity_hold:reason='existing_identity_or_compliance_conflict:'+','.join(identity_hold[sku])
 elif re.search(r'\b\d{5,}\s*Sheets|\b\d{4,}\s*Pads|\b(?:25|48) Packs',r.get(TITLE,''),re.I):reason='unverified_bulk_pack_quantity'
 elif re.search(r'3\s*x\s*3/4\s*in',r.get(TITLE,''),re.I):reason='ambiguous_mixed_size_title'
 if reason:holds.append({'sku':sku,'asin':r.get('amzn1.volt.ca.product_id_value'),'reason':reason});continue
 changes={};basis={}
 if any('asin_in_highlight' in i['reasons'] for i in issues):
  current_name=current[sku].get('item-name','')
  current_parts=current_name.split(' | ',1)
  already_pair=len(current_parts)==2 and len(current_parts[0])<=75 and len(current_parts[1])<=125 and not re.fullmatch(r'B[A-Z0-9]{9}',current_parts[1].strip())
  equalwords=lambda text:sorted(x for x in re.findall(r'[a-z0-9]+',text.lower()) if x not in ['4a','aaaa','office','product'])
  normalized=lambda text:re.sub(r'[^a-z0-9]','',text.lower())
  current_same=normalized(r.get(TITLE,'')) in normalized(current_name) or equalwords(r.get(TITLE,''))==equalwords(current_parts[0])
  if already_pair:pr,why=None,'already_corrected_title_highlight_in_latest_report'
  elif not current_same:pr,why=None,'latest_report_title_changed_preserve_newer_text'
  elif sku in manual_pairs:
   n,h=manual_pairs[sku];pr,why={'title':n,'highlight':h,'removed_redundancy':['Reviewed manually against source facts']},None
  else:pr,why=pair(r.get(TITLE,''))
  if pr:
   changes[TITLE]=pr['title'];changes[HIGH]=pr['highlight'];basis['title_pair']=pr
   pairs.append({'sku':sku,'asin':r.get('amzn1.volt.ca.product_id_value'),'before':r.get(TITLE,''),**pr})
  else:
   holds.append({'sku':sku,'asin':r.get('amzn1.volt.ca.product_id_value'),'reason':why,'title':r.get(TITLE,'')})
   if why=='latest_report_title_changed_preserve_newer_text':continue
 bullets=[r.get(k,'') for k in BUL]
 suspect_bullets=[i for i in issues if i['field'].startswith('bullet_point')]
 if suspect_bullets and sku not in pending_bullets and r.get('amzn1.volt.ca.product_id_value') not in previous_live_bullet_asins:
  for i,b in enumerate(bullets):
   if b and any(z['field']==BUL[i] for z in suspect_bullets):bullets[i]=clean_bullet(b,i)
  if sku in ['4A 303x12-N','AAAA 4A 3031']:
   bullets[2]='Use different note colors to separate tasks or topics.'
  if len(set(bullets))<len([b for b in bullets if b]):
   holds.append({'sku':sku,'reason':'duplicate_replacement_bullet_requires_review'})
  else:
   for k,b in zip(BUL,bullets):
    if b:changes[k]=b
 if any(i['field'].startswith('product_description') for i in issues):
  desc=factual_description(r,bullets)
  if desc:changes[DESC]=desc
  else:holds.append({'sku':sku,'reason':'description_facts_insufficient'})
 if changes:
  cols={k:chr(65+i) for i,(_,k) in enumerate(scan.raw['headers']) if i<26}
  from openpyxl.utils import get_column_letter
  colmap={k:get_column_letter(i+1) for i,(_,k) in enumerate(scan.raw['headers'])}
  cells={'C':sku,'D':r['product_type#1.value'],'E':'Edit (Partial Update)','L':'ASIN','M':r['amzn1.volt.ca.product_id_value']}
  cells.update({colmap[k]:v for k,v in changes.items()})
  ops.append({'sku':sku,'asin':r['amzn1.volt.ca.product_id_value'],'cells':cells,'before':{k:r.get(k) for k in changes},'changes':changes,'basis':basis})
result={'rows':len(ops),'fields':dict(collections.Counter(k.split('[')[0] for o in ops for k in o['changes'])),'holds':holds,'operations':ops,'official_title_guidance':'https://sellercentral.amazon.com/seller-forums/discussions/t/4ba9a173-d896-4b69-81fb-57e148f98356?mons_sel_locale=en_US','uploaded':False}
(P/'12-text-operations-draft.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
(P/'12-title-pair-review.txt').write_text('\n\n'.join(f"{x['sku']} | {len(x['title'])}/{len(x['highlight'])}\nOLD {x['before']}\nNEW {x['title']}\nHL  {x['highlight']}" for x in pairs),encoding='utf8')
print('BATCH',result['rows'],result['fields'],'HOLDS',collections.Counter(h['reason'] for h in holds))
