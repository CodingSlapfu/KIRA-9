#!/bin/sh
# Back up an already verified artifact. This job never recompiles or reruns tests.
set -eu
: "${CHECKPOINT_SHA:?source SHA is required}"
: "${RUNNER_TEMP:?isolated runner temporary directory is required}"
(cd build/checkpoint && sha256sum -c SHA256SUMS)
python3 - "$CHECKPOINT_SHA" <<'PY'
import sys,zipfile,json,hashlib
with zipfile.ZipFile('build/checkpoint/KIRA-9-development-checkpoint.zip') as z:
 m=json.loads(z.read('CHECKPOINT.json'))
 if m['source_commit']!=sys.argv[1]:raise SystemExit('Backup source does not match this workflow')
 for name,digest in m['files'].items():
  if hashlib.sha256(z.read(name)).hexdigest()!=digest:raise SystemExit('Invalid archive member: '+name)
 print('Verified',len(m['files']),'member hashes before preservation')
PY
backup_dir="$RUNNER_TEMP/kira9-backup"
if git ls-remote --exit-code origin refs/heads/kira-9-development-backups >/dev/null 2>&1; then
 git fetch origin kira-9-development-backups
 git worktree add --detach "$backup_dir" FETCH_HEAD
 git -C "$backup_dir" switch -c kira9-backup-write
else
 git worktree add --detach "$backup_dir" HEAD
 git -C "$backup_dir" checkout --orphan kira9-backup-write
 git -C "$backup_dir" rm -rf .
fi
mkdir -p "$backup_dir/checkpoints"
destination="$backup_dir/checkpoints/$CHECKPOINT_SHA.zip"
if test -f "$destination"; then
 cmp "$destination" build/checkpoint/KIRA-9-development-checkpoint.zip || {
  echo 'A different archive already exists for this source SHA; refusing to overwrite it.'; exit 1;
 }
else
 cp build/checkpoint/KIRA-9-development-checkpoint.zip "$destination"
fi
sha256sum "$destination" | sed "s|$backup_dir/||" > "$backup_dir/checkpoints/$CHECKPOINT_SHA.sha256"
printf 'Development backups only. No archive here is a release acceptance claim. Each ZIP contains source, dependency source, native artifacts, website, and checksum manifest.\n' > "$backup_dir/README.md"
git -C "$backup_dir" config user.name 'github-actions[bot]'
git -C "$backup_dir" config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git -C "$backup_dir" add .
if ! git -C "$backup_dir" diff --cached --quiet; then
 git -C "$backup_dir" commit -m "backup: verified development checkpoint $CHECKPOINT_SHA"
 git -C "$backup_dir" push origin HEAD:refs/heads/kira-9-development-backups
fi
expected=$(git -C "$backup_dir" rev-parse HEAD)
actual=$(git ls-remote origin refs/heads/kira-9-development-backups | cut -f1)
test "$actual" = "$expected"
echo "Verified remote backup commit $actual"
