# -*- coding: utf-8 -*-
#
from lib import Ctlr_Base_RSS_2_0

class Ctlr(Ctlr_Base_RSS_2_0):
  _created_on = '2013-07-25T16:33:26Z'

  _my_feeds = [
    {"title": "全部文章", "url": "http://e-info.org.tw/rss.xml"},
  ]

  def parse_response(self, payload):
    hits = payload['html'].cssselect(
      '.maincol2-padding .title, .maincol2-padding #page'
    )

    if hits is None or len(hits) < 2: return None
    payload['content'] = hits
    return payload
