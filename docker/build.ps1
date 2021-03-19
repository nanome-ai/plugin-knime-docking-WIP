param ([switch] $u, [switch] $update)

Set-Variable -name OS -value debian

if ($u -or $update) {
  $contents = Get-Date
  Out-File -FilePath .\.cachebust -InputObject $contents -Encoding ASCII
}

$cachebust = Get-Content -Path .\.cachebust
docker build -f "$((Get-Variable -name OS).value).Dockerfile" --build-arg CACHEBUST=$cachebust -t "nanome-knime-$((Get-Variable -name OS).value):latest" ..