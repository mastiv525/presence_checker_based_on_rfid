import mysql.connector
from datetime import datetime, timedelta


def addstudent():
    # wpisywanie danych
    card_id = int(input("Wczytaj kartę: "))
    first_name = input("Podaj imię: ")
    last_name = input("Podaj nazwisko: ")

    database = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="presence_check"
    )
    mycursor = database.cursor(buffered=True)
    # wypisywanie dostepnych klas
    mycursor.execute("SELECT * FROM klasa")
    for x in mycursor:
        print(x)
    student_class = input("Podaj klase: ")
    variables = [card_id, first_name, last_name, student_class]
    sql = "INSERT INTO uczen (id_ucznia, karta, imie, nazwisko, id_klasy_fk) VALUES(NULL, %s, %s, %s, " \
          "(SELECT id_klasy FROM klasa WHERE nazwa_klasy = %s))"
    mycursor.execute(sql, variables)
    database.commit()
    database.close()


def check_presence2(sala):
    database = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="presence_check"
    )
    mycursor = database.cursor(buffered=True)
    elo = 1
    # sprawdza czy do sali jest przypisana lekcja
    while elo == 1:
        time_now = datetime.now()
        var_lekcja = [time_now, time_now, sala]
        q_lekcja = "SELECT lekcja.id_lekcji, sala.numer_sali, dataiczas.dic_start, dataiczas.dic_stop," \
                   " klasa.nazwa_klasy, przedmiot.nazwa_przedmiotu " \
                   "FROM ((((lekcja LEFT JOIN dataiczas ON dataiczas.id_dic=lekcja.id_dic_fk) " \
                   "LEFT JOIN sala ON sala.id_sali=lekcja.id_sali_fk) " \
                   "LEFT JOIN klasa ON klasa.id_klasy=lekcja.id_klasy_fk)" \
                   "LEFT JOIN przedmiot ON przedmiot.id_przedmiotu=lekcja.id_przedmiotu_fk)" \
                   "WHERE dataiczas.dic_start < %s AND dataiczas.dic_stop > %s AND sala.numer_sali = %s"
        mycursor.execute(q_lekcja, var_lekcja)
        chk_lekcja = mycursor.rowcount
        if chk_lekcja != 1:
            if input("Nie ma lekcji w tej sali\n Kliknij Enter aby sprawdzić ponownie...") == '1':
                elo = 0
                check_presence1()

        # jeśli jest przypisana pokazuje jej wartości i pozwala zczytać kartę
        else:
            wp_lekcja = []
            for x in mycursor:
                wp_lekcja = x
            d0 = time_now.strftime("%H:%M")
            d1 = wp_lekcja[2].strftime("%H:%M")
            d2 = wp_lekcja[3].strftime("%H:%M")
            print("Sala: " + str(wp_lekcja[
                                     1]) + "\nAktualny czas: " + d0 + "\nRozpoczęcie lekcji: " + d1 +
                  "\nKoniec lekcji: " + d2 + "\nKlasa: " +
                  wp_lekcja[4] + "\nPrzedmiot: " + wp_lekcja[5])
            benc = 1
            while benc == 1:
                nr_karty = int(input("Przyłóż karte: "))
                var_uczen = [nr_karty]

                # wprowadzenie 0 sprawdza ponownie status lekcji
                if nr_karty == 0:
                    benc = 0

                # następnie sprawdza ucznia, najpierw czy istnieje a potem
                # czy lekcja przypisana do sali jest dla jego klasy
                else:
                    q_uczen = "SELECT uczen.id_ucznia, uczen.karta, uczen.imie, uczen.nazwisko, klasa.nazwa_klasy " \
                              "FROM uczen LEFT JOIN klasa ON uczen.id_klasy_fk = klasa.id_klasy WHERE karta = %s"
                    mycursor.execute(q_uczen, var_uczen)
                    chk_uczen = mycursor.rowcount
                    if chk_uczen == 0:
                        print("Nie znaleziono ucznia z tą kartą")
                    else:
                        wp_uczen = []
                        for x in mycursor:
                            print(x)
                            wp_uczen = x
                        if wp_uczen[4] != wp_lekcja[4]:
                            print("Chyba klasy ci się pomyliły XD")

                        # Jęśli wszystko się zgadza sprawdza czy uczen ma już wpisana
                        # obecnosc a jesli nie wpisuje ja
                        else:
                            q_preputis = "SELECT * FROM wpis WHERE id_lekcji_fk = %s AND id_ucznia_fk = %s"
                            var_preputis = [wp_lekcja[0], wp_uczen[0]]
                            mycursor.execute(q_preputis, var_preputis)
                            chk_puttis = mycursor.rowcount
                            if chk_puttis == 1:
                                print("Już masz obecność XD")
                            else:
                                var_putis = [wp_lekcja[0], wp_uczen[0], 1]
                                q_putis = "INSERT INTO wpis (id_lekcji_fk, id_ucznia_fk, obecnosc) VALUES (%s ,%s , %s)"
                                mycursor.execute(q_putis, var_putis)
                                database.commit()
                                print("Dodano obecność byczku")
                                var_end = [wp_lekcja[0], wp_uczen[0]]
                                q_end = "SELECT * FROM wpis WHERE id_lekcji_fk = %s AND id_ucznia_fk = %s"
                                mycursor.execute(q_end, var_end)


