import calendar

from datetime import datetime

class MyCalendar(calendar.LocaleHTMLCalendar):
    def __init__(self, username, linked_data: dict):
        calendar.LocaleHTMLCalendar.__init__(
            self,
            firstweekday=6,
            locale='ja_jp',
        )
        self.username = username
        self.linked_data = linked_data
    
    def formatmonth(self, theyear, themonth, withyear=True):
        """ 親クラスとほとんど同じ形で継承 (クラスだけ違う) """
        v = []
        a = v.append
        # = ここが違う =
        a('<table class="table table-bordered table-sm" style="table-layout: fixed;">')
        # == ここまで ==
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week, theyear, themonth))
            a('\n')
        a('</table><br>')
        a('\n')
        return ''.join(v)
    
    def formatweek(self, theweek, theyear, themonth):
        s = ''.join(self.formatday(d, wd, theyear, themonth) for (d, wd) in theweek)
        return '<tr>%s</tr>' % s
    
    def formatday(self, day, weekday, theyear, themonth):
        if day == 0:
            return '<td style="background-color: #eeeee">&nbsp;</td>'
        else:
            html = '<td class="text-center {highlight}><a href="{url}" style="color:{text}">{day}</a></td>'
            text = 'blue'
            highlight = ''
            # もし予定があるなら強調
            date = datetime(year=theyear, month=themonth, day=day)
            date_str = date.strftime('%Y%m%d')
            if date_str in self.linked_data:
                # 終了した予定
                if self.linked_data[date_str]:
                    highlight = 'bg-success'
                    text = 'white'
                # 過去の予定
                elif date < datetime.now():
                    highlight = 'bg-secondary'
                    text = 'white'
                # これからの予定
                else:
                    highlight = 'bg-warning'
            
            return html.format(
                url='/todo/{}/{}/{}/{}'.format(self.username, theyear, themonth, day),
                text=text,
                day=day,
                highlight=highlight,
            )