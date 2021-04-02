$OS = "debian"
$containerName = "nanome-knime-$OS"
$containerID = $(Invoke-Expression -Command "docker ps -aqf name=nanome-knime-$OS")

if ($null -ne $containerID) {
    Write-Host "Removing previous container"
    docker stop -t0 $containerName
    docker rm -f $containerName
}

docker run --init --mount source=C:\Users\Admin\Desktop\Nanome\plugin-knime-docking\knime-workspace\knime-workflow,target=/app/mounts/knime-workflow,type=bind --mount source=C:\Users\Admin\Desktop\Nanome\plugin-knime-docking\knime-workspace\docking_grids,target=/app/mounts/docking_grids,type=bind --mount source=C:\Users\Admin\Desktop\Nanome\plugin-knime-docking\knime-workspace\data\sdf_test,target=/app/mounts/sdf_test,type=bind --mount source=C:\Users\Admin\Desktop\Nanome\plugin-knime-docking\knime-workspace,target=/app/mounts/knime-workspace,type=bind -d --memory=10g --name $containerName --restart unless-stopped -e ARGS="--wkflw_dir /app/mounts/knime-workflow --grid_dir /app/mounts/docking_grids --output_dir /app/mounts/sdf_test --preferences_dir /app/mounts/knime-workspace --address plugins.nanome.ai --port 9999 --restart --verbose " $containerName
