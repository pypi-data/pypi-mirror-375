/*
 * m bs4 import BeautifulSoup
 * import json
 * import ujson
 * body = BeautifulSoup('<div><b>hello</b></div>')
 * val = body.find_all('b')[0].string
 * print('value: {} type: {}'.format(val, type(val)))
 * print(sjts.dumps({
 *     'series': [{'series_id': 'test', 'fields': {'test_field': val}}]
 *     }))
 *     print(ujson.dumps({'test_field': val}))
 *     print(json.dumps({'test_field': val}))
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
#include <stdio.h>
#include <datetime.h>
#include "py_sjts.h"


#ifndef NAN // Visual C++ for Python doesn't have a NAN definition
#ifndef _HUGE_ENUF
    #define _HUGE_ENUF  1e+300  // _HUGE_ENUF*_HUGE_ENUF must overflow
#endif

#define INFINITY   ((float)(_HUGE_ENUF * _HUGE_ENUF))
#define NAN        ((float)(INFINITY * 0.0F))
#endif // NAN

#define EPOCH_ORD 719163
static PyObject* type_decimal = NULL;

typedef void *(*PFN_PyTypeToJSON)(JSOBJ obj, JSONTypeContext *ti, void *outValue, size_t *_outLen);

#if (PY_VERSION_HEX < 0x02050000)
typedef ssize_t Py_ssize_t;
#endif

typedef struct __TypeContext
{
  JSPFN_ITEREND iterEnd;
  JSPFN_ITERNEXT iterNext;
  JSPFN_ITERGETNAME iterGetName;
  JSPFN_ITERGETVALUE iterGetValue;
  PFN_PyTypeToJSON PyTypeToJSON;
  PyObject *newObj;
  PyObject *dictObj;
  Py_ssize_t index;
  Py_ssize_t size;
  PyObject *itemValue;
  PyObject *itemName;
  PyObject *attrList;
  PyObject *iterator;

  SJContext *sjCtx;
  int level;

  union
  {
    PyObject *rawJSONValue;
    JSINT64 longValue;
    JSUINT64 unsignedLongValue;
  } un;
} TypeContext;

#define GET_TC(__ptrtc) ((TypeContext *)((__ptrtc)->prv))

struct PyDictIterState
{
  PyObject *keys;
  size_t i;
  size_t sz;
};

//#define PRINTMARK() fprintf(stderr, "%s: MARK(%d)\n", __FILE__, __LINE__)
#define PRINTMARK()

void initObjToJSON(void)
{
  PyObject* mod_decimal = PyImport_ImportModule("decimal");
  if (mod_decimal)
  {
    type_decimal = PyObject_GetAttrString(mod_decimal, "Decimal");
    Py_INCREF(type_decimal);
    Py_DECREF(mod_decimal);
  }
  else
    PyErr_Clear();

  PyDateTime_IMPORT;
}

#ifdef _LP64
static void *PyIntToINT64(JSOBJ _obj, JSONTypeContext *tc, void *outValue, size_t *_outLen)
{
  PyObject *obj = (PyObject *) _obj;
  *((JSINT64 *) outValue) = PyInt_AS_LONG (obj);
  return NULL;
}
#else
static void *PyIntToINT32(JSOBJ _obj, JSONTypeContext *tc, void *outValue, size_t *_outLen)
{
  PyObject *obj = (PyObject *) _obj;
  *((JSINT32 *) outValue) = PyInt_AS_LONG (obj);
  return NULL;
}
#endif

static void *PyLongToINT64(JSOBJ _obj, JSONTypeContext *tc, void *outValue, size_t *_outLen)
{
  *((JSINT64 *) outValue) = GET_TC(tc)->un.longValue;
  return NULL;
}

static void *PyLongToUINT64(JSOBJ _obj, JSONTypeContext *tc, void *outValue, size_t *_outLen)
{
  *((JSUINT64 *) outValue) = GET_TC(tc)->un.unsignedLongValue;
  return NULL;
}

static void *PyFloatToDOUBLE(JSOBJ _obj, JSONTypeContext *tc, void *outValue, size_t *_outLen)
{
  PyObject *obj = (PyObject *) _obj;
  *((double *) outValue) = PyFloat_AsDouble (obj);
  return NULL;
}

static void *PyStringToUTF8(JSOBJ _obj, JSONTypeContext *tc, void *outValue, size_t *_outLen)
{
  PyObject *obj = (PyObject *) _obj;
  *_outLen = PyString_GET_SIZE(obj);
  return PyString_AS_STRING(obj);
}

static void *PyUnicodeToUTF8(JSOBJ _obj, JSONTypeContext *tc, void *outValue, size_t *_outLen)
{
  PyObject *obj = (PyObject *) _obj;
  PyObject *newObj;
#if (PY_VERSION_HEX >= 0x03030000)
  if(PyUnicode_IS_COMPACT_ASCII(obj))
  {
    Py_ssize_t len;
    char *data = PyUnicode_AsUTF8AndSize(obj, &len);
    *_outLen = len;
    return data;
  }
#endif
  newObj = PyUnicode_AsUTF8String(obj);
  if(!newObj)
  {
    return NULL;
  }

  GET_TC(tc)->newObj = newObj;

  *_outLen = PyString_GET_SIZE(newObj);
  return PyString_AS_STRING(newObj);
}

static void *PyRawJSONToUTF8(JSOBJ _obj, JSONTypeContext *tc, void *outValue, size_t *_outLen)
{
  PyObject *obj = GET_TC(tc)->un.rawJSONValue;
  if (PyUnicode_Check(obj)) {
    return PyUnicodeToUTF8(obj, tc, outValue, _outLen);
  }
  else {
    return PyStringToUTF8(obj, tc, outValue, _outLen);
  }
}

static void *PyDateTimeToINT64(JSOBJ _obj, JSONTypeContext *tc, void *outValue, size_t *_outLen)
{
  PyObject *obj = (PyObject *) _obj;
  PyObject *date, *ord, *utcoffset;
  int y, m, d, h, mn, s, days;

  utcoffset = PyObject_CallMethod(obj, "utcoffset", NULL);
  if(utcoffset != Py_None){
    obj = PyNumber_Subtract(obj, utcoffset);
  }

  y = PyDateTime_GET_YEAR(obj);
  m = PyDateTime_GET_MONTH(obj);
  d = PyDateTime_GET_DAY(obj);
  h = PyDateTime_DATE_GET_HOUR(obj);
  mn = PyDateTime_DATE_GET_MINUTE(obj);
  s = PyDateTime_DATE_GET_SECOND(obj);

  date = PyDate_FromDate(y, m, 1);
  ord = PyObject_CallMethod(date, "toordinal", NULL);
  days = PyInt_AS_LONG(ord) - EPOCH_ORD + d - 1;
  Py_DECREF(date);
  Py_DECREF(ord);
  *( (JSINT64 *) outValue) = (((JSINT64) ((days * 24 + h) * 60 + mn)) * 60 + s);
  return NULL;
}

static void *PyDateToINT64(JSOBJ _obj, JSONTypeContext *tc, void *outValue, size_t *_outLen)
{
  PyObject *obj = (PyObject *) _obj;
  PyObject *date, *ord;
  int y, m, d, days;

  y = PyDateTime_GET_YEAR(obj);
  m = PyDateTime_GET_MONTH(obj);
  d = PyDateTime_GET_DAY(obj);

  date = PyDate_FromDate(y, m, 1);
  ord = PyObject_CallMethod(date, "toordinal", NULL);
  days = PyInt_AS_LONG(ord) - EPOCH_ORD + d - 1;
  Py_DECREF(date);
  Py_DECREF(ord);
  *( (JSINT64 *) outValue) = ((JSINT64) days * 86400);

  return NULL;
}

static int Tuple_iterNext(JSOBJ obj, JSONTypeContext *tc)
{
  PyObject *item;

  if (GET_TC(tc)->index >= GET_TC(tc)->size)
  {
    return 0;
  }

  item = PyTuple_GET_ITEM (obj, GET_TC(tc)->index);

  GET_TC(tc)->itemValue = item;
  GET_TC(tc)->index ++;
  return 1;
}

static void Tuple_iterEnd(JSOBJ obj, JSONTypeContext *tc)
{
}

static JSOBJ Tuple_iterGetValue(JSOBJ obj, JSONTypeContext *tc)
{
  return GET_TC(tc)->itemValue;
}

static char *Tuple_iterGetName(JSOBJ obj, JSONTypeContext *tc, size_t *outLen)
{
  return NULL;
}

static int Iter_iterNext(JSOBJ obj, JSONTypeContext *tc)
{
  PyObject *item;

  if (GET_TC(tc)->itemValue)
  {
    Py_DECREF(GET_TC(tc)->itemValue);
    GET_TC(tc)->itemValue = NULL;
  }

  if (GET_TC(tc)->iterator == NULL)
  {
    return 0;
  }

  item = PyIter_Next(GET_TC(tc)->iterator);

  if (item == NULL)
  {
    return 0;
  }

  GET_TC(tc)->itemValue = item;
  return 1;
}

static void Iter_iterEnd(JSOBJ obj, JSONTypeContext *tc)
{
  if (GET_TC(tc)->itemValue)
  {
    Py_DECREF(GET_TC(tc)->itemValue);
    GET_TC(tc)->itemValue = NULL;
  }

  if (GET_TC(tc)->iterator)
  {
    Py_DECREF(GET_TC(tc)->iterator);
    GET_TC(tc)->iterator = NULL;
  }
}

static JSOBJ Iter_iterGetValue(JSOBJ obj, JSONTypeContext *tc)
{
  return GET_TC(tc)->itemValue;
}

static char *Iter_iterGetName(JSOBJ obj, JSONTypeContext *tc, size_t *outLen)
{
  return NULL;
}

static void Dir_iterEnd(JSOBJ obj, JSONTypeContext *tc)
{
  if (GET_TC(tc)->itemValue)
  {
    Py_DECREF(GET_TC(tc)->itemValue);
    GET_TC(tc)->itemValue = NULL;
  }

  if (GET_TC(tc)->itemName)
  {
    Py_DECREF(GET_TC(tc)->itemName);
    GET_TC(tc)->itemName = NULL;
  }

  Py_DECREF( (PyObject *) GET_TC(tc)->attrList);
  PRINTMARK();
}

static int Dir_iterNext(JSOBJ _obj, JSONTypeContext *tc)
{
  PyObject *obj = (PyObject *) _obj;
  PyObject *itemValue = GET_TC(tc)->itemValue;
  PyObject *itemName = GET_TC(tc)->itemName;
  PyObject* attr;
  PyObject* attrName;
  char* attrStr;

  if (itemValue)
  {
    Py_DECREF(GET_TC(tc)->itemValue);
    GET_TC(tc)->itemValue = itemValue = NULL;
  }

  if (itemName)
  {
    Py_DECREF(GET_TC(tc)->itemName);
    GET_TC(tc)->itemName = itemName = NULL;
  }

  for (; GET_TC(tc)->index  < GET_TC(tc)->size; GET_TC(tc)->index ++)
  {
    attrName = PyList_GET_ITEM(GET_TC(tc)->attrList, GET_TC(tc)->index);
#if PY_MAJOR_VERSION >= 3
    attr = PyUnicode_AsUTF8String(attrName);
#else
    attr = attrName;
    Py_INCREF(attr);
#endif
    attrStr = PyString_AS_STRING(attr);

    if (attrStr[0] == '_')
    {
      PRINTMARK();
      Py_DECREF(attr);
      continue;
    }

    itemValue = PyObject_GetAttr(obj, attrName);
    if (itemValue == NULL)
    {
      PyErr_Clear();
      Py_DECREF(attr);
      PRINTMARK();
      continue;
    }

    if (PyCallable_Check(itemValue))
    {
      Py_DECREF(itemValue);
      Py_DECREF(attr);
      PRINTMARK();
      continue;
    }

    PRINTMARK();
    itemName = attr;
    break;
  }

  if (itemName == NULL)
  {
    GET_TC(tc)->index = GET_TC(tc)->size;
    GET_TC(tc)->itemValue = NULL;
    return 0;
  }

  GET_TC(tc)->itemName = itemName;
  GET_TC(tc)->itemValue = itemValue;
  GET_TC(tc)->index ++;

  PRINTMARK();
  return 1;
}

static JSOBJ Dir_iterGetValue(JSOBJ obj, JSONTypeContext *tc)
{
  PRINTMARK();
  return GET_TC(tc)->itemValue;
}

static char *Dir_iterGetName(JSOBJ obj, JSONTypeContext *tc, size_t *outLen)
{
  PRINTMARK();
  *outLen = PyString_GET_SIZE(GET_TC(tc)->itemName);
  return PyString_AS_STRING(GET_TC(tc)->itemName);
}

static int List_iterNext(JSOBJ obj, JSONTypeContext *tc)
{
  if (GET_TC(tc)->index >= GET_TC(tc)->size)
  {
    PRINTMARK();
    return 0;
  }

  GET_TC(tc)->itemValue = PyList_GET_ITEM (obj, GET_TC(tc)->index);
  GET_TC(tc)->index ++;
  return 1;
}

static void List_iterEnd(JSOBJ obj, JSONTypeContext *tc)
{
}

static JSOBJ List_iterGetValue(JSOBJ obj, JSONTypeContext *tc)
{
  return GET_TC(tc)->itemValue;
}

static char *List_iterGetName(JSOBJ obj, JSONTypeContext *tc, size_t *outLen)
{
  return NULL;
}

//=============================================================================
// Dict iteration functions
// itemName might converted to string (Python_Str). Do refCounting
// itemValue is borrowed from object (which is dict). No refCounting
//=============================================================================

static int Dict_iterNext(JSOBJ obj, JSONTypeContext *tc)
{
#if PY_MAJOR_VERSION >= 3
  PyObject* itemNameTmp;
#endif

  if (GET_TC(tc)->itemName)
  {
    Py_DECREF(GET_TC(tc)->itemName);
    GET_TC(tc)->itemName = NULL;
  }


  if (!PyDict_Next ( (PyObject *)GET_TC(tc)->dictObj, &GET_TC(tc)->index, &GET_TC(tc)->itemName, &GET_TC(tc)->itemValue))
  {
    PRINTMARK();
    return 0;
  }

  if (PyUnicode_Check(GET_TC(tc)->itemName))
  {
    GET_TC(tc)->itemName = PyUnicode_AsUTF8String (GET_TC(tc)->itemName);
  }
  else
    if (!PyString_Check(GET_TC(tc)->itemName))
    {
      GET_TC(tc)->itemName = PyObject_Str(GET_TC(tc)->itemName);
#if PY_MAJOR_VERSION >= 3
      itemNameTmp = GET_TC(tc)->itemName;
      GET_TC(tc)->itemName = PyUnicode_AsUTF8String (GET_TC(tc)->itemName);
      Py_DECREF(itemNameTmp);
#endif
    }
    else
    {
      Py_INCREF(GET_TC(tc)->itemName);
    }
    PRINTMARK();
    return 1;
}

static void Dict_iterEnd(JSOBJ obj, JSONTypeContext *tc)
{
  if (GET_TC(tc)->itemName)
  {
    Py_DECREF(GET_TC(tc)->itemName);
    GET_TC(tc)->itemName = NULL;
  }
  Py_DECREF(GET_TC(tc)->dictObj);
  PRINTMARK();
}

static JSOBJ Dict_iterGetValue(JSOBJ obj, JSONTypeContext *tc)
{
  return GET_TC(tc)->itemValue;
}

static char *Dict_iterGetName(JSOBJ obj, JSONTypeContext *tc, size_t *outLen)
{
  *outLen = PyString_GET_SIZE(GET_TC(tc)->itemName);
  return PyString_AS_STRING(GET_TC(tc)->itemName);
}

static int SortedDict_iterNext(JSOBJ obj, JSONTypeContext *tc)
{
  PyObject *items = NULL, *item = NULL, *key = NULL, *value = NULL;
  Py_ssize_t i, nitems;
#if PY_MAJOR_VERSION >= 3
  PyObject* keyTmp;
#endif

  // Upon first call, obtain a list of the keys and sort them. This follows the same logic as the
  // stanard library's _json.c sort_keys handler.
  if (GET_TC(tc)->newObj == NULL)
  {
    // Obtain the list of keys from the dictionary.
    items = PyMapping_Keys(GET_TC(tc)->dictObj);
    if (items == NULL)
    {
      goto error;
    }
    else if (!PyList_Check(items))
    {
      PyErr_SetString(PyExc_ValueError, "keys must return list");
      goto error;
    }

    // Sort the list.
    if (PyList_Sort(items) < 0)
    {
      goto error;
    }

    // Obtain the value for each key, and pack a list of (key, value) 2-tuples.
    nitems = PyList_GET_SIZE(items);
    for (i = 0; i < nitems; i++)
    {
      key = PyList_GET_ITEM(items, i);
      value = PyDict_GetItem(GET_TC(tc)->dictObj, key);

      // Subject the key to the same type restrictions and conversions as in Dict_iterGetValue.
      if (PyUnicode_Check(key))
      {
        key = PyUnicode_AsUTF8String(key);
      }
      else if (!PyString_Check(key))
      {
        key = PyObject_Str(key);
#if PY_MAJOR_VERSION >= 3
        keyTmp = key;
        key = PyUnicode_AsUTF8String(key);
        Py_DECREF(keyTmp);
#endif
      }
      else
      {
        Py_INCREF(key);
      }

      item = PyTuple_Pack(2, key, value);
      if (item == NULL)
      {
        goto error;
      }
      if (PyList_SetItem(items, i, item))
      {
        goto error;
      }
      Py_DECREF(key);
    }

    // Store the sorted list of tuples in the newObj slot.
    GET_TC(tc)->newObj = items;
    GET_TC(tc)->size = nitems;
  }

  if (GET_TC(tc)->index >= GET_TC(tc)->size)
  {
    PRINTMARK();
    return 0;
  }

  item = PyList_GET_ITEM(GET_TC(tc)->newObj, GET_TC(tc)->index);
  GET_TC(tc)->itemName = PyTuple_GET_ITEM(item, 0);
  GET_TC(tc)->itemValue = PyTuple_GET_ITEM(item, 1);
  GET_TC(tc)->index++;
  return 1;

error:
  Py_XDECREF(item);
  Py_XDECREF(key);
  Py_XDECREF(value);
  Py_XDECREF(items);
  return -1;
}

static void SortedDict_iterEnd(JSOBJ obj, JSONTypeContext *tc)
{
  GET_TC(tc)->itemName = NULL;
  GET_TC(tc)->itemValue = NULL;
  Py_DECREF(GET_TC(tc)->newObj);
  Py_DECREF(GET_TC(tc)->dictObj);
  PRINTMARK();
}

static JSOBJ SortedDict_iterGetValue(JSOBJ obj, JSONTypeContext *tc)
{
  return GET_TC(tc)->itemValue;
}

static char *SortedDict_iterGetName(JSOBJ obj, JSONTypeContext *tc, size_t *outLen)
{
  *outLen = PyString_GET_SIZE(GET_TC(tc)->itemName);
  return PyString_AS_STRING(GET_TC(tc)->itemName);
}


static void SetupDictIter(PyObject *dictObj, TypeContext *pc, JSONObjectEncoder *enc)
{
  if (enc->sortKeys) {
    pc->iterEnd = SortedDict_iterEnd;
    pc->iterNext = SortedDict_iterNext;
    pc->iterGetValue = SortedDict_iterGetValue;
    pc->iterGetName = SortedDict_iterGetName;
  }
  else {
    pc->iterEnd = Dict_iterEnd;
    pc->iterNext = Dict_iterNext;
    pc->iterGetValue = Dict_iterGetValue;
    pc->iterGetName = Dict_iterGetName;
  }
  pc->dictObj = dictObj;
  pc->index = 0;
}

static void Object_beginTypeContext (JSOBJ _obj, JSONTypeContext *tc, JSONObjectEncoder *enc)
{
  PyObject *obj, *exc, *iter;
  TypeContext *pc;
  PRINTMARK();
  if (!_obj) {
    tc->type = JT_INVALID;
    return;
  }

  obj = (PyObject*) _obj;

  tc->prv = PyObject_Malloc(sizeof(TypeContext));
  pc = (TypeContext *) tc->prv;
  if (!pc)
  {
    tc->type = JT_INVALID;
    PyErr_NoMemory();
    return;
  }
  pc->newObj = NULL;
  pc->dictObj = NULL;
  pc->itemValue = NULL;
  pc->itemName = NULL;
  pc->iterator = NULL;
  pc->attrList = NULL;
  pc->index = 0;
  pc->size = 0;
  pc->un.longValue = 0;
  pc->un.rawJSONValue = NULL;

  pc->sjCtx = (SJContext*)enc->prv;
  pc->level = enc->level;

  if (PyIter_Check(obj) && !PyUnicode_Check(obj) && !PyString_Check(obj))
  {
    PRINTMARK();
    goto ISITERABLE;
  }

  if (PyBool_Check(obj))
  {
    PRINTMARK();
    tc->type = (obj == Py_True) ? JT_TRUE : JT_FALSE;
    return;
  }
  else
  if (PyLong_Check(obj))
  {
    PRINTMARK();
    pc->PyTypeToJSON = PyLongToINT64;
    tc->type = JT_LONG;
    GET_TC(tc)->un.longValue = PyLong_AsLongLong(obj);

    exc = PyErr_Occurred();
    if (!exc)
    {
        return;
    }

    if (exc && PyErr_ExceptionMatches(PyExc_OverflowError))
    {
      PyErr_Clear();
      pc->PyTypeToJSON = PyLongToUINT64;
      tc->type = JT_ULONG;
      GET_TC(tc)->un.unsignedLongValue = PyLong_AsUnsignedLongLong(obj);

      exc = PyErr_Occurred();
      if (exc && PyErr_ExceptionMatches(PyExc_OverflowError))
      {
        PRINTMARK();
        goto INVALID;
      }
    }

    return;
  }
  else
  if (PyInt_Check(obj))
  {
    PRINTMARK();
#ifdef _LP64
    pc->PyTypeToJSON = PyIntToINT64; tc->type = JT_LONG;
#else
    pc->PyTypeToJSON = PyIntToINT32; tc->type = JT_INT;
#endif
    return;
  }
  else
  if (PyString_Check(obj) && !PyObject_HasAttrString(obj, "__json__"))
  {
    PRINTMARK();
    pc->PyTypeToJSON = PyStringToUTF8; tc->type = JT_UTF8;
    return;
  }
  else
  if (PyUnicode_Check(obj))
  {
    PRINTMARK();
    pc->PyTypeToJSON = PyUnicodeToUTF8; tc->type = JT_UTF8;
    return;
  }
  else
  if (PyFloat_Check(obj) || (type_decimal && PyObject_IsInstance(obj, type_decimal)))
  {
    PRINTMARK();
    pc->PyTypeToJSON = PyFloatToDOUBLE; tc->type = JT_DOUBLE;
    return;
  }
  else
  if (PyDateTime_Check(obj))
  {
    PRINTMARK();
    pc->PyTypeToJSON = PyDateTimeToINT64; tc->type = JT_LONG;
    return;
  }
  else
  if (PyDate_Check(obj))
  {
    PRINTMARK();
    pc->PyTypeToJSON = PyDateToINT64; tc->type = JT_LONG;
    return;
  }
  else
  if (obj == Py_None)
  {
    PRINTMARK();
    tc->type = JT_NULL;
    return;
  }

ISITERABLE:
  if (PyDict_Check(obj))
  {
    PRINTMARK();
    tc->type = JT_OBJECT;
    SetupDictIter(obj, pc, enc);
    Py_INCREF(obj);
    return;
  }
  else
  if (PyList_Check(obj))
  {
    PRINTMARK();
    tc->type = JT_ARRAY;
    pc->iterEnd = List_iterEnd;
    pc->iterNext = List_iterNext;
    pc->iterGetValue = List_iterGetValue;
    pc->iterGetName = List_iterGetName;
    GET_TC(tc)->index =  0;
    GET_TC(tc)->size = PyList_GET_SIZE( (PyObject *) obj);
    return;
  }
  else
  if (PyTuple_Check(obj))
  {
    PRINTMARK();
    tc->type = JT_ARRAY;
    pc->iterEnd = Tuple_iterEnd;
    pc->iterNext = Tuple_iterNext;
    pc->iterGetValue = Tuple_iterGetValue;
    pc->iterGetName = Tuple_iterGetName;
    GET_TC(tc)->index = 0;
    GET_TC(tc)->size = PyTuple_GET_SIZE( (PyObject *) obj);
    GET_TC(tc)->itemValue = NULL;

    return;
  }
  /*
  else
  if (PyAnySet_Check(obj))
  {
    PRINTMARK();
    tc->type = JT_ARRAY;
    pc->iterBegin = NULL;
    pc->iterEnd = Iter_iterEnd;
    pc->iterNext = Iter_iterNext;
    pc->iterGetValue = Iter_iterGetValue;
    pc->iterGetName = Iter_iterGetName;
    return;
  }
  */

  if (PyObject_HasAttrString(obj, "toDict"))
  {
    PyObject* toDictFunc = PyObject_GetAttrString(obj, "toDict");
    PyObject* tuple = PyTuple_New(0);
    PyObject* toDictResult = PyObject_Call(toDictFunc, tuple, NULL);
    Py_DECREF(tuple);
    Py_DECREF(toDictFunc);

    if (toDictResult == NULL)
    {
      goto INVALID;
    }

    if (!PyDict_Check(toDictResult))
    {
      Py_DECREF(toDictResult);
      tc->type = JT_NULL;
      return;
    }

    PRINTMARK();
    tc->type = JT_OBJECT;
    SetupDictIter(toDictResult, pc, enc);
    return;
  }
  else
  if (PyObject_HasAttrString(obj, "__json__"))
  {
    PyObject* toJSONFunc = PyObject_GetAttrString(obj, "__json__");
    PyObject* tuple = PyTuple_New(0);
    PyObject* toJSONResult = PyObject_Call(toJSONFunc, tuple, NULL);
    Py_DECREF(tuple);
    Py_DECREF(toJSONFunc);

    if (toJSONResult == NULL)
    {
      goto INVALID;
    }

    if (PyErr_Occurred())
    {
      Py_DECREF(toJSONResult);
      goto INVALID;
    }

    if (!PyString_Check(toJSONResult) && !PyUnicode_Check(toJSONResult))
    {
      Py_DECREF(toJSONResult);
      PyErr_Format (PyExc_TypeError, "expected string");
      goto INVALID;
    }

    PRINTMARK();
    pc->PyTypeToJSON = PyRawJSONToUTF8;
    tc->type = JT_RAW;
    GET_TC(tc)->un.rawJSONValue = toJSONResult;
    return;
  }

  PRINTMARK();
  PyErr_Clear();

  iter = PyObject_GetIter(obj);

  if (iter != NULL)
  {
    PRINTMARK();
    tc->type = JT_ARRAY;
    pc->iterator = iter;
    pc->iterEnd = Iter_iterEnd;
    pc->iterNext = Iter_iterNext;
    pc->iterGetValue = Iter_iterGetValue;
    pc->iterGetName = Iter_iterGetName;
    return;
  }

  PRINTMARK();
  PyErr_Clear();

  PRINTMARK();
  tc->type = JT_OBJECT;
  GET_TC(tc)->attrList = PyObject_Dir(obj);
  
  if (GET_TC(tc)->attrList == NULL)
  {
    PyErr_Clear();
    goto INVALID;
  }

  GET_TC(tc)->index = 0;
  GET_TC(tc)->size = PyList_GET_SIZE(GET_TC(tc)->attrList);
  PRINTMARK();
  
  pc->iterEnd = Dir_iterEnd;
  pc->iterNext = Dir_iterNext;
  pc->iterGetValue = Dir_iterGetValue;
  pc->iterGetName = Dir_iterGetName;
  return;

