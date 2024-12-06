from ehdokas import Ehdokas, Tila
from lipuke import Lipuke
from utils import ceil_5dec, etsi_ehdokkaat_tilassa
from laske_summat import laske_summat
from vaalilogger import vaalilogger
import secrets


def nollaa_summat(ehdokkaat: list[Ehdokas]):
    for ehdokas in ehdokkaat:
        ehdokas.summa = 0.0


def laske_äänikynnys(
    hyväksytyt_äänet: int, äänihukka: float, paikkamäärä: int
) -> float:
    return ceil_5dec((hyväksytyt_äänet - äänihukka) / paikkamäärä)


def päivitä_painokertoimet(ehdokkaat: list[Ehdokas], äänikynnys: float):
    print("Äänikynnys:", äänikynnys)
    for ehdokas in ehdokkaat:
        if ehdokas.tila != Tila.Valittu:
            continue

        print(f"Ehdokas {ehdokas.nimi}, summa: {ehdokas.summa}")

        ehdokas.painokerroin *= äänikynnys / ehdokas.summa


def valittujen_summat_oikein(ehdokkaat: list[Ehdokas], äänikynnys: float) -> bool:
    for ehdokas in ehdokkaat:
        if not ehdokas.tila == Tila.Valittu:
            continue

        if round(100_000 * abs(ehdokas.summa - äänikynnys)) > 1:
            return False

    return True


def valitse_toiveikkaat(toiveikkaat: list[Ehdokas], äänikynnys) -> list[Ehdokas]:
    valitut = []
    for ehdokas in toiveikkaat:
        assert ehdokas.tila == Tila.Toiveikas
        if ehdokas.summa >= äänikynnys:
            print(f"Valitaan ehdokas [{ehdokas._id}]: {ehdokas.nimi}")
            ehdokas.valitse()
            valitut.append(ehdokas)

    return valitut


def arvo_pudotettava(pienimmät: list[Ehdokas]) -> Ehdokas:
    vaalilogger.arvonnan_aloitus(pienimmät)
    valittu = secrets.choice(pienimmät)
    valittu.pudota()
    vaalilogger.arvonnan_tulos(valittu)
    return valittu


def pudota_pienin(toiveikkaat: list[Ehdokas]) -> Ehdokas | None:
    pienin_summa = min(map(lambda ehdokas: ehdokas.summa, toiveikkaat))
    pienimmät = [ehdokas for ehdokas in toiveikkaat if ehdokas.summa == pienin_summa]

    if len(pienimmät) == 1:
        pienimmät[0].pudota()

        return pienimmät[0]

    pudotettu = arvo_pudotettava(pienimmät)
    return pudotettu


def kierros(paikkamäärä, ehdokkaat, lipukkeet):
    jatketaan = True
    äänikynnys = float("inf")

    while jatketaan:
        for ehdokas in ehdokkaat:
            ehdokas.alusta_painokerroin()

        nollaa_summat(ehdokkaat)

        äänihukka, hyväksytyt_äänet = laske_summat(ehdokkaat, lipukkeet)

        äänikynnys = laske_äänikynnys(hyväksytyt_äänet, äänihukka, paikkamäärä)

        päivitä_painokertoimet(ehdokkaat, äänikynnys)
        jatketaan = not valittujen_summat_oikein(ehdokkaat, äänikynnys)

    valitut = etsi_ehdokkaat_tilassa(ehdokkaat, Tila.Valittu)
    toiveikkaat = etsi_ehdokkaat_tilassa(ehdokkaat, Tila.Toiveikas)

    if len(valitut) + len(toiveikkaat) == paikkamäärä:
        # valitaan loput
        for toiveikas in toiveikkaat:
            toiveikas.tila = Tila.Valittu

        return

    valitut = valitse_toiveikkaat(toiveikkaat, äänikynnys)

    if len(valitut) > 0:
        return

    pudotettu = pudota_pienin(toiveikkaat)

    if pudotettu is not None:
        print(f"Pudotetaan ehdokas [{pudotettu._id}]: {pudotettu.nimi}")
        return


def suorita_vaali(paikkamäärä: int, ehdokkaat: list[Ehdokas], lipukkeet: list[Lipuke]):
    print(f"Paikkoja: {paikkamäärä}\nehdokkaita: {len(ehdokkaat)}")
    kierros_nro = 1
    while True:
        valitut = etsi_ehdokkaat_tilassa(ehdokkaat, Tila.Valittu)
        print(f"valittuja: {len(valitut)}")
        if len(valitut) == paikkamäärä:
            break

        vaalilogger.uusi_kierros(kierros_nro)
        kierros(paikkamäärä, ehdokkaat, lipukkeet)
        vaalilogger.nykytilanne(ehdokkaat)
        kierros_nro += 1
