/*
 * Copyright (c) 2021-2024, NVIDIA CORPORATION & AFFILIATES
 * SPDX-License-Identifier: BSD-3-Clause
 */

#include <cudensitymat.h> // cuDensityMat library header

#include <mpi.h> // MPI library header

#include <stdlib.h>
#include <stdio.h>

/** Converts CUDA data type to the corresponding MPI data type */
static MPI_Datatype convertCudaToMpiDataType(const cudaDataType_t cudaDataType)
{
    MPI_Datatype mpiDataType;
    switch (cudaDataType)
    {
    case CUDA_R_8I:  mpiDataType = MPI_INT8_T; break;
    case CUDA_R_16I: mpiDataType = MPI_INT16_T; break;
    case CUDA_R_32I: mpiDataType = MPI_INT32_T; break;
    case CUDA_R_64I: mpiDataType = MPI_INT64_T; break;
    case CUDA_R_32F: mpiDataType = MPI_FLOAT; break;
    case CUDA_R_64F: mpiDataType = MPI_DOUBLE; break;
    case CUDA_C_32F: mpiDataType = MPI_C_FLOAT_COMPLEX; break;
    case CUDA_C_64F: mpiDataType = MPI_C_DOUBLE_COMPLEX; break;
    default:
        printf("#FATAL(cudensitymat:mpi-interface): Unknown CUDA data type: %d\n", (int)(cudaDataType));
        exit(EXIT_FAILURE);
    }
    return mpiDataType;
}

/** Unpacks the MPI_Comm object */
static MPI_Comm unpackMpiCommunicator(const cudensitymatDistributedCommunicator_t * comm)
{
    if (comm->commPtr == NULL) return MPI_COMM_NULL;
    if (sizeof(MPI_Comm) != comm->commSize)
    {
        printf("#FATAL(cudensitymat:mpi-interface): MPI_Comm object has unexpected size!\n");
        exit(EXIT_FAILURE);
    }
    return *((MPI_Comm *)(comm->commPtr));
}