INVALID:
  PRINTMARK();
  tc->type = JT_INVALID;
  PyObject_Free(tc->prv);
  tc->prv = NULL;
  return;
}

static void Object_endTypeContext(JSOBJ obj, JSONTypeContext *tc)
{
  Py_XDECREF(GET_TC(tc)->newObj);

  PyObject_Free(tc->prv);
  tc->prv = NULL;
}

static const char *Object_getStringValue(JSOBJ obj, JSONTypeContext *tc, size_t *_outLen)
{
  return GET_TC(tc)->PyTypeToJSON (obj, tc, NULL, _outLen);
}

static JSINT64 Object_getLongValue(JSOBJ obj, JSONTypeContext *tc)
{
  JSINT64 ret;
  GET_TC(tc)->PyTypeToJSON (obj, tc, &ret, NULL);
  return ret;
}

static JSUINT64 Object_getUnsignedLongValue(JSOBJ obj, JSONTypeContext *tc)
{
  JSUINT64 ret;
  GET_TC(tc)->PyTypeToJSON (obj, tc, &ret, NULL);
  return ret;
}

static JSINT32 Object_getIntValue(JSOBJ obj, JSONTypeContext *tc)
{
  JSINT32 ret;
  GET_TC(tc)->PyTypeToJSON (obj, tc, &ret, NULL);
  return ret;
}

