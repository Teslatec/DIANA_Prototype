FROM ubuntu
WORKDIR '/app'
RUN apt-get update && apt-get install --no-install-recommends -y \
                        git \
                        python3 \
                        python3-pip \ 
                        python3-setuptools
RUN pip3 install --no-cache-dir \
                 ipython \
                 tensorflow==1.14 \
                 Keras==2.1.5 \
                 Keras-Applications==1.0.8 \
                 Keras-Preprocessing==1.1.0 \
                 scikit-image

RUN git clone -b master --depth 1 https://github.com/matterport/Mask_RCNN \
                                    /usr/local/src/Mask_RCNN
ENV PYTHONPATH /usr/local/src/Mask_RCNN
COPY mask_rcnn_tooth_0030.h5 /app
COPY tooth.py /app
COPY tooth_service.py /app

VOLUME /images

CMD python3 /app/tooth_service.py --weights=/app/mask_rcnn_tooth_0030.h5 \
    --image=/images/
