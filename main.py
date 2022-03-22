import sqlite3
import pandas as pd

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
2. Vis liste over brukere som har smakt flest kaffer
3. Vis liste over kaffe sortert etter hva som gir deg mest for pengene
4. Skriv inn et nøkkelord og søk etter kaffer beskrevet med det nøkkelordet
5. Vis kaffer fra Rwanda og Colombia som ikke er vaskede
6. Avslutt programmet \n"""

def main():
   
    print(logoIntro)
    print(intro)
    
    while True:

        print(menu)
        tall = input("Skriv inn et tall mellom 1 og 6 for å velge hva du vil gjøre: ")

        if(tall == "1"):
            print("Funksjon 1 kommer her \n")

        elif(tall == "2"):
            getListOverUsersWithMostTasted()

        elif(tall == "3"):
            getMostCoffePerPrice()

        elif(tall == "4"):
            keyword=input('Hvilket nøkkelord vil du søke etter? ')
            getCoffeByKeyWord(keyword)

        elif(tall == "5"):
            print("Funksjon 5 kommer her")
            
        elif(tall == "6"):
            exitProgram()
        else:
            print("Ugyldig input! Input må være et tall mellom 1 og 6. \n")
            
        handleFollowUp()

# input = 2
def getListOverUsersWithMostTasted():
    query = ("""SELECT Bruker.Fornavn, Bruker.Etternavn, count (distinct KaffeID) as antallUnikeKafferSmakt
                    FROM  Kaffesmaking NATURAL JOIN Bruker
                    WHERE Smaksdato LIKE '%2022'
                    GROUP BY Kaffesmaking.Epostadresse
                    ORDER BY antallUnikeKafferSmakt DESC
                    """)

    cursor.execute("""SELECT Bruker.Fornavn, Bruker.Etternavn, count (distinct KaffeID) as antallUnikeKafferSmakt
                    FROM  Kaffesmaking NATURAL JOIN Bruker
                    WHERE Smaksdato LIKE '%2022'
                    GROUP BY Kaffesmaking.Epostadresse
                    ORDER BY antallUnikeKafferSmakt DESC
                    """)
    row=cursor.fetchall()
    print("")
    print("Resultatet ble: \n")
    print(pd.read_sql_query(query, con))
   # print(row)  # denne gir styggere output

# input = 3 
def getMostCoffePerPrice():
    query = ("""SELECT KaffeNavn, avg(Poeng) as SnittPoeng, KiloprisNOK, BrenneriNavn
                    FROM Kaffesmaking
                    NATURAL JOIN Kaffe
                    NATURAL JOIN KaffeBrentAvBrenneri
                    NATURAL JOIN Kaffebrenneri
                    GROUP BY kaffeID
                    ORDER BY (Snittpoeng/KiloprisNOK) DESC
                    """)
    
    cursor.execute("""SELECT KaffeNavn, avg(Poeng) as SnittPoeng, KiloprisNOK, BrenneriNavn
                    FROM Kaffesmaking
                    NATURAL JOIN Kaffe
                    NATURAL JOIN KaffeBrentAvBrenneri
                    NATURAL JOIN Kaffebrenneri
                    GROUP BY kaffeID
                    ORDER BY (Snittpoeng/KiloprisNOK) DESC
                    """)
    print("")
    print("Resultatet ble: \n")
    print(pd.read_sql_query(query, con))

    #Hjemmesnekra print:
    """
    row=cursor.fetchall()
    i=1
    for entry in row:
        print(str(i) + ".", entry)
        i=i + 1 """


# input = 4
def getCoffeByKeyWord(keyword):
    keyword="%" + keyword + "%"
    print(keyword)
    query = ("""SELECT BrenneriNavn, KaffeNavn
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

                    """, keyword)


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


    row=cursor.fetchall()

    if len(row) == 0:
        print("Det var ingen kaffer som stemte med søket ditt etter '" + keyword[1:-1] + "'")
    else:
        print("")
        print("Resultatet ble: \n")
        #print(pd.read_sql_query(query, con))

        print("BrenneriNavn".rjust(19) + "KaffeNavn".rjust(30))
        i=0
        for entry in row:
            print(str(i) + entry[0].rjust(18) + " " + entry[1].rjust(29))
            i=i + 1
        #print(row)

#input = 5
# def ....


# input = 6
def exitProgram():
    print("\n---- Takk for nå! ----\n")
    con.close()
    quit()

def handleFollowUp():
    choice = str(input("\nTast 'J' for å se menyen på nytt eller 'N' for å avslutte programmet: "))
    while True:
        if(choice == "J" or choice == "j" ):
           return True
        elif(choice == 'N' or choice == "n"):
            exitProgram()
        else:
            choice = str(input("Ugyldig input! Tast 'J' for å se menyen på nytt eller 'N' for å avslutte programmet: "))


main()