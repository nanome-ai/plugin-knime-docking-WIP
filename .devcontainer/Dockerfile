# Note: You can use any Debian/Ubuntu based image you want.
FROM nanome/plugin-env
# [Option] Install zsh
ARG INSTALL_ZSH="true"
# [Option] Upgrade OS packages to their latest versions
ARG UPGRADE_PACKAGES="false"
# [Option] Enable non-root Docker access in container
ARG ENABLE_NONROOT_DOCKER="true"
# [Option] Use the OSS Moby CLI instead of the licensed Docker CLI
ARG USE_MOBY="true"

# Install needed packages and setup non-root user. Use a separate RUN statement to add your
# own dependencies. A user of "automatic" attempts to reuse an user ID if one already exists.
ARG USERNAME=automatic
ARG USER_UID=1000
ARG USER_GID=$USER_UID
COPY library-scripts/*.sh /tmp/library-scripts/
RUN apt-get update \
    && /bin/bash /tmp/library-scripts/common-debian.sh "${INSTALL_ZSH}" "${USERNAME}" "${USER_UID}" "${USER_GID}" "${UPGRADE_PACKAGES}" \
    # Use Docker script from script library to set things up
    && /bin/bash /tmp/library-scripts/docker-debian.sh "${ENABLE_NONROOT_DOCKER}" "/var/run/docker-host.sock" "/var/run/docker.sock" "${USERNAME}" "${USE_MOBY}" \
    # Clean up
    && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/* /tmp/library-scripts/

# Setting the ENTRYPOINT to docker-init.sh will configure non-root access to
# the Docker socket if "overrideCommand": false is set in devcontainer.json.
# The script will also execute CMD if you need to alter startup behaviors.

WORKDIR /workspaces/plugin-knime-docking
# Give environment 'display' for x11 interface
ENV DISPLAY="0.0.0.0"
# add DISPLAY to .bashrc
RUN export DISPLAY=${DISPLAY}
# Remember session using xfce4
RUN echo xfce4-session > ~/.xsession

# Install xterm (& wget & default-jre) for graphical applications (Knime)
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends --fix-missing xterm wget default-jre libswt-glx-gtk-4-jni python3-pip

# Install nanome-lib
RUN pip3 install setuptools
RUN pip3 install -e git+https://github.com/nanome-ai/nanome-lib.git#egg=nanome

# download & install Knime Analytics Platform
RUN wget https://download.knime.org/analytics-platform/linux/knime-latest-linux.gtk.x86_64.tar.gz -O knime.tar.gz
WORKDIR /workspaces/plugin-knime-docking/knime_install
RUN mv ../knime.tar.gz .
# go in, extract, remove tar, enter extracted dir, move it to 'knime'
RUN tar -xzf ./knime.tar.gz && \
    rm -f ./knime.tar.gz && \
    cd $(ls) && \
    mkdir --parents ../../knime && \
    mv ./* ../../knime
# remove installation directory
WORKDIR /workspaces/plugin-knime-docking/
RUN rm -rf ./knime_install

ENTRYPOINT [ "/usr/local/share/docker-init.sh" ]
CMD [ "sleep", "infinity" ]