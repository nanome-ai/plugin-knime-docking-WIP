param($wkflw_dir, $grid_dir, $knime_path, $output_dir)

Set-Variable -name OS -value debian
Set-Variable -name volumeID -value "docker ps -aqf name=nanome-knime-$((Get-Variable -name OS).value)"

if ($(Invoke-Expression -Command $((Get-Variable -name volumeID).value)) -ne $null) {
    Write-Host "Removing previous container"
    docker stop -t0 "nanome-knime-$((Get-Variable -name OS).value)"
    docker rm -f "nanome-knime-$((Get-Variable -name OS).value)"
}

$mountargs = '', '', '', '', '', '', '', ''
$mountcount = 0
$mounts = $wkflw_dir, $grid_dir, $knime_path, $output_dir
foreach ($mount in $mounts.GetEnumerator()) {
    Write-Host mount is $mount
    $mountargs[$mountcount] = "--mount"
    $unixpath = "/app/mounts/$($mount.Split("\")[-1])"
    $mountargs[$mountcount+1] = "source=$($mount),target=$($unixpath),type=bind"
    $mountcount += 2
}

Write-Host @mountargs

docker run @mountargs -d --memory=10g --name "nanome-knime-$((Get-Variable -name OS).value)" --restart unless-stopped -e ARGS="$args" "nanome-knime-$((Get-Variable -name OS).value)"
