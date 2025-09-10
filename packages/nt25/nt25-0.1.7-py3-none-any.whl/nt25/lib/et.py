import io
import os
import time
import json
import struct
import argparse

from PIL import Image as pi

from datetime import UTC, datetime, timedelta, timezone
from exif import Image, DATETIME_STR_FORMAT

VERSION = "0.1.3"
COMMENT_SEGMENT = b"\xff\xfe"
EPOCH = datetime.fromtimestamp(0, UTC)


def dms2dec(dms: tuple):
  d, m, s = dms
  return d + m/60 + s/3600


def dtFormatter(str):
  return datetime.strptime(str, DATETIME_STR_FORMAT)


def dt2str(dt):
  return None if dt is None else dt.strftime(DATETIME_STR_FORMAT)


def gpsDt2Dt(date, time, offset=8):
  d = dtFormatter(f"{date} {int(time[0])}:{int(time[1])}:{int(time[2])}")
  utc = d.replace(tzinfo=timezone.utc)
  return utc.astimezone(timezone(timedelta(hours=offset)))


def optimizeFile(file, q=80):
  less = False
  ofile = file + '.jpg'
  pi.open(file).save(ofile, quality=q, optimize=True, progression=True)

  if os.path.getsize(ofile) < os.path.getsize(file) * 0.9:
    less = True
    transplant(file, ofile)
    os.replace(ofile, file)
  else:
    os.remove(ofile)

  return less


def tryGet(img, key, default):
  value = default

  try:
    value = img[key]
  except Exception:
    pass

  return value


def dumpExif(file, optimize=False):
  result = {}

  if optimize:
    optimizeFile(file)

  with open(file, 'rb') as f:
    img = Image(f)
    for key in img.get_all():
      try:
        result[key] = str(img[key])
      except Exception:
        pass

  return result


def parseExif(file, optimize=False):
  if optimize:
    optimizeFile(file)

  with open(file, 'rb') as f:
    try:
      img = Image(f)
    except Exception:
      return {}

  width = tryGet(img, 'pixel_x_dimension', -1)
  height = tryGet(img, 'pixel_y_dimension', -1)

  if width < 0:
    width = tryGet(img, 'image_width', -1)
    height = tryGet(img, 'image_height', -1)

  create = tryGet(img, 'datetime_original', None)
  modify = tryGet(img, 'datetime', None)

  createDt = None if create is None else dtFormatter(create)
  modifyDt = None if modify is None else dtFormatter(modify)

  latitude = tryGet(img, 'gps_latitude', None)
  latitude = None if latitude is None else dms2dec(latitude)

  latRef = tryGet(img, "gps_latitude_ref", default='N')
  if latRef != 'N' and latitude:
    latitude = -latitude

  longitude = tryGet(img, 'gps_longitude', None)
  longitude = None if longitude is None else dms2dec(longitude)

  longRef = tryGet(img, "gps_longitude_ref", default='E')
  if longRef != 'E' and longitude:
    longitude = -longitude

  gpsDatetime = None
  gd = tryGet(img, 'gps_datestamp', None)
  gt = tryGet(img, 'gps_timestamp', None)

  if gd and gt:
    offset = int(time.localtime().tm_gmtoff / 3600)
    gpsDatetime = gpsDt2Dt(gd, gt, offset=offset)

  ts = -1 if createDt is None else int(createDt.timestamp())
  mTs = -1 if modifyDt is None else int(modifyDt.timestamp())
  gpsTs = -1 if gpsDatetime is None else int(gpsDatetime.timestamp())

  if ts > 0:
    offset = max(mTs, gpsTs) - ts
    offsetDelta = str(datetime.fromtimestamp(offset, UTC) - EPOCH)
  else:
    offset = None
    offsetDelta = None

  return {
      "width": width,
      "height": height,
      "latitude": latitude,
      "longitude": longitude,
      "datetime.create": dt2str(createDt),
      "datetime.modify": dt2str(modifyDt),
      "datetime.gps": dt2str(gpsDatetime),
      "ts": ts,
      "offset": offset,
      "offset.delta": offsetDelta,
  }


class InvalidImageDataError(ValueError):
  pass


def genSegments(data):
  if data[0:2] != b"\xff\xd8":
    raise InvalidImageDataError("Given data isn't JPEG.")

  head = 2
  segments = [b"\xff\xd8"]

  while 1:
    if data[head: head + 2] == b"\xff\xda":
      segments.append(data[head:])
      break

    else:
      length = struct.unpack(">H", data[head + 2: head + 4])[0]
      endPoint = head + length + 2
      seg = data[head: endPoint]
      segments.append(seg)
      head = endPoint

    if (head >= len(data)):
      raise InvalidImageDataError("Wrong JPEG data.")

  return segments


