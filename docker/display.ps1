$OS = "debian"
$containerName = "nanome-knime-$OS"
$containerID = $(Invoke-Expression -Command "docker ps -aqf name=$containerName")
$DISPLAY = "$((Get-NetIPAddress -InterfaceAlias 'vEthernet (WSL)' -AddressFamily IPv4).IPAddress+':0.0')"

Write-Host containerID is $containerID

if ($null -eq $containerID) {
    Write-Host "Please deploy the plugin."
    exit 0
}

$command = "exec", "--env", "DISPLAY=$DISPLAY", "$containerID", "/app/knime/knime"
Write-Host docker $command
docker @command