def check_presence1():
    database = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="presence_check"
    )

    # sprawdza czy podana sala istnieje, jesli nie sprawdza do skutku
    nr_sali = 0
    while nr_sali == 0:
        nr_sali = int(input("Podaj numer sali: "))
        var_nr_sali = [nr_sali]
        q_nr_sali = "SELECT * FROM sala WHERE numer_sali = %s"
        mycursor = database.cursor(buffered=True)
        mycursor.execute(q_nr_sali, var_nr_sali)
        chk_nr_sali = mycursor.rowcount
        if chk_nr_sali != 1:
            print("Podano zły numer sali")
            nr_sali = 0
        else:
            database.close()
            check_presence2(nr_sali)


def addclass():
    # DoDawAnie KlasY
    class_name = input("Podaj nazwe klasy: ")

    database = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="presence_check"
    )
    mycursor = database.cursor(buffered=True)
    variables = [class_name]
    sql = "INSERT INTO klasa (id_klasy, nazwa_klasy) VALUES(NULL, %s)"
    mycursor.execute(sql, variables)
    database.commit()
    database.close()


def addabsence():
    database = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="presence_check"
    )
    mycursor = database.cursor(buffered=True)
    # wpisywanie danych
    klasa = input("Podaj klasę: ")
    dic = input("Podaj date: ")
    dic = datetime.strptime(dic, "%Y-%m-%d")
    dice = dic + timedelta(days=1)
    uczen = []
    lekcje = []
    dict = []
    variable = [klasa]
    # wrzuca wszystkich uczniów z podanej klasy do listy
    q_klasa = "SELECT uczen.id_ucznia FROM uczen LEFT JOIN klasa ON klasa.id_klasy=uczen.id_klasy_fk " \
              "WHERE klasa.nazwa_klasy = %s"
    mycursor.execute(q_klasa, variable)
    for x in mycursor:
        uczen.append(x[0])
    # wrzuca wszystkie wpisy czasu do listy
    variable = [dic, dice]
    q_data = "SELECT id_dic FROM dataiczas WHERE dic_start > %s AND dic_start < %s"
    mycursor.execute(q_data, variable)
    for x in mycursor:
        dict.append(x[0])
    print(dict)  # wypisuje id dat i czasu
    # dodaje wszystkie lekcje z podanego dnia do listy
    elo = 0
    for x in dict:
        variable = [dict[elo], klasa]
        q_chkdic = "SELECT lekcja.id_lekcji FROM lekcja LEFT JOIN klasa ON klasa.id_klasy = lekcja.id_klasy_fk " \
                   "WHERE id_dic_fk = %s AND klasa.nazwa_klasy = %s"
        mycursor.execute(q_chkdic, variable)
        for x in mycursor:
            lekcje.append(x[0])
        elo = elo + 1
    print(lekcje)
    # sprawdzanie długości tabel, potrzebne do petel
    dllek = len(lekcje)
    dlucz = len(uczen)
    x = 0
    y = 0
    # wybiera lekcje z tabeli
    while x < dllek:
        # wybiera uczniow z tabeli
        while y < dlucz:
            variable = [lekcje[x], uczen[y]]
            q_prefinal = "SELECT * FROM wpis WHERE id_lekcji_fk = %s AND id_ucznia_fk = %s"
            mycursor.execute(q_prefinal, variable)
            # jesli uczen nie ma wpisu do lekcji wpisuje mu na niej nieobecnosc, a jesli ma wpis przechodzi dalej
            prefinalc = mycursor.rowcount
            if prefinalc == 0:
                q_final = "INSERT INTO wpis (id_lekcji_fk, id_ucznia_fk, obecnosc) VALUES (%s, %s, 0)"
                mycursor.execute(q_final, variable)
                database.commit()
            y = y + 1
        y = 0
        x = x + 1
    database.close()


