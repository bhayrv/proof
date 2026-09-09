<#
.SYNOPSIS
End-to-End CLI Demonstration of the PROOF Protocol.

.DESCRIPTION
This script demonstrates the complete CLI lifecycle of a PROOF record.
It creates a claim, inspects it, computes its identity, generates a key,
signs the record, verifies it, tampers with it, and observes the
verification failure.
#>

Write-Host "=================================================="
Write-Host "PROOF PROTOCOL: END-TO-END CLI LIFECYCLE"
Write-Host "=================================================="

# Create a temporary directory for the demo
$DemoDir = Join-Path $env:TEMP "proof_demo"
if (Test-Path $DemoDir) { Remove-Item -Recurse -Force $DemoDir }
New-Item -ItemType Directory -Path $DemoDir | Out-Null
Set-Location $DemoDir

Write-Host "`n[1] Creating a Claim..." -ForegroundColor Cyan
python -m proof.cli create --subject "Acme" --predicate "raised" --object "USD 40M" --evidence-type web --evidence-source "https://example.invalid/funding" > record.json
Write-Host "Saved to record.json"

Write-Host "`n[2] Inspecting the Record..." -ForegroundColor Cyan
Get-Content record.json | python -m proof.cli inspect

Write-Host "`n[3] Computing Immutable Identity (SHA-256)..." -ForegroundColor Cyan
$IdentityData = Get-Content record.json | python -m proof.cli identity | ConvertFrom-Json
$Identity = $IdentityData.id
Write-Host "Computed Identity: $Identity"

Write-Host "`n[4] Generating Ed25519 Keypair..." -ForegroundColor Cyan
python -m proof.cli keygen > private.key
Write-Host "Saved to private.key (Keep this safe!)"

Write-Host "`n[5] Signing the Record..." -ForegroundColor Cyan
$KeyJson = Get-Content private.key | ConvertFrom-Json
Get-Content record.json | python -m proof.cli sign --private-key $KeyJson.private_key > signed_record.json
Write-Host "Saved to signed_record.json"

Write-Host "`n[6] Verifying the Signed Record (SUCCESS EXPECTED)..." -ForegroundColor Cyan
Get-Content signed_record.json | python -m proof.cli verify
if ($LASTEXITCODE -eq 0) {
    Write-Host "Verification PASSED as expected." -ForegroundColor Green
} else {
    Write-Host "Verification FAILED unexpectedly." -ForegroundColor Red
}

Write-Host "`n[7] Tampering with the Record..." -ForegroundColor Cyan
# Read the signed record, modify the object value, and write it back
$JsonData = Get-Content signed_record.json | ConvertFrom-Json
$JsonData.claim.object = "USD 400M" # Tampered!
$JsonData | ConvertTo-Json -Depth 10 | Set-Content tampered_record.json
Write-Host "Tampered claim object from 'USD 40M' to 'USD 400M'. Saved to tampered_record.json"

Write-Host "`n[8] Verifying the Tampered Record (FAILURE EXPECTED)..." -ForegroundColor Cyan
$VerifyOut = Get-Content tampered_record.json | python -m proof.cli verify
if ($LASTEXITCODE -ne 0) {
    Write-Host "Verification FAILED as expected. The signature protects the immutable content." -ForegroundColor Green
    Write-Host $VerifyOut
} else {
    Write-Host "Verification PASSED unexpectedly. Tampering was not caught!" -ForegroundColor Red
}

Write-Host "`n=================================================="
Write-Host "DEMONSTRATION COMPLETE"
Write-Host "=================================================="
Set-Location -Path $PSScriptRoot
Remove-Item -Recurse -Force $DemoDir
