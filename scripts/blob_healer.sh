#!/bin/bash
# Boykin's Fiesta blob healer: keeps the 3 redundant JSONBlob stores alive.
# - GETs each blob (also counts as "access" against idle purge)
# - Unions surviving state, backs it up locally
# - Recreates any dead blob with the union; if IDs changed, rewires index.html,
#   commits, pushes, and dispatches a fresh Pages deploy.
# Hang-proof: every network op has a timeout; total runtime capped by launchd cadence.
set -u
REPO="/Users/Jackson/.openclaw/workspace/research/BoykinsFiesta"
HTML="$REPO/index.html"
BACKUP="$REPO/state_backup.json"
LOG="$REPO/healer.log"
BASE="https://jsonblob.com/api/jsonBlob"
cd "$REPO" || exit 1
IDS=$(python3 - "$HTML" <<'EOF'
import re,sys
t=open(sys.argv[1]).read()
m=re.search(r'BLOB_IDS = \[([^\]]*)\]',t)
print(" ".join(re.findall(r'"([0-9a-f-]{36})"',m.group(1))) if m else "")
EOF
)
[ -z "$IDS" ] && { echo "$(date) no ids found" >> "$LOG"; exit 0; }

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
alive=(); dead=()
for id in $IDS; do
  if curl -sf -m 20 "$BASE/$id" -H "Accept: application/json" -o "$TMP/$id.json"; then
    alive+=("$id")
  else
    dead+=("$id")
  fi
done

# union surviving states (earliest 'at' wins)
python3 - "$TMP" "$BACKUP" <<'EOF'
import json,glob,os,sys
tmp,backup=sys.argv[1],sys.argv[2]
m={}
files=glob.glob(os.path.join(tmp,"*.json"))
if os.path.exists(backup): files.append(backup)
for p in files:
    try: d=json.load(open(p)).get("drunk",{})
    except Exception: continue
    for k,e in d.items():
        if not isinstance(e,dict): continue
        if k not in m or e.get("at",0)<m[k].get("at",float("inf")): m[k]=e
json.dump({"drunk":m}, open(os.path.join(tmp,"union.json"),"w"))
json.dump({"drunk":m}, open(backup,"w"))
EOF

if [ ${#dead[@]} -eq 0 ]; then
  # refresh alive blobs with union (keeps them consistent + touched)
  for id in "${alive[@]}"; do
    curl -sf -m 20 -X PUT "$BASE/$id" -H "Content-Type: application/json" --data-binary @"$TMP/union.json" -o /dev/null
  done
  echo "$(date) all ${#alive[@]} blobs alive" >> "$LOG"
  exit 0
fi

echo "$(date) dead blobs: ${dead[*]} — recreating" >> "$LOG"
for id in "${dead[@]}"; do
  loc=$(curl -sf -m 20 -X POST "$BASE" -H "Content-Type: application/json" --data-binary @"$TMP/union.json" -D - -o /dev/null | grep -i "^location:" | tr -d '\r' | awk -F/ '{print $NF}')
  if [ -n "$loc" ]; then
    /usr/bin/sed -i '' "s/$id/$loc/" "$HTML"
    echo "$(date) replaced $id -> $loc" >> "$LOG"
  fi
done
for id in "${alive[@]}"; do
  curl -sf -m 20 -X PUT "$BASE/$id" -H "Content-Type: application/json" --data-binary @"$TMP/union.json" -o /dev/null
done
if ! git diff --quiet -- index.html; then
  git add index.html state_backup.json 2>/dev/null
  git -c user.name="Jackson Davis" -c user.email="jhdavis789@gmail.com" commit -qm "healer: replace dead blob store" && \
  timeout 60 git push -q origin main 2>>"$LOG" && \
  timeout 60 gh workflow run pages.yml --repo jhdavis789/boykins-fiesta 2>>"$LOG"
  echo "$(date) redeployed with new blob ids" >> "$LOG"
fi
