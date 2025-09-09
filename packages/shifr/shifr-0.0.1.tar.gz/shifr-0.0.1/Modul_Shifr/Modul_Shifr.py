
len_RU=['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я', 'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я']
len_EN=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


len_RU_s=['к', 'ц', 'р', 'е', 'э', 'у', 'ё', 'ъ', 'й', 'ю', 'з', 'х', 'ж', 'л', 'б', 'щ', 'г', 'т', 'с', 'в', 'н', 'ф', 'о', 'а', 'д', 'и', 'ч', 'я', 'ш', 'ь', 'м', 'п', 'ы', 'Ч', 'Н', 'Ъ', 'Ж', 'Ю', 'А', 'Ш', 'Т', 'Я', 'Б', 'З', 'Е', 'Л', 'П', 'У', 'К', 'С', 'Й', 'Р', 'Ы', 'В', 'Х', 'Ф', 'О', 'Ё', 'Д', 'Г', 'Щ', 'Ь', 'М', 'И', 'Э', 'Ц']
len_EN_s=['N', 'S', 'G', 'Y', 'F', 'X', 'O', 'Z', 'M', 'R', 'L', 'U', 'A', 'E', 'V', 'P', 'I', 'D', 'Q', 'B', 'C', 'K', 'J', 'H', 'W', 'T', 'q', 'f', 'b', 'k', 'i', 'm', 'p', 'z', 'c', 'v', 'a', 'r', 't', 'w', 'd', 'o', 'u', 'e', 'j', 'x', 's', 'l', 'y', 'n', 'h', 'g']


m=[]
n=[]


def RU_s(text):
    for i in range(len(text)):
        m.append(len_RU.index(text[i]))
    for j in range(len(m)):
        n.append(len_RU_s[m[j]])
    f = ''.join(n)
    return f

def RU_rs(text):
    for i in range(len(text)):
        m.append(len_RU_s.index(text[i]))
    for j in range(len(m)):
        n.append(len_RU[m[j]])
    f = ''.join(n)
    return f

def EN_s(text):
    for i in range(len(text)):
        m.append(len_EN.index(text[i]))
    for j in range(len(m)):
        n.append(len_EN_s[m[j]])
    f=''.join(n)
    return f

def EN_rs(text):
    for i in range(len(text)):
        m.append(len_EN_s.index(text[i]))
    for j in range(len(m)):
        n.append(len_EN[m[j]])
    f = ''.join(n)
    return f




