import datetime
import yaml


def get_weekday():
    now = datetime.datetime.now()
    weekday = now.weekday()
    hour = now.hour
    is_weekend = (weekday == 5) or (weekday == 6)  # 判断是否为周末
    if 5 <= hour < 9:
        day_time = "早上"
    elif 9 <= hour < 12:
        day_time = '上午'
    elif 12 <= hour < 14:
        day_time = '中午'
    elif 14 <= hour < 19:
        day_time = '下午'
    elif 19 <= hour < 24:
        day_time = '晚上'
    else:
        day_time = "半夜"
    weekday_dict = {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"}
    weekday_str = weekday_dict[weekday]
    return weekday_str, day_time, is_weekend


def _read_config(filename):
    with open(filename, 'r') as file:
        config_dict = yaml.safe_load(file)
    return config_dict


def _write_config(filename, config_dict):
    with open(filename, 'w') as file:
        yaml.dump(config_dict, file, default_flow_style=False)


# 调用函数读取配置文件
config_filename = 'config.yml'
config = _read_config(config_filename)


def add_config(key: str, value):
    if key in config:
        config[key].append(value)
    else:
        config[key] = [value]
    _write_config(config_filename, config)


def update_config(key: str, value):
    config[key] = value
    _write_config(config_filename, config)


def get_time_str(second: int | float) -> str:
    hour = int(second / 3600)
    minute = int((second - hour * 3600) / 60)
    second = int(second - hour * 3600 - minute * 60)
    if hour:
        return str(hour) + '时' + str(minute) + '分' + str(second) + '秒'
    elif minute:
        return str(minute) + '分' + str(second) + '秒'
    else:
        return str(second) + '秒'
