FROM conda/miniconda2:latest
MAINTAINER chester

ENV PYTHONIOENCODING=UTF-8
ENV GIT_LFS_SKIP_SMUDGE=1
ENV FINDDOCK_VERSION=1.0.0
ENV AUTODOCKTOOL_VERSION=1.5.7

# Install ubuntu packages
RUN apt-get update \
 && apt-get upgrade -y \
 && apt-get install -y vim \
 && apt-get install -y git \
 && apt-get install -y wget \
 && apt-get install -y time \
 && apt-get install -y software-properties-common \
 && apt-get install -y cmake \
 && apt-get install -y g++ \
 && apt-get install -y build-essential \
 && apt-get install -y python2.7 \
 && apt-get install -y python-pip \
 && conda install -c conda-forge git-lfs -y \
 && git lfs install \

# Download FindDock from git lfs
# We stored all of the 3'rd party packages in our git repository.
# Due to license issue, please download them for your own. 
 && cd /tmp/ \
 && git clone https://gitlab+deploy-token-4:WjMMZ33rcmz17RHfqszz@gitlab.corp.ailabs.tw/engine/3rd-party.git \
 && cd /tmp/3rd-party/ \
 && git lfs pull --include "openbabel-openbabel-3-0-0.tar.gz" \
 && git lfs pull --include "autodock_vina_1_1_2_linux_x86.tgz" \
 && git lfs pull --include "autodocktools-prepare-"${AUTODOCKTOOL_VERSION}"-py27_0.tar.bz2" \
 && git lfs pull --include "download_sdf.py" \
 && git lfs pull --include "FindDock.py" \
 && cd /tmp/3rd-party/FindDock-"${FINDDOCK_VERSION}"/ \
 && tar -zxvf /tmp/3rd-party/FindDock-"${FINDDOCK_VERSION}"/openbabel-openbabel-3-0-0.tar.gz \
 && tar -zxvf /tmp/3rd-party/FindDock-"${FINDDOCK_VERSION}"/autodock_vina_1_1_2_linux_x86.tgz \

# Setup FinDock
 && cd /opt/ \
 && cp -r /tmp/3rd-party/FindDock-"${FINDDOCK_VERSION}"/autodock_vina_1_1_2_linux_x86 ./ \
 && mkdir build \
 && cd /opt/build/ \
 && cmake /tmp/3rd-party/FindDock-"${FINDDOCK_VERSION}"/openbabel-openbabel-3-0-0/ \
 && make \
 && make install \
 && cp /tmp/3rd-party/FindDock-1.0.0/download_sdf.py /opt/ \
 && python -m pip install requests \
 && python -m pip install ipywidgets \
 && python -m pip install nglview \
 && python -m pip install requests \
 && cp /tmp/3rd-party/FindDock-1.0.0/FindDock.py /opt/ \
 && python -m pip install numpy \
 && conda install /tmp/3rd-party/autodocktools-prepare-"${AUTODOCKTOOL_VERSION}"/autodocktools-prepare-"${AUTODOCKTOOL_VERSION}"-py27_0.tar.bz2 \

# Clean up
 && rm -rf /tmp/*