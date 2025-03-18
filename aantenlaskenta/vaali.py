from aantenlaskenta.ehdokas import Ehdokas, Tila
from aantenlaskenta.lipuke import Lipuke
from aantenlaskenta.utils import (
    ceil_5dec,
    etsi_ehdokkaat_tilassa,
)


from aantenlaskenta.laske_summat import laske_summat
from aantenlaskenta.vaalilogger import vaalilogger
from aantenlaskenta.pudotus import suorita_pudotus


def nollaa_summat(ehdokkaat: list[Ehdokas]):
    for ehdokas in ehdokkaat:
        ehdokas.summa = 0.0


def laske_äänikynnys(
    hyväksytyt_äänet: int, äänihukka: float, paikkamäärä: int
) -> float:
    return ceil_5dec((hyväksytyt_äänet - äänihukka) / (paikkamäärä+1) + 1)


def päivitä_painokertoimet(ehdokkaat: list[Ehdokas], äänikynnys: float):
    for ehdokas in ehdokkaat:
        if ehdokas.tila != Tila.Valittu:
            continue

        ehdokas.painokerroin *= äänikynnys / ehdokas.summa
        vaalilogger.lisää_rivi(
            f"Päivitetään painokerroin ehdokkaalle {ehdokas}:  {ehdokas.painokerroin}",
            vain_tiedostoon=True,
        )


def valittujen_summat_oikein(ehdokkaat: list[Ehdokas], äänikynnys: float) -> bool:
    vaalilogger.lisää_rivi(
        f"Tarkistetaan, onko kaikilla valituilla summa oikein (äänikynnys = {äänikynnys})",
        vain_tiedostoon=True,
    )
    for ehdokas in ehdokkaat:
        if not ehdokas.tila == Tila.Valittu:
            continue

        if round(100_000 * abs(ehdokas.summa - äänikynnys)) > 1:
            vaalilogger.lisää_rivi(
                f"Ehdokkaan {ehdokas} summa ei täsmännyt vielä: {ehdokas.summa}",
                vain_tiedostoon=True,
            )
            return False

    return True


def valitse_toiveikkaat(toiveikkaat: list[Ehdokas], äänikynnys) -> list[Ehdokas]:
    valitut = []
    for ehdokas in toiveikkaat:
        assert ehdokas.tila == Tila.Toiveikas
        if ehdokas.summa >= äänikynnys:
            vaalilogger.lisää_rivi(f"Valitaan ehdokas {ehdokas}")
            ehdokas.valitse()
            valitut.append(ehdokas)

    return valitut


def kierros(paikkamäärä, ehdokkaat, lipukkeet):
    jatketaan = True
    äänikynnys = float("inf")

    vaalilogger.lisää_rivi("\nIteroidaan painokertoimia.", vain_tiedostoon=True)
    while jatketaan:
        for ehdokas in ehdokkaat:
            ehdokas.alusta_painokerroin()

        nollaa_summat(ehdokkaat)

        äänihukka, hyväksytyt_äänet = laske_summat(ehdokkaat, lipukkeet)
        vaalilogger.lisää_rivi(f"äänihukka: {äänihukka}", vain_tiedostoon=True)
        vaalilogger.lisää_rivi(
            f"hyväksytyt äänet: {hyväksytyt_äänet}", vain_tiedostoon=True
        )

        äänikynnys = laske_äänikynnys(hyväksytyt_äänet, äänihukka, paikkamäärä)
        vaalilogger.lisää_rivi(f"äänikynnys: {äänikynnys}", vain_tiedostoon=True)

        vaalilogger.lisää_rivi("päivitetään painokertoimet", vain_tiedostoon=True)
        päivitä_painokertoimet(ehdokkaat, äänikynnys)
        jatketaan = not valittujen_summat_oikein(ehdokkaat, äänikynnys)
        vaalilogger.lisää_rivi(
            f"kaikkien valittujen painokertoimet oikein: {not jatketaan}\n",
            vain_tiedostoon=True,
        )

    valitut = etsi_ehdokkaat_tilassa(ehdokkaat, Tila.Valittu)
    toiveikkaat = etsi_ehdokkaat_tilassa(ehdokkaat, Tila.Toiveikas)

    if len(valitut) + len(toiveikkaat) == paikkamäärä:
        vaalilogger.lisää_rivi("Valitaan loput ehdokkaat:")
        for toiveikas in toiveikkaat:
            toiveikas.tila = Tila.Valittu
            vaalilogger.lisää_rivi(f"\t{toiveikas}")

        return

    valitut = valitse_toiveikkaat(toiveikkaat, äänikynnys)

    if len(valitut) > 0:
        return

    suorita_pudotus(ehdokkaat, lipukkeet)


def suorita_vaali(paikkamäärä: int, ehdokkaat: list[Ehdokas], lipukkeet: list[Lipuke]):
    vaalilogger.lisää_rivi(f"Paikkoja: {paikkamäärä}\nehdokkaita: {len(ehdokkaat)}")
    kierros_nro = 1
    while True:
        valitut = etsi_ehdokkaat_tilassa(ehdokkaat, Tila.Valittu)
        if len(valitut) == paikkamäärä:
            break

        vaalilogger.uusi_kierros(kierros_nro)
        kierros(paikkamäärä, ehdokkaat, lipukkeet)
        vaalilogger.lisää_rivi("\nTilanne kierroksen lopussa:")
        vaalilogger.nykytilanne(ehdokkaat)
        kierros_nro += 1
    bs_n="\n"
    vaalilogger.lisää_rivi(f"\n{('='*80 + bs_n)*2}")
    vaalilogger.lisää_rivi("\nValitaan ehdokkaat: \n")
    for ehdokas in etsi_ehdokkaat_tilassa(ehdokkaat, Tila.Valittu):
        vaalilogger.lisää_rivi(f"\t{ehdokas}")
