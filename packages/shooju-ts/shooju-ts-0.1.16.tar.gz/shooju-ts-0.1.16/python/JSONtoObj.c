/*
Developed by ESN, an Electronic Arts Inc. studio. 
Copyright (c) 2014, Electronic Arts Inc.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
* Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.
* Neither the name of ESN, Electronic Arts Inc. nor the
names of its contributors may be used to endorse or promote products
derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL ELECTRONIC ARTS INC. BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


Portions of code from MODP_ASCII - Ascii transformations (upper/lower, etc)
http://code.google.com/p/stringencoders/
Copyright (c) 2007  Nick Galbreath -- nickg [at] modp [dot] com. All rights reserved.

Numeric decoder derived from from TCL library
http://www.opensource.apple.com/source/tcl/tcl-14/tcl/license.terms
 * Copyright (c) 1988-1993 The Regents of the University of California.
 * Copyright (c) 1994 Sun Microsystems, Inc.
*/

#include "py_defines.h"
#include "py_sjts.h"


//#define PRINTMARK() fprintf(stderr, "%s: MARK(%d)\n", __FILE__, __LINE__)
#define PRINTMARK()

static void Object_objectAddKey(void *prv, JSOBJ obj, JSOBJ name, JSOBJ value)
{
  PyDict_SetItem (obj, name, value);
  Py_DECREF( (PyObject *) name);
  Py_DECREF( (PyObject *) value);
  return;
}

static void Object_arrayAddItem(void *prv, JSOBJ obj, JSOBJ value)
{
  PyList_Append(obj, value);
  Py_DECREF( (PyObject *) value);
  return;
}

static JSOBJ Object_newString(void *prv, wchar_t *start, wchar_t *end)
{
  return PyUnicode_FromWideChar (start, (end - start));
}

static JSOBJ Object_newTrue(void *prv)
{
  Py_RETURN_TRUE;
}

static JSOBJ Object_newFalse(void *prv)
{
  Py_RETURN_FALSE;
}

static JSOBJ Object_newNull(void *prv)
{
  Py_RETURN_NONE;
}

static JSOBJ Object_newObject(void *prv)
{
  return PyDict_New();
}

static JSOBJ Object_newArray(void *prv)
{
  return PyList_New(0);
}

static JSOBJ Object_newInteger(void *prv, JSINT32 value)
{
  return PyInt_FromLong( (long) value);
}

static JSOBJ Object_newLong(void *prv, JSINT64 value)
{
  return PyLong_FromLongLong (value);
}

static JSOBJ Object_newUnsignedLong(void *prv, JSUINT64 value)
{
  return PyLong_FromUnsignedLongLong (value);
}

static JSOBJ Object_newDouble(void *prv, double value)
{
  return PyFloat_FromDouble(value);
}

static void Object_releaseObject(void *prv, JSOBJ obj)
{
  Py_DECREF( ((PyObject *)obj));
}

static char *g_kwlist[] = {"obj", "use_numpy", "precise_float", NULL};

static int calc_point_arr_size(SJTSObjectDecoder *dec)
{
	return 2 + (dec->includes_job ? 1 : 0) + (dec->includes_timestamp ? 1 : 0);
}

static int getCount(SJTSObjectDecoder *dec, int level)
{
  const char *key = (level ? "points" : "series");
  PyObject *obj = dec->obj[level];
  if (obj && PyDict_Check(obj)) {
    PyObject *key_obj = PyDict_GetItemString(obj, key);
    if (key_obj && PyInt_Check(key_obj)) {
      int len = PyInt_AS_LONG(key_obj);
      PyObject *arr;
      if (level && dec->use_numpy) {
        npy_intp dims[2] = { len, calc_point_arr_size(dec) };
        PyArray_Descr *descr;
        PyObject *op;
        if (dec->includes_job && dec->includes_timestamp) {
          op = Py_BuildValue("[(s, s), (s, s), (s, s), (s, s)]", "dates", "i8", "values", "f8", "jobs", "i4", "ts", "u8");
        } else if (dec->includes_job) {
          op = Py_BuildValue("[(s, s), (s, s), (s, s)]", "dates", "i8", "values", "f8", "jobs", "i4");
        } else if (dec->includes_timestamp) {
          op = Py_BuildValue("[(s, s), (s, s), (s, s)]", "dates", "i8", "values", "f8", "ts", "u8");
        } else {
          op = Py_BuildValue("[(s, s), (s, s)]", "dates", "i8", "values", "f8");
        }
        if (op && PyArray_DescrConverter(op, &descr) != -1) {
          arr =  PyArray_SimpleNewFromDescr(1, dims, descr);
        } else {
          arr = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
        }
        if (op) Py_DECREF(op);
      } else {
        arr = PyList_New(len);
      }
      PyDict_SetItemString(obj, key, arr);
      Py_DECREF(arr);
      dec->arr[level] = arr;
      return len;
    }
  }
  return 0;
}

