#!/bin/sh
# Preserve only the NEW experiment; no previous archive or firmware gate is replayed.
set -eu
(cd build/checkpoint && sha256sum -c SHA256SUMS)
python3 - <<'PY'
import zipfile,json,hashlib,os
with zipfile.ZipFile('build/checkpoint/nucleus-evidence.zip') as z:
 m=json.loads(z.read('EXPERIMENT.json'));assert m['source_commit']==os.environ['GITHUB_SHA'];assert not m['firmware_changed']
 for name,digest in m['files'].items():assert hashlib.sha256(z.read(name)).hexdigest()==digest,name
 print('Verified new experiment',len(m['files']),'member hashes')
PY
git fetch origin kira-9-development-backups
destination="$RUNNER_TEMP/kira9-nucleus-backup"
git worktree add --detach "$destination" FETCH_HEAD
mkdir -p "$destination/experiments"
if test -f "$destination/experiments/$GITHUB_SHA.zip"; then
 cmp build/checkpoint/nucleus-evidence.zip "$destination/experiments/$GITHUB_SHA.zip" || { echo 'Refusing to replace different experiment archive for the same SHA'; exit 1; }
else
 cp build/checkpoint/nucleus-evidence.zip "$destination/experiments/$GITHUB_SHA.zip"
fi
printf 'Research evidence only. These archives contain source, paired audio and measured/failed results; no native firmware acceptance or release claim. Prior checkpoints/ firmware backups stay intact.\n' > "$destination/experiments/README.md"
(cd "$destination" && sha256sum "experiments/$GITHUB_SHA.zip" > "experiments/$GITHUB_SHA.sha256")
git -C "$destination" config user.name 'github-actions[bot]'
git -C "$destination" config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git -C "$destination" add experiments
if ! git -C "$destination" diff --cached --quiet; then
 git -C "$destination" commit -m "backup: isolated nucleus/transition experiment $GITHUB_SHA"
 git -C "$destination" push origin HEAD:refs/heads/kira-9-development-backups
fi
expected=$(git -C "$destination" rev-parse HEAD)
actual=$(git ls-remote origin refs/heads/kira-9-development-backups | cut -f1)
test "$actual" = "$expected"
echo "Verified new experiment backup commit $actual"
