from caspian.layers import Pooling1D, Pooling2D, Pooling3D, PoolingND
from caspian.pooling import Maximum, Minimum, Average
from caspian.utilities import InvalidDataException, UnsafeMemoryAccessException
import numpy as np
import pytest

def test_pooling1D():
    # Incorrect sizes
    with pytest.raises(InvalidDataException):
        layer = Pooling1D(Maximum(), 2, 5)

    with pytest.raises(InvalidDataException):
        layer = Pooling1D(Maximum(), 2, (5,))


    # Inference mode grad variables
    layer = Pooling1D(Maximum(), 2, (2, 10), 2)
    data_in = np.zeros((2, 10))
    _ = layer(data_in)
    data_out = np.zeros((2, 5))
    with pytest.raises(AttributeError):
        _ = layer.backward(data_out)


    # Private variables not accessable outside of layer
    _ = layer(data_in, True)
    with pytest.raises(AttributeError):
        _ = layer.__last_in == None
    layer.clear_grad()


    # Forward sizes
    layer = Pooling1D(Maximum(), 2, (2, 20), 2)
    data_in = np.zeros((2, 20))
    assert layer(data_in).shape == (2, 10)

    layer = Pooling1D(Maximum(), 3, (2, 20), 1)
    data_in = np.zeros((2, 20))
    assert layer(data_in).shape == (2, 18)


    # Backward sizes
    layer = Pooling1D(Maximum(), 2, (2, 20), 2)
    data_in = np.zeros((2, 20))
    data_out = np.zeros((2, 10))
    _ = layer(data_in, True)
    assert layer.backward(data_out).shape == (2, 20)

    layer = Pooling1D(Maximum(), 2, (2, 20), 1)
    data_in = np.zeros((2, 20))
    data_out = np.zeros((2, 19))
    _ = layer(data_in, True)
    assert layer.backward(data_out).shape == (2, 20)    


    # Type failure checking
    with pytest.raises(InvalidDataException):
        layer = Pooling1D(Maximum(), 1.1, (2, 10))
    
    with pytest.raises(InvalidDataException):
        layer = Pooling1D(Maximum(), 1, "test")

    with pytest.raises(InvalidDataException):
        layer = Pooling1D(Maximum(), 2, (2, 10), "c")

    with pytest.raises(InvalidDataException):
        layer = Pooling1D(Maximum(), 2, (2, 10), 0)

    with pytest.raises(InvalidDataException):
        layer = Pooling1D(Maximum(), 2, (2, 10), 1, -1)

    with pytest.raises(InvalidDataException):
        layer = Pooling1D(None, 2, (2, 10))

    with pytest.raises(InvalidDataException):
        layer = Pooling1D(Maximum(), 2, (-1, -1, -1))
 
    
    # Incorrect shape tests
    layer = Pooling1D(Maximum(), 2, (2, 20), 2)
    data_in = np.zeros((2, 20))
    data_false_in = np.zeros((3, 20))
    data_false_out = np.zeros((2, 11))
    with pytest.raises(UnsafeMemoryAccessException):
        _ = layer(data_false_in)

    _ = layer(data_in, True)
    with pytest.raises(UnsafeMemoryAccessException):
        _ = layer.backward(data_false_out)


    # Saving + Loading
    layer = Pooling1D(Maximum(), 2, (2, 20), 2, 3)
    l_save = layer.save_to_file()
    load_layer = Pooling1D.from_save(l_save)
    assert np.allclose(load_layer.in_size, layer.in_size)
    assert np.allclose(load_layer.out_size, layer.out_size)
    assert load_layer.kernel_size == layer.kernel_size
    assert load_layer.padding_all == layer.padding_all
    assert load_layer.strides == layer.strides


    # Deepcopy
    layer2 = layer.deepcopy()
    assert layer2 is not layer
    assert np.allclose(load_layer.in_size, layer.in_size)
    assert np.allclose(load_layer.out_size, layer.out_size)
    assert load_layer.kernel_size == layer.kernel_size
    assert load_layer.padding_all == layer.padding_all
    assert load_layer.strides == layer.strides




