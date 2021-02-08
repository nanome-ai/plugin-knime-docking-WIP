$volumeID = docker ps -aqf nanome-knime-windows
if ($volumeID -ne "") {
    Write-Host "Removing previous container"

    docker stop -t0 nanome-knime-removehs-poc
    docker rm -f nanome-knime-removehs-poc
}

docker run -d \
--name nanome-knime-windows \
--restart unless-stopped \
-e ARGS="$args" \
nanome-knime-windows
