$volumeID = docker ps -aqf name=nanome-knime-removehs-poc
if ($volumeID -ne "") { 
Write-Host "Removing previous container"

docker stop -t0 nanome-knime-removehs-poc
docker rm -f nanome-knime-removehs-poc
}

docker run -d \
--name nanome-knime-removehs-poc \
--restart unless-stopped \
-e ARGS="$args" \
nanome-knime-removehs-poc
