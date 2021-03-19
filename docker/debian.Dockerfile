FROM nanome/plugin-env

ENV ARGS=''

COPY . /app
WORKDIR /app

ARG CACHEBUST
RUN pip install nanome

# Give environment 'display' for x11 interface
ENV DISPLAY="0.0.0.0"
# add DISPLAY to .bashrc
RUN export DISPLAY=${DISPLAY}
# Remember session using xfce4
RUN echo xfce4-session > ~/.xsession

# Install xterm (& wget & default-jre) for graphical applications (Knime)
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends --fix-missing xterm wget default-jre libswt-glx-gtk-4-jni python3-pip

# download & install Knime Analytics Platform
RUN wget https://download.knime.org/analytics-platform/linux/knime-latest-linux.gtk.x86_64.tar.gz -O knime.tar.gz
WORKDIR /app/knime_install
RUN mv ../knime.tar.gz .
# go in, extract, remove tar, enter extracted dir, move it to 'knime'
RUN tar -xzf ./knime.tar.gz && \
    rm -f ./knime.tar.gz && \
    cd $(ls) && \
    mkdir --parents ../../knime && \
    mv ./* $_
# remove installation directory
RUN rm -rf ./knime_install && cd /app

WORKDIR /app
CMD python run.py ${ARGS}