static double Object_getDoubleValue(JSOBJ obj, JSONTypeContext *tc)
{
  double ret;
  GET_TC(tc)->PyTypeToJSON (obj, tc, &ret, NULL);
  return ret;
}

static void Object_releaseObject(JSOBJ _obj)
{
  Py_DECREF( (PyObject *) _obj);
}

static int Object_iterNext(JSOBJ obj, JSONTypeContext *tc)
{
  return GET_TC(tc)->iterNext(obj, tc);
}

static void Object_iterEnd(JSOBJ obj, JSONTypeContext *tc)
{
  GET_TC(tc)->iterEnd(obj, tc);
}

static JSOBJ Object_iterGetValue(JSOBJ obj, JSONTypeContext *tc)
{
  TypeContext *ctx = GET_TC(tc);
  JSOBJ res;

  if (ctx->level == 0 && strcmp(ctx->sjCtx->name, PyString_AS_STRING(ctx->itemName)) == 0) {
    Py_ssize_t len = 0;
    if (PyList_Check(ctx->itemValue)) {
      len = PyList_Size(ctx->itemValue);
    } else if (PyArray_Check(ctx->itemValue)) {
      len = PyArray_DIM((PyArrayObject *)ctx->itemValue, 0);
    }
    ctx->sjCtx->len = len;
    ctx->sjCtx->obj = ctx->itemValue;
    res = PyLong_FromUnsignedLongLong(len);
    Py_DECREF(res);
  } else res = ctx->iterGetValue(obj, tc);
  return res;
}

