def F_1(test):
    print(test)
    return 0

def F_2():
    print("F2")
    return 0

dictFunct = {1: F_1,
             2: F_2
             }

function = dictFunct[1]
function("adsd")