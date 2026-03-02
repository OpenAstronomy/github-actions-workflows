#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject* example_func(PyObject* self, PyObject* args) {
    return PyLong_FromLong(42);
}

static PyMethodDef ExampleMethods[] = {
    {"example_func", example_func, METH_NOARGS, "Return 42"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef examplemodule = {
    PyModuleDef_HEAD_INIT,
    "_example",
    NULL,
    -1,
    ExampleMethods
};

PyMODINIT_FUNC PyInit__example(void) {
    return PyModule_Create(&examplemodule);
}