static char *Object_iterGetName(JSOBJ obj, JSONTypeContext *tc, size_t *outLen)
{
  return GET_TC(tc)->iterGetName(obj, tc, outLen);
}

static PyObject *getPointValue(JSOBJ obj, int idx, int i, struct __SJTSObjectEncoder *enc)
{
  PyObject *res = NULL;
  if (enc->is_numpy) {
    res = PyArray_GETITEM(obj, PyArray_GETPTR2(obj, idx, i));
  } else {
    PyObject *pnt = PyList_GetItem(obj, idx);

    if (PyList_Check(pnt)) {
      res = PyList_GetItem(pnt, i);
    } else {
      res = PyTuple_GetItem(pnt, i);
    }
  }
  return res;
}

static double getPointValueDouble(JSOBJ obj, int idx, int i, struct __SJTSObjectEncoder *enc)
{
  PyObject *p = getPointValue(obj, idx, i, enc);
  double res;

  if (p == Py_None) return NAN;

  res = PyFloat_AsDouble(p);

  if (enc->is_numpy) Py_XDECREF(p);
  return res;
}

static JSINT64 getPointValueLongLong(JSOBJ obj, int idx, int i, struct __SJTSObjectEncoder *enc)
{
  PyObject *p = getPointValue(obj, idx, i, enc);
  JSINT64 res = PyLong_AsLongLong(PyLong_FromDouble(PyFloat_AsDouble(p)));
  if (enc->is_numpy) Py_XDECREF(p);
  return res;
}

