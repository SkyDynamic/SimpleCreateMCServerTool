import datetime


def format_time(time_str: str) -> int:
    l_s1 = time_str.split("+")
    l_s1[-1] = l_s1[-1].replace(":", "")
    l_s1[0] = l_s1[0].replace("T", " ")
    new_time_str = "+".join(l_s1)
    fmt = "%Y-%m-%d %H:%M:%S%z"
    uxin = datetime.datetime.strptime(new_time_str, fmt)
    return int(uxin.timestamp())
