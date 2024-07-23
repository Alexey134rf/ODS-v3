FROM ubuntu:24.04
ENV DEBIAN_FRONTEND="noninteractive" 
ENV TZ="Europe/Moscow"
RUN mkdir -p /root/ods_v3_lxc && mkdir -p /root/ods_v3_lxc/lxc_build_files && mkdir -p /root/ods_v3_lxc/lxc_project
WORKDIR /root/ods_v3_lxc/lxc_build_files
RUN apt update && \
apt-get install wget -y && \
apt-get install build-essential -y && \
wget https://www.python.org/ftp/python/3.10.4/Python-3.10.4.tgz && \
tar -xf Python-3.10.4.tgz && \
rm Python-3.10.4.tgz && \
apt install libssl-dev &&\
apt install zlib1g-dev && \
./Python-3.10.4/configure --enable-optimizations && \
make install ./Python-3.10.4 && \
python3 -m pip install --upgrade pip
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
apt install ./google-chrome-stable_current_amd64.deb -y && \
rm ./google-chrome-stable_current_amd64.deb && \
apt-get install -y poppler-utils
COPY ./requirements_selenium_linux.txt /root/ods_v3_lxc/lxc_project/requirements_selenium_linux.txt
RUN pip3 install -r /root/ods_v3_lxc/lxc_project/requirements_selenium_linux.txt
# CMD /bin/sh -c "python3 /root/ods_v3_lxc/lxc_project/ODS_linux.py"
CMD /bin/sh -c "while sleep 1000; do :; done"