static JSINT64 getDate(JSOBJ obj, int idx, struct __SJTSObjectEncoder *enc)
{
  if (enc->is_numpy) {
      return *(JSINT64 *)PyArray_GETPTR1(obj, idx);
  }
  return getPointValueLongLong(obj, idx, 0, enc);
}

static double getValue(JSOBJ obj, int idx, struct __SJTSObjectEncoder *enc)
{
  int extra = 0;
  if (enc->is_numpy) {
      char *ptr = (char *)PyArray_GETPTR1(obj, idx);
      if (enc->includes_job) {
        *(JSUINT32*)(enc->buffer + enc->extraOffset) = *(JSUINT32*)(ptr + 16);
        extra = 4;
	enc->extraOffset += 4;
      }
      if (enc->includes_timestamp) {
        *(JSUINT64*)(enc->buffer + enc->extraOffset) = *(JSUINT64*)(ptr + 16 + extra);
	enc->extraOffset += 8;
      }
      return *(double *)(ptr + 8);
  }
  if (enc->includes_job) {
	*(JSUINT32*)(enc->buffer + enc->extraOffset) = (JSUINT32)getPointValueLongLong(obj, idx, 1 + ++extra, enc);
	enc->extraOffset += 4;
  }
  if (enc->includes_timestamp) {
	*(JSINT64*)(enc->buffer + enc->extraOffset) = getPointValueLongLong(obj, idx, 1 + ++extra, enc);
	enc->extraOffset += 8;
  }
  return getPointValueDouble(obj, idx, 1, enc);
}

