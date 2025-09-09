import io
import time
import json
import struct
import argparse

from datetime import UTC, datetime, timedelta, timezone
from exif import Image, DATETIME_STR_FORMAT

VERSION = "0.1.2"
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


def tryGet(img, key, default):
  value = default

  try:
    value = img[key]
  except Exception:
    pass

  return value


def dumpExif(file):
  result = {}
  with open(file, 'rb') as f:
    img = Image(f)
    for key in img.get_all():
      try:
        result[key] = str(img[key])
      except Exception:
        pass

  return result


def parseExif(file):
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

    longitude = tryGet(img, 'gps_longitude', None)
    longitude = None if longitude is None else dms2dec(longitude)

    gpsDatetime = None
    gd = tryGet(img, 'gps_datestamp', None)
    gt = tryGet(img, 'gps_timestamp', None)

    if gd and gt:
      offset = int(time.localtime().tm_gmtoff / 3600)
      gpsDatetime = gpsDt2Dt(gd, gt, offset=offset)

    ts = -1 if createDt is None else int(createDt.timestamp())
    mTs = -1 if modifyDt is None else int(modifyDt.timestamp())
    gpsTs = -1 if gpsDatetime is None else int(gpsDatetime.timestamp())
    offset = max(mTs, gpsTs) - ts
    offsetDelta = datetime.fromtimestamp(offset, UTC) - EPOCH

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
        "offset.delta": str(offsetDelta),
    }


class InvalidImageDataError(ValueError):
  pass


def split_into_segments(data):
  """Slices JPEG meta data into a list from JPEG binary data.
  """
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


def read_exif_from_file(filename):
  """Slices JPEG meta data into a list from JPEG binary data.
  """
  f = open(filename, "rb")
  data = f.read(6)

  if data[0:2] != b"\xff\xd8":
    raise InvalidImageDataError("Given data isn't JPEG.")

  head = data[2:6]
  HEAD_LENGTH = 4
  exif = None
  while len(head) == HEAD_LENGTH:
    length = struct.unpack(">H", head[2: 4])[0]

    if head[:2] == b"\xff\xe1":
      segment_data = f.read(length - 2)
      if segment_data[:4] != b'Exif':
        head = f.read(HEAD_LENGTH)
        continue
      exif = head + segment_data
      break
    elif head[0:1] == b"\xff":
      f.read(length - 2)
      head = f.read(HEAD_LENGTH)
    else:
      break

  f.close()
  return exif


def get_exif_seg(segments):
  """Returns Exif from JPEG meta data list
  """
  for seg in segments:
    if seg[0:2] == b"\xff\xe1" and seg[4:10] == b"Exif\x00\x00":
      return seg

  return None


def merge_segments(segments, exif=b""):
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


def remove(src, new_file=None):
  """
  py:function:: piexif.remove(filename)

  Remove exif from JPEG.

  :param str filename: JPEG
  """
  output_is_file = False
  if src[0:2] == b"\xff\xd8":
    src_data = src
    file_type = "jpeg"
  else:
    with open(src, 'rb') as f:
      src_data = f.read()
    output_is_file = True
    if src_data[0:2] == b"\xff\xd8":
      file_type = "jpeg"

  if file_type == "jpeg":
    segments = split_into_segments(src_data)
    exif = get_exif_seg(segments)
    if exif:
      new_data = src_data.replace(exif, b"")
    else:
      new_data = src_data

  if isinstance(new_file, io.BytesIO):
    new_file.write(new_data)
    new_file.seek(0)
  elif new_file:
    with open(new_file, "wb+") as f:
      f.write(new_data)
  elif output_is_file:
    with open(src, "wb+") as f:
      f.write(new_data)
  else:
    raise ValueError("Give a second argument to 'remove' to output file")


def transplant(exif_src, image, new_file=None):
  """
  py:function:: piexif.transplant(filename1, filename2)

  Transplant exif from filename1 to filename2.

  :param str filename1: JPEG
  :param str filename2: JPEG
  """
  if exif_src[0:2] == b"\xff\xd8":
    src_data = exif_src
  else:
    with open(exif_src, 'rb') as f:
      src_data = f.read()

  segments = split_into_segments(src_data)
  exif = get_exif_seg(segments)

  if exif is None:
    raise ValueError("not found exif in input")

  output_file = False
  if image[0:2] == b"\xff\xd8":
    image_data = image
  else:
    with open(image, 'rb') as f:
      image_data = f.read()
    output_file = True

  segments = split_into_segments(image_data)
  new_data = merge_segments(segments, exif)

  if isinstance(new_file, io.BytesIO):
    new_file.write(new_data)
    new_file.seek(0)
  elif new_file:
    with open(new_file, "wb+") as f:
      f.write(new_data)
  elif output_file:
    with open(image, "wb+") as f:
      f.write(new_data)
  else:
    raise ValueError("Give a 3rd argument to 'transplant' to output file")


def main():
  parser = argparse.ArgumentParser(description="EXIF tool")
  parser.add_argument('-v', '--version',
                      help='echo version', action='store_true')
  parser.add_argument('-d', '--dump', help='dump meta', action='store_true')
  parser.add_argument('-r', '--rm', help='remove meta', action='store_true')
  parser.add_argument('-c', '--copy', type=str, help='copy meta')
  parser.add_argument('-f', '--file', type=str, help='image file')

  args = parser.parse_args()

  if args.version:
    print(f"et: {VERSION}")
    return

  if args.file is None:
    print("usage: et [-h] [-v] [-r FILE] [-c FILE] [-d] [-f FILE]")
    return

  if args.dump:
    r = dumpExif(args.file)
  elif args.rm:
    r = remove(args.file)
  elif args.copy:
    r = transplant(args.copy, args.file)
  else:
    r = parseExif(args.file)

  if r is not None:
    print(json.dumps(r, indent=2, sort_keys=False))


if __name__ == "__main__":
  main()
