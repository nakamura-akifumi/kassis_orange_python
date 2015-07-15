import datetime

def datetimeformat(value, format='%Y/%m/%d %H:%M'):
    if type(value) == str:
        value = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')

    return value.strftime(format)

def checked(value):
    if value == None:
        return ""
    elif value == False:
        return ""
    else:
        return "checked"