static void init_numpy()
{
  import_array();
}

PyObject* objToJSON(PyObject* self, PyObject *args, PyObject *kwargs)
{
  static char *kwlist[] = { "obj", "includes_job", "includes_timestamp", NULL };

  size_t rootSz;
  char *extraRoot;
  char buffer[65536];
  int new_buffer;
  int nErr = 0;
  int iErr;
  int i;
  PyObject *success;
  PyObject *newobj = NULL;
  PyObject *oinput = NULL;
  PyObject *ojob = NULL;
  PyObject *otimestamp = NULL;

  SJContext sjCtx;

  SJTSObjectEncoder encoder =
  {
    {
      Object_beginTypeContext,
      Object_endTypeContext,
      Object_getStringValue,
      Object_getLongValue,
      Object_getUnsignedLongValue,
      Object_getIntValue,
      Object_getDoubleValue,
      Object_iterNext,
      Object_iterEnd,
      Object_iterGetValue,
      Object_iterGetName,
      Object_releaseObject,
      PyObject_Malloc,
      PyObject_Realloc,
      PyObject_Free,
      -1, //recursionMax
      10,  // default double precision setting
      1, //forceAscii
      0, //encodeHTMLChars
      1, //escapeForwardSlashes
      1, //sortKeys
      0, //indent
      NULL, //prv
    },
    getDate,
    getValue,
    NULL,
    0
  };

  init_numpy();

  encoder.includes_job = encoder.includes_timestamp = 0;
  encoder.ujson.prv = &sjCtx;

  PRINTMARK();

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|OO", kwlist, &oinput, &ojob, &otimestamp))
  {
    return NULL;
  }

  if (!PyDict_Check(oinput)) return SJ_ERR("input should be an object");
  success = PyDict_GetItemString(oinput, "success");
  if (success && !PyBool_Check(success)) return SJ_ERR("success key should be a boolean");
  if (PyDict_GetItemString(oinput, "sjts")) return SJ_ERR("sjts key is not allowed");

  encoder.includes_job = encoder.includes_timestamp = 0;
  encoder.nItems = 0;
  if (ojob != NULL && PyObject_IsTrue(ojob))
  {
    encoder.includes_job = 1;
  }
  if (otimestamp != NULL && PyObject_IsTrue(otimestamp))
  {
    encoder.includes_timestamp = 1;
  }

  PRINTMARK();
  sjCtx.name = SJ_RESPONSES_KEY;
  sjCtx.obj = NULL;
  encoder.rootBuffer = JSON_EncodeObject (oinput, &encoder.ujson, buffer, sizeof(buffer) - 100);
  new_buffer = buffer != encoder.rootBuffer;
  PRINTMARK();

  if (PyErr_Occurred())
  {
    return NULL;
  }

  if (encoder.ujson.errorMsg)
  {
    if (new_buffer)
    {
      encoder.ujson.free(encoder.rootBuffer);
    }

    PyErr_Format (PyExc_OverflowError, "%s", encoder.ujson.errorMsg);
    return NULL;
  }

  extraRoot = encoder.rootBuffer + strlen(encoder.rootBuffer) - 1;
  if ((encoder.includes_job || encoder.includes_timestamp) && *extraRoot == '}') {
    if (extraRoot[-1] != '{') *extraRoot++ = ',';
    sprintf(extraRoot, "\"sjts\":{\"includes_job\":%s,\"includes_timestamp\":%s}}",
            encoder.includes_job ? "true" : "false", encoder.includes_timestamp ? "true" : "false");
  }

  rootSz = (encoder.includes_job || encoder.includes_timestamp) ? 1 : 0;

  if (sjCtx.obj)
  {
    PyObject *arr = sjCtx.obj;
    if (success == Py_False) nErr = 1;
    if (!PyList_Check(arr)) nErr = 2;
    if (!nErr)
    {
      int i;
      encoder.nItems = sjCtx.len;
      sjCtx.name = "points";
      encoder.items = (SJItem*)PyObject_Malloc(sizeof(SJItem) * encoder.nItems);
      if (encoder.items) {
        for (i = 0; i < encoder.nItems; i++)
        {
          PyObject *item = PyList_GetItem(arr, i);
          sjCtx.obj = NULL;
          encoder.items[i].buffer = JSON_EncodeObject(item, &encoder.ujson, NULL, 0);
          encoder.items[i].sz = strlen(encoder.items[i].buffer);
          encoder.items[i].len = sjCtx.len;
          encoder.items[i].obj = (JSOBJ *)sjCtx.obj;
          encoder.items[i].is_numpy = 0;
          rootSz += ((encoder.includes_job ? 4 : 0) + (encoder.includes_timestamp ? 8 : 0)) * sjCtx.len;
          if (sjCtx.obj) {
            if (PyArray_Check(sjCtx.obj)) {
              encoder.items[i].is_numpy = 1;
            } else if (!PyList_Check(sjCtx.obj)) {
              iErr = i;
              nErr = 3;
              break;
            }
          }
        }
      } else {
        nErr = 5;
      }
    }
  } else if (success == Py_True) nErr = 4;


  rootSz += strlen(encoder.rootBuffer);

  PRINTMARK();

  if (!nErr) {
    ProcessItems(&encoder, rootSz);
    if (encoder.buffer) {
      newobj = PyBytes_FromStringAndSize(encoder.buffer, encoder.offset);
      PyObject_Free(encoder.buffer);
    } else {
      nErr = 5;
    }
  }

  PRINTMARK();

  if (new_buffer) encoder.ujson.free(encoder.rootBuffer);
  for (i = 0; i < encoder.nItems; i++)
  {
    if (encoder.items) encoder.ujson.free(encoder.items[i].buffer);
    if (i == iErr) break;
  }
  encoder.ujson.free(encoder.items);
  switch(nErr)
  {
    case 1: return SJ_ERR1("%s present but success is False", SJ_RESPONSES_KEY);
    case 2: return SJ_ERR1("%s should be a list", SJ_RESPONSES_KEY);
    case 3: return SJ_ERR("points should be a list");
    case 4: return SJ_ERR1("%s missing but success is True", SJ_RESPONSES_KEY);
    case 5: return SJ_ERR("not enough memory");
  }
  return newobj;
}

