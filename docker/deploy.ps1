param($wkflw_dir, $grid_dir, $output_dir, $preferences_dir)

$OS = "debian"
$containerName = "nanome-knime-$OS"
$containerID = $(Invoke-Expression -Command "docker ps -aqf name=nanome-knime-$OS")

if ($null -ne $containerID) {
    Write-Host "Removing previous container"
    docker stop -t0 $containerName
    docker rm -f $containerName
}

$exists = @{}
$mountargs = @('', '', '', '', '', '', '', '')
$mountcount = 0
$unixmounts = @()
foreach ($mount in $PSBoundParameters.GetEnumerator()) {
    Write-Host mount is $mount
    $mountname = $mount.Key
    $localpath = $mount.Value
    $mountargs[2 * $mountcount] = "--mount"
    $unixpath = "/app/mounts/$($localpath.Split("\")[-1])"
    $mountargs[$(2 * $mountcount) + 1] = "source=$($localpath),target=$($unixpath),type=bind"
    $mountcount += 1

    if (-Not $exists.ContainsKey($localpath)) {
        $unixmounts += "--$mountname"
        $unixmounts += $unixpath
        $exists[$localpath] = $true
    }
}

$unixargs = ''
foreach ($arg in $args.GetEnumerator()) {
    Write-Host "<ARG>" $arg "</ARG>"
    $unixargs += "-$($arg.Replace('=', ' ')) "
}

Write-Host unixargs are $unixargs
Write-Host mount args are @mountargs
Write-Host unixmounts are $unixmounts
Write-Host "args are $args"

docker run --init @mountargs -d --memory=10g --name $containerName --restart unless-stopped -e ARGS="$unixmounts $unixargs" $containerName

$redeploy = @"
`$OS = `"debian`"
`$containerName = `"nanome-knime-`$OS`"
`$containerID = `$(Invoke-Expression -Command `"docker ps -aqf name=nanome-knime-`$OS`")

if (`$null -ne `$containerID) {
    Write-Host `"Removing previous container`"
    docker stop -t0 `$containerName
    docker rm -f `$containerName
}

docker run --init $mountargs -d --memory=10g --name `$containerName --restart unless-stopped -e ARGS=`"$unixmounts $unixargs`" `$containerName
"@

Set-Content -Path redeploy.ps1 -Value $redeploy