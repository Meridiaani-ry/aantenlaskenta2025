from aantenlaskenta.ehdokas import Ehdokas, Tila
from aantenlaskenta.lipuke import Lipuke
from aantenlaskenta.vaalilogger import vaalilogger
from aantenlaskenta.utils import etsi_ehdokas, etsi_ehdokkaat_tilassa, VaaliException
import secrets


def arvo_pudotettava(pienimmät: list[Ehdokas]) -> Ehdokas:
    print("Jos arvonta halutaan suorittaa secrets-kirjaston choice funtiolla, syötä 'y', muuten paina enter ja arvonta suoritetaan manuaalisesti:")
    metodi = input("> ")
    if metodi == "y":
        vaalilogger.lisää_rivi("")
        vaalilogger.lisää_rivi("Arvontaan käytetään secrets-kirjastoa")
        valittu = [secrets.choice(pienimmät)]
    else:
        vaalilogger.lisää_rivi("")
        vaalilogger.lisää_rivi("Arvonta suoritetaan manuaalisesti")

        for ehdokas in pienimmät:
            print(f"[{ehdokas._id}]: {ehdokas.nimi}")
        print("\nSyötä pois arvotun ehdokkaan id (nimeä edeltävä numero).")
        print("Esimerkiksi: 2\n")


        syöte = input("> ")
        try:
            id = int(syöte)
        except ValueError:
            raise VaaliException("Kirjoita syöte oikeassa muodossa!")

        valittu = list(filter(lambda ehdokas: ehdokas._id == id, pienimmät))

        if len(valittu) == 0:
            raise VaaliException(f"Ehdokasta numero {id} ei löytynyt!")
        
    return valittu[0]


def etsi_pienimmät(toiveikkaat: list[Ehdokas], pudotusvertailu=False) -> list[Ehdokas]:
    if pudotusvertailu:
        pienin_summa = min(
            map(lambda ehdokas: ehdokas.pudotusvertailu_summa, toiveikkaat)
        )
        pienimmät = [
            ehdokas
            for ehdokas in toiveikkaat
            if ehdokas.pudotusvertailu_summa == pienin_summa
        ]
    else:
        pienin_summa = min(map(lambda ehdokas: ehdokas.summa, toiveikkaat))
        pienimmät = [
            ehdokas for ehdokas in toiveikkaat if ehdokas.summa == pienin_summa
        ]

    vaalilogger.lisää_rivi(f"Pienin summa: {pienin_summa}", vain_tiedostoon=True)
    vaalilogger.lisää_rivi("Pienimmän summan omaavat ehdokkaat:", vain_tiedostoon=True)

    for ehdokas in pienimmät:
        vaalilogger.lisää_rivi(f"\t{ehdokas}", vain_tiedostoon=True)
    return pienimmät


def vertaile_pienimpiä(
    pienimmät: list[Ehdokas], lipukkeet: list[Lipuke]
) -> list[Ehdokas]:
    vanhat_pienimmät = None
    while True:
        for ehdokas in pienimmät:
            ehdokas.pudotusvertailu_summa = 0.0

        for lipuke in lipukkeet:
            for ehdokas_id in lipuke.ehdokkaat:
                ehdokas = etsi_ehdokas(pienimmät, ehdokas_id)  # type: ignore
                if ehdokas is not None:
                    ehdokas.pudotusvertailu_summa += 1.0
                    break

        vanhat_pienimmät = pienimmät
        pienimmät = etsi_pienimmät(pienimmät, pudotusvertailu=True)
        if len(pienimmät) == 1 or pienimmät == vanhat_pienimmät:
            return pienimmät


def suorita_pudotus(ehdokkaat: list[Ehdokas], lipukkeet: list[Lipuke]):
    vaalilogger.lisää_rivi("Kierroksella ei valittu ketään. Aloitetaan pudotus.\n")
    toiveikkaat = etsi_ehdokkaat_tilassa(ehdokkaat, Tila.Toiveikas)
    pienimmät = etsi_pienimmät(toiveikkaat)

    if len(pienimmät) == 0:
        raise VaaliException("ei löytynyt pienimmän summan ehdokkaita.")
    if len(pienimmät) == 1:
        vaalilogger.lisää_rivi(f"Pudotetaan ehdokas {pienimmät[0]}")
        pienimmät[0].pudota()
        return

    pienimmät = vertaile_pienimpiä(pienimmät, lipukkeet)

    if len(pienimmät) == 0:
        raise VaaliException("vertailun jälkeen ei löytynyt pudotettavia.")
    if len(pienimmät) == 1:
        vaalilogger.lisää_rivi(f"Pudotetaan ehdokas {pienimmät[0]}")
        pienimmät[0].pudota()
        return

    vaalilogger.arvonnan_aloitus(pienimmät)
    pudotettava = arvo_pudotettava(pienimmät)
    vaalilogger.lisää_rivi(f"Arvonnalla valittiin pudotettavaksi {pudotettava}")
    pudotettava.pudota()
