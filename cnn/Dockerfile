FROM ubuntu
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
                 ipython \
                 Keras==2.1.5 \
                 Keras-Applications==1.0.8 \
                 Keras-Preprocessing==1.1.0 \
                 opencv-python \
                 tensorflow==1.14 \
                 scikit-image \
                 imantics

ENV PYTHONPATH /usr/local/src/Mask_RCNN
COPY tooth_weights.h5 /app
COPY brace_weights.h5 /app
COPY tooth.py /app
COPY tooth_service.py /app
COPY tooth_cli.py /app
COPY purity_index.py /app

VOLUME /images
VOLUME /app/config

CMD python3 /app/tooth_service.py \
    --tooth=/app/tooth_weights.h5 \
    --brace=brace_weights.h5 --image=/images/ \
    --purity /app/config/purity.ini
