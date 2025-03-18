from aantenlaskenta.lipuke import Lipuke
from aantenlaskenta.ehdokas import Ehdokas
from aantenlaskenta.vaalilogger import vaalilogger

import csv


def luo_opavote(vaalitiedosto: str) -> str:
    """
    Ottaa parametrina csv vaalitiedoston tiedostonimen.
    Luo uuden vaalitiedoston OpaVote formaatilla.
    Palauttaa luodun tiedoston nimen.

    ```
    if tiedostotyyppi != "y":
        vaalitiedosto = luo_opavote(vaalitiedosto)
    ```
    """
    
    print("Anna vaalin nimi:")
    vaalin_nimi = input("> ")
    print("Anna valittavien paikkojen määrä:")
    paikkamäärä = input("> ")
    lipukkeet = []
    ehdokkaat = set()
    with open(vaalitiedosto, "r") as f:
        csvFile = csv.reader(f)
        for line in csvFile:
            lipukkeet.append(line)
            ehdokkaat.update(line)
    ehdokkaat.remove("")
    printti = f"{len(ehdokkaat)} {paikkamäärä}\n"
    for i,ehdokas in enumerate(ehdokkaat):
        for j in range(len(lipukkeet)):
            for k in range(len(lipukkeet[j])):
                if lipukkeet[j][k] == ehdokas:
                    lipukkeet[j][k] = i+1
    for j in range(len(lipukkeet)):
        printti += "1 "
        for k in range(len(lipukkeet[j])):
            if lipukkeet[j][k] != "":
                printti += f"{str(lipukkeet[j][k])} "
        printti += "0\n"
    printti += "0\n"
    for i,ehdokas in enumerate(ehdokkaat):
        printti += f'"{ehdokas}"\n'
    printti += f'"{vaalin_nimi}"'
    print("Anna uuden vaalitiedoston nimi:")
    opavote_tiedosto = input("> ")
    f = open(opavote_tiedosto, "w")
    f.write(printti)
    f.close()
    return opavote_tiedosto
    


def lue_lipukkeet(syöte: list[str]) -> tuple[str, int, list[Ehdokas], list[Lipuke], int]:
    """
    Ottaa parametrina opavoten generoiman datan rivitettynä.
    Palauttaa (vaalin nimi, paikkojen määrä, ehdokkaat, lipukkeet)

    ```
    with open("vaali.txt") as f:
        vaali, paikat, ehdokkaat, lipukkeet = lue_lipukkeet(f.readlines())
    ```
    """
    iteraattori = iter(map(str.strip, syöte))

    eka_rivi = next(iteraattori).split()
    if len(eka_rivi) != 2:
        raise Exception("Ensimmäisellä rivillä pitää olla tasan kaksi lukua")

    ehdokasmäärä, paikkamäärä = [int(x) for x in eka_rivi]

    vaalilogger.lisää_rivi(f"Ehdokkaita on {ehdokasmäärä}")
    vaalilogger.lisää_rivi(f"Valitaan {paikkamäärä} ehdokasta")

    lipukkeet = []
    hylätyt_äänet = 0
    while (rivi := next(iteraattori)) != "0":
        osat = rivi.split()[1:-1]
        ids = [int(x) for x in osat]
        if len(ids) == 0:
            hylätyt_äänet += 1
            continue

        lipukkeet.append(Lipuke(ids))

    i = 1
    ehdokkaat = []
    while i <= ehdokasmäärä:
        nimi = next(iteraattori)[1:-1]
        ehdokkaat.append(Ehdokas(nimi, i))
        i += 1

    vaalin_nimi = next(iteraattori)[1:-1]

    return (vaalin_nimi, paikkamäärä, ehdokkaat, lipukkeet, hylätyt_äänet)
