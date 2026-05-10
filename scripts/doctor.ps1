$ErrorActionPreference = "Stop"

function Test-Command($Name) {
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  if ($null -eq $cmd) {
    if ($Name -eq "docker") {
      $dockerBin = "C:\Program Files\Docker\Docker\resources\bin"
      if (Test-Path (Join-Path $dockerBin "docker.exe")) {
        $env:Path += ";$dockerBin"
        $cmd = Get-Command $Name -ErrorAction SilentlyContinue
      }
    }
  }
  if ($null -eq $cmd) {
    Write-Warning "$Name nao encontrado no PATH"
    return $false
  }
  Write-Host "$Name encontrado: $($cmd.Source)"
  return $true
}

$ok = $true
$ok = (Test-Command "python") -and $ok
$ok = (Test-Command "node") -and $ok
$ok = (Test-Command "npm") -and $ok
$ok = (Test-Command "git") -and $ok
$dockerOk = Test-Command "docker"
if ($dockerOk) {
  docker --version
  docker compose version
  try {
    docker ps | Out-Null
    Write-Host "Docker daemon respondendo."
  } catch {
    Write-Warning "Docker existe no PATH, mas o daemon nao respondeu. Abra o Docker Desktop e tente de novo."
  }
} else {
  Write-Warning "Docker Desktop e necessario para a stack completa, mas os builds locais ainda podem rodar."
  Write-Host 'Dica: se Docker Desktop estiver instalado, tente: $env:Path += ";C:\Program Files\Docker\Docker\resources\bin"'
}

if ($ok) {
  Write-Host "Ambiente Windows parece pronto para validacao local."
} else {
  exit 1
}