static void setItem(struct __SJTSObjectDecoder *dec, int idx)
{
  PyList_SET_ITEM(dec->arr[0], idx, dec->obj[1]);
}


static void setPoint(struct __SJTSObjectDecoder *dec, int idx, JSINT64 date, double value)
{
  int i = 0;
  PyObject *pnt;
  char *numpy_ptr;
  if (dec->use_numpy) {
    numpy_ptr = (char*)PyArray_GETPTR1(dec->arr[1], idx);
    *(JSINT64*)numpy_ptr = date;
    numpy_ptr += 8;
    *(double*)numpy_ptr = value;
    numpy_ptr += 8;
  } else {
    PyObject *dat = PyLong_FromLongLong(date);
    PyObject *val = PyFloat_FromDouble(value);
    pnt = PyTuple_New(calc_point_arr_size(dec));
    PyTuple_SET_ITEM(pnt, i++, dat);
    PyTuple_SET_ITEM(pnt, i++, val);
  }
  if (dec->includes_job) {
    if (dec->use_numpy) {
      *(JSUINT32*)numpy_ptr = *(JSUINT32*)dec->extraBuffer;
      numpy_ptr += 4;
    } else {
      PyObject *val = PyLong_FromLongLong(*(JSUINT32*)dec->extraBuffer);
      PyTuple_SET_ITEM(pnt, i++, val);
    }
    dec->extraBuffer += 4;
  }
  if (dec->includes_timestamp) {
    if (dec->use_numpy) {
      *(JSINT64*)numpy_ptr = *(JSINT64*)dec->extraBuffer;
    } else {
      PyObject *val = PyLong_FromLongLong(*(JSINT64*)dec->extraBuffer);
      PyTuple_SET_ITEM(pnt, i++, val);
    }
    dec->extraBuffer += 8;
  }
  if (!dec->use_numpy) {
    PyList_SET_ITEM(dec->arr[1], idx, pnt);
  }
}

static int checkRoot(struct __SJTSObjectDecoder *dec, char *root)
{
  PyObject *sjts = PyDict_GetItemString(dec->obj[0], "sjts");
  dec->includes_job = dec->includes_timestamp = 0;
  if (sjts) {
  	PyObject *includes = PyDict_GetItemString(sjts, "includes_job");
  	if (includes && PyObject_IsTrue(includes)) dec->includes_job = 1;
  	includes = PyDict_GetItemString(sjts, "includes_timestamp");
  	if (includes && PyObject_IsTrue(includes)) dec->includes_timestamp = 1;
    dec->extraBuffer = root + strlen(root) + 1;
  }
  return 0;
}

static void init_numpy()
{
  import_array();
}

PyObject* JSONToObj(PyObject* self, PyObject *args, PyObject *kwargs)
{
  PyObject *ret;
  PyObject *sarg;
  PyObject *arg;
  PyObject *useNumpy = NULL;
  PyObject *opreciseFloat = NULL;
  char *json_str;
  JSUINT64 json_offs = 0;
  SJTSObjectDecoder decoder = {
    {
      Object_newString,
      Object_objectAddKey,
      Object_arrayAddItem,
      Object_newTrue,
      Object_newFalse,
      Object_newNull,
      Object_newObject,
      Object_newArray,
      Object_newInteger,
      Object_newLong,
      Object_newUnsignedLong,
      Object_newDouble,
      Object_releaseObject,
      PyObject_Malloc,
      PyObject_Free,
      PyObject_Realloc
    },
    getCount,
    setItem,
    setPoint,
    checkRoot,
  };
  
  decoder.ujson.preciseFloat = 0;
  decoder.ujson.prv = &decoder;
  
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|OO", g_kwlist, &arg, &useNumpy, &opreciseFloat))
  {
      return NULL;
  }

  if (useNumpy && PyObject_IsTrue(useNumpy))
  {
      init_numpy();
      decoder.use_numpy = 1;
  } else {
      decoder.use_numpy = 0;
  }
  
  if (opreciseFloat && PyObject_IsTrue(opreciseFloat))
  {
      decoder.ujson.preciseFloat = 1;
  }
  
  if (PyString_Check(arg))
  {
      sarg = arg;
  }
  else
  if (PyUnicode_Check(arg))
  {
    sarg = PyUnicode_AsUTF8String(arg);
    if (sarg == NULL)
    {
      //Exception raised above us by codec according to docs
      return NULL;
    }
  }
  else
  {
    PyErr_Format(PyExc_TypeError, "Expected String or Unicode");
    return NULL;
  }

  decoder.ujson.errorStr = NULL;
  decoder.ujson.errorOffset = NULL;

  json_str = PyString_AS_STRING(sarg);

  ret = SJTS_DecodeObjectEx(&decoder, json_str, PyString_GET_SIZE(sarg), 1);
  if (sarg != arg)
  {
    Py_DECREF(sarg);
  }

  if (decoder.ujson.errorStr)
  {
    /*
    FIXME: It's possible to give a much nicer error message here with actual failing element in input etc*/

    PyErr_Format (PyExc_ValueError, "%s", decoder.ujson.errorStr);

    if (ret)
    {
        Py_DECREF( (PyObject *) ret);
    }

    return NULL;
  }

  if (PyDict_GetItemString(ret, "sjts")) PyDict_DelItemString(ret, "sjts");
  return ret;
}

