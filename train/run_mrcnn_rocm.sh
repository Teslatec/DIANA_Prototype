docker run -it --rm \
    --device=/dev/kfd --device=/dev/dri \
    --group-add video \
    --cap-add=SYS_PTRACE \
    --security-opt seccomp=unconfined \
    --network=host \
    -v /media/anatole/86961DF8961DEA07/Users/Anatoly/Documents/work/teeth/:/images \
    mrcnn-rocm

