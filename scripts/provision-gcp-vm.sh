#!/usr/bin/env bash
# Create the API VM, a static IP, and firewall rules for ports 80 and 443.
# Run from a machine where `gcloud auth login` is already done.
#
#   export GCP_PROJECT=your-project-id
#   bash scripts/provision-gcp-vm.sh
#
# Optional: GCP_ZONE (default asia-south1-a), GCP_MACHINE (default e2-medium),
#           GCP_INSTANCE (default aidesign-api)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

die() { echo "ERROR: $*" >&2; exit 1; }
info() { echo "==> $*"; }

command -v gcloud >/dev/null 2>&1 || die "Install the Google Cloud SDK, then run: gcloud auth login"

PROJECT="${GCP_PROJECT:-$(gcloud config get-value project 2>/dev/null || true)}"
[[ -n "$PROJECT" && "$PROJECT" != "(unset)" ]] || die "Set GCP_PROJECT or run: gcloud config set project YOUR_PROJECT_ID"

ZONE="${GCP_ZONE:-asia-south1-a}"
REGION="${ZONE%-*}"
NAME="${GCP_INSTANCE:-aidesign-api}"
MACHINE="${GCP_MACHINE:-e2-medium}"
ADDRESS="${NAME}-ip"
TAG="aidesign-api"
NETWORK="${GCP_NETWORK:-default}"

info "Project ${PROJECT}, zone ${ZONE}, machine ${MACHINE}"
gcloud config set project "$PROJECT" >/dev/null

ensure_firewall() {
  local rule="$1"
  local port="$2"
  if gcloud compute firewall-rules describe "$rule" --project "$PROJECT" >/dev/null 2>&1; then
    info "Firewall rule ${rule} already exists"
  else
    info "Creating firewall rule ${rule} (tcp:${port})"
    gcloud compute firewall-rules create "$rule" \
      --project "$PROJECT" \
      --network "$NETWORK" \
      --direction INGRESS \
      --action ALLOW \
      --rules "tcp:${port}" \
      --target-tags "$TAG"
  fi
}

ensure_firewall aidesign-allow-http 80
ensure_firewall aidesign-allow-https 443

if gcloud compute addresses describe "$ADDRESS" --region "$REGION" --project "$PROJECT" >/dev/null 2>&1; then
  info "Static IP ${ADDRESS} already reserved"
else
  info "Reserving static IP ${ADDRESS} in ${REGION}"
  gcloud compute addresses create "$ADDRESS" \
    --project "$PROJECT" \
    --region "$REGION" \
    --network-tier PREMIUM
fi

IP="$(gcloud compute addresses describe "$ADDRESS" --region "$REGION" --project "$PROJECT" --format='value(address)')"

if gcloud compute instances describe "$NAME" --zone "$ZONE" --project "$PROJECT" >/dev/null 2>&1; then
  info "VM ${NAME} already exists"
else
  info "Creating VM ${NAME}"
  gcloud compute instances create "$NAME" \
    --project "$PROJECT" \
    --zone "$ZONE" \
    --machine-type "$MACHINE" \
    --image-family ubuntu-2404-lts-amd64 \
    --image-project ubuntu-os-cloud \
    --boot-disk-size 30GB \
    --boot-disk-type pd-balanced \
    --tags "$TAG" \
    --address "$IP" \
    --metadata-from-file "startup-script=${ROOT}/scripts/gcp-vm-startup.sh"
fi

cat <<EOF

VM is up.
  Name:    ${NAME}
  Zone:    ${ZONE}
  Address: ${IP}

1. DNS: A record for the API host (for example api.yourdomain.com) -> ${IP}
2. SSH in after a minute so Docker can finish installing:
     gcloud compute ssh ${NAME} --zone ${ZONE} --project ${PROJECT}
3. On the VM, clone this repo, create .env from .env.example, then:
     bash scripts/deploy-gcp.sh
4. In Netlify, set:
     NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api
     NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com/ws
   and redeploy the site.

EOF
