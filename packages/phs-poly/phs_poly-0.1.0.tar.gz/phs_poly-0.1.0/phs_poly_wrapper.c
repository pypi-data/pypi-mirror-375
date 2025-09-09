#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <numpy/arrayobject.h>

/* Adjust symbol name if your Fortran has BIND(C) */
extern void c_phs3_p2(int *n, double *x, double *y,
                        double *coeffs, int *ldc,
                        double *wrk, int *iwrk, int *ierr);

static PyObject *
py_phs3_poly2(PyObject *self, PyObject *args)
{
    int n, ldc;
    PyObject *px, *py, *pcoeffs, *pwrk, *piwrk;

    if (!PyArg_ParseTuple(args, "iOOOiOO",
                          &n, &px, &py, &pcoeffs, &ldc, &pwrk, &piwrk)) {
        return NULL;
    }

    if (!PyArray_Check(px) || !PyArray_Check(py) ||
        !PyArray_Check(pcoeffs) || !PyArray_Check(pwrk) || !PyArray_Check(piwrk)) {
        PyErr_SetString(PyExc_TypeError, "All array arguments must be NumPy arrays");
        return NULL;
    }

    PyArrayObject *arr_x      = (PyArrayObject*)px;
    PyArrayObject *arr_y      = (PyArrayObject*)py;
    PyArrayObject *arr_coeffs = (PyArrayObject*)pcoeffs;
    PyArrayObject *arr_wrk    = (PyArrayObject*)pwrk;
    PyArrayObject *arr_iwrk   = (PyArrayObject*)piwrk;

    /* dtype checks */
    if (PyArray_TYPE(arr_x) != NPY_DOUBLE ||
        PyArray_TYPE(arr_y) != NPY_DOUBLE ||
        PyArray_TYPE(arr_coeffs) != NPY_DOUBLE ||
        PyArray_TYPE(arr_wrk) != NPY_DOUBLE) {
        PyErr_SetString(PyExc_TypeError, "x,y,coeffs,wrk must be float64 arrays");
        return NULL;
    }
    if (PyArray_TYPE(arr_iwrk) != NPY_INT32) {
        PyErr_SetString(PyExc_TypeError, "iwrk must be int32 array");
        return NULL;
    }

    /* shape checks */
    if (PyArray_NDIM(arr_x) != 1 || PyArray_DIM(arr_x,0) != n) {
        PyErr_SetString(PyExc_ValueError, "x must be 1D of length n");
        return NULL;
    }
    if (PyArray_NDIM(arr_y) != 1 || PyArray_DIM(arr_y,0) != n) {
        PyErr_SetString(PyExc_ValueError, "y must be 1D of length n");
        return NULL;
    }
    if (PyArray_NDIM(arr_coeffs) != 2 ||
        PyArray_DIM(arr_coeffs,0) != ldc ||
        PyArray_DIM(arr_coeffs,1) != 5) {
        PyErr_SetString(PyExc_ValueError, "coeffs must have shape (ldc,5)");
        return NULL;
    }
    if (PyArray_NDIM(arr_wrk) != 2 ||
        PyArray_DIM(arr_wrk,0) != ldc ||
        PyArray_DIM(arr_wrk,1) != n+6) {
        PyErr_SetString(PyExc_ValueError, "wrk must have shape (ldc,n+6)");
        return NULL;
    }
    if (PyArray_NDIM(arr_iwrk) != 1 ||
        PyArray_DIM(arr_iwrk,0) != n+6) {
        PyErr_SetString(PyExc_ValueError, "iwrk must be 1D of length n+6");
        return NULL;
    }

    /* Fortran order check where needed */
    if (!PyArray_ISFARRAY(arr_coeffs) || !PyArray_ISFARRAY(arr_wrk)) {
        PyErr_SetString(PyExc_ValueError, "coeffs and wrk must be Fortran-contiguous");
        return NULL;
    }

    double *x      = (double*)PyArray_DATA(arr_x);
    double *y      = (double*)PyArray_DATA(arr_y);
    double *coeffs = (double*)PyArray_DATA(arr_coeffs);
    double *wrk    = (double*)PyArray_DATA(arr_wrk);
    int    *iwrk   = (int*)   PyArray_DATA(arr_iwrk);

    int ierr = 0;
    c_phs3_p2(&n, x, y, coeffs, &ldc, wrk, iwrk, &ierr);

    return PyLong_FromLong(ierr);
}

static PyMethodDef Phs3Methods[] = {
    {"phs3_poly2", py_phs3_poly2, METH_VARARGS,
     "phs3_poly2(n, x, y, coeffs, ldc, wrk, iwrk) -> ierr"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef phs3module = {
    PyModuleDef_HEAD_INIT,
    "phs_poly",
    NULL,
    -1,
    Phs3Methods
};

PyMODINIT_FUNC
PyInit_phs_poly(void)
{
    import_array();
    return PyModule_Create(&phs3module);
}
