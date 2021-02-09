$volumeID = docker ps -aqf nanome-knime-windows
if ($volumeID -ne "") {
    Write-Host "Removing previous container"

    docker stop -t0 nanome-knime-windows
    docker rm -f nanome-knime-windows
}

docker run -d \
--name nanome-knime-windows \
--restart unless-stopped \
-e ARGS="$args" \