def test_pooling2D():
    # Incorrect sizes
    with pytest.raises(InvalidDataException):
        layer = Pooling2D(Maximum(), 2, 5)

    with pytest.raises(InvalidDataException):
        layer = Pooling1D(Maximum(), 2, (5,))


    # Inference mode grad variables
    layer = Pooling2D(Maximum(), 2, (2, 10, 10), 2)
    data_in = np.zeros((2, 10, 10))
    _ = layer(data_in)
    data_out = np.zeros((2, 5, 5))
    with pytest.raises(AttributeError):
        _ = layer.backward(data_out)


    # Private variables not accessable outside of layer
    _ = layer(data_in, True)
    with pytest.raises(AttributeError):
        _ = layer.__last_in == None
    layer.clear_grad()


    # Forward sizes
    layer = Pooling2D(Maximum(), (2, 4), (2, 20, 20), (2, 4))
    data_in = np.zeros((2, 20, 20))
    assert layer(data_in).shape == (2, 10, 5)

    layer = Pooling2D(Maximum(), 3, (2, 20, 20), 1)
    data_in = np.zeros((2, 20, 20))
    assert layer(data_in).shape == (2, 18, 18)


    # Backward sizes
    layer = Pooling2D(Maximum(), (2, 4), (2, 20, 20), (2, 4))
    data_in = np.zeros((2, 20, 20))
    data_out = np.zeros((2, 10, 5))
    _ = layer(data_in, True)
    assert layer.backward(data_out).shape == (2, 20, 20)

    layer = Pooling2D(Maximum(), 3, (2, 20, 20), 1)
    data_in = np.zeros((2, 20, 20))
    data_out = np.zeros((2, 18, 18))
    _ = layer(data_in, True)
    assert layer.backward(data_out).shape == (2, 20, 20)    


    # Type failure checking
    with pytest.raises(InvalidDataException):
        layer = Pooling2D(Maximum(), 1.1, (2, 10, 10))
    
    with pytest.raises(InvalidDataException):
        layer = Pooling2D(Maximum(), 1, "test")

    with pytest.raises(InvalidDataException):
        layer = Pooling2D(Maximum(), 2, (2, 10, 10), "c")

    with pytest.raises(InvalidDataException):
        layer = Pooling2D(Maximum(), 2, (2, 10, 10), 0)

    with pytest.raises(InvalidDataException):
        layer = Pooling2D(Maximum(), 1, (2, 10, 10), (2,))

    with pytest.raises(InvalidDataException):
        layer = Pooling2D(Maximum(), 2, (2, 10, 10), 1, -1)

    with pytest.raises(InvalidDataException):
        layer = Pooling2D(None, 2, (2, 10, 10))

    with pytest.raises(InvalidDataException):
        layer = Pooling2D(Maximum(), 2, (-2, 10, 10))
 

    # Incorrect shape tests
    layer = Pooling2D(Maximum(), 2, (2, 20, 20), 2)
    data_in = np.zeros((2, 20, 20))
    data_false_in = np.zeros((3, 20, 20))
    data_false_out = np.zeros((2, 11, 10))
    with pytest.raises(UnsafeMemoryAccessException):
        _ = layer(data_false_in)

    _ = layer(data_in, True)
    with pytest.raises(UnsafeMemoryAccessException):
        _ = layer.backward(data_false_out)


    # Saving + Loading
    layer = Pooling2D(Maximum(), 2, (2, 20, 20), 2, 3)
    l_save = layer.save_to_file()
    load_layer = Pooling2D.from_save(l_save)
    assert np.allclose(load_layer.in_size, layer.in_size)
    assert np.allclose(load_layer.out_size, layer.out_size)
    assert load_layer.kernel_height == layer.kernel_height
    assert load_layer.kernel_width == layer.kernel_width
    assert load_layer.pad_height == layer.pad_height
    assert load_layer.pad_width == layer.pad_width
    assert load_layer.stride_h == layer.stride_h
    assert load_layer.stride_w == layer.stride_w


    # Deepcopy
    layer2 = layer.deepcopy()
    assert layer2 is not layer
    assert np.allclose(load_layer.in_size, layer.in_size)
    assert np.allclose(load_layer.out_size, layer.out_size)
    assert load_layer.kernel_height == layer.kernel_height
    assert load_layer.kernel_width == layer.kernel_width
    assert load_layer.pad_height == layer.pad_height
    assert load_layer.pad_width == layer.pad_width
    assert load_layer.stride_h == layer.stride_h
    assert load_layer.stride_w == layer.stride_w