def choice():
    print("Dostępne funkcje: \n1. Sprawdź obecność\n2. Dodaj ucznia\n3. Dodaj klasę\n4. Dodaj lekcję\n5. "
          "Dodaj przedmiot\n6. Dodaj nieobecności"
          "\n7. Sprawdź plan lekcji")
    user_choice = input("Wybierz, co chcesz zrobić: ")
    if user_choice == "1":
        check_presence1()
    elif user_choice == "2":
        addstudent()
    elif user_choice == "3":
        addclass()
    elif user_choice == "4":
        addlesson()
    elif user_choice == "5":
        addsubject()
    elif user_choice == "6":
        addabsence()
    elif user_choice  == "7":
        lessonplan()
    else:
        print("DEBUG. Wrong choice")


def dic():

    database = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="presence_check"
    )
    mycursor = database.cursor(buffered=True)

    chk_if_empty = "SELECT * FROM dataiczas LIMIT 1"
    mycursor.execute(chk_if_empty)
    dic_chk_s = mycursor.rowcount
    if dic_chk_s == 0:
        datastr = "2020-09-01"
        datastopstr = "2021-06-26"
        # konwersja stringow na datetime
        data = datetime.strptime(datastr, "%Y-%m-%d")
        datastop = datetime.strptime(datastopstr, "%Y-%m-%d")
        # wpisywanie dat i czasu to tabel
        while data <= datastop:
            # sprawdza czy dzien nie jest w weekend
            dtyg = datetime.weekday(data)
            if 0 <= dtyg <= 4:
                dic10 = datastr + " 8:00"
                dic11 = datastr + " 8:45"
                dic20 = datastr + " 8:50"
                dic21 = datastr + " 9:35"
                dic30 = datastr + " 9:40"
                dic31 = datastr + " 10:25"
                dic40 = datastr + " 10:30"
                dic41 = datastr + " 11:15"
                dic50 = datastr + " 11:30"
                dic51 = datastr + " 12:15"
                dic60 = datastr + " 12:25"
                dic61 = datastr + " 13:10"
                dic70 = datastr + " 13:20"
                dic71 = datastr + " 14:05"
                dic80 = datastr + " 14:15"
                dic81 = datastr + " 15:00"
                dic90 = datastr + " 15:05"
                dic91 = datastr + " 15:50"
                dicstart = (dic10, dic20, dic30, dic40, dic50, dic60, dic70, dic80, dic90)
                dicstop = (dic11, dic21, dic31, dic41, dic51, dic61, dic71, dic81, dic91)
                # sprawdza najpierw czy wpis istnieje
                x = 0
                while x <= 8:
                    variables = [dicstart[x], dicstop[x]]
                    dic_check = "SELECT * FROM dataiczas WHERE dic_start = %s AND dic_stop = %s"
                    mycursor.execute(dic_check, variables)
                    dic_check_w = mycursor.rowcount
                    if dic_check_w == 1:
                        x = x + 1
                        # do nothing
                    else:
                        # potem dodaje wpis
                        dic_add = "INSERT dataiczas (id_dic, dic_start, dic_stop) VALUES (NULL, %s, %s)"
                        mycursor.execute(dic_add, variables)
                        database.commit()
                        x = x + 1
            data = data + timedelta(days=1)
            datastr = datetime.strftime(data, "%Y-%m-%d")
        database.close()


def addlesson():

    database = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="presence_check"
    )

    mycursor = database.cursor(buffered=True)
    gn = 0
    # whileuje sie ile chcesz
    while gn == 0:
        przedmiot = input("Podaj nazwę przedmiotu: ")
        dic = input("Podaj date i czas rozpoczecia(rrrr-mm-dd gg-mm-ss): ")
        klasa = input("Podaj klasę: ")
        sala = input("Podaj salę: ")
        print("Przedmiot: " + przedmiot + "\nData i czas start: " + dic + "\nKlasa: " + klasa + "\nSala: " + sala)
        czk = input("Jeśli jest git wpisz 1: ")
        if czk == '1':
            gn = 1

    sala = int(sala)

    # wrzucanie do bazy danych
    variables = [przedmiot, dic, klasa, sala]
    sql = "INSERT INTO lekcja (id_lekcji, id_przedmiotu_fk, id_dic_fk,id_klasy_fk, id_sali_fk)" \
          "VALUES(NULL, (SELECT id_przedmiotu FROM przedmiot WHERE nazwa_przedmiotu = %s)," \
          "(SELECT id_dic FROM dataiczas WHERE dic_start = %s)," \
          "(SELECT id_klasy FROM klasa WHERE nazwa_klasy = %s)," \
          "(SELECT id_sali FROM sala WHERE numer_sali = %s))"
    mycursor.execute(sql, variables)
    database.commit()

    # wrzuca na ekran dodany wpis, no chyba że źle wpisałeś to najnowszy
    mycursor.execute("SELECT * FROM lekcja order by id_lekcji desc limit 1")
    for x in mycursor:
        print(x)

    database.close()


