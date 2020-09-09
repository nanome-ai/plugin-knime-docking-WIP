#!/bin/bash

if [ -n "$(docker ps -aqf name=nanome-knime-removehs-poc)" ]; then
    echo "removing exited container"
    docker rm -f nanome-knime-removehs-poc
fi

docker run -d \
--name nanome-knime-removehs-poc \
--restart unless-stopped \
-e ARGS="$*" \
nanome-knime-removehs-poc
