# -*- encoding:utf-8 -*-

class Ctlr_Base:
  """
  抓取並解析單篇文章的基底類別
  """
  # ==============================
  # Controller Configs
  # ==============================

  # Ctlr 生效時間
  _date_online = 0

  # Ctlr 失效時間
  _date_expire = None

  # ==============================
  # Abstract Methods
  # ==============================
  def parse_article(self, payload):
    """解析單篇文章，將解析後之結果回傳以儲存

    輸出之 Content 至少包含下列欄位：{
      'title': '[TITLE]'
      'text': '[TEXT]'
      'html': '[HTML]',
    }

    若解析失敗則回傳 False，由 dispatch_article 儲存 Article
    """
    pass

  def run(self):
    """在子類別中覆蓋此函式, 並將抓出的文章內容以 payload
    型式傳至 dispatch_article """
    pass

  # ==============================
  #
  # ==============================

  def __init__(self):
    # @todo : date values
    pass

  def dispatch_article(self, payload):
    """
    處理單則新聞的 callback

    對 payload 進行前處理，調用 parse_article 解析其內容，並儲存輸出結果。
    """
    from . import db

    try:
      payload['pub_ts'] = Ctlr_Base.to_timestamp(payload['meta']['pub_date'])
    except KeyError: pass

    # Keep in meta so it's passed to content.meta
    payload['url_rss'] = payload['meta']['url_rss']

    content = self.parse_article(payload)

    if content:
      # content parsed successfully
      del content['response']

      Ctlr_Base.move_out_of_meta(payload, 'title')

      content["text_md5"] = Ctlr_Base.md5(content['text'].encode('utf-8'))
      content["html_md5"] = Ctlr_Base.md5(content['html'].encode('utf-8'))
      content["parser_classname"] = str(self.__class__)
      db.save_content(content)
    else:
      payload["response_md5"] = Ctlr_Base.md5(payload['response'])
      db.save_article(payload)

  @staticmethod
  def dispatch_catchups(self, payload):
    """處理前次解析失敗的資料"""
    raise Exception('Not Implemented, yet')

  @staticmethod
  def dispatch_revisit(self, payload):
    """處理 revisit 取得之資料"""

    content = self.parse_article(payload)
    if not content:
      payload["response_md5"] = Ctlr_Base.md5(payload['response'])
      db.save_article(payload)

    db.save_revisit(content_extract)

  # ==============================
  # Utilities
  # ==============================

  @staticmethod
  def md5(unicode_str):
    from hashlib import md5
    return md5(unicode_str).hexdigest()

  @staticmethod
  def move_into_meta(payload, key):
    try:
      payload['meta'][key] = payload[key]
      del payload[key]
    except KeyError: pass

  @staticmethod
  def move_out_of_meta(payload, key):
    try:
      payload[key] = payload['meta'][key]
      del payload['meta'][key]
    except KeyError: pass

  @staticmethod
  def to_date(value):
    """將 value 轉換為 datetime object, 包含時差資訊"""
    from dateutil import parser
    from datetime import datetime

    if type(value) is int:
      # interpret as timestamp, utc
      return datetime(value)

    if type(value) is datetime:
      return value

    dt = parser.parse(value)
    return dt

  @staticmethod
  def to_timestamp(value):
    import time
    return time.mktime(Ctlr_Base.to_date(value).utctimetuple())
