from dataclasses import dataclass

@dataclass
class OpeningHour:
    orariAperturaId: int
    giornoSettimanaId: int
    oraAperturaMattina: str
    oraChiusuraMattina: str
    oraAperturaPomeriggio: str
    oraChiusuraPomeriggio: str
    flagOrarioContinuato: bool
    oraAperturaOrarioContinuato: str
    oraChiusuraOrarioContinuato: str
    flagH24: bool
    flagChiusura: bool
    flagNonComunicato: bool
    flagServito: bool
    flagSelf: bool