PyObject* objToJSONFile(PyObject* self, PyObject *args, PyObject *kwargs)
{
  PyObject *data;
  PyObject *file;
  PyObject *string;
  PyObject *write;
  PyObject *argtuple;

  PRINTMARK();

  if (!PyArg_ParseTuple (args, "OO", &data, &file))
  {
    return NULL;
  }

  if (!PyObject_HasAttrString (file, "write"))
  {
    PyErr_Format (PyExc_TypeError, "expected file");
    return NULL;
  }

  write = PyObject_GetAttrString (file, "write");

  if (!PyCallable_Check (write))
  {
    Py_XDECREF(write);
    PyErr_Format (PyExc_TypeError, "expected file");
    return NULL;
  }

  argtuple = PyTuple_Pack(1, data);

  string = objToJSON (self, argtuple, kwargs);

  if (string == NULL)
  {
    Py_XDECREF(write);
    Py_XDECREF(argtuple);
    return NULL;
  }

  Py_XDECREF(argtuple);

  argtuple = PyTuple_Pack (1, string);
  if (argtuple == NULL)
  {
    Py_XDECREF(write);
    return NULL;
  }
  if (PyObject_CallObject (write, argtuple) == NULL)
  {
    Py_XDECREF(write);
    Py_XDECREF(argtuple);
    return NULL;
  }

  Py_XDECREF(write);
  Py_DECREF(argtuple);
  Py_XDECREF(string);

  PRINTMARK();

  Py_RETURN_NONE;
}

