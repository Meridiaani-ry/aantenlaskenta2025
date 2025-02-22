from aantenlaskenta.ehdokas import Ehdokas
import aantenlaskenta.utils as utils


class VaaliLogger:
    tapahtumat: list[str]

    def __init__(self):
        self.tapahtumat = []

    def lisää_rivi(self, tapahtuma: str, vain_tiedostoon=False):
        if not vain_tiedostoon:
            print(tapahtuma)
        self.tapahtumat.append(tapahtuma + "\n")

    def arvonnan_aloitus(self, ehdokkaat: list[Ehdokas]):
        self.lisää_rivi("Arvotaan pudotettava seuraavista:")
        for ehdokas in ehdokkaat:
            self.lisää_rivi(f"\t{ehdokas}")

    def uusi_kierros(self, kierros_nro: int):
        tulostus = f"\n{'-'*80}\n Kierros {kierros_nro}\n"
        self.lisää_rivi(tulostus)

    def nykytilanne(self, ehdokkaat: list[Ehdokas], vain_tiedostoon=False):
        tulostus = "\n".join(utils.nykytilanne(ehdokkaat))
        self.lisää_rivi(tulostus, vain_tiedostoon)

    def tulosta_tiedostoon(self, tiedosto):
        tiedosto.writelines(self.tapahtumat)


vaalilogger = VaaliLogger()