def addsubject():
    database = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="presence_check"
    )
    mycursor = database.cursor(buffered=True)
    mycursor.execute("SELECT nazwa_przedmiotu FROM przedmiot")
    benc = mycursor.fetchall()
    # wypisuje aktywne przedmioty, po czym można dodać nowy przedmiot
    print("Aktywne przedmioty:\n")
    for x in benc:
        print(x)
    lesson_name = input("Podaj nazwę przedmiotu do dodania: ")
    variable = [lesson_name]
    chkles = "SELECT nazwa_przedmiotu FROM przedmiot WHERE nazwa_przedmiotu = %s"
    mycursor.execute(chkles, variable)
    # sprawdza czy przedmiot istnieje
    chk = mycursor.rowcount
    if chk == 1:
        print("Podany przedmiot już istnieje")
    else:
        push = "INSERT INTO przedmiot (id_przedmiotu, nazwa_przedmiotu) VALUES (NULL, %s)"
        mycursor.execute(push, variable)
        database.commit()
        mycursor.execute("SELECT * FROM przedmiot ORDER BY id_przedmiotu DESC LIMIT 1")
        for x in mycursor:
            print(x)
    database.close()


def lessonplan():
    database = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="presence_check"
    )
    mycursor = database.cursor(buffered=True)
    classpl = input("Podaj klase: ")
    week = datetime.today()
    week = week.replace(hour=0, minute=0, second=0, microsecond=0)
    print(week)
    dtyg = datetime.weekday(week)
    print(dtyg)
    if dtyg > 0:
        week = week - timedelta(days=dtyg)
    weekedt = week + timedelta(days=1)
    qhour = "SELECT dic_start, dic_stop FROM dataiczas WHERE dic_start >= %s AND dic_stop < %s"
    varhour = [week, weekedt]
    mycursor.execute(qhour, varhour)
    tablica = [row[:] for row in mycursor]
    pas_godz = 0
    while pas_godz <= 8:
        elo = tablica[pas_godz][0]
        elo = datetime.strftime(elo, "%H:%M")
        benc = tablica[pas_godz][1]
        benc = datetime.strftime(benc, "%H:%M")
        pas_godz += 1
        print(elo + " - " + benc)
    print("\nPLAN LEKCJI")

    all_tablica = [[]]
    zdicstart = 0
    while zdicstart <= 4:
        qdicstart = "SELECT dic_start FROM dataiczas WHERE dic_start >= %s AND dic_stop < %s"
        vardicstart = [week, weekedt]
        mycursor.execute(qdicstart, vardicstart)
        tablica = mycursor.fetchall()
        all_tablica.insert(zdicstart, tablica)
        week = weekedt
        weekedt = week + timedelta(days=1)
        zdicstart += 1

    weekday = 0
    show_weekday = ["------/:Poniedziałek:/------", "------/:Wtorek:/------", "------/:Środa:/------",
                    "------/:Czwartek:/------", "------/:Piątek:/------"]
    while weekday <= 4:
        print(show_weekday[weekday])
        lesson_hour = 0
        while lesson_hour <= 8:
            qplan_lekcji = "SELECT przedmiot.nazwa_przedmiotu, sala.numer_sali " \
                           "FROM ((((lekcja LEFT JOIN dataiczas ON dataiczas.id_dic=lekcja.id_dic_fk)" \
                           "LEFT JOIN sala ON sala.id_sali=lekcja.id_sali_fk)" \
                           "LEFT JOIN klasa ON klasa.id_klasy=lekcja.id_klasy_fk)" \
                           "LEFT JOIN przedmiot ON przedmiot.id_przedmiotu=lekcja.id_przedmiotu_fk)" \
                           "WHERE dataiczas.dic_start = %s AND klasa.nazwa_klasy = %s"
            pog_champ = all_tablica[weekday][lesson_hour]
            final = pog_champ[0]
            varplan_lekcji = [final, classpl]
            mycursor.execute(qplan_lekcji, varplan_lekcji)
            chk_lekcja = mycursor.rowcount
            if chk_lekcja != 1:
                print("----Wolne----")
            else:
                xd = mycursor.fetchone()
                print(str(xd[0]) + " Sala: " + str(xd[1]))
            lesson_hour += 1
        weekday += 1

    database.close()


def main():
    dic()
    choice()


if __name__ == "__main__":
    main()