PyObject* SeriesToSJTS(PyObject* self, PyObject *args, PyObject *kwargs)
{
  static char *kwlist[] = { "obj", "includes_job", "includes_timestamp", NULL };
  PyObject *newobj = NULL;
  PyObject *ojob = NULL;
  PyObject *otimestamp = NULL;
  SJTSObjectEncoder encoder =
  {
    {
      Object_beginTypeContext,
      Object_endTypeContext,
      Object_getStringValue,
      Object_getLongValue,
      Object_getUnsignedLongValue,
      Object_getIntValue,
      Object_getDoubleValue,
      Object_iterNext,
      Object_iterEnd,
      Object_iterGetValue,
      Object_iterGetName,
      Object_releaseObject,
      PyObject_Malloc,
      PyObject_Realloc,
      PyObject_Free,
      -1, //recursionMax
      10,  // default double precision setting
      1, //forceAscii
      0, //encodeHTMLChars
      1, //escapeForwardSlashes
      1, //sortKeys
      0, //indent
      NULL, //prv
    },
    getDate,
    getValue,
    NULL,
    0
  };
  SJItem item;
  SJContext sjCtx;
  PyObject *oinput = NULL;
  size_t rootSz;
  char rootBuffer[128];

  init_numpy();

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|OO", kwlist, &oinput, &ojob, &otimestamp)) {
    return NULL;
  }

  if (!PyDict_Check(oinput)) return SJ_ERR("input should be an object");
  if (PyDict_GetItemString(oinput, "sjts")) return SJ_ERR("sjts key is not allowed");

  encoder.includes_job = encoder.includes_timestamp = 0;
  if (ojob != NULL && PyObject_IsTrue(ojob))
  {
    encoder.includes_job = 1;
  }
  if (otimestamp != NULL && PyObject_IsTrue(otimestamp))
  {
    encoder.includes_timestamp = 1;
  }
  encoder.rootBuffer = rootBuffer;
  sprintf(rootBuffer, "{\"success\":true,\"sjts\":{\"single\":true,\"includes_job\":%s,\"includes_timestamp\":%s},\"%s\":1}",
          encoder.includes_job ? "true" : "false", encoder.includes_timestamp ? "true" : "false", SJ_RESPONSES_KEY);
  rootSz = strlen(rootBuffer);
  encoder.nItems = 1;
  encoder.items = &item;
  encoder.ujson.prv = &sjCtx;
  sjCtx.name = "points";
  sjCtx.obj = NULL;
  item.buffer = JSON_EncodeObject(oinput, &encoder.ujson, NULL, 0);
  item.sz = strlen(item.buffer);
  item.len = sjCtx.len;
  item.is_numpy = 0;
  item.obj = (JSOBJ *)sjCtx.obj;
  if (sjCtx.obj)
  {
    if (PyArray_Check(sjCtx.obj)) {
      item.is_numpy = 1;
    } else if (!PyList_Check(sjCtx.obj))
      return SJ_ERR("points should be a list or a numpy array");
  }
  if (encoder.includes_job || encoder.includes_timestamp) {
    rootSz += 1 + ((encoder.includes_job ? 4 : 0) + (encoder.includes_timestamp ? 8 : 0)) * item.len;
  }
  ProcessItems(&encoder, rootSz);
  newobj = PyBytes_FromStringAndSize(encoder.buffer, encoder.offset);
  PyObject_Free(encoder.buffer);
  return newobj;
}

