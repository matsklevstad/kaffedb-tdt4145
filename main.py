import sqlite3
import pandas as pd
from datetime import datetime

con = sqlite3.connect("kaffe.db")
cursor = con.cursor()

logoIntro = """
    __ __      ________     ____  ____ 
   / //_/___ _/ __/ __/__  / __ \/ __ )
  / ,< / __ `/ /_/ /_/ _ \/ / / / __  |
 / /| / /_/ / __/ __/  __/ /_/ / /_/ / 
/_/ |_\__,_/_/ /_/  \___/_____/_____/ 
                                """

intro = "Velkommen!"

menu = """\n---- Valgmuligheter i programmet ----\n
1. Skriv en kaffesmaking
2. Vis liste over brukere som har smakt flest unike kaffer det siste året 
3. Vis liste over kaffe sortert etter hva som gir deg mest for pengene
4. Skriv inn et nøkkelord og søk etter kaffer beskrevet med det nøkkelordet
5. Vis kaffer fra Rwanda og Colombia som ikke er vaskede
6. Avslutt programmet \n"""

def main():

    print(logoIntro)
    print(intro)

    while True:

        print(menu)

        choice = input(
            "Skriv inn et tall mellom 1 og 6 for å velge hva du vil gjøre: ")

        if(choice == "1"):
            handleUserTasting()

        elif(choice == "2"):
            getListOverUsersWithMostTasted()

        elif(choice == "3"):
            getMostCoffePerPrice()

        elif(choice == "4"):
            keyword = input('Hvilket nøkkelord vil du søke etter? ')
            getCoffeByKeyWord(keyword)

        elif(choice == "5"):
            getUnwashedCoffeeFromRwandaAndColombia()

        elif(choice == "6"):
            exitProgram()
        else:
            print("Ugyldig input! Input må være et tall mellom 1 og 6.")

        handleFollowUp()

# input = 1
def handleUserTasting():
    # Henter først ut liste over alle tilgjengelige kaffer slik at brukeren kan velge hvilken hen vil skrive smaksnotat til.
    # Har her fjernet Kaffe.KiloprisNOK, Kaffeboenne.Art, Kaffeboenne.Type for å spare plass og gi en bedre brukeropplevelse.

    print("Liste over tilgjengelige kaffer: \n")
    query = ("""SELECT Kaffe.KaffeID, Kaffe.KaffeNavn, Kaffe.KaffeBeskrivelse, Kaffebrenneri.BrenneriNavn, KaffeBrentAvBrenneri.Dato, 
    Kaffegaard.GaardNavn, Kaffegaard.Region, Kaffegaard.Land, Kaffeparti.KiloprisUSD, Kaffeparti.Innhoestingsaar
                FROM KAFFE
                    NATURAL JOIN KaffeBrentAvBrenneri
                    NATURAL JOIN Kaffebrenneri
                    NATURAL JOIN Kaffeparti
                    NATURAL JOIN Kaffegaard
                    NATURAL JOIN BestaarAv
                    NATURAL JOIN Kaffeboenne
                    NATURAL JOIN Foredlingsmetode """)

    print(pd.read_sql_query(query, con))
    print("")

    # Henter ut kaffeID-ene som er i databasen og lagrer disse.
    cursor.execute("""SELECT Kaffe.KaffeID 
                      FROM KAFFE""")

    coffeeList = (cursor.fetchall())

    # Så velger brukeren riktig notat fra tabellen og vi sjekker om kaffen har en gyldig ID
    validation = False
    while not validation:
        try:
            coffeeId = int(input("Skriv inn ID til kaffen du vil smake på: "))
            for i in coffeeList:
                if (list(i)[0] == coffeeId):
                    validation = True
            if not validation:
                print(
                    "IDen du valgte stemmer ikke overens med noen som finnes i databasen. Prøv igjen!")
        except:
            print("ID-en til en kaffe må være et tall!")

    # Tar datoen nå og formaterer den til en streng
    now = datetime.now()
    date = now.strftime("%d.%m.%Y")

    # Her håndterer vi at poengene som gis er gyldige poeng
    validation = False
    while not validation:
        try:
            points = int(input("Hvor mange poeng vil du gi til kaffen? "))
            while (points < 1 or points > 10):
                points = int(
                    input("Smakspoeng kan ikke være mindre enn 1 eller større enn 10. Prøv igjen: "))
            validation = True
        except:
            print("Poeng må være på tallformat! Prøv igjen.")

    # Smaksnotatet lagres
    tastenote = input("Fyll inn smaksnotat... ")
    print("")

    # Generer id til smaksnotatet
    cursor.execute("""SELECT Kaffesmaking.NotatID FROM Kaffesmaking""")
    idlist = (cursor.fetchall())
    id = len(idlist) + 1

    # Insert til databasen skjer her. Epostadressen vi lagrer notatet under eksisterer allerede i databasen:
    cursor.execute("""INSERT INTO Kaffesmaking VALUES (:ID, :tastenote, :points, :date, :coffeeId, "bruker@historie1.no")""",
                   {"ID": (id), "tastenote": (tastenote), "points": (points), "date": (date), "coffeeId": (coffeeId)})

    print("-"*30)
    print("Smaksnotat: " + tastenote)
    print("Smakspoeng: " + str(points))
    print("Smakdato: " + date)
    print("KaffeID valgt: " + str(coffeeId))
    print("-"*30 + "\n")

    # Lar brukeren få dobbeltsjekke at kaffesmakingen er det man ønsket
    choice = input(
        "Vil du lagre kaffesmakingen til databasen? Skriv 'J' eller 'j' for å lagre eller hva som helst for å avbryte: ")
    if(choice == "J" or choice == "j"):
        try:
            con.commit()
            print("Kaffesmakingen ble lagret suksessfullt!")
        except:
            print("Kaffesmakingen kunne ikke lagres. Prøv igjen!")
    else:
        print("Kaffesmakingen ble ikke lagret.")

