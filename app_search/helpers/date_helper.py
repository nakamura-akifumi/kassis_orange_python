import re
from datetime import date as Date
from calendar import monthrange

class SimpleDate:
    def __init__(self, year, month = None, day = None):
        self.d = None

        if type(year) == str:
            year = int(year)
        if type(month) == str:
            month = int(month)
        if type(day) == str:
            day = int(day)

        if month and day:
            self.d = Date(year, month, day)
        elif month and day == None:
            self.d = Date(year, month, 1)
        elif month == None and day == None:
            self.d = Date(year, 1, 1)

    def to_date(self):
        return Date(self.d.year, self.d.month, self.d.day)

    def end_of_year(self):
        d = self.d
        return Date(d.year, 12, 31)

    def end_of_month(self):
        d = self.d
        return Date(d.year, d.month, monthrange(d.year, d.month)[1])

    def is_leap(year):
        return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0

class REMatcher(object):
    def match(self, regexp, matchstring):
        self.rematch = re.match(regexp, matchstring)
        return bool(self.rematch)

    def group(self,i):
        return self.rematch.group(i)

class DateHelper:

    #see: http://ja.wikipedia.org/wiki/%E5%85%83%E5%8F%B7%E4%B8%80%E8%A6%A7_(%E6%97%A5%E6%9C%AC)
    GENGOUS = [
        {"key": "寛政", "from": '17890219', "to": '18010319'},
        {"key": "享和", "from": '18010319', "to": '18040322'},
        {"key": "文化", "from": '18040322', "to": '18180526'},
        {"key": "文政", "from": '18180526', "to": '18310123'},
        {"key": "天保", "from": '18310123', "to": '18450109'},
        {"key": "弘化", "from": '18440109', "to": '18480401'},
        {"key": "嘉永", "from": '18480401', "to": '18550115'},
        {"key": "安政", "from": '18550115', "to": '18600408'},
        {"key": "万延", "from": '18600408', "to": '18610329'},
        {"key": "文久", "from": '18610329', "to": '18640327'},
        {"key": "元治", "from": '18640327', "to": '18650501'},
        {"key": "慶応", "from": '18650501', "to": '18681023'},
        {"key": "明治", "from": '18681023', "to": '19120730'},
        {"key": "M", "from": '18681023', "to": '19120730'},
        {"key": "大正", "from": '19120730', "to": '19261225'},
        {"key": "T", "from": '19120730', "to": '19261225'},
        {"key": "昭和", "from": '19261225', "to": '19890107'},
        {"key": "S", "from": '19261225', "to": '19890107'},
        {"key": "平成", "from": '19890108', "to": '20991231'},
        {"key": "H", "from": '19890108', "to": '20991231'},
    ]

    def wareki2yyyy(gengou_label, yy):
        r = None
        gengou = next((filter(lambda x:x['key'] == gengou_label, DateHelper.GENGOUS)), None)

        if gengou:
            if type(yy) == "string":
                yyi = int(yy)
            else:
                yyi = yy

            r = (int(gengou['from'][0:4])) - 1 + yyi

        return r

    def generate_merge_range(pub_date_from_str, pub_date_to_str):
        if pub_date_from_str and pub_date_from_str.strip() != "":
            from4, to4 = DateHelper.hiduke2yyyymmdd_sub(pub_date_from_str)

        if pub_date_to_str and pub_date_to_str.strip() != "":
            from5, to5 = DateHelper.hiduke2yyyymmdd_sub(pub_date_to_str)

        from0 = from4
        to0 = to5 if to5 else to4

        return from0, to0

    def hiduke2yyyymmdd_sub(datestr):
        yyyymmdd_from = None
        yyyymmdd_to = None
        dfrom = None
        dto = None

        if datestr == None or (datestr and datestr.strip() == ""):
            return None, None

        datestr = datestr.strip()
        datestr = datestr.replace("[]?？()（）", "")   # あいまい記号を削除
        datestr = datestr.replace(" 　", "")           # 半角全角スペースを削除
        datestr = datestr.translate(str.maketrans("１２３４５６７８９０", '1234567890')) # 全角数字を半角に変換
        datestr = datestr.translate(str.maketrans("一二三四五六七八九〇元", '12345678901')) # 漢数字を半角数字に変換
        datestr = datestr.upper()               # アルファベット半角小文字を半角大文字に変換
        datestr = datestr.translate(str.maketrans(".-", '//'))

        #print("datestr={0}".format(datestr))

        gengou_label = datestr[0:2]
        gengou = next((filter(lambda x:x['key'] == gengou_label, DateHelper.GENGOUS)), None)

        m = REMatcher()

        if gengou:
            # 和暦
            datestr = datestr.translate(str.maketrans("年月日", '///'))

            key = gengou['key']

            if m.match("^({0})(\d{{1,2}})\/(\d{{1,2}})\/(\d{{1,2}})".format(key) , datestr):
                syyyy = DateHelper.wareki2yyyy(m.group(1), m.group(2))
                dfrom = dto = Date(syyyy, int(re.group(3)), int(re.group(4)))
            elif m.match("^({0})(\d{{1,2}})\/(\d{{1,2}})".format(key), datestr):
                syyyy = DateHelper.wareki2yyyy(m.group(1), int(m.group(2)))
                dfrom = SimpleDate(syyyy, m.group(3)).to_date()
                dto = SimpleDate(syyyy, m.group(3)).end_of_month()
            elif m.match("^({0})(\d{{1,2}})".format(key), datestr):
                syyyy = DateHelper.wareki2yyyy(m.group(1), int(m.group(2)))
                dfrom = SimpleDate(syyyy).to_date()
                dto = SimpleDate(syyyy).end_of_year()
            else:
                dfrom = Date.strptime(gengou['from'], '%Y%m%d')
                dto = Date.strptime(gengou['to'], '%Y%m%d')

            # union
            if dfrom:
                yyyymmdd_from = dfrom.strftime("%Y%m%d")
            if dto:
                yyyymmdd_to = dto.strftime("%Y%m%d")
        elif m.match(r"^\d{4}", datestr):
            # 西暦
            datestr = datestr.translate(str.maketrans("年月日", '///'))
            #print("datestr={0}".format(datestr))
            if m.match(r"^(\d{4})\/(\d{1,2})\/(\d{1,2})", datestr):
                dfrom = dto = SimpleDate(m.group(1), m.group(2), m.group(3)).to_date()
            elif m.match(r"^(\d{4})\/(\d{1,2})", datestr):
                dfrom = SimpleDate(m.group(1), m.group(2)).to_date()
                dto = SimpleDate(m.group(1), m.group(2)).end_of_month()
            elif m.match(r"^(\d{4})", datestr):
                dfrom = SimpleDate(m.group(1)).to_date()
                dto = SimpleDate(m.group(1)).end_of_year()
            else:
                print("format error (3) #{datestr}")

            # union
            if dfrom:
                yyyymmdd_from = dfrom.strftime("%Y%m%d")
            if dto:
                yyyymmdd_to = dto.strftime("%Y%m%d")
        else:
            print("format error (1) #{datestr}")

        return yyyymmdd_from, yyyymmdd_to



    def expand_date(datestr, options = { "mode": 'from' }):
        """
        # 西暦もしくは和暦をYYYYMMDD(from,to)の範囲に変換しdate型で返す。
        # 西暦の場合は、半角のハイフンをセパレータとする。
        # 一致しない場合は、nil,nil を返す
        # 昭和49年 => 19740101,19741231
        # 昭和49年3月 => 19740301,19740331
        # 昭和49年3月9日 => 19740309,19740309
        # 1974 => 19740101,19741231
        # 1974-3 => 19740301,19740331
        # 1974-3-9 => 19740309,19740331
        """

        if datestr == None or (datestr and datestr.strip() == ""):
            return None

        result = None

        #puts "datestr0=#{datestrs[0]} datestr1=#{datestrs[1]}"
        from0, to0 = DateHelper.hiduke2yyyymmdd_sub(datestr)
        if from0:
            if options["mode"] == 'from':
                date  = from0
            else:
                date  = to0

            result = SimpleDate(date[0:4], date[4:6], date[6:8]).to_date()

        return result

if __name__ == '__main__':
    print(DateHelper.expand_date("昭和45年"))
    print(DateHelper.expand_date("1975/10/23"))
    print(DateHelper.expand_date("2015.3"))
    print(DateHelper.expand_date("2015.3", {"mode": "to"}))
    print(DateHelper.expand_date("平成元年"))
