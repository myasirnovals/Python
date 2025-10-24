import numpy as np

A = np.array([[2, 3], [1, 4]])
determinant = np.linalg.det(A)
print("Determinant: ", determinant)

inverse = np.linalg.inv(A)
print("Inverse of Matrix A: \n", inverse)

eigenValues, eigenVectors = np.linalg.eig(A)
print("Eigenvalues: ", eigenValues)
print("Eigenvectors: \n", eigenVectors)

B = np.array([[4, 2], [1, 1]])
eigval, eigvec = np.linalg.eig(B)
print("Eigenvalues of B: ", eigval)
print("Eigenvectors of B: \n", eigvec)

U, S, Vt = np.linalg.svd(A)
print("U: \n", U)
print("Singular Values: \n", S)
print("V Transpose: \n", Vt)