#!/usr/bin/env python3
"""Archive only this NEW failed output-weight experiment; previous backups untouched."""
import argparse,pathlib,json,zipfile,hashlib
p=argparse.ArgumentParser();p.add_argument('--source-commit',required=True);a=p.parse_args();root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/output-weight-study'
files={}
for name in ['tools/output_weight_build.py','tools/output_weight_measure.py','tools/output_weight_archive.py','tests/nucleus_transition.c']:
 files['source/'+name]=root/name
for name in ['kira.h','engine-baseline.c','engine-output.c','bridge.c','corpus.json','results.json','guard.txt']:
 files['experiment/'+name]=out/name
for path in out.glob('transitions-*.wav.gz'):files['audio/'+path.name]=path
for path in (root/'validation/output-weight-2026-11-06').glob('*'):
 if path.is_file():files['evidence/'+path.name]=path
manifest={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in files.items()}
archive=out/'output-weight-evidence.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name,path in sorted(files.items()):z.write(path,name)
 z.writestr('EXPERIMENT.json',json.dumps({'source_commit':a.source_commit,'baseline_commit':'d40d55852562e6e572f72f160c669c521fccbe00','firmware_changed':False,'promoted':False,'recognition_run':False,'decision':'Headroom failed; stop recognition and reassess synthesis architecture.','files':manifest},indent=2))
digest=hashlib.sha256(archive.read_bytes()).hexdigest();(out/'SHA256SUMS').write_text(digest+'  output-weight-evidence.zip\n');print(json.dumps({'bytes':archive.stat().st_size,'sha256':digest,'members':len(manifest),'path':str(archive)}))
