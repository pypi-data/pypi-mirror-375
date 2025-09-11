cimport numpy as np
import cython
import numpy as np


cdef extern int rescale_float_to_int8(float* Input, unsigned char* Output, float input_min, float input_max, float factor, size_t total_elements);
cdef extern int rescale_float_to_int16(float* Input, unsigned short* Output, float input_min, float input_max, float factor, size_t total_elements);
cdef extern int rescale_float_to_int32(float* Input, unsigned int* Output, float input_min, float input_max, float factor, size_t total_elements);

def rescale_to_int_8bit_C(np.ndarray[np.float32_t, ndim=3, mode="c"] inputData,
                     float input_min, float input_max, float factor):

    cdef long dims[3]
    dims[0] = inputData.shape[0]
    dims[1] = inputData.shape[1]
    dims[2] = inputData.shape[2]
    
    cdef np.ndarray[np.uint8_t, ndim=3, mode="c"] outputData = np.zeros([dims[0],dims[1],dims[2]], dtype='uint8')

    rescale_float_to_int8(&inputData[0,0,0], &outputData[0,0,0],
                        input_min, input_max, factor,
                        dims[0]*dims[1]*dims[2])

    return outputData


def rescale_to_int_16bit_C(np.ndarray[np.float32_t, ndim=3, mode="c"] inputData,
                     float input_min, float input_max, float factor):

    cdef long dims[3]
    dims[0] = inputData.shape[0]
    dims[1] = inputData.shape[1]
    dims[2] = inputData.shape[2]
    
    cdef np.ndarray[np.uint16_t, ndim=3, mode="c"] outputData = np.zeros([dims[0],dims[1],dims[2]], dtype='uint16')

    rescale_float_to_int16(&inputData[0,0,0], &outputData[0,0,0],
                        input_min, input_max, factor,
                        dims[0]*dims[1]*dims[2])

    return outputData

def rescale_to_int_32bit_C(np.ndarray[np.float32_t, ndim=3, mode="c"] inputData,
                     float input_min, float input_max, float factor):

    cdef long dims[3]
    dims[0] = inputData.shape[0]
    dims[1] = inputData.shape[1]
    dims[2] = inputData.shape[2]
    
    cdef np.ndarray[np.uint32_t, ndim=3, mode="c"] outputData = np.zeros([dims[0],dims[1],dims[2]], dtype='uint32')

    rescale_float_to_int32(&inputData[0,0,0], &outputData[0,0,0],
                        input_min, input_max, factor,
                        dims[0]*dims[1]*dims[2])

    return outputData