def test_pooling3D():
    # Incorrect sizes
    with pytest.raises(InvalidDataException):
        layer = Pooling3D(Maximum(), 2, 5)

    with pytest.raises(InvalidDataException):
        layer = Pooling3D(Maximum(), 2, (5,))


    # Inference mode grad variables
    layer = Pooling3D(Maximum(), 2, (2, 10, 10, 10), 2)
    data_in = np.zeros((2, 10, 10, 10))
    _ = layer(data_in)
    data_out = np.zeros((2, 5, 5, 5))
    with pytest.raises(AttributeError):
        _ = layer.backward(data_out)


    # Private variables not accessable outside of layer
    _ = layer(data_in, True)
    with pytest.raises(AttributeError):
        _ = layer.__last_in == None
    layer.clear_grad()


    # Forward sizes
    layer = Pooling3D(Maximum(), (2, 4, 5), (2, 20, 20, 20), (2, 4, 5))
    data_in = np.zeros((2, 20, 20, 20))
    assert layer(data_in).shape == (2, 10, 5, 4)

    layer = Pooling3D(Maximum(), 3, (2, 20, 20, 20), 1)
    data_in = np.zeros((2, 20, 20, 20))
    assert layer(data_in).shape == (2, 18, 18, 18)


    # Backward sizes
    layer = Pooling3D(Maximum(), (2, 4, 5), (2, 20, 20, 20), (2, 4, 5))
    data_in = np.zeros((2, 20, 20, 20))
    data_out = np.zeros((2, 10, 5, 4))
    _ = layer(data_in, True)
    assert layer.backward(data_out).shape == (2, 20, 20, 20)

    layer = Pooling3D(Maximum(), 3, (2, 20, 20, 20), 1)
    data_in = np.zeros((2, 20, 20, 20))
    data_out = np.zeros((2, 18, 18, 18))
    _ = layer(data_in, True)
    assert layer.backward(data_out).shape == (2, 20, 20, 20)    


    # Type failure checking
    with pytest.raises(InvalidDataException):
        layer = Pooling3D(Maximum(), 1.1, (2, 10, 10, 10))
    
    with pytest.raises(InvalidDataException):
        layer = Pooling3D(Maximum(), 1, "test")

    with pytest.raises(InvalidDataException):
        layer = Pooling3D(Maximum(), 2, (2, 10, 10, 10), "c")

    with pytest.raises(InvalidDataException):
        layer = Pooling3D(Maximum(), 1, (2, 10, 10), (2,))

    with pytest.raises(InvalidDataException):
        layer = Pooling3D(Maximum(), 2, (2, 10, 10, 10), 0)

    with pytest.raises(InvalidDataException):
        layer = Pooling3D(Maximum(), 2, (2, 10, 10, 10), 1, -1)

    with pytest.raises(InvalidDataException):
        layer = Pooling3D(None, 2, (2, 10, 10, 10))
 

    # Incorrect shape tests
    layer = Pooling3D(Maximum(), 2, (2, 20, 20, 20), 2)
    data_in = np.zeros((2, 20, 20, 20))
    data_false_in = np.zeros((3, 20, 20, 20))
    data_false_out = np.zeros((2, 11, 10, 10))
    with pytest.raises(UnsafeMemoryAccessException):
        _ = layer(data_false_in)

    _ = layer(data_in, True)
    with pytest.raises(UnsafeMemoryAccessException):
        _ = layer.backward(data_false_out)


    # Saving + Loading
    layer = Pooling3D(Maximum(), 2, (2, 20, 20, 20), 2, 3)
    l_save = layer.save_to_file()
    load_layer = Pooling3D.from_save(l_save)
    assert np.allclose(load_layer.in_size, layer.in_size)
    assert np.allclose(load_layer.out_size, layer.out_size)
    assert load_layer.kernel_height == layer.kernel_height
    assert load_layer.kernel_width == layer.kernel_width
    assert load_layer.kernel_depth == layer.kernel_depth
    assert load_layer.pad_height == layer.pad_height
    assert load_layer.pad_width == layer.pad_width
    assert load_layer.pad_depth == layer.pad_depth
    assert load_layer.stride_h == layer.stride_h
    assert load_layer.stride_w == layer.stride_w
    assert load_layer.stride_d == layer.stride_d


    # Deepcopy
    layer2 = layer.deepcopy()
    assert layer2 is not layer
    assert np.allclose(load_layer.in_size, layer.in_size)
    assert np.allclose(load_layer.out_size, layer.out_size)
    assert load_layer.kernel_height == layer.kernel_height
    assert load_layer.kernel_width == layer.kernel_width
    assert load_layer.kernel_depth == layer.kernel_depth
    assert load_layer.pad_height == layer.pad_height
    assert load_layer.pad_width == layer.pad_width
    assert load_layer.pad_depth == layer.pad_depth
    assert load_layer.stride_h == layer.stride_h
    assert load_layer.stride_w == layer.stride_w
    assert load_layer.stride_d == layer.stride_d




