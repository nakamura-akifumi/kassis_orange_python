import re
import datetime
import pytz

class SolrHelper:

    SEARCH_RESULTS_PAGES = [{"key":"10", "display_name":"10", "v": "10"},
                            {"key":"50", "display_name":"50", "v": "50"},
                            {"key":"100", "display_name":"100", "v": "100"},
                            ]
    SEARCH_RESULTS_SORT = [{"key":"ma", "display_name":"適合順", "v": "score desc"},
                           {"key":"ca", "display_name":"登録：新しい順", "v": "created_at asc"},
                           {"key":"cd", "display_name":"登録：古い順", "v": "created_at desc"},
                           {"key":"ta", "display_name":"タイトル（昇順）", "v":"title desc"},
                           {"key":"td", "display_name":"タイトル（降順）", "v":"title desc"},
                          ]


    def escape(value):
        ESCAPE_CHARS_RE = re.compile(r'(?<!\\)(?P<char>[&|+\-!(){}[\]^"~*?:])')
        return ESCAPE_CHARS_RE.sub(r'\\\g<char>', value)

    def search_query(self, params):
        pass

    def date2solrtime(d):
        """
        date型をsolr用のtimestamp型に変換する。時刻は00:00:00.000とする。
        :param s:
        :return:
        """
        utc = pytz.timezone('UTC')
        t = datetime.datetime(d.year, d.month, d.day, 0, 0, 0, 0, tzinfo=utc)
        return SolrHelper.datetime2solrtime(t)

    def datetime2solrtime(d):
        """
        datetime型をsolr用のtimestamp型に変換する。
        :param s:
        :return:
        """
        utc = pytz.timezone('UTC')
        t = datetime.datetime(d.year, d.month, d.day, d.hour, d.minute, d.second, 0, tzinfo=utc)
        return "{0}".format(t.strftime('%Y-%m-%dT%H:%M:%SZ'))
