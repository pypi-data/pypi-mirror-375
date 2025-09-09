from dataclasses import dataclass

@dataclass
class LogoImg:
    tipoFile: str
    estensione: str
    content: str
    
    def __init__(self, 
                 tipoFile: str, 
                 estensione: str,
                 content: str):
        
        self.tipoFile = tipoFile
        self.estensione = estensione
        self.content = content