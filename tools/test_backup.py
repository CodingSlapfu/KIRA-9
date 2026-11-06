#!/usr/bin/env python3
"""Exercise preservation and idempotent retry against an isolated local Git remote."""
import hashlib,json,os,pathlib,subprocess,tempfile,zipfile
script=pathlib.Path(__file__).with_name('preserve_backup.sh').resolve()
def run(args,cwd,**kw):return subprocess.run(args,cwd=cwd,check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,**kw)
with tempfile.TemporaryDirectory(prefix='k9-backup-test-') as tmp:
 t=pathlib.Path(tmp);remote=t/'remote.git';repo=t/'source';repo.mkdir()
 run(['git','init','--bare',str(remote)],t);run(['git','init'],repo)
 for k,v in [('user.name','Backup fixture'),('user.email','fixture@example.invalid')]:run(['git','config',k,v],repo)
 (repo/'source.txt').write_text('preserve me\n');run(['git','add','.'],repo);run(['git','commit','-m','fixture'],repo)
 sha=run(['git','rev-parse','HEAD'],repo).stdout.decode().strip();run(['git','remote','add','origin',str(remote)],repo)
 out=repo/'build/checkpoint';out.mkdir(parents=True);archive=out/'KIRA-9-development-checkpoint.zip';payload=b'original source\n'
 with zipfile.ZipFile(archive,'w') as z:
  z.writestr('source/source.txt',payload);z.writestr('CHECKPOINT.json',json.dumps({'source_commit':sha,'files':{'source/source.txt':hashlib.sha256(payload).hexdigest()}}))
 (out/'SHA256SUMS').write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name+'\n')
 def preserve(label,ok=True):
  runner=t/label;runner.mkdir();env={**os.environ,'CHECKPOINT_SHA':sha,'RUNNER_TEMP':str(runner)}
  p=subprocess.run([str(script)],cwd=repo,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  assert (p.returncode==0)==ok,p.stdout.decode()
 preserve('first');before=run(['git','ls-remote','origin','refs/heads/kira-9-development-backups'],repo).stdout
 preserve('retry');assert before==run(['git','ls-remote','origin','refs/heads/kira-9-development-backups'],repo).stdout
 archive.write_bytes(b'corrupt');preserve('corrupt',False)
 assert before==run(['git','ls-remote','origin','refs/heads/kira-9-development-backups'],repo).stdout
 print('PASS isolated backup publish, identical retry without new commit, corrupt archive rejection and remote preservation')