def test_poolingND():
    # Incorrect sizes
    with pytest.raises(InvalidDataException):
        layer = PoolingND(Maximum(), 2, 5)

    with pytest.raises(InvalidDataException):
        layer = PoolingND(Maximum(), 2, (5,))


    # Inference mode grad variables
    layer = PoolingND(Maximum(), 2, (2, 10, 10, 10, 10), 2)
    data_in = np.zeros((2, 10, 10, 10, 10))
    _ = layer(data_in)
    data_out = np.zeros((2, 5, 5, 5, 5))
    with pytest.raises(AttributeError):
        _ = layer.backward(data_out)


    # Private variables not accessable outside of layer
    _ = layer(data_in, True)
    with pytest.raises(AttributeError):
        _ = layer.__last_in == None
    layer.clear_grad()
    

    # Forward sizes
    layer = PoolingND(Maximum(), (2, 4, 5, 4), (2, 20, 20, 20, 20), (2, 4, 5, 4))
    data_in = np.zeros((2, 20, 20, 20, 20))
    assert layer(data_in).shape == (2, 10, 5, 4, 5)

    layer = PoolingND(Maximum(), 3, (2, 20, 20, 20, 10), 1)
    data_in = np.zeros((2, 20, 20, 20, 10))
    assert layer(data_in).shape == (2, 18, 18, 18, 8)

    layer = PoolingND(Maximum(), 3, (2, 18, 15), 3)
    data_in = np.zeros((2, 18, 15))
    assert layer(data_in).shape == (2, 6, 5)

    layer = PoolingND(Maximum(), (2, 5, 2, 3, 2), (2, 5, 20, 5, 10, 5), (1, 2, 2, 2, 1), 3)
    data_in = np.zeros((2, 5, 20, 5, 10, 5))
    assert layer(data_in).shape == (2, 7, 10, 4, 6, 7)


    # Backward sizes
    layer = PoolingND(Maximum(), (2, 4, 5, 4), (2, 20, 20, 20, 20), (2, 4, 5, 4))
    data_in = np.zeros((2, 20, 20, 20, 20))
    data_out = np.zeros((2, 10, 5, 4, 5))
    _ = layer(data_in, True)
    assert layer.backward(data_out).shape == (2, 20, 20, 20, 20)

    layer = PoolingND(Maximum(), 3, (2, 20, 20, 20, 10), 1)
    data_in = np.zeros((2, 20, 20, 20, 10))
    data_out = np.zeros((2, 18, 18, 18, 8))
    _ = layer(data_in, True)
    assert layer.backward(data_out).shape == (2, 20, 20, 20, 10)

    layer = PoolingND(Maximum(), 3, (2, 18, 15), 3)
    data_in = np.zeros((2, 18, 15))
    data_out = np.zeros((2, 6, 5))
    _ = layer(data_in, True)
    assert layer.backward(data_out).shape == (2, 18, 15)

    layer = PoolingND(Maximum(), (2, 5, 2, 3, 2), (2, 5, 20, 5, 10, 5), (1, 2, 2, 2, 1), 3)
    data_in = np.zeros((2, 5, 20, 5, 10, 5))
    data_out = np.zeros((2, 7, 10, 4, 6, 7))
    _ = layer(data_in, True)
    assert layer.backward(data_out).shape == (2, 5, 20, 5, 10, 5)


    # Type failure checking
    with pytest.raises(InvalidDataException):
        layer = PoolingND(Maximum(), 1.1, (2, 10, 10, 10))
    
    with pytest.raises(InvalidDataException):
        layer = PoolingND(Maximum(), 1, "test")

    with pytest.raises(InvalidDataException):
        layer = PoolingND(Maximum(), 2, (2, 10, 10, 10), "c")

    with pytest.raises(InvalidDataException):
        layer = PoolingND(Maximum(), 1, (2, 10, 10), (2,))

    with pytest.raises(InvalidDataException):
        layer = PoolingND(Maximum(), 2, (2, 10, 10, 10), 0)

    with pytest.raises(InvalidDataException):
        layer = PoolingND(Maximum(), 2, (2, 10, 10, 10), 1, -1)

    with pytest.raises(InvalidDataException):
        layer = PoolingND(None, 2, (2, 10, 10, 10))

    with pytest.raises(InvalidDataException):
        layer = PoolingND(Maximum(), (2, 1), (2, 10, 10, 10))

    with pytest.raises(InvalidDataException):
        layer = PoolingND(Maximum(), 2, (2, 10, 10, 10), (2, 2))

    with pytest.raises(InvalidDataException):
        layer = PoolingND(Maximum(), 2, (2, 10, 10, 10), 2, (1, 0))

    with pytest.raises(InvalidDataException):
        layer = PoolingND(Maximum(), 2, (2,))


    # Incorrect shape tests
    layer = Pooling3D(Maximum(), 2, (2, 20, 20, 20), 2)
    data_in = np.zeros((2, 20, 20, 20))
    data_false_in = np.zeros((3, 20, 20, 20))
    data_false_out = np.zeros((2, 11, 10, 10))
    with pytest.raises(UnsafeMemoryAccessException):
        _ = layer(data_false_in)

    _ = layer(data_in, True)
    with pytest.raises(UnsafeMemoryAccessException):
        _ = layer.backward(data_false_out)

    data_false_in = np.zeros((2, 20, 20))
    with pytest.raises(UnsafeMemoryAccessException):
        _ = layer(data_false_in)

    data_false_out = np.zeros((2, 10, 10))
    _ = layer(data_in, True)
    with pytest.raises(UnsafeMemoryAccessException):
        _ = layer.backward(data_false_out)  


    # Saving + Loading
    layer = PoolingND(Maximum(), (2, 4, 2), (2, 20, 20, 20), (3, 2, 3), (1, 1, 7))
    l_save = layer.save_to_file()
    load_layer = PoolingND.from_save(l_save)
    assert np.allclose(load_layer.in_size, layer.in_size)
    assert np.allclose(load_layer.out_size, layer.out_size)
    assert load_layer.kernel_size == layer.kernel_size
    assert load_layer.input_length == layer.input_length
    assert load_layer.padding_all == layer.padding_all
    assert load_layer.pad_details == layer.pad_details
    assert load_layer.strides_all == layer.strides_all


    # Deepcopy
    layer2 = layer.deepcopy()
    assert layer2 is not layer
    assert np.allclose(load_layer.in_size, layer.in_size)
    assert np.allclose(load_layer.out_size, layer.out_size)
    assert load_layer.kernel_size == layer.kernel_size
    assert load_layer.input_length == layer.input_length
    assert load_layer.padding_all == layer.padding_all
    assert load_layer.pad_details == layer.pad_details
    assert load_layer.strides_all == layer.strides_all    




