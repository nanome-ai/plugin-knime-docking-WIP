#!/bin/bash

if [ -n "$(docker ps -aqf name=nanome-knime-removehs-poc)" ]; then
    echo "removing exited container"
    docker rm -t0 -f nanome-knime-removehs-poc
fi

docker_args=(
"wkflw_dir"
"grid_dir"
"knime_dir"
"output_dir"
"preferences_dir"
)
mounts=()
arg_index=-1
ARGS=$*

lookup_arg() {
    arg_index=-1
    for i in "${!docker_args[@]}"; do
        echo "checking" ${docker_args[i]}
        if [ "$arg" == "--${docker_args[$i]}" ]; then
            arg_index=$i
            echo "found" $arg "!"
        fi
    done
}

while [ $# -gt 0 ]
do
    arg=$1
    lookup_arg
    if [ $arg_index -ge 0 ]; then
        shift
        value=$1
        mounts[$arg_index]="--mount type=bind,source=$value,target=$value "
    fi
    shift
done

echo ${mounts[@]}
echo "${ARGS[*]}"

docker run -d \
${mounts[@]} \
--name nanome-knime-removehs-poc \
--restart unless-stopped \
-e ARGS="${ARGS[@]}" \
nanome-knime-removehs-poc