# input = 2
def getListOverUsersWithMostTasted():
    now = datetime.now()
    date = now.strftime("%d.%m.%Y")
    getYear = "%." + date[-4:]

    cursor.execute("""SELECT Bruker.Fornavn, Bruker.Etternavn, count (distinct KaffeID) as AntallUnikeKafferSmakt
                FROM  Kaffesmaking NATURAL JOIN Bruker
                WHERE Smaksdato LIKE :getYear
                GROUP BY Kaffesmaking.Epostadresse
                ORDER BY AntallUnikeKafferSmakt DESC""", {"getYear": (getYear)})

    # Hadde problemer med at Pandas ikke likte SQL-spørringer hvor vi har variabler, i dette tilfellet "getYear"
    # som input fra brukeren. Måtte derfor bruker cursor.execute og lage en hjemmelagd "finere" tabell. Håper det er OK!
    row = cursor.fetchall()
    print("")
    print("Resultatet ble: \n")
    print("Fornavn".rjust(20) + "Etternavn".rjust(17) +
          "AntallUnikeKafferSmakt".rjust(26))
    i = 0
    for entry in row:
        print(str(i) + entry[0].rjust(19) + " " +
              entry[1].rjust(16) + " " + str(entry[2]).rjust(25))
        i += 1

# input = 3
def getMostCoffePerPrice():
    query = ("""SELECT KaffeNavn, avg(Poeng) as SnittPoeng, KiloprisNOK, BrenneriNavn
                FROM Kaffesmaking
                    NATURAL JOIN Kaffe
                    NATURAL JOIN KaffeBrentAvBrenneri
                    NATURAL JOIN Kaffebrenneri
                GROUP BY kaffeID
                ORDER BY (Snittpoeng/KiloprisNOK) DESC""")

    print("")
    print("Resultatet ble: \n")
    print(pd.read_sql_query(query, con))

# input = 4
def getCoffeByKeyWord(keyword):
    keyword = "%" + keyword + "%"

    cursor.execute("""SELECT BrenneriNavn, KaffeNavn
                        FROM Kaffe
                            NATURAL JOIN KaffeBrentAvBrenneri
                            NATURAL JOIN Kaffebrenneri
                        WHERE Kaffe.KaffeBeskrivelse LIKE :keyword

                        UNION

                        SELECT BrenneriNavn, KaffeNavn
                        FROM Kaffesmaking
                            NATURAL JOIN Kaffe
                            NATURAL JOIN KaffeBrentAvBrenneri
                            NATURAL JOIN Kaffebrenneri
                        WHERE Kaffesmaking.Smaksnotat LIKE :keyword

                    """, {"keyword": (keyword)})

    row = cursor.fetchall()
    if len(row) == 0:
        print("Det var ingen kaffer som stemte med søket ditt etter '" +
              keyword[1:-1] + "'")
    else:
        # Hadde problemer med at Pandas ikke likte SQL-spørringer hvor vi har variabler, i dette tilfellet "keyword"
        # som input fra brukeren. Måtte derfor bruker cursor.execute og lage en hjemmelagd "finere" tabell. Håper det er OK!
        print("")
        print("Resultatet ble: \n")
        print("BrenneriNavn".rjust(29) + "KaffeNavn".rjust(40))
        i = 0
        for entry in row:
            print(str(i) + entry[0].rjust(28) + " " + entry[1].rjust(39))
            i += 1

#input = 5
def getUnwashedCoffeeFromRwandaAndColombia():
    query = ("""SELECT  Kaffebrenneri.BrenneriNavn, Kaffe.KaffeNavn
	FROM Kaffe
	NATURAL JOIN KaffeBrentAvBrenneri
	NATURAL JOIN Kaffebrenneri
	NATURAL JOIN Kaffeparti
	NATURAL JOIN Kaffegaard
	NATURAL JOIN DyrkesAv
	NATURAL JOIN Kaffeboenne
	NATURAL JOIN Foredlingsmetode 
    WHERE Kaffegaard.Land LIKE "Colombia" OR Kaffegaard.Land LIKE "Rwanda"

    EXCEPT

    SELECT  Kaffebrenneri.BrenneriNavn, Kaffe.KaffeNavn
    FROM Kaffe
        NATURAL JOIN KaffeBrentAvBrenneri
        NATURAL JOIN Kaffebrenneri
        NATURAL JOIN Kaffeparti
        NATURAL JOIN Kaffegaard
        NATURAL JOIN DyrkesAv
        NATURAL JOIN Kaffeboenne
        NATURAL JOIN Foredlingsmetode
    WHERE (Kaffegaard.Land LIKE "Colombia" OR Kaffegaard.Land LIKE "Rwanda") AND Foredlingsmetode.MetodeNavn LIKE "Vasket"
        """)

    print(pd.read_sql_query(query, con))

# input = 6
# Stenger tilkoblingen og avslutter programmet.
def exitProgram():
    print("\n---- Takk for nå! ----\n")
    con.close()
    quit()

# Håndtere om brukeren vil sjekke ut de andre valgmulighetene uten å måtte starte programmet på nytt
def handleFollowUp():
    choice = str(input(
        "\nTast 'J' eller 'j' for å se menyen på nytt eller 'N' eller 'n' for å avslutte programmet: "))
    while True:
        if(choice == "J" or choice == "j"):
            return True
        elif(choice == 'N' or choice == "n"):
            exitProgram()
        else:
            choice = str(input(
                "Ugyldig input! Tast 'J' eller 'j' for å se menyen på nytt eller 'N' eller 'n' for å avslutte programmet: "))

main()