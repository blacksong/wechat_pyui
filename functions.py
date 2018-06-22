import time
def get_latest_time(latest_time: str):
    latest_time = time.localtime(float(latest_time))
    now_time = time.localtime()

    if latest_time.tm_year == now_time.tm_year:
        if now_time.tm_yday - latest_time.tm_yday == 0:
            r_time = '{0}:{1}'.format(
                latest_time.tm_hour, latest_time.tm_min)
        elif now_time.tm_yday - latest_time.tm_yday == 1:
            r_time = '昨天'
        elif now_time.tm_yday - latest_time.tm_yday == 2:
            r_time = '前天'
        elif 2 < now_time.tm_yday - latest_time.tm_yday < 7:
            chinese_week = '一二三四五六日'
            r_time = '周{0}'.format(chinese_week[latest_time.tm_wday])
        else:
            r_time = '{0}月{1}日'.format(
                latest_time.tm_mon, latest_time.tm_mday)
    else:
        r_time = '{0}年{1}月{2}日'.format(
            latest_time.tm_year, latest_time.tm_mon, latest_time.tm_mday)
    return r_time
