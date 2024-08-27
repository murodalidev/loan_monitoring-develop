import re

def digit_from_str(name):
    if name is not None:
        if name.isdigit():
            return name
        elif name.find('(', 0, 2)==0:
            res = re.findall(r'\(.*?\)', name)
            return re.sub(r"[\([{})\]]", "", res[0])
        else:
            if name.split('-', 1)[0].isdigit():
                return name.split('-', 1)[0]
            else:
                dig = name.split(' ', 1)[0]
                if (dig == 'I'):
                    return 1
                if (dig == 'II'):
                    return 2
                if (dig == 'III'):
                    return 3
                if (dig == 'IV'):
                    return 4
                else:
                    return name
    else: return None
        
    