def setComment(segments, comment: str, enc='utf-8'):
  contains = False
  cb = comment.encode(enc)
  length = len(cb) + 2

  cbSeg = COMMENT_SEGMENT + length.to_bytes(2, byteorder='big') + cb

  for i in range(len(segments)):
    if segments[i][0:2] == COMMENT_SEGMENT:
      contains = True
      segments[i] = cbSeg

  if not contains:
    length = len(segments)
    segments.insert(1 if length == 2 else length - 2, cbSeg)

  return segments


def getComment(segments, enc='utf-8'):
  for seg in segments:
    if seg[0:2] == COMMENT_SEGMENT:
      return seg[4:].decode(encoding=enc, errors='replace')

  return None


def getExif(segments):
  """Returns Exif from JPEG meta data list
  """
  for seg in segments:
    if seg[0:2] == b"\xff\xe1" and seg[4:10] == b"Exif\x00\x00":
      return seg

  return b""


def mergeSegments(segments, exif=b""):
  """Merges Exif with APP0 and APP1 manipulations.
  """
  if segments[1][0:2] == b"\xff\xe0" and \
     segments[2][0:2] == b"\xff\xe1" and \
     segments[2][4:10] == b"Exif\x00\x00":
    if exif:
      segments[2] = exif
      segments.pop(1)
    elif exif is None:
      segments.pop(2)
    else:
      segments.pop(1)

  elif segments[1][0:2] == b"\xff\xe0":
    if exif:
      segments[1] = exif

  elif (segments[1][0:2] == b"\xff\xe1" and
        segments[1][4:10] == b"Exif\x00\x00"):

    if exif:
      segments[1] = exif
    elif exif is None:
      segments.pop(1)

  else:
    if exif:
      segments.insert(1, exif)

  return b"".join(segments)


def removeExif(src, optimize=False):
  if optimize:
    optimizeFile(src)

  with open(src, 'rb') as f:
    src_data = f.read()

  segments = genSegments(src_data)
  segments = list(filter(lambda seg: not (seg[0:2] == b"\xff\xe1"
                                          and seg[4:10] == b"Exif\x00\x00"),
                         segments))

  segments = setComment(segments, "nt25.et")
  new_data = b"".join(segments)

  with open(src, "wb+") as f:
    f.write(new_data)


def transplant(exif_src, image, optimize=False):
  if optimize:
    optimizeFile(image)

  if exif_src[0:2] == b"\xff\xd8":
    src_data = exif_src
  else:
    with open(exif_src, 'rb') as f:
      src_data = f.read()

  segments = genSegments(src_data)
  exif = getExif(segments)

  with open(image, 'rb') as f:
    image_data = f.read()

  segments = genSegments(image_data)
  segments = setComment(segments, "nt25.et")
  new_data = mergeSegments(segments, exif)

  with open(image, "wb+") as f:
    f.write(new_data)


def main():
  parser = argparse.ArgumentParser(description="EXIF tool")
  parser.add_argument('-v', '--version', action='store_true',
                      help='echo version')
  parser.add_argument('-o', '--optimize', action='store_true',
                      help='optimize jpg file, work with -r, -d, -c, -f')
  parser.add_argument('-r', '--rm', action='store_true',
                      help='remove meta, use: -r -f FILE')
  parser.add_argument('-d', '--dump', action='store_true',
                      help='dump meta, use: -d -f FILE')
  parser.add_argument('-c', '--copy', type=str,
                      help='copy meta, use: -c SRC -f DST')
  parser.add_argument('-f', '--file', type=str, help='image file')

  args = parser.parse_args()

  if args.version:
    print(f"et: {VERSION}")
    return

  if args.file is None:
    print("usage: et [-h] [-v] [-o] [-f FILE] [-d -f FILE]\n"
          "\t\t[-r -f FILE] [-c SRC -f DST]")
    return

  opt = True if args.optimize else False

  if args.dump:
    r = dumpExif(args.file, optimize=opt)
  elif args.rm:
    r = removeExif(args.file, optimize=opt)
  elif args.copy:
    r = transplant(args.copy, args.file, optimize=opt)
  else:
    r = parseExif(args.file, optimize=opt)

  if r is not None:
    print(json.dumps(r, indent=2, sort_keys=False))


if __name__ == "__main__":
  main()