#ifdef __cplusplus
extern "C" {
#endif

/** MPI_Comm_size wrapper */
int cudensitymatMpiCommSize(const cudensitymatDistributedCommunicator_t * comm,
                         int32_t * numRanks)
{
    int nranks = 0;
    int mpiErr = MPI_Comm_size(unpackMpiCommunicator(comm), &nranks);
    *numRanks = nranks;
    return mpiErr;
}

/** Returns the size of the local subgroup of processes sharing node memory */
int cudensitymatMpiCommSizeShared(const cudensitymatDistributedCommunicator_t * comm,
                               int32_t * numRanks)
{
    *numRanks = 0;
    MPI_Info info;
    MPI_Info_create(&info);
    MPI_Info_set(info, "mpi_hw_resource_type", "mpi_shared_memory");
    int procRank = -1;
    int mpiErr = MPI_Comm_rank(unpackMpiCommunicator(comm), &procRank);
    if (mpiErr == MPI_SUCCESS)
    {
        MPI_Comm localComm;
        mpiErr = MPI_Comm_split_type(unpackMpiCommunicator(comm), MPI_COMM_TYPE_SHARED,
                                     procRank, info, &localComm);
        if (mpiErr == MPI_SUCCESS)
        {
            int nranks = 0;
            mpiErr = MPI_Comm_size(localComm, &nranks);
            *numRanks = nranks;
            MPI_Comm_free(&localComm);
        }
    }
    return mpiErr;
}

/** MPI_Comm_rank wrapper */
int cudensitymatMpiCommRank(const cudensitymatDistributedCommunicator_t * comm,
                         int32_t *procRank)
{
    int prank = -1;
    int mpiErr = MPI_Comm_rank(unpackMpiCommunicator(comm), &prank);
    *procRank = prank;
    return mpiErr;
}

/** MPI_Barrier wrapper */
int cudensitymatMpiBarrier(const cudensitymatDistributedCommunicator_t * comm)
{
    return MPI_Barrier(unpackMpiCommunicator(comm));
}

/** Allocates an MPI_Request */
int cudensitymatMpiCreateRequest(cudensitymatDistributedRequest_t * request)
{
    *request = malloc(sizeof(MPI_Request));
    if (*request == NULL) return -1;
    return 0;
}

/** Frees a previously allocated MPI_Request */
int cudensitymatMpiDestroyRequest(cudensitymatDistributedRequest_t request)
{
    if (request == NULL) return -1;
    free(request);
    return 0;
}

/** MPI_Wait wrapper (waits for completion of MPI_Request) */
int cudensitymatMpiWaitRequest(cudensitymatDistributedRequest_t request)
{
    MPI_Status waitStatus;
    return MPI_Wait((MPI_Request*)request,
                    &waitStatus);
}

/** MPI_Test wrapper (tests for completion of MPI_Request) */
int cudensitymatMpiTestRequest(cudensitymatDistributedRequest_t request,
                               int32_t * completed)
{
    MPI_Status testStatus;
    return MPI_Test((MPI_Request*)request,
                    completed,
                    &testStatus);
}

/** MPI_Send wrapper */
int cudensitymatMpiSend(const cudensitymatDistributedCommunicator_t * comm,
                     const void * buffer,
                     int32_t count,
                     cudaDataType_t datatype,
                     int32_t destination,
                     int32_t tag)
{
    return MPI_Send(buffer,
                    (int)count,
                    convertCudaToMpiDataType(datatype),
                    (int)destination,
                    (int)tag,
                    unpackMpiCommunicator(comm));
}

/** MPI_Isend wrapper */
int cudensitymatMpiSendAsync(const cudensitymatDistributedCommunicator_t * comm,
                          const void * buffer,
                          int32_t count,
                          cudaDataType_t datatype,
                          int32_t destination,
                          int32_t tag,
                          cudensitymatDistributedRequest_t request)
{
    return MPI_Isend(buffer,
                     (int)count,
                     convertCudaToMpiDataType(datatype),
                     (int)destination,
                     (int)tag,
                     unpackMpiCommunicator(comm),
                     (MPI_Request*)request);
}

/** MPI_Recv wrapper */
int cudensitymatMpiRecv(const cudensitymatDistributedCommunicator_t * comm,
                     void * buffer,
                     int32_t count,
                     cudaDataType_t datatype,
                     int32_t source,
                     int32_t tag)
{
    MPI_Status recvStatus;
    return MPI_Recv(buffer,
                    (int)count,
                    convertCudaToMpiDataType(datatype),
                    (int)source,
                    (int)tag,
                    unpackMpiCommunicator(comm),
                    &recvStatus);
}

/** MPI_Irecv wrapper */
int cudensitymatMpiRecvAsync(const cudensitymatDistributedCommunicator_t * comm,
                          void * buffer,
                          int32_t count,
                          cudaDataType_t datatype,
                          int32_t source,
                          int32_t tag,
                          cudensitymatDistributedRequest_t request)
{
    return MPI_Irecv(buffer,
                     (int)count,
                     convertCudaToMpiDataType(datatype),
                     (int)source,
                     (int)tag,
                     unpackMpiCommunicator(comm),
                     (MPI_Request*)request);
}

/** MPI_Bcast wrapper */
int cudensitymatMpiBcast(const cudensitymatDistributedCommunicator_t * comm,
                      void * buffer,
                      int32_t count,
                      cudaDataType_t datatype,
                      int32_t root)
{
    return MPI_Bcast(buffer,
                     (int)count,
                     convertCudaToMpiDataType(datatype),
                     (int)root,
                     unpackMpiCommunicator(comm));
}

/** MPI_Allreduce wrapper */
int cudensitymatMpiAllreduce(const cudensitymatDistributedCommunicator_t * comm,
                          const void * bufferIn,
                          void * bufferOut,
                          int32_t count,
                          cudaDataType_t datatype)
{
    return MPI_Allreduce(bufferIn,
                         bufferOut,
                         (int)count,
                         convertCudaToMpiDataType(datatype),
                         MPI_SUM,
                         unpackMpiCommunicator(comm));
}

/** MPI_Allreduce IN_PLACE wrapper */
int cudensitymatMpiAllreduceInPlace(const cudensitymatDistributedCommunicator_t * comm,
                                 void * buffer,
                                 int32_t count,
                                 cudaDataType_t datatype)
{
    return MPI_Allreduce(MPI_IN_PLACE,
                         buffer,
                         (int)count,
                         convertCudaToMpiDataType(datatype),
                         MPI_SUM,
                         unpackMpiCommunicator(comm));
}

/** MPI_Allreduce IN_PLACE MIN wrapper */
int cudensitymatMpiAllreduceInPlaceMin(const cudensitymatDistributedCommunicator_t * comm,
                                    void * buffer,
                                    int32_t count,
                                    cudaDataType_t datatype)
{
    return MPI_Allreduce(MPI_IN_PLACE,
                         buffer,
                         (int)count,
                         convertCudaToMpiDataType(datatype),
                         MPI_MIN,
                         unpackMpiCommunicator(comm));
}

/** MPI_Allreduce DOUBLE_INT MINLOC wrapper */
int cudensitymatMpiAllreduceDoubleIntMinloc(const cudensitymatDistributedCommunicator_t * comm,
                                         const void * bufferIn, // *struct {double; int;}
                                         void * bufferOut)      // *struct {double; int;}
{
    return MPI_Allreduce(bufferIn,
                         bufferOut,
                         1,
                         MPI_DOUBLE_INT,
                         MPI_MINLOC,
                         unpackMpiCommunicator(comm));
}

/** MPI_Allgather wrapper */
int cudensitymatMpiAllgather(const cudensitymatDistributedCommunicator_t * comm,
                          const void * bufferIn,
                          void * bufferOut,
                          int32_t count,
                          cudaDataType_t datatype)
{
    return MPI_Allgather(bufferIn,
                         (int)count,
                         convertCudaToMpiDataType(datatype),
                         bufferOut,
                         (int)count,
                         convertCudaToMpiDataType(datatype),
                         unpackMpiCommunicator(comm));
}

/**
 * Distributed communication service API wrapper binding table (imported by cuDensityMat).
 * The exposed C symbol must be named as "cudensitymatCommInterface".
 */
cudensitymatDistributedInterface_t cudensitymatCommInterface = {
    CUDENSITYMAT_DISTRIBUTED_INTERFACE_VERSION,
    cudensitymatMpiCommSize,
    cudensitymatMpiCommSizeShared,
    cudensitymatMpiCommRank,
    cudensitymatMpiBarrier,
    cudensitymatMpiCreateRequest,
    cudensitymatMpiDestroyRequest,
    cudensitymatMpiWaitRequest,
    cudensitymatMpiTestRequest,
    cudensitymatMpiSend,
    cudensitymatMpiSendAsync,
    cudensitymatMpiRecv,
    cudensitymatMpiRecvAsync,
    cudensitymatMpiBcast,
    cudensitymatMpiAllreduce,
    cudensitymatMpiAllreduceInPlace,
    cudensitymatMpiAllreduceInPlaceMin,
    cudensitymatMpiAllreduceDoubleIntMinloc,
    cudensitymatMpiAllgather
};

#ifdef __cplusplus
} // extern "C"
#endif
