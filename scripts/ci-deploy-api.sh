#!/usr/bin/env bash
# Called only by the explicit production workflow dispatch after validation.
set -euo pipefail
for name in DEPLOY_HOST DEPLOY_USER DEPLOY_PATH DEPLOY_SSH_KEY DEPLOY_KNOWN_HOSTS GITHUB_SHA; do
  [[ -n "${!name:-}" ]] || { echo "Missing deployment configuration: $name" >&2; exit 1; }
done
[[ "$DEPLOY_HOST" =~ ^[a-zA-Z0-9][a-zA-Z0-9.-]*$ ]] || { echo 'Invalid deployment host' >&2; exit 1; }
[[ "$DEPLOY_USER" =~ ^[a-zA-Z_][a-zA-Z0-9_-]*$ ]] || { echo 'Invalid deployment user' >&2; exit 1; }
[[ "$DEPLOY_PATH" = /* ]] || { echo 'DEPLOY_PATH must be absolute' >&2; exit 1; }
[[ "$GITHUB_SHA" =~ ^[0-9a-f]{40}$ ]] || { echo 'Invalid release commit' >&2; exit 1; }

credentials_dir="$(mktemp -d)"
trap 'rm -rf -- "$credentials_dir"' EXIT
chmod 700 "$credentials_dir"
printf '%s\n' "$DEPLOY_SSH_KEY" > "$credentials_dir/key"
printf '%s\n' "$DEPLOY_KNOWN_HOSTS" > "$credentials_dir/known_hosts"
chmod 600 "$credentials_dir/key" "$credentials_dir/known_hosts"

printf -v remote_command 'bash -s -- %q %q' "$DEPLOY_PATH" "$GITHUB_SHA"
ssh -i "$credentials_dir/key" -o BatchMode=yes -o StrictHostKeyChecking=yes \
  -o "UserKnownHostsFile=$credentials_dir/known_hosts" \
  "$DEPLOY_USER@$DEPLOY_HOST" "$remote_command" <<'REMOTE'
set -euo pipefail
cd -- "$1"
release_sha="$2"
[[ -f .env ]] || { echo 'Configure .env on the deployment host first' >&2; exit 1; }
[[ -z "$(git status --porcelain --untracked-files=no)" ]] || { echo 'Deployment checkout has tracked changes; refusing to overwrite them' >&2; exit 1; }
git fetch origin "$release_sha"
git checkout --detach "$release_sha"
bash scripts/deploy-gcp.sh
REMOTE
