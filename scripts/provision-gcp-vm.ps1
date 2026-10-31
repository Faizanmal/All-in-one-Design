# Create the API VM from Windows. Requires the Google Cloud SDK and `gcloud auth login`.
#   $env:GCP_PROJECT = "your-project-id"
#   .\scripts\provision-gcp-vm.ps1

$ErrorActionPreference = "Stop"
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

function Die($Message) {
    Write-Error $Message
    exit 1
}

if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Die "Install the Google Cloud SDK, then run: gcloud auth login"
}

$Project = $env:GCP_PROJECT
if (-not $Project) {
    $Project = (gcloud config get-value project 2>$null)
}
if (-not $Project -or $Project -eq "(unset)") {
    Die "Set `$env:GCP_PROJECT or run: gcloud config set project YOUR_PROJECT_ID"
}

$Zone = if ($env:GCP_ZONE) { $env:GCP_ZONE } else { "asia-south1-a" }
$Region = $Zone.Substring(0, $Zone.LastIndexOf("-"))
$Name = if ($env:GCP_INSTANCE) { $env:GCP_INSTANCE } else { "aidesign-api" }
$Machine = if ($env:GCP_MACHINE) { $env:GCP_MACHINE } else { "e2-medium" }
$Address = "$Name-ip"
$Tag = "aidesign-api"
$Network = if ($env:GCP_NETWORK) { $env:GCP_NETWORK } else { "default" }
$Startup = Join-Path $Root "scripts\gcp-vm-startup.sh"

Write-Host "==> Project $Project, zone $Zone, machine $Machine"
gcloud config set project $Project | Out-Null

function Ensure-Firewall($Rule, $Port) {
    gcloud compute firewall-rules describe $Rule --project $Project 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "==> Firewall rule $Rule already exists"
    } else {
        Write-Host "==> Creating firewall rule $Rule (tcp:$Port)"
        gcloud compute firewall-rules create $Rule `
            --project $Project `
            --network $Network `
            --direction INGRESS `
            --action ALLOW `
            --rules "tcp:$Port" `
            --target-tags $Tag
        if ($LASTEXITCODE -ne 0) { Die "Could not create firewall rule $Rule" }
    }
}

Ensure-Firewall "aidesign-allow-http" "80"
Ensure-Firewall "aidesign-allow-https" "443"

gcloud compute addresses describe $Address --region $Region --project $Project 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "==> Static IP $Address already reserved"
} else {
    Write-Host "==> Reserving static IP $Address in $Region"
    gcloud compute addresses create $Address --project $Project --region $Region --network-tier PREMIUM
    if ($LASTEXITCODE -ne 0) { Die "Could not reserve the static IP" }
}

$IP = (gcloud compute addresses describe $Address --region $Region --project $Project --format "value(address)").Trim()
if (-not $IP) { Die "Could not read the static IP" }

gcloud compute instances describe $Name --zone $Zone --project $Project 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "==> VM $Name already exists"
} else {
    Write-Host "==> Creating VM $Name"
    gcloud compute instances create $Name `
        --project $Project `
        --zone $Zone `
        --machine-type $Machine `
        --image-family ubuntu-2404-lts-amd64 `
        --image-project ubuntu-os-cloud `
        --boot-disk-size 30GB `
        --boot-disk-type pd-balanced `
        --tags $Tag `
        --address $IP `
        --metadata-from-file "startup-script=$Startup"
    if ($LASTEXITCODE -ne 0) { Die "Could not create the VM" }
}

Write-Host ""
Write-Host "VM is up."
Write-Host "  Name:    $Name"
Write-Host "  Zone:    $Zone"
Write-Host "  Address: $IP"
Write-Host ""
Write-Host "1. DNS: A record for the API host (for example api.yourdomain.com) -> $IP"
Write-Host "2. SSH in after a minute so Docker can finish installing:"
Write-Host "     gcloud compute ssh $Name --zone $Zone --project $Project"
Write-Host "3. On the VM, clone this repo, create .env from .env.example, then:"
Write-Host "     bash scripts/deploy-gcp.sh"
Write-Host "4. In Netlify, set NEXT_PUBLIC_API_URL and NEXT_PUBLIC_WS_URL to this host and redeploy."
