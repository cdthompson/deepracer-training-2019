CUDAPATH=/usr/local/cuda

# Have this point to an old enough gcc (for nvcc)
GCCPATH=/usr

NVCC=nvcc
CCPATH=${GCCPATH}/bin

drv:
	PATH=${PATH}:.:${CCPATH}:${CUDAPATH}/bin:${PATH} ${NVCC} -I${CUDAPATH}/include -arch=compute_30 -ptx compare.cu -o compare.ptx
	g++ -O3 -Wno-unused-result -I${CUDAPATH}/include -c gpu_burn-drv.cpp
	g++ -o gpu_burn gpu_burn-drv.o -O3 -L${CUDAPATH}/lib64 -L${CUDAPATH}/lib -lcuda -Wl,-rpath=${CUDAPATH}/lib64 -Wl,-rpath=${CUDAPATH}/lib -lcublas -lcudart -o gpu_burn
