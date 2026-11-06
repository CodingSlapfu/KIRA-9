#!/usr/bin/env python3
"""KIRA-9 scope traceability gate; release mode intentionally rejects the unbuilt starter."""
import argparse,json,pathlib,sys
STATES={"new","partial","blocked","software_completed"}
def check(manifest,ids,phase):
    errors=[]; rows=manifest.get("requirements",[])
    required=[v.strip() for v in ids.splitlines() if v.strip() and not v.startswith("#")]
    actual=[v.get("id","") for v in rows]
    if len(actual)!=len(set(actual)): errors.append("duplicate requirement IDs")
    if len(required)!=len(set(required)): errors.append("duplicate frozen required IDs")
    for rid in required:
        if rid not in actual: errors.append("missing required task "+rid)
    for r in rows:
        rid=r.get("id","")
        if rid not in required: errors.append("unregistered task "+rid)
        if r.get("status") not in STATES: errors.append(rid+": invalid/missing status")
        if r.get("priority") not in {"P0","P1","P2"}: errors.append(rid+": missing priority")
        if not r.get("title") or not r.get("source_refs"): errors.append(rid+": missing owner scope provenance")
        if r.get("status")=="software_completed":
            for k in ("source_commit","implementation_files","test_refs","artifact_refs"):
                if not r.get(k): errors.append(rid+": unsupported completion ("+k+")")
        if r.get("deferred_to") and not r.get("deferral_approval"):
            errors.append(rid+": deferral without explicit owner approval")
        if phase=="release" and r.get("priority")=="P0" and r.get("status")!="software_completed":
            errors.append(rid+": P0 task not completed")
        if phase=="release" and r.get("status")=="blocked": errors.append(rid+": unresolved blocker")
    if phase=="release":
        review=manifest.get("review",{})
        for k in ("source_comments_reviewed","issue_snapshot_date","review_evidence"):
            if not review.get(k): errors.append("missing current owner-comments audit: "+k)
        if review.get("unmapped_owner_requests"): errors.append("unmapped owner requests")
    return errors

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--phase",choices=["plan","release"],default="plan")
    ap.add_argument("--manifest",default="requirements/manifest.json")
    ap.add_argument("--ids",default="requirements/required_ids.txt")
    args=ap.parse_args()
    problems=check(json.loads(pathlib.Path(args.manifest).read_text()),pathlib.Path(args.ids).read_text(),args.phase)
    for p in problems: print("FAIL:",p)
    if problems:
        print(f"REJECTED: {len(problems)} errors");return 1
    print("PASS: requirement register and "+args.phase+" gate")
    return 0
if __name__=="__main__": sys.exit(main())