def test_maxpool():
    # Variable inheritence test
    pool = Maximum()
    assert pool.axis == -1
    
    pool = Maximum(2)
    assert pool.axis == 2


    # Forward functionality tests
    pool = Maximum()
    array1 = np.array([[2.0, 1.0, 3.0, 2.5],
                       [9.0, 2.0, 1.5, 4.0]])
    expected = np.array([3.0, 9.0])
    result = pool(array1)
    assert result.shape == (2,)
    assert np.allclose(expected, result)


    # Backward functionality tests
    expected = np.array([[0.0, 0.0, 1.0, 0.0],
                         [1.0, 0.0, 0.0, 0.0]])
    result = pool.backward(array1)
    assert result.shape == array1.shape
    assert np.allclose(expected, result)




def test_avgpool():
    # Variable inheritence test
    pool = Average()
    assert pool.axis == -1
    
    pool = Average(2)
    assert pool.axis == 2


    # Forward functionality tests
    pool = Average()
    array1 = np.array([[1.0, 2.0, 3.0, 4.0],
                       [3.5, 2.5, 1.5, 0.5]])
    expected = np.array([2.5, 2.0])
    result = pool(array1)
    assert result.shape == (2,)
    assert np.allclose(expected, result)


    # Backward functionality tests
    expected = np.array([[0.25, 0.5, 0.75, 1.0],
                         [0.875, 0.625, 0.375, 0.125]])
    result = pool.backward(array1)
    assert result.shape == array1.shape
    assert np.allclose(expected, result)




def test_minpool():
    # Variable inheritence test
    pool = Minimum()
    assert pool.axis == -1
    
    pool = Minimum(2)
    assert pool.axis == 2


    # Forward functionality tests
    pool = Minimum()
    array1 = np.array([[1.0, 2.0, 3.0, 4.0],
                       [3.5, 2.5, 1.5, 0.5]])
    expected = np.array([1.0, 0.5])
    result = pool(array1)
    assert result.shape == (2,)
    assert np.allclose(expected, result)


    # Backward functionality tests
    expected = np.array([[1.0, 0.0, 0.0, 0.0],
                         [0.0, 0.0, 0.0, 1.0]])
    result = pool.backward(array1)
    assert result.shape == array1.shape
    assert np.allclose(expected, result)