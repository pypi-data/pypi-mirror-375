
#include "sjts.h"

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

#include "numpy/arrayobject.h"

typedef struct __SJContext
{
  const char *name;
  Py_ssize_t len;
  PyObject *obj;
} SJContext;

extern PyObject *SJException;

#define SJ_ERR(fmt) PyErr_Format(SJException, fmt)
#define SJ_ERR1(fmt, v1) PyErr_Format(SJException, fmt, v1)
#define SJ_RESPONSES_KEY ("series")
