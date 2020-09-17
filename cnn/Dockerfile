FROM ubuntu:18.04
WORKDIR '/app'

RUN apt-get update && apt-get install --no-install-recommends -y \
                        git \
                        python3 \
                        python3-pip \ 
                        python3-setuptools \
                        libglib2.0-0 \
                        libsm6 \
                        libxext6 \
                        libxrender-dev

RUN git clone -b master --depth 1 https://github.com/matterport/Mask_RCNN \
                                    /usr/local/src/Mask_RCNN

RUN pip3 install --no-cache-dir \
                 grpcio==1.25.0 \
                 ipython==7.13.0 \
                 Keras==2.1.5 \
                 Keras-Applications==1.0.8 \
                 Keras-Preprocessing==1.1.0 \
                 opencv-python==4.2.0.34 \
                 opencv-contrib-python==4.2.0.34 \
                 tensorflow==1.14 \
                 scikit-image==0.16.2 \
                 imantics==0.1.12 \
                 numpy==1.18.3 \
                 pika

ENV PYTHONPATH /usr/local/src/Mask_RCNN
COPY tooth_weights.h5 brace_weights.h5 weights_md5.txt /app/
RUN md5sum -c weights_md5.txt

COPY tooth.py tooth_service.py purity_index.py tooth_cli.py /app/

VOLUME /images
VOLUME /app/config

CMD python3 /app/tooth_service.py \
    --tooth=/app/tooth_weights.h5 \
    --brace=brace_weights.h5 --image=/images/ \
    --purity=/app/config/purity.ini \
    --rabbit=$RABBIT_URL
