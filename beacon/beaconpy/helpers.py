# -*- coding: utf-8 -*-

import json, time, datetime, httplib

"""Helper classes and functions."""

def ToIso(date):
  """
  Transform a date to ISO 8601.   
  
  @param date -- timestamp      
  @return date in ISO 8601
  """
  
  try:
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(int(date)))
  except:
    return date

def UtcNow():
  """
  Give current time in epoch.
  
  @return utc time in epoch (float)
  """
  
  now = datetime.datetime.utcnow()
  return (now - datetime.datetime(1970, 1, 1)).total_seconds()

def haveInternet():
  """
  Check if an internet connection is avaiable.
  Makes a HEAD request to google.com (no HTML will be fetched, fast)
  
  @return True if connection is avaiable
  @return False if no connection is avaiable
  """
  
  conn = httplib.HTTPConnection("www.google.com")
  try:
    conn.request("HEAD", "/")
    return True
  except:
    return False
    
def flatten(l):
  """
  Flatten a nested list.
  
  @param list
  @return flattened list
  """
  
  for el in l:
    if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
      for sub in flatten(el):
        yield sub
      else:
        yield el

class Bunch:
  """
  Helper class to init json-printable objects.
  """
  
  def __init__(self, **kwds):
    self.__dict__.update(kwds)
  def to_JSON(self):
    return json.dumps(self, default = lambda o: o.__dict__, 
      sort_keys = True)