#include <Python.h>

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "simple",
    NULL,
    -1,
    NULL
};
PyMODINIT_FUNC
PyInit_simple(void) {
    return PyModule_Create(&moduledef);
}
