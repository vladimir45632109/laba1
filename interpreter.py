import sys


class OshibkaVyrazheniya(Exception):
    pass


def razbit_na_tokeny(stroka):
    tokeny = []
    i = 0
    while i < len(stroka):
        c = stroka[i]
        if c == " ":
            i += 1
        elif c in "0123456789.":
            start = i
            while i < len(stroka) and stroka[i] in "0123456789.":
                i += 1
            try:
                tokeny.append(float(stroka[start:i]))
            except ValueError:
                raise OshibkaVyrazheniya("Неправильное число")
        elif c.isalpha():
            start = i
            while i < len(stroka) and stroka[i].isalpha():
                i += 1
            tokeny.append(stroka[start:i].lower())
        elif stroka[i:i + 2] == ">=":
            tokeny.append(">=")
            i += 2
        elif c in "+-*/(),":
            tokeny.append(c)
            i += 1
        else:
            raise OshibkaVyrazheniya("Недопустимый символ")
    return tokeny


tokeny = []
poz = 0


def posmotret():
    if poz < len(tokeny):
        return tokeny[poz]
    return None


def vzyat():
    global poz
    poz += 1
    return tokeny[poz - 1]


def sravnenie():
    itog = slozhenie(True)
    while posmotret() == ">=":
        vzyat()
        pravoe = slozhenie(False)
        itog = 1 if itog >= pravoe else 0
    return itog


def slozhenie(znak_mozhno):
    itog = umnozhenie(znak_mozhno)
    while posmotret() == "+" or posmotret() == "-":
        deistvie = vzyat()
        pravoe = umnozhenie(False)
        if deistvie == "+":
            itog = itog + pravoe
        else:
            itog = itog - pravoe
    return itog


def umnozhenie(znak_mozhno):
    itog = element(znak_mozhno)
    while posmotret() == "*" or posmotret() == "/":
        deistvie = vzyat()
        pravoe = element(False)
        if deistvie == "*":
            itog = itog * pravoe
        else:
            if pravoe == 0:
                raise OshibkaVyrazheniya("Деление на ноль")
            itog = itog / pravoe
    return itog


def element(znak_mozhno):
    t = posmotret()

    if t == "+" or t == "-":
        if not znak_mozhno:
            raise OshibkaVyrazheniya("Два знака подряд")
        vzyat()
        znachenie = element(False)
        return -znachenie if t == "-" else znachenie

    if isinstance(t, float):
        vzyat()
        return t

    if t == "(":
        vzyat()
        znachenie = sravnenie()
        if posmotret() != ")":
            raise OshibkaVyrazheniya("Неправильные скобки")
        vzyat()
        return znachenie

    if t == "round":
        vzyat()
        if posmotret() != "(":
            raise OshibkaVyrazheniya("Неправильный синтаксис")
        vzyat()
        x = sravnenie()
        n = 0
        if posmotret() == ",":
            vzyat()
            n = sravnenie()
        if posmotret() != ")":
            raise OshibkaVyrazheniya("Неправильный синтаксис")
        vzyat()
        return okruglenie(x, n)

    raise OshibkaVyrazheniya("Неправильный синтаксис")


def okruglenie(x, n):
    if n != int(n) or n < 0:
        raise OshibkaVyrazheniya("Неправильное число знаков в round")
    return round(x, int(n))


def vychislit(stroka):
    global tokeny, poz
    tokeny = razbit_na_tokeny(stroka)
    poz = 0
    if len(tokeny) == 0:
        raise OshibkaVyrazheniya("Пустое выражение")
    itog = sravnenie()
    if poz < len(tokeny):
        if tokeny[poz] == ")":
            raise OshibkaVyrazheniya("Неправильные скобки")
        raise OshibkaVyrazheniya("Неправильный синтаксис")
    return itog


def format_rezultata(znachenie):
    znachenie = round(float(znachenie), 12)
    if znachenie.is_integer():
        return str(int(znachenie))
    return str(znachenie)


TESTY = [
    ("2 + 3 * (4 - 1) / 2", "6.5"),
    ("2 + 3 * 4", "14"),
    ("(2 + 3) * 4", "20"),
    ("10 / 4", "2.5"),
    ("10 - 3 - 2", "5"),
    ("-5 + 3", "-2"),
    ("+3 + 4", "7"),
    ("-(2 + 3)", "-5"),
    ("(-5) * 2", "-10"),
    ("3.5 + 1.25", "4.75"),
    ("0.1 + 0.2", "0.3"),
    ("round(3.14159, 2)", "3.14"),
    ("round(10 / 3, 3)", "3.333"),
    ("round(-2.46, 1)", "-2.5"),
    ("round(2.567, 1)", "2.6"),
    ("5 >= 3", "1"),
    ("4 >= 4", "1"),
    ("3 >= 5", "0"),
    ("1 + 2 >= 3", "1"),
]


TESTY_OSHIBOK = [
    "5 / 0",
    "(2 + 3",
    "2 + 3)",
    "2 $ 3",
    "2 ++ 3",
    "2 + -3",
    "2 * -3",
    "--5",
    "sqrt(4)",
    "round(1, 2, 3)",
    "round(2.5, -1)",
    "round(2.5, 1.5)",
]


def zapusk_testov():
    proshlo = 0
    for vyrazhenie, ozhidalos in TESTY:
        poluchilos = format_rezultata(vychislit(vyrazhenie))
        ok = (poluchilos == ozhidalos)
        proshlo += ok
        print(f"[{'OK ' if ok else 'FAIL'}] {vyrazhenie:24} = {poluchilos}")
    for vyrazhenie in TESTY_OSHIBOK:
        try:
            vychislit(vyrazhenie)
            ok, msg = False, "ошибки нет, а должна быть"
        except OshibkaVyrazheniya as e:
            ok, msg = True, str(e)
        proshlo += ok
        print(f"[{'OK ' if ok else 'FAIL'}] {vyrazhenie:24} -> {msg}")
    vsego = len(TESTY) + len(TESTY_OSHIBOK)
    print(f"\nПройдено тестов: {proshlo} из {vsego}")
    return proshlo == vsego


def dialog():
    print("Интерпретатор (вариант 10: round, >=). Для выхода введите exit")
    while True:
        try:
            vvod = input(">>> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if vvod.strip().lower() == "exit":
            break
        if vvod.strip() == "":
            continue
        try:
            print(format_rezultata(vychislit(vvod)))
        except OshibkaVyrazheniya as e:
            print("Ошибка:", e)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sys.exit(0 if zapusk_testov() else 1)
    dialog()
