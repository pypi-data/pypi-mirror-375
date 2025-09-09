import time
import json
import argparse

from datetime import UTC, datetime, timedelta, timezone
from exif import Image

VERSION = "0.1.1"

EPOCH = datetime.fromtimestamp(0, UTC)
IGNORE = ['orientation', 'maker_note', '_interoperability_ifd_Pointer',
          'components_configuration', 'scene_type', 'flashpix_version',
          'gps_processing_method',]


def dms2dec(dms: tuple):
  d, m, s = dms
  return d + m/60 + s/3600


def dtFormatter(str):
  return datetime.strptime(str, '%Y:%m:%d %H:%M:%S')


def dt2str(dt):
  return None if dt is None else dt.strftime('%Y-%m-%d %H:%M:%S')


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

    # da = []
    # for d in (d1, d2, d3):
    #     if d is not None:
    #         print(d)
    #         da.append(dtFormatter(d))
    # dt = None if len(da) == 0 else max(da)

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


def main():
  parser = argparse.ArgumentParser(description="EXIF tool")
  parser.add_argument('-v', '--version',
                      help='echo version', action='store_true')
  parser.add_argument('-d', '--dump', help='dump meta', action='store_true')
  parser.add_argument('-f', '--file', type=str, help='image file')

  args = parser.parse_args()

  if args.version:
    print(f"et: {VERSION}")
    return

  if args.file is None:
    print("usage: et [-h] [-v] [-d] [-f FILE]")
    return

  r = dumpExif(args.file) if args.dump else parseExif(args.file)
  print(json.dumps(r, indent=2, sort_keys=False))


if __name__ == "__main__":
  main()
