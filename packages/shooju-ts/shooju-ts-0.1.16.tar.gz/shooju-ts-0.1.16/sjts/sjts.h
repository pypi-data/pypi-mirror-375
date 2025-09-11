
#define SJTS_MAGIC 0x53544a53

#ifndef SJTS_TEMPLATE_ONLY

#include "ultrajson.h"

#ifdef __cplusplus
extern "C" {
#endif


typedef struct __SJTSObjectDecoder {
  JSONObjectDecoder ujson;
  int (*getCount)(struct __SJTSObjectDecoder *dec, int level);
  void (*setItem)(struct __SJTSObjectDecoder *dec, int idx);
  void (*setPoint)(struct __SJTSObjectDecoder *dec, int idx, JSINT64 date, double value);
  int (*checkRoot)(struct __SJTSObjectDecoder *dec, char *root);
  JSOBJ obj[2];
  JSOBJ arr[2];
  JSOBJ prv;
  int includes_job;
  int includes_timestamp;
  char *extraBuffer;
  int use_numpy;
} SJTSObjectDecoder;

typedef struct __SJItem
{
  char *buffer;
  size_t sz;
  size_t nextSz;
  size_t len;
  int is_numpy;
  JSUINT64 pntSz;
  JSOBJ *obj;
} SJItem;

typedef struct __SJTSObjectEncoder {
  JSONObjectEncoder ujson;
  JSINT64 (*getDate)(JSOBJ obj, int idx, struct __SJTSObjectEncoder *enc);
  double (*getValue)(JSOBJ obj, int idx, struct __SJTSObjectEncoder *enc);
  SJItem *items;
  size_t nItems;
  char *rootBuffer;
  char *buffer;
  size_t size;
  size_t offset;
  int includes_job;
  int includes_timestamp;
  int is_numpy;
  size_t extraOffset;
} SJTSObjectEncoder;

JSOBJ SJTS_DecodeObject(SJTSObjectDecoder *dec, const char *buffer, size_t cbBuffer);
JSOBJ SJTS_DecodeObjectEx(SJTSObjectDecoder *dec, const char *buffer, size_t cbBuffer, int flags);
void ProcessItems(SJTSObjectEncoder *enc, size_t rootSize);

#ifdef __cplusplus
}
#endif

#endif