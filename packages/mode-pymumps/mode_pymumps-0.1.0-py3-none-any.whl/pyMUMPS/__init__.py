# import ctypes, pathlib
# ctypes.CDLL(str(pathlib.Path(__file__).with_name('_pyMUMPS.pyd')))

# from . import _pyMUMPS
from ._pyMUMPS import call_selectedInvert
from scipy.sparse import coo_matrix, tril
import numpy as np

def selectedInvert(A, targetIndices_rows, targetIndices_cols):
    if targetIndices_rows.size != targetIndices_cols.size:
        raise ValueError
    
    A = tril(A) # lower triangle
    n = A.shape[0]

    values = A.data
    rowIndices = A.row
    colIndices = A.col
    
    rawUpperPairRowIndices = targetIndices_rows[targetIndices_cols >= targetIndices_rows].astype(np.int32)
    rawUpperPairColIndices = targetIndices_cols[targetIndices_cols >= targetIndices_rows].astype(np.int32)

    # convert to 1-based indexing for MUMPS
    rowIndices = A.row.astype(np.int32) + 1
    colIndices = A.col.astype(np.int32) + 1
    upperPairRowIndices = rawUpperPairRowIndices + 1
    upperPairColIndices = rawUpperPairColIndices + 1

    upperPairValues = call_selectedInvert(
        n,
        rowIndices.astype(np.int32),
        colIndices.astype(np.int32),
        A.data.astype(np.float64),
        upperPairRowIndices.astype(np.int32),
        upperPairColIndices.astype(np.int32))

    offDiagonalEntries = rawUpperPairColIndices > rawUpperPairRowIndices
    lowerPairRowIndices = rawUpperPairColIndices[offDiagonalEntries]
    lowerPairColIndices = rawUpperPairRowIndices[offDiagonalEntries]
    lowerPairValues = upperPairValues[offDiagonalEntries]

    rows = np.concatenate([rawUpperPairRowIndices, lowerPairRowIndices])
    cols = np.concatenate([rawUpperPairColIndices, lowerPairColIndices])
    values = np.concatenate([upperPairValues, lowerPairValues])

    A_inv = coo_matrix((values, (rows, cols)), shape=[n,n])
    return A_inv.tocsc()

testArray = [
    [21, -4,  0,  0,  0,  0,  0,  0,  0,  0],
    [-4, 13, -4,  0,  0,  0,  0,  0,  0,  0],
    [ 0, -4,  8, -4,  0,  0,  0,  0,  0,  0],
    [ 0,  0, -4,  8, -4,  0,  0,  0,  0,  0],
    [ 0,  0,  0, -4,  8, -4,  0,  0,  0,  0],
    [ 0,  0,  0,  0, -4,  8, -4,  0,  0,  0],
    [ 0,  0,  0,  0,  0, -4,  8, -4,  0,  0],
    [ 0,  0,  0,  0,  0,  0, -4,  8, -4,  0],
    [ 0,  0,  0,  0,  0,  0,  0, -4,  8, -4],
    [ 0,  0,  0,  0,  0,  0,  0,  0, -4, 20],
]


# K = csc_matrix((vals, (rows, cols)), shape=[10,10], dtype=np.float64)

K = coo_matrix(testArray)

rowTargets = np.array([0,2,2,3], dtype=np.int32)
colTargets = np.array([0,0,1,3], dtype=np.int32)
rowTargets = np.array([
    np.arange(4),
    np.arange(4),
    np.arange(4),
    np.arange(4)])
colTargets = np.ones([4,4])
colTargets[0] *= 0
colTargets[1] *= 1
colTargets[2] *= 2
colTargets[3] *= 3

K_inv = selectedInvert(K, rowTargets, colTargets)
# print(K_inv)             # prints summary: shape, nnz
# print(K_inv.toarray())   # dense 2D NumPy array
# print(repr(K_inv))       # SciPy shows row/col/data for small matrices