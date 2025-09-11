
#include "sjts.h"

static void ProcessPoints(SJTSObjectEncoder *enc, size_t  idx, size_t start, size_t  len)
{
  int checkSeq = 1;
  double *points;
  JSINT32 diff;
  size_t cnt = 1;
  JSINT64 firstDate;
  char *offsStart;
  char *buf;
  int i;
  JSOBJ pnts = enc->items[idx].obj;

  enc->is_numpy = enc->items[idx].is_numpy;
  if (len <= 0) return;

  firstDate = enc->getDate(pnts, start, enc);

  if (enc->size - enc->offset < len * 8 + 20 + enc->items[idx].nextSz) {
    enc->size = enc->size * 2;
    enc->buffer = enc->ujson.realloc(enc->buffer, enc->size);
    if (!enc->buffer) return;
  }

  offsStart = enc->buffer + enc->offset;
  buf = offsStart + 8;

  *(JSINT64*)(buf) = firstDate;
  buf += 8;

  if (len > 1)
  {
    JSINT64 secondDate = enc->getDate(pnts, start + 1, enc);
    diff = (JSINT32) (secondDate - firstDate);
    if (firstDate + diff == secondDate) {
      JSINT64 lastDate = enc->getDate(pnts,start + len - 1, enc);
      *(JSINT32*)buf = diff;
      buf += 4;
      checkSeq = checkSeq || (lastDate != firstDate + diff * (len - 1));
      cnt = len;
    }
  }
  points = (double*)buf;
  for (i = 0; i < cnt; i++) {
    if (checkSeq && i > 1) {
      JSINT64 date = enc->getDate(pnts, start + i, enc);
      if (date != firstDate + diff * i) {
        cnt = i;
        break;
      }
    }
    points[i] = enc->getValue(pnts, start + i, enc);
    buf += 8;
  }

  *(JSUINT64*)offsStart = (buf - offsStart) - 8;
  enc->offset += (buf - offsStart);
  if (cnt < len) ProcessPoints(enc, idx, start + cnt, len - cnt);
}

static JSUINT64 calcItemsSize(SJTSObjectEncoder *enc)
{
  JSUINT64 sz = 0;
  int i;
  for (i = 0; i < enc->nItems; i++) {
    int j;
    JSUINT64 len = enc->items[i].len;
    sz += 4 + enc->items[i].sz;
    enc->items[i].nextSz = 0;
    for (j = i - 1; j >= 0; j--) enc->items[j].nextSz += 4 + enc->items[i].sz;
    if (enc->items[i].obj && len) {
      enc->items[i].pntSz = 8 + (len > 1 ? (len * 8 + 12) : 16);
      sz += enc->items[i].pntSz;
    }
  }
  return sz;
}

void ProcessItems(SJTSObjectEncoder *enc, size_t rootSz)
{
  int i;
  enc->size = 8 + rootSz + calcItemsSize(enc);
  enc->offset = 8 + rootSz;
  enc->buffer = (char*)enc->ujson.malloc(enc->size);
  if (!enc->buffer) return;

  (((JSUINT32 *)enc->buffer)[0]) = SJTS_MAGIC;
  (((JSUINT32 *)enc->buffer)[1]) = rootSz;
  if (enc->nItems) strcpy(enc->buffer + 8, enc->rootBuffer);
  else memcpy(enc->buffer + 8, enc->rootBuffer, rootSz);
  enc->extraOffset = 8 + strlen(enc->rootBuffer) + 1;
  for (i = 0; i < enc->nItems; i++) {
    size_t sz = enc->items[i].sz;
    (((JSUINT32 *)(enc->buffer + enc->offset))[0]) = sz;
    memcpy(enc->buffer + enc->offset + 4, enc->items[i].buffer, sz);
    enc->offset += sz + 4;
    if (enc->items[i].obj) {
      ProcessPoints(enc, i, 0, enc->items[i].len);
      if (!enc->buffer) return;
    }
  }
}