PyObject* JSONFileToObj(PyObject* self, PyObject *args, PyObject *kwargs)
{
  PyObject *read;
  PyObject *string;
  PyObject *result;
  PyObject *file = NULL;
  PyObject *argtuple;

  if (!PyArg_ParseTuple (args, "O", &file))
  {
    return NULL;
  }

  if (!PyObject_HasAttrString (file, "read"))
  {
    PyErr_Format (PyExc_TypeError, "expected file");
    return NULL;
  }

  read = PyObject_GetAttrString (file, "read");

  if (!PyCallable_Check (read)) {
    Py_XDECREF(read);
    PyErr_Format (PyExc_TypeError, "expected file");
    return NULL;
  }

  string = PyObject_CallObject (read, NULL);
  Py_XDECREF(read);

  if (string == NULL)
  {
    return NULL;
  }

  argtuple = PyTuple_Pack(1, string);

  result = JSONToObj (self, argtuple, kwargs);

  Py_XDECREF(argtuple);
  Py_XDECREF(string);

  if (result == NULL) {
    return NULL;
  }

  return result;
}

PyObject* SJTSToSeries(PyObject* self, PyObject *args, PyObject *kwargs)
{
  SJTSObjectDecoder decoder = {
    {
      Object_newString,
      Object_objectAddKey,
      Object_arrayAddItem,
      Object_newTrue,
      Object_newFalse,
      Object_newNull,
      Object_newObject,
      Object_newArray,
      Object_newInteger,
      Object_newLong,
      Object_newUnsignedLong,
      Object_newDouble,
      Object_releaseObject,
      PyObject_Malloc,
      PyObject_Free,
      PyObject_Realloc
    },
    getCount,
    setItem,
    setPoint,
    checkRoot
  };
  PyObject *arg;
  PyObject *useNumpy = NULL;
  PyObject *opreciseFloat = NULL;
  PyObject *sarg;
  PyObject *res;
  PyObject *res2;
  char *json_str;

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|OO", g_kwlist, &arg, &useNumpy, &opreciseFloat))
  {
      return NULL;
  }

  if (useNumpy && PyObject_IsTrue(useNumpy))
  {
      init_numpy();
      decoder.use_numpy = 1;
  } else {
      decoder.use_numpy = 0;
  }

  if (opreciseFloat && PyObject_IsTrue(opreciseFloat))
  {
      decoder.ujson.preciseFloat = 1;
  }

  if (PyString_Check(arg))
  {
      sarg = arg;
  }
  else
  if (PyUnicode_Check(arg))
  {
    sarg = PyUnicode_AsUTF8String(arg);
    if (sarg == NULL)
    {
      //Exception raised above us by codec according to docs
      return NULL;
    }
  }
  else
  {
    PyErr_Format(PyExc_TypeError, "Expected String or Unicode");
    return NULL;
  }

  json_str = PyString_AS_STRING(sarg);
  res = SJTS_DecodeObjectEx(&decoder, json_str, PyString_GET_SIZE(sarg), 1);
  if (sarg != arg)
  {
    Py_DECREF(sarg);
  }
  if (PyDict_GetItemString(res, "sjts")) PyDict_DelItemString(res, "sjts");

  res2 = PyDict_GetItemString(res, SJ_RESPONSES_KEY);
  if (res2 && PyList_Check(res2)) {
    res2 = PyList_GET_ITEM(res2, 0);
    Py_INCREF(res2);
    Py_DECREF(res);
    res = res2;
  } else {
    return SJ_ERR("");
  }
  return res;
}
