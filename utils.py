import re

def extract_route_id(text):
   
    regex = r'(?<=Маршрут: )[0-9]+'
    route_id = re.search(regex, text).group()

    return route_id


def extract_point_num(text):
   
    regex = r'(?<=паллеты )[0-9]+'
    points_num = int(re.search(regex, text).group())

    return points_num


def extract_current_status(text):
   
    regex = r'(?<=коробки )[0-9]+'
    current_status = int(re.search(regex, text).group())

    return current_status