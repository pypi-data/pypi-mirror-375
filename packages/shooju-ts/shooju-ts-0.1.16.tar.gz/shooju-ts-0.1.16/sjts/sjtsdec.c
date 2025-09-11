
#include "sjts.h"

#ifndef SJTS_TEMPLATE_ONLY

#define GET_UINT32(offs) *(JSUINT32*)(json_str + (offs))
#define GET_INT32(offs) *(JSINT32*)(json_str + (offs))
#define GET_INT64(offs) *(JSINT64*)(json_str + (offs))
#define GET_DOUBLE(offs, offs2) ((double*)(json_str + (offs)))[offs2]
#define SET_POINT dec->setPoint(dec, idx++, date, val)
#define GET_COUNT(idx) dec->getCount(dec, idx)

JSOBJ SJTS_DecodeObject(SJTSObjectDecoder *dec, const char *json_str, size_t json_size)
{
  return SJTS_DecodeObjectEx(dec, json_str, json_size, 0);
}

JSOBJ SJTS_DecodeObjectEx(SJTSObjectDecoder *dec, const char *json_str, size_t json_size, int flags)
{
#endif
   JSUINT64 json_offs = 0;

  if (json_size > 8) {
    JSUINT32 magic = GET_UINT32(0);
    if (magic == SJTS_MAGIC) {
      json_offs = 8;
      json_size = GET_UINT32(4);
    }
  }
#ifndef SJTS_TEMPLATE_ONLY
  {
	  size_t real_json_size = 0;
	  while (real_json_size < json_size && json_str[json_offs + real_json_size]) real_json_size++;
	  dec->obj[0] = JSON_DecodeObject(&dec->ujson, json_str + json_offs, real_json_size);
  }
  if (flags == 1 && dec->checkRoot(dec, json_str + json_offs)) return dec->obj[0];
  if (!dec->ujson.errorStr && json_offs) {
#else
  if (PARSE_JSON) {
#endif
	  int i, len = GET_COUNT(0);
	  for (i = 0; i < len; i++) {
      json_offs += json_size;
      json_size = GET_UINT32(json_offs);
      json_offs += 4;
#ifndef SJTS_TEMPLATE_ONLY
      dec->obj[1] = JSON_DecodeObject(&dec->ujson, json_str + json_offs, json_size);
	  dec->setItem(dec, i);
	  if (!dec->ujson.errorStr) {
#else
	  if (PARSE_JSON) {
#endif
		int len = GET_COUNT(1);
		int idx = 0;
		while (len > 0) {
			JSINT64 date = GET_INT64((json_offs += json_size) + 8);
			JSINT32 diff = GET_INT32(json_offs + 16);
			JSINT64 cnt = (GET_INT64(json_offs) - 8) / 8;
			int i;
			JSINT64 points_offs = json_offs + (cnt > 1 ? 20 : 16);
			for (i = 0; i < cnt; i++) {
				double val = GET_DOUBLE(points_offs, i);
				SET_POINT;
				date += diff;
			}
			len -= cnt;
			json_size = 8 + GET_INT64(json_offs);
		}
	  }
    }
  }
#ifndef SJTS_TEMPLATE_ONLY
  return dec->obj[0];
}
#endif
