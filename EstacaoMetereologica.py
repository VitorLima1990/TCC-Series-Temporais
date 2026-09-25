import math
import copy
from datetime import datetime

class _Progress:
    def __init__(self):
        self.Maximum = 0
        self.Value = 0
        self.Text = ""
    def Refresh(self):
        pass
    def Increment(self, value=1):
        self.Value += value


def _set_attr(obj, name, value):
    try:
        setattr(obj, name, value)
    except Exception:
        pass


def _pad(text, width):
    return str(text).rjust(width)


def _fmt(value, decimals=None):
    if decimals is None:
        return str(value)
    return f"{value:.{decimals}f}"


def _csharp_round(value, digits=0):
    # Math.Round(x, digits) sem modo explícito usa ToEven em C#.
    return round(value, digits)


class Medicao:
    def __init__(self, dataHora, RadiacaoSolar, temperatura):
        self.dataHora = dataHora
        self.radiacaoSolar = RadiacaoSolar
        self.temperatura = temperatura

    def ValoresValidos(self):
        return self.radiacaoSolar != -9999 and self.temperatura != -9999

    def __str__(self):
        return (_pad(self.dataHora.strftime("%d/%m/%Y"), 10) +
                _pad(f"{self.dataHora.hour:02d}", 10) +
                _pad(_fmt(self.radiacaoSolar, 2), 22) +
                _pad(_fmt(self.temperatura, 1), 17))

    def ToString(self):
        return str(self)


class Diaria:
    def __init__(self, dataHora, estacao, RadiacaoSolar, tempMinima, tempMaxima):
        self.dataHora = dataHora
        self.estacao = estacao
        self.radiacaoSolar = RadiacaoSolar
        self.tempMinima = tempMinima
        self.tempMaxima = tempMaxima

    def __str__(self):
        return (_pad(self.dataHora.strftime("%d/%m/%Y"), 10) +
                _pad(self.dataHora.year, 8) +
                _pad(self.estacao, 10) +
                _pad(_fmt(self.tempMinima, 1), 12) +
                _pad(_fmt(self.tempMaxima, 1), 12) +
                _pad(_fmt(self.radiacaoSolar, 2), 13))

    def ToString(self):
        return str(self)


class TemperaturasCalculadas:
    def __init__(self, regime, condicao, riscoTermico, Temp_VD, Temp_VN, Temp_ID, Temp_IN):
        self.regime = regime
        self.condicao = condicao
        self.riscoTermico = riscoTermico
        self.periodo = 1 / self.riscoTermico
        self.Temp_VD = Temp_VD
        self.Temp_VN = Temp_VN
        self.Temp_ID = Temp_ID
        self.Temp_IN = Temp_IN

    def __str__(self):
        return (_pad(self.regime, 15) + _pad(self.condicao, 9) +
                _pad(str(self.riscoTermico * 100), 17) +
                _pad(_fmt(self.Temp_VD, 0), 14) +
                _pad(_fmt(self.Temp_VN, 0), 14) +
                _pad(_fmt(self.Temp_ID, 0), 14) +
                _pad(_fmt(self.Temp_IN, 0), 14))

    def ToString(self):
        return str(self)


class Anual:
    def __init__(self, ano, radiacaoSolarInverno, radiacaoSolarVerao,
                 tempMinima, tempMaxima, TempVeraoDia, TempVeraoNoite,
                 TempInvernoDia, TempInvernoNoite):
        self.ano = ano
        self.radiacaoSolarInverno = radiacaoSolarInverno
        self.radiacaoSolarVerao = radiacaoSolarVerao
        self.tempMinima = tempMinima
        self.tempMaxima = tempMaxima
        self.TempVeraoDia = TempVeraoDia
        self.TempVeraoNoite = TempVeraoNoite
        self.TempInvernoDia = TempInvernoDia
        self.TempInvernoNoite = TempInvernoNoite

    def ProcessaAno(self, W_Alt, W_dist, ponderarAlt, ponderarDist, EMs):
        def ponderar(campo):
            numerador = 0.0
            denominador = 0.0
            for em in EMs:
                valor = Anual.RetornaInfo(self.ano, campo, em)
                if ponderarAlt:
                    numerador += W_Alt[em.codigo] * valor
                    denominador += W_Alt[em.codigo]
                if ponderarDist:
                    numerador += W_dist[em.codigo] * valor
                    denominador += W_dist[em.codigo]
            return _csharp_round(numerador / denominador, 1)

        return Anual(
            self.ano,
            ponderar("Radiação Solar Inverno"),
            ponderar("Radiação Solar Verão"),
            ponderar("Temperatura Mínima"),
            ponderar("Temperatura Máxima"),
            ponderar("Temperatura Verão-Dia"),
            ponderar("Temperatura Verão-Noite"),
            ponderar("Temperatura Inverno-Dia"),
            ponderar("Temperatura Inverno-Noite"),
        )

    @staticmethod
    def RetornaInfo(anoDesejado, ValorDesejado, em):
        anoTemp = em.SerieAnual[0]
        for ano in em.SerieAnual:
            if ano.ano == anoDesejado:
                anoTemp = ano
                break
        mapa = {
            "Temperatura Mínima": "tempMinima",
            "Temperatura Máxima": "tempMaxima",
            "Radiação Solar Verão": "radiacaoSolarVerao",
            "Radiação Solar Inverno": "radiacaoSolarInverno",
            "Temperatura Verão-Dia": "TempVeraoDia",
            "Temperatura Verão-Noite": "TempVeraoNoite",
            "Temperatura Inverno-Dia": "TempInvernoDia",
        }
        return getattr(anoTemp, mapa.get(ValorDesejado, "TempInvernoNoite"))

    def __str__(self):
        return (_pad(self.ano, 8) +
                _pad(_fmt(self.tempMinima, 1), 12) +
                _pad(_fmt(self.tempMaxima, 1), 12) +
                _pad(_fmt(self.radiacaoSolarVerao, 2), 14) +
                _pad(_fmt(self.radiacaoSolarInverno, 2), 14) +
                _pad(_fmt(self.TempVeraoDia, 1), 14) +
                _pad(_fmt(self.TempVeraoNoite, 1), 14) +
                _pad(_fmt(self.TempInvernoDia, 1), 14) +
                _pad(_fmt(self.TempInvernoNoite, 1), 14))

    def ToString(self):
        return str(self)


class EstacaoMetereologica:
    def __init__(self, *args):
        # Campos da classe original
        self.nomeArquivo = ""
        self.nome = ""
        self.caminho = ""
        self.codigo = ""
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0
        self.situacao = ""
        self.inicioInverno = 0
        self.finalInverno = 0
        self.inicioDia = 0
        self.finalDia = 0
        self.FixarRadSolar = False
        self.RadSolarFixa = 0.0
        self.desconsiderarRadSolarMenor = 0.0
        self.desconsiderarRadSolarMaior = 0.0
        self.limiteDiasEstacao = 0
        self.dataInicial = None
        self.dataFinal = None
        self.SerieHoraria = []
        self.ReportSerieHoraria = ""
        self.SerieDiaria = []
        self.ReportSerieDiaria = ""
        self.SerieAnual = []
        self.ReportSerieAnual = ""
        self.Resultado_Temperaturas = []
        self.ReportTemperaturasCalculadas = ""
        self.ReportProcessamentoEstatistico = ""
        self.descricao = []
        self.Vel_Vento = []
        self.AngIncid = []
        self.CoefAbsorcao = []
        self.CoefEmiss = []
        self.RadSolar = []
        self.CLongaDur = []
        self.CCurtaDur = []
        self.nomeCondutor = ""
        self.nCondFeixe = 0.0
        self.d_Total = 0.0
        self.d_Fios = 0.0
        self.area_Total = 0.0
        self.camadas = 0.0
        self.R20DC = 0.0
        self.DC_AC = ""
        self.C_Var = 0.0
        self.AltMedia = 0.0
        self.TempInicial = 0
        self.TempFinal = 0
        self.quantDesvP = 0
        self.riscoNormalTipico = 0.0
        self.riscoNormalLimite = 0.0
        self.riscoSobreTipico = 0.0
        self.riscoSobreLimite = 0.0
        self.NormalMax_VD = []
        self.NormalMax_VN = []
        self.NormalMax_ID = []
        self.NormalMax_IN = []
        self.SobreMax_VD = []
        self.SobreMax_VN = []
        self.SobreMax_ID = []
        self.SobreMax_IN = []
        for n in [
            "TempNormal_Tipica_VD", "TempNormal_Tipica_VN", "TempNormal_Tipica_ID", "TempNormal_Tipica_IN",
            "TempNormal_Limite_VD", "TempNormal_Limite_VN", "TempNormal_Limite_ID", "TempNormal_Limite_IN",
            "TempSobre_Tipica_VD", "TempSobre_Tipica_VN", "TempSobre_Tipica_ID", "TempSobre_Tipica_IN",
            "TempSobre_Limite_VD", "TempSobre_Limite_VN", "TempSobre_Limite_ID", "TempSobre_Limite_IN"]:
            setattr(self, n, 0.0)
        self.PossuiRadSolar = False
        self.PossuiTempAr = False
        self.progressBar = _Progress()
        self.progress_Label = _Progress()

        if len(args) == 1 and isinstance(args[0], str):
            self.nomeArquivo = args[0]
        elif len(args) == 6 and isinstance(args[0], str):
            self._init_report(*args)
        elif len(args) >= 15 and isinstance(args[0], list):
            self._init_dados(*args)

    @staticmethod
    def _num(s):
        return float(str(s).strip().replace(",", "."))

    @staticmethod
    def _int(s):
        return int(float(str(s).strip().replace(",", ".")))

    def _retorna_dado(self, linhas, chave, idx):
        # Equivalente funcional ao Funcoes.RetornaDado usado no arquivo original.
        for j in range(idx, len(linhas)):
            if linhas[j].startswith(chave):
                return linhas[j][len(chave):].strip(), j + 1
        raise ValueError(f"Dado não encontrado: {chave}")

    def _init_dados(self, A, _nomeArquivo, _caminho, _inicioInverno, _finalInverno,
                    _inicioDia, _finalDia, _FixarRadSolar, _RadSolarFixa,
                    _desconsiderarRadSolarMenor, _desconsiderarRadSolarMaior,
                    _limiteDiasEstacao, _desvPadrao, _progressBar1=None,
                    _progress_Label=None):
        self.progressBar = _progressBar1 or _Progress(); self.progress_Label = _progress_Label or _Progress()
        self.nomeArquivo = _nomeArquivo; 
        self.caminho = _caminho
        self.inicioInverno = _inicioInverno
        self.finalInverno = _finalInverno
        self.inicioDia = _inicioDia
        self.finalDia = _finalDia
        self.FixarRadSolar = _FixarRadSolar
        self.RadSolarFixa = _RadSolarFixa
        self.desconsiderarRadSolarMenor = _desconsiderarRadSolarMenor
        self.desconsiderarRadSolarMaior = _desconsiderarRadSolarMaior
        self.limiteDiasEstacao = _limiteDiasEstacao; 
        self.quantDesvP = _desvPadrao        
        self.nome = A[0].replace("Nome: ", "")
        self.codigo = A[1].replace("Codigo Estacao: ", "")
        self.latitude = self._num(A[2].replace("Latitude: ", ""))
        self.longitude = self._num(A[3].replace("Longitude: ", ""))
        self.altitude = self._num(A[4].replace("Altitude: ", ""))
        self.situacao = A[5].replace("Situacao: ", "")
        # self.dataInicial = datetime.strptime(A[6].replace("Data Inicial: ", ""), "%Y-%m-%d")
        # self.dataFinal = datetime.strptime(A[7].replace("Data Final: ", ""), "%Y-%m-%d")
        i = 10;
        self.progressBar.Maximum = len(A)
        self.progressBar.Value = i
        self.progressBar.Refresh()
        temp = A[i].split(';')
        iRadSolar = 0; iTempAr = 0
        for y, value in enumerate(temp):
            if value == "RADIACAO GLOBAL(Kj/m²)": 
                iRadSolar = y
                self.PossuiRadSolar = True
            if value == "TEMPERATURA DO AR - BULBO SECO, HORARIA(°C)": 
                iTempAr = y
                self.PossuiTempAr = True
        i += 1
        _set_attr(self.progress_Label, "Text", self.nomeArquivo + " - Leitura das medições...") 
        self.progress_Label.Refresh()
        if self.PossuiTempAr and (self.PossuiRadSolar or self.FixarRadSolar):
            while i < len(A) and A[i] != "":
                temp = A[i].split(';')
                if len(temp)>1:
                    horaUTC = int(temp[1])
                    hora = (horaUTC // 100) - 4
                    if hora < 0: 
                        hora += 24
                    data = datetime.strptime(temp[0], "%Y-%m-%d").replace(hour=hora)
                    radiacaoSolar = -9999
                    temperatura = -9999
                    if temp[iRadSolar] != "null":
                        if self.FixarRadSolar: 
                            radiacaoSolar = self.RadSolarFixa
                        else:
                            radiacaoSolar = self._num(temp[iRadSolar])
                            if self.desconsiderarRadSolarMenor * 3.6 < radiacaoSolar < self.desconsiderarRadSolarMaior * 3.6:
                                radiacaoSolar /= 3.6
                            elif (radiacaoSolar < 0):
                                radiacaoSolar = 1
                            else: 
                                radiacaoSolar = -9999
                    if temp[iTempAr] != "null": 
                        temperatura = self._num(temp[iTempAr])
                    m = Medicao(data, radiacaoSolar, temperatura)
                    if m.ValoresValidos(): 
                        self.SerieHoraria.append(m)
                i += 1
                self.progressBar.Increment(1) 
                self.progressBar.Refresh()
            self.progressBar.Value = 0 
            _set_attr(self.progress_Label, "Text", self.nomeArquivo + " - Processando a Série Diária...") 
            self.progress_Label.Refresh()             
            
            _set_attr(self.progress_Label, "Text", self.nomeArquivo + " - Processando a Série Anual...")
            self.progress_Label.Refresh()            

    def GerarRelatorioSerieHoraria(self):
        _set_attr(self.progress_Label, "Text", self.nomeArquivo + " - Escrevendo Relatório com os dados de entrada..."); self.progress_Label.Refresh()
        self.progressBar.Maximum = len(self.SerieHoraria); self.progressBar.Value = 0
        self.ReportSerieHoraria = "DADOS DA SÉRIE HORÁRIA DA ESTAÇÃO " + self.nome + "\n" + _pad("DATA", 10) + _pad("HORA", 10) + _pad("RADIAÇÃO SOLAR (W/m²)", 22) + _pad("TEMPERATURA (°C)", 17)
        for m in self.SerieHoraria:
            self.ReportSerieHoraria += "\n" + m.ToString(); self.progressBar.Increment(1)

    def VeraoOuInverno(self, m):
        date = m.dataHora if hasattr(m, 'dataHora') else m
        return "Inverno" if self.inicioInverno <= date.month <= self.finalInverno else "Verão"

    def DiaOuNoite(self, m):
        date = m.dataHora if hasattr(m, 'dataHora') else m
        return "Dia" if self.inicioDia <= date.hour <= self.finalDia else "Noite"

    def ProcessarSerieDiaria(self):
        i = 0; self.progressBar.Maximum = len(self.SerieHoraria)
        while i < len(self.SerieHoraria):
            dataAtual = self.SerieHoraria[i].dataHora 
            primeira = False
            tempMinima = 9999
            tempMaxima = -9999
            radMax = -9999
            while i < len(self.SerieHoraria) and not primeira:
                if dataAtual.date() == self.SerieHoraria[i].dataHora.date() and i != len(self.SerieHoraria)-1:
                    m = self.SerieHoraria[i]
                    if m.temperatura < tempMinima: 
                        tempMinima = m.temperatura
                    elif m.temperatura > tempMaxima: 
                        tempMaxima = m.temperatura
                    if m.radiacaoSolar > radMax: 
                        radMax = m.radiacaoSolar
                    i += 1
                elif i == len(self.SerieHoraria)-1:
                    m = self.SerieHoraria[i]
                    if m.temperatura < tempMinima: 
                        tempMinima = m.temperatura
                    elif m.temperatura > tempMaxima: 
                        tempMaxima = m.temperatura
                    if m.radiacaoSolar > radMax: 
                        radMax = m.radiacaoSolar
                    if tempMinima != 9999 and tempMaxima != -9999 and radMax != -9999:
                        self.SerieDiaria.append(Diaria(dataAtual, self.VeraoOuInverno(dataAtual), radMax, tempMinima, tempMaxima))
                    primeira = True
                    i += 1
                else:
                    if tempMinima != 9999 and tempMaxima != -9999 and radMax != -9999:
                        self.SerieDiaria.append(Diaria(dataAtual, self.VeraoOuInverno(dataAtual), radMax, tempMinima, tempMaxima))
                    primeira = True
            i += 1
            self.progressBar.Increment(1)
            self.progressBar.Refresh()
            
        self.ReportSerieDiaria = "DADOS DA SÉRIE DIÁRIA DA ESTAÇÃO " + self.nome + "\n"
        self.ReportSerieDiaria += _pad("",10)+_pad("",8)+_pad("",10)+_pad("TEMPERATURA",12)+_pad("TEMPERATURA",12)+_pad("RADIAÇÃO",13)+"\n"
        self.ReportSerieDiaria += _pad("DATA",10)+_pad("ANO",8)+_pad("ESTAÇÃO",10)+_pad("MÍNIMA (°C)",12)+_pad("MÁXIMA (°C)",12)+_pad("SOLAR (W/m²)",13)
        for d in self.SerieDiaria: self.ReportSerieDiaria += "\n" + d.ToString()
        self.progressBar.Value = 0; self.progressBar.Refresh()

    def ProcessarSerieAnual(self):
        self.progressBar.Value = 0 
        self.progressBar.Maximum = len(self.SerieDiaria)
        i = 0
        while i < len(self.SerieDiaria):
            dataAtual = self.SerieDiaria[i].dataHora
            primeira = False
            tempMinima=9999;
            tempMaxima=-9999 
            radV=radI=0
            cRV=cRI=0
            tempVD=tempID=0 
            cVD=cID=0
            while i < len(self.SerieDiaria) and not primeira:
                ultimo = i == len(self.SerieDiaria)-1
                if dataAtual.year == self.SerieDiaria[i].dataHora.year and not ultimo or ultimo:
                    d=self.SerieDiaria[i]
                    if d.tempMinima < tempMinima: 
                        tempMinima=d.tempMinima
                    if d.tempMaxima > tempMaxima: 
                        tempMaxima=d.tempMaxima
                    if self.VeraoOuInverno(d)=="Verão": 
                        radV+=d.radiacaoSolar
                        cRV+=1
                        tempVD+=d.tempMaxima
                        cVD+=1
                    else: 
                        radI+=d.radiacaoSolar
                        cRI+=1
                        tempID+=d.tempMaxima
                        cID+=1
                    if ultimo:
                        # Preserva a lógica do C#: usa contadores de temperatura para dividir radiação.
                        radV = radV / cVD
                        radI = radI / cID
                        tempVD=tempVD/cVD
                        tempID=tempID/cID
                        self.SerieAnual.append(Anual(dataAtual.year, radI, radV, tempMinima, tempMaxima, tempVD,0,tempID,0)); primeira=True; i+=1
                    else: i+=1
                else:
                    radV=radV/cVD
                    radI=radI/cID
                    tempVD=tempVD/cVD 
                    tempID=tempID/cID
                    self.SerieAnual.append(Anual(dataAtual.year, radI, radV, tempMinima, tempMaxima,tempVD,0,tempID,0))
                    primeira=True
            self.progressBar.Increment(1)
            self.progressBar.Refresh()
        # Temperaturas noturnas às 00:00
        self.progressBar.Value=0; self.progressBar.Maximum=len(self.SerieAnual)
        y=0 
        i=0
        while y < len(self.SerieAnual):
            anoAtual=self.SerieAnual[y].ano 
            primeira=False
            tempVN=tempIN=0
            cVN=cIN=0
            while i < len(self.SerieHoraria) and not primeira:
                ultimo=i==len(self.SerieHoraria)-1
                m=self.SerieHoraria[i]
                if anoAtual==m.dataHora.year and not ultimo or ultimo:
                    if m.dataHora.hour==0:
                        if self.VeraoOuInverno(m)=="Verão": 
                            tempVN+=m.temperatura
                            cVN+=1
                        else:
                            tempIN+=m.temperatura
                            cIN+=1
                    if ultimo:
                        tempVN/=cVN
                        tempIN/=cIN
                        self.SerieAnual[y].TempVeraoNoite=tempVN
                        self.SerieAnual[y].TempInvernoNoite=tempIN
                        primeira=True
                        i+=1
                    else: 
                        i+=1
                else:
                    tempVN/=cVN
                    tempIN/=cIN
                    self.SerieAnual[y].TempVeraoNoite=tempVN 
                    self.SerieAnual[y].TempInvernoNoite=tempIN
                    primeira=True
            y+=1
            self.progressBar.Increment(1)
            self.progressBar.Refresh()
            
        # Elimina anos sem o número mínimo de dias de verão/inverno.
        indices=[]
        for idx, anual in enumerate(self.SerieAnual):
            dias=[d for d in self.SerieDiaria if d.dataHora.year==anual.ano]
            cv=sum(1 for d in dias if self.VeraoOuInverno(d)=="Verão")
            ci=sum(1 for d in dias if self.VeraoOuInverno(d)!="Verão")
            if cv < self.limiteDiasEstacao or ci < self.limiteDiasEstacao: 
                indices.append(idx)
        for idx in reversed(indices): 
            self.SerieAnual.pop(idx)
        self.ReportSerieAnual="DADOS DA SÉRIE ANUAL DA ESTAÇÃO "+self.nome+"\n"
        self.ReportSerieAnual += _pad("",8)+_pad("TEMPERATURA",12)+_pad("TEMPERATURA",12)+_pad("RADIAÇÃO",14)+_pad("RADIAÇÃO",14)+_pad("TEMPERATURA",14)+_pad("TEMPERATURA",14)+_pad("TEMPERATURA",14)+_pad("TEMPERATURA",14)+"\n"
        self.ReportSerieAnual += _pad("ANO",8)+_pad("MÍNIMA",12)+_pad("MÁXIMA",12)+_pad("SOLAR VERÃO",14)+_pad("SOLAR INVERNO",14)+_pad("VERÃO-DIA",14)+_pad("VERÃO-NOITE",14)+_pad("INVERNO-DIA",14)+_pad("INVERNO-NOITE",14)+"\n"
        self.ReportSerieAnual += _pad("",8)+_pad("(°C)",12)+_pad("(°C)",12)+_pad("(W/m²)",14)+_pad("(W/m²)",14)+_pad("(°C)",14)+_pad("(°C)",14)+_pad("(°C)",14)+_pad("(°C)",14)
        for a in self.SerieAnual: 
            self.ReportSerieAnual += "\n"+a.ToString()
        self.progressBar.Value=self.progressBar.Maximum
        self.progressBar.Refresh()
        self.progressBar.Value=0
        self.progressBar.Refresh()

    @staticmethod
    def Nu_n(Tc, Ta, D):
        g=9.80665; Tf=(Tc+Ta)/2; Npra=0.715-0.00025*Tf; vf=0.0000132+0.000000095*Tf
        Gr=(D**3*(Tc-Ta)*g)/((Tf+273)*vf**2); GrxNpra=Gr*Npra; A2=0; m2=0
        if 100<GrxNpra<10000: A2=0.850; m2=0.188
        elif 10000<GrxNpra<1000000: A2=0.480; m2=0.250
        return A2*((Gr*Npra)**m2)

    @staticmethod
    def Nu_f(Tc, Ta, vento, D, d, ALT):
        dra=math.exp(-0.000116*ALT); vf=0.0000132+0.000000095*((Tc+Ta)/2); Re=(D*vento*dra)/vf; B2=0; M2=0; RR=d/(2*(D-2*d))
        if 0.05<RR<0.718 and 100<Re<2650: B2=0.641; M2=0.471
        elif RR<0.05 and RR<0.718 and 2650<Re<50000: B2=0.048; M2=0.8
        elif RR>0.05 and 2650<Re<50000: B2=0.178; M2=0.633
        return B2*(Re**M2)

    @staticmethod
    def Nu_corrigido(Nf, angulo):
        A1=0; B2=0; m1=0; pi=math.pi
        if 0<=angulo<=24: A1=0.42; B2=0.68; m1=1.08
        elif angulo<24 and angulo<=90: A1=0.42; B2=0.58; m1=0.90
        return Nf*(A1+B2*(math.sin(angulo*(pi/180))**m1))

    @staticmethod
    def P_c(Tc, Ta, Nu):
        Lf=0.0242+0.000072*((Tc+Ta)/2); return math.pi*Lf*(Tc-Ta)*Nu

    @staticmethod
    def Q_s(As, D, Ib): return As*D*Ib

    @staticmethod
    def P_r(E, D, Tc, Ta): return 0.0000000567*E*math.pi*D*((Tc+273)**4-(Ta+273)**4)

    @staticmethod
    def ConverterDC_AC(camadas, Idc, area):
        if camadas>=3: return Idc/math.sqrt(1.0123+0.0000236)
        Ik=Idc/area
        if Ik<=0.742: return Idc
        if Ik<=2.486:
            return Idc/math.sqrt(1+0.02*(25.62-133.9*Ik+288.8*Ik**2-334.5*Ik**3+226.5*Ik**4-89.73*Ik**5+19.31*Ik**6-1.744*Ik**7))
        if Ik<=3.908:
            return Idc/math.sqrt(1+0.02*(2.978-22.02*Ik+24.87*Ik**2-11.64*Ik**3+2.973*Ik**4-0.4135*Ik**5+0.02445*Ik**6))
        return Idc/math.sqrt(1.1)

    def CalculoTemperaturaLocacao(self,nCondFeixe,d_Total,d_Fios,area_Total,camadas,R20DC,DC_AC,C_Var,Vel_Vento,AngIncid,AltMedia,TempAmb,CoefAbsorcao,CoefEmiss,radincGlobal,CLongaDur,CCurtaDur,TempInicial,TempFinal):
        Temps=[]; Amp=[]
        TL_=TC_=Qs=PcL_=PrL_=PcC_=PrC_=0.0 
        resultado=""
        CLongaDur=_csharp_round(CLongaDur/nCondFeixe,0)
        CCurtaDur=_csharp_round(CCurtaDur/nCondFeixe,0)
        Qs=self.Q_s(CoefAbsorcao,d_Total,radincGlobal)
        T=TempInicial
        proxL=True
        proxC=True
        while T<=TempFinal:
            if Vel_Vento>0.5:
                Nu=self.Nu_f(T,TempAmb,Vel_Vento,d_Total,d_Fios,AltMedia)
                if AngIncid!=90: 
                    Nu=self.Nu_corrigido(Nu,AngIncid)
            elif Vel_Vento==0: 
                Nu=self.Nu_n(T,TempAmb,d_Total)
            else:
                vals=[self.Nu_corrigido(self.Nu_f(T,TempAmb,Vel_Vento,d_Total,d_Fios,AltMedia),45),
                      0.55*self.Nu_f(T,TempAmb,Vel_Vento,d_Total,d_Fios,AltMedia),self.Nu_n(T,TempAmb,d_Total)]
                Nu=max(vals)
            Pc=self.P_c(T,TempAmb,Nu)
            Pr=self.P_r(CoefEmiss,d_Total,T,TempAmb)
            RTc=R20DC*(1+C_Var*(T-20))
            rad=(Pc+Pr-Qs)/RTc
            I=math.sqrt(rad) if rad>=0 else float('nan')
            if DC_AC=="DC": 
                I=self.ConverterDC_AC(camadas,I,area_Total)
            if not math.isnan(I) and not math.isinf(I): 
                resultado += f"{T:14.0f}{I:14.0f}\n"
            if I<CLongaDur: 
                TL_=T; PcL_=Pc; PrL_=Pr
            elif not math.isnan(I) and not math.isinf(I) and proxL: 
                TL_=T; PcL_=Pc; PrL_=Pr; proxL=False
            if I<CCurtaDur: 
                TC_=T; PcC_=Pc; PrC_=Pr
            elif not math.isnan(I) and not math.isinf(I) and proxC: 
                TC_=T; PcC_=Pc; PrC_=Pr; proxC=False
            Amp.append(I) 
            Temps.append(T)
            T+=0.1
        return Temps,Amp,[Qs,PcL_,PrL_,PcC_,PrC_],TL_,TC_,resultado


    def CalculoCorrente(self,nCondFeixe,d_Total,d_Fios,area_Total,camadas,R20DC,DC_AC,C_Var,Vel_Vento,AngIncid,AltMedia,TempAmb,CoefAbsorcao,CoefEmiss,radincGlobal,Temp_Loc):

        Qs=self.Q_s(CoefAbsorcao,d_Total,radincGlobal)
    
        if Vel_Vento>0.5:
            Nu=self.Nu_f(Temp_Loc,TempAmb,Vel_Vento,d_Total,d_Fios,AltMedia)
            if AngIncid!=90: 
                Nu=self.Nu_corrigido(Nu,AngIncid)
        elif Vel_Vento==0: 
            Nu=self.Nu_n(Temp_Loc,TempAmb,d_Total)
        else:
            vals=[self.Nu_corrigido(self.Nu_f(Temp_Loc,TempAmb,Vel_Vento,d_Total,d_Fios,AltMedia),45),
                  0.55*self.Nu_f(Temp_Loc,TempAmb,Vel_Vento,d_Total,d_Fios,AltMedia),self.Nu_n(Temp_Loc,TempAmb,d_Total)]
            Nu=max(vals)
        Pc=self.P_c(Temp_Loc,TempAmb,Nu)
        Pr=self.P_r(CoefEmiss,d_Total,Temp_Loc,TempAmb)
        RTc=R20DC*(1+C_Var*(Temp_Loc-20))
        rad=(Pc+Pr-Qs)/RTc
        I=math.sqrt(rad) if rad>=0 else float('nan')
        if DC_AC=="DC": 
            I=self.ConverterDC_AC(camadas,I,area_Total)
        return I
    
    
    def ProcessarTemperaturasLocacao(self, _descricao=None, _Vel_Vento=None, _AngIncid=None, _CoefAbsorcao=None, _CoefEmiss=None, _RadSolar=None, _CLongaDur=None, _CCurtaDur=None, _nomeCondutor=None, _nCondFeixe=None, _d_Total=None, _d_Fios=None, _area_Total=None, _camadas=None, _R20DC=None, _DC_AC=None, _C_Var=None, _AltMedia=None, _TempInicial=None, _TempFinal=None):
        explicit = _descricao is not None
        if explicit:
            self.descricao=_descricao; self.Vel_Vento=_Vel_Vento; self.AngIncid=_AngIncid; self.CoefAbsorcao=_CoefAbsorcao; self.CoefEmiss=_CoefEmiss; self.RadSolar=_RadSolar; self.CLongaDur=_CLongaDur; self.CCurtaDur=_CCurtaDur; self.nomeCondutor=_nomeCondutor; self.nCondFeixe=_nCondFeixe; self.d_Total=_d_Total; self.d_Fios=_d_Fios; self.area_Total=_area_Total; self.camadas=_camadas; self.R20DC=_R20DC; self.DC_AC=_DC_AC; self.C_Var=_C_Var; self.AltMedia=_AltMedia; self.TempInicial=_TempInicial; self.TempFinal=_TempFinal
        for i, desc in enumerate(self.descricao):
            for anual in self.SerieAnual:
                vel=self.Vel_Vento[i]; ang=self.AngIncid[i]; cL=self.CLongaDur[i]; cC=self.CCurtaDur[i]; ca=self.CoefAbsorcao[i]; ce=self.CoefEmiss[i]; rad=0
                if self.RadSolar[i]=="Sim":
                    rad=self.RadSolarFixa if self.FixarRadSolar else (anual.radiacaoSolarVerao if desc.startswith("Verão") else anual.radiacaoSolarInverno)
                temp = {"Verão-Dia":anual.TempVeraoDia,"Verão-Noite":anual.TempVeraoNoite,"Inverno-Dia":anual.TempInvernoDia,"Inverno-Noite":anual.TempInvernoNoite}[desc]
                tl=self.CalculoTemperaturaLocacao(self.nCondFeixe,self.d_Total,self.d_Fios,self.area_Total,self.camadas,self.R20DC,self.DC_AC,self.C_Var,vel,ang,self.AltMedia,temp,ca,ce,rad,cL,cC,self.TempInicial,self.TempFinal)
                if desc=="Verão-Dia": 
                    self.NormalMax_VD.append(tl[3]) 
                    self.SobreMax_VD.append(tl[4])
                elif desc=="Verão-Noite": 
                    self.NormalMax_VN.append(tl[3])
                    self.SobreMax_VN.append(tl[4])
                elif desc=="Inverno-Dia": 
                    self.NormalMax_ID.append(tl[3])
                    self.SobreMax_ID.append(tl[4])
                elif desc=="Inverno-Noite": 
                    self.NormalMax_IN.append(tl[3])
                    self.SobreMax_IN.append(tl[4])
        self._gerar_relatorio_temperaturas()

    def _gerar_relatorio_temperaturas(self):
        r=""
        r += "\n\nDADOS DO CONDUTOR"+f"\nCONDUTOR: {self.nomeCondutor}"+f"\nQUANT. DE SUBCONDUTORES: {self.nCondFeixe}"
        r += f"\nDIÂMETRO EXTERNO (mm): {self.d_Total*1000:.15g}"+f"\nDIÂMETRO DOS FIOS (mm): {self.d_Fios*1000:.15g}"+f"\nÁREA TOTAL DO CABO (mm²): {self.area_Total*1000000:.15g}"
        r += f"\nCAMADAS DE ALUMÍNIO (unid.): {self.camadas}"+f"\nRESISTÊNCIA ELÉTRICA A 20°C (ohm/km): {self.R20DC*1000:.15g}"+f"\nTIPO DA RESISTÊNCIA ELÉTRICA: {self.DC_AC}"+f"\nCOEFICIENTE DE VARIAÇÃO DA RESISTÊNCIA (ohm/°C): {self.C_Var}"
        r += f"\nFAIXA DE VALORES PARA TEMPERATURA\nTEMPERATURA INICIAL (°C): {self.TempInicial}\nTEMPERATURA FINAL (°C): {self.TempFinal}"
        r += "\n\nDADOS CLIMATOLÓGICOS"+f"\nO INVERNO COMEÇA NO MÊS: {self.inicioInverno}\nO INVERNO TERMINA NO MÊS: {self.finalInverno}\nO DIA COMEÇA NA HORA: {self.inicioDia}\nO DIA TERMINA NA HORA: {self.finalDia}\nDESCONSIDERAR ANOS QUE TENHAM VERÃO E/OU INVERNO COM MENOS DO QUE (DIAS): {self.limiteDiasEstacao}"
        r += "\nFIXAR RADIAÇÃO SOLAR? " + ("SIM" if self.FixarRadSolar else "NÃO") + f"\nVALOR FIXO DA RADIAÇÃO SOLAR (W/M²): {self.RadSolarFixa}\nDESCONSIDERAR VALORES MENORES QUE (W/M²): {self.desconsiderarRadSolarMenor}\nDESCONSIDERAR VALORES MAIORES QUE (W/M²): {self.desconsiderarRadSolarMaior}\nQUANTIDADE DE DESVIOS PADRÃO: {self.quantDesvP}"
        r += f"\n\nDADOS DO PROJETO\nALTITUDE MÉDIA (m): {self.AltMedia}"
        r += "\n"+_pad("VELOCIDADE",27)+_pad("ÂNGULO DE",13)+_pad("",14)+_pad("",14)+_pad("RADIÇÃO",13)+_pad("CORRENTE",13)+_pad("CORRENTE",13)
        r += "\n"+_pad("DESCRIÇÃO",14)+_pad("DO VENTO",13)+_pad("INCIDÊNCIA",13)+_pad("COEF. DE",14)+_pad("COEF. DE",14)+_pad("SOLAR",13)+_pad("LONGA",13)+_pad("CURTA",13)
        r += "\n"+_pad("",14)+_pad("(m/s)",13)+_pad("DO VENTO (°)",13)+_pad("ABSORÇÃO",14)+_pad("EMISSIVIDADE",14)+_pad("[SIM OU NÃO]",13)+_pad("DURAÇÃO (A)",13)+_pad("DURAÇÃO (A)",13)
        for i in range(len(self.descricao)):
            r += "\n"+_pad(self.descricao[i],14)+_pad(f"{self.Vel_Vento[i]:.1f}",13)+_pad(self.AngIncid[i],13)+_pad(self.CoefAbsorcao[i],14)+_pad(self.CoefEmiss[i],14)+_pad(self.RadSolar[i],13)+_pad(self.CLongaDur[i],13)+_pad(self.CCurtaDur[i],13)
        r += "\n\nRESULTADOS\n"+_pad("TEMPERATURA NORMAL",49)+_pad("TEMPERATURA SOBRECORRENTE",56)+"\n"
        r += _pad("ANO",5)+_pad("VERÃO-DIA",14)+_pad("VERÃO-NOITE",14)+_pad("INVERNO-DIA",14)+_pad("INVERNO-NOITE",14)+_pad("VERÃO-DIA",14)+_pad("VERÃO-NOITE",14)+_pad("INVERNO-DIA",14)+_pad("INVERNO-NOITE",14)+"\n"+_pad("",5)+_pad("(°C)",14)*8
        for i in range(len(self.NormalMax_VD)):
            r += "\n"+_pad(self.SerieAnual[i].ano,5)+''.join(_pad(_fmt(v,0),14) for v in [self.NormalMax_VD[i],self.NormalMax_VN[i],self.NormalMax_ID[i],self.NormalMax_IN[i],self.SobreMax_VD[i],self.SobreMax_VN[i],self.SobreMax_ID[i],self.SobreMax_IN[i]])
        self.ReportTemperaturasCalculadas=r

    def Mean(self,A): 
        return sum(A)/len(A)
    def StandardDeviation(self,data):
        if len(data)==0:
            return 0
        mean=self.Mean(data); 
        return math.sqrt(sum((v-mean)**2 for v in data)/len(data))
    
    def CoefGumbel(self,nAmostras):
        N=float(nAmostras)
        Z=[-math.log(-math.log(1-i/(N+1))) for i in range(1,nAmostras+1)]; return self.StandardDeviation(Z),self.Mean(Z)

    def ProcessamentoEstatistico(self,*args):
        if args:
            self.quantDesvP,self.riscoNormalTipico,self.riscoNormalLimite,self.riscoSobreTipico,self.riscoSobreLimite=args
        MN=[self.Mean(x) for x in [self.NormalMax_VD,self.NormalMax_VN,self.NormalMax_ID,self.NormalMax_IN]]; MS=[self.Mean(x) for x in [self.SobreMax_VD,self.SobreMax_VN,self.SobreMax_ID,self.SobreMax_IN]]
        SN=[self.StandardDeviation(x) for x in [self.NormalMax_VD,self.NormalMax_VN,self.NormalMax_ID,self.NormalMax_IN]]; SS=[self.StandardDeviation(x) for x in [self.SobreMax_VD,self.SobreMax_VN,self.SobreMax_ID,self.SobreMax_IN]]
        risks=[self.riscoNormalTipico,self.riscoNormalLimite,self.riscoSobreTipico,self.riscoSobreLimite]; C1,C2=self.CoefGumbel(len(self.NormalMax_VD))
        vals=[]
        for means,sds,risk,reg,cond in [(MN,SN,risks[0],"Nominal","Típica"),(MN,SN,risks[1],"Nominal","Limite"),(MS,SS,risks[2],"Sobrecorrente","Típica"),(MS,SS,risks[3],"Sobrecorrente","Limite")]:
            P=1/(risk/100); Y=-math.log(-math.log(1-1/P)); temps=[m+s*(Y-C2)/C1 for m,s in zip(means,sds)]; vals.append(TemperaturasCalculadas(reg,cond,risk/100,*temps))
        self.TempNormal_Tipica_VD,self.TempNormal_Tipica_VN,self.TempNormal_Tipica_ID,self.TempNormal_Tipica_IN=vals[0].Temp_VD,vals[0].Temp_VN,vals[0].Temp_ID,vals[0].Temp_IN
        self.TempNormal_Limite_VD,self.TempNormal_Limite_VN,self.TempNormal_Limite_ID,self.TempNormal_Limite_IN=vals[1].Temp_VD,vals[1].Temp_VN,vals[1].Temp_ID,vals[1].Temp_IN
        self.TempSobre_Tipica_VD,self.TempSobre_Tipica_VN,self.TempSobre_Tipica_ID,self.TempSobre_Tipica_IN=vals[2].Temp_VD,vals[2].Temp_VN,vals[2].Temp_ID,vals[2].Temp_IN
        self.TempSobre_Limite_VD,self.TempSobre_Limite_VN,self.TempSobre_Limite_ID,self.TempSobre_Limite_IN=vals[3].Temp_VD,vals[3].Temp_VN,vals[3].Temp_ID,vals[3].Temp_IN
        self.Resultado_Temperaturas.extend(vals)
        r="\nRESULTADOS APÓS PROCESSAMENTO ESTATÍSTICO\n"+_pad("REGIME",15)+_pad("CONDIÇÃO",9)+_pad("RISCO TÉRMICO",17)+_pad("VERÃO-DIA",14)+_pad("VERÃO-NOITE",14)+_pad("INVERNO-DIA",14)+_pad("INVERNO-NOITE",14)
        for tc in self.Resultado_Temperaturas:r += "\n"+tc.ToString()
        self.ReportProcessamentoEstatistico=r+"\n\n"

    def ProcessamentoEstatistico2(self,*args):
        if args:
            self.quantDesvP,self.riscoNormalTipico,self.riscoNormalLimite,self.riscoSobreTipico,self.riscoSobreLimite=args
        r="\nRESULTADOS APÓS PROCESSAMENTO ESTATÍSTICO\n"+_pad("REGIME",15)+_pad("CONDIÇÃO",8)+_pad("RISCO TÉRMICO(%)",17)+_pad("VERÃO-DIA",14)+_pad("VERÃO-NOITE",14)+_pad("INVERNO-DIA",14)+_pad("INVERNO-NOITE",14)
        for tc in self.Resultado_Temperaturas:r += "\n"+tc.ToString()
        self.ReportProcessamentoEstatistico=r

    def __str__(self):
        return "\n"+self.ReportSerieDiaria+"\n\n"+self.ReportSerieAnual+"\n\n"+self.ReportTemperaturasCalculadas+self.ReportProcessamentoEstatistico+"\n"
    def ToString(self): return str(self)
    def Clone(self): return copy.copy(self)

    @staticmethod
    def Ponderar(altLT, Lat, Long, pesoAlt, pesoDist, ponderarAlt, ponderarDist, Estacoes):
        r="RESULTADOS APÓS PONDERAÇÃO DAS ESTAÇÕES\n\nMETODOLOGIA CONSIDERADA\n\nVd = SUM(WiVi) / SUM(Wi)\n\nSENDO:\nVd - VALOR DESEJADO\nVi - VALOR DA ESTAÇÃO i\nWi - PESO ASSOCIADO, SENDO DEFINIDO POR:\nWi = 1 / (Di)^P\n\nSENDO:\nDi - DISTÂNCIA ENTRE AS COORDENADAS DAS ESTAÇÕES E O PONTO DESEJADO (W_Di) OU A DIFERENÇA ENTRE AS ALTITUDES (W_ALTi)\nP - PESO ARBITRÁRIO ADOTADO (QUANTO MAIOR, MAIOR A INFLUÊNCIA)\n\nCOORDENADAS CONSIDERADAS"
        r+=f"\nLATITUDE (°): {Lat}\nLONGITUDE (°): {Long}\nALTITUDE (m): {altLT}\nPESO DISTÂNCIA: {pesoDist}\nPESO ALTITUDE: {pesoAlt}\n\n"+_pad("CÓDIGO",8)+_pad("ESTAÇÃO",20)+_pad("LATITUDE(°)",14)+_pad("LONGITUDE(°)",14)+_pad("ALTITUDE(m)",14)
        if ponderarAlt:r+=_pad("DISTÂNCIA(km)",15)+_pad("W_Di",10)
        if ponderarDist:r+=_pad("DIF. ALTITUDE(m)",17)+_pad("W_ALTi",10)
        EMs=list(Estacoes.values()); W_D={}; W_Alt={}
        for em in EMs:
            r+="\n"+_pad(em.codigo,8)+_pad(em.nome,20)+_pad(f"{em.latitude:0.6f}",14)+_pad(f"{em.longitude:0.6f}",14)+_pad(em.altitude,14)
            if ponderarDist:
                dLat=(em.latitude-Lat)*111.1; dLong=(em.longitude-Long)*96.2; dist=math.sqrt(dLat*dLat+dLong*dLong); wd=1/(dist**pesoDist); W_D[em.codigo]=wd; r+=_pad(f"{dist:.3f}",15)+_pad(f"{wd:.4g}",10)
            if ponderarAlt:
                dif=altLT-em.altitude; wa=1/(dif**pesoAlt); W_Alt[em.codigo]=wa; r+=_pad(f"{dif:.2f}",17)+_pad(f"{wa:.4g}",10)
        anoInicial=min(em.SerieAnual[0].ano for em in EMs); anoFinal=max(em.SerieAnual[-1].ano for em in EMs); serie=[]
        for ano in range(anoInicial,anoFinal):
            if all(any(a.ano==ano for a in em.SerieAnual) for em in EMs): serie.append(Anual(ano,0,0,0,0,0,0,0,0))
        EM_Pond=copy.copy(EMs[0]); EM_Pond.nome="RESULTADO DA PONDERAÇÃO ENTRE AS ESTAÇÕES"; serie=[a.ProcessaAno(W_Alt,W_D,ponderarAlt,ponderarDist,EMs) for a in serie]; EM_Pond.SerieAnual=serie
        for name in ["NormalMax_VD","NormalMax_VN","NormalMax_ID","NormalMax_IN","SobreMax_VD","SobreMax_VN","SobreMax_ID","SobreMax_IN"]: setattr(EM_Pond,name,[])
        EM_Pond.ProcessarTemperaturasLocacao(); EM_Pond.Resultado_Temperaturas=[]; EM_Pond.ProcessamentoEstatistico()
        r+="\n\nDADOS DA SÉRIE ANUAL APÓS PONDERAÇÃO\n"+"\n".join(a.ToString() for a in serie)+EM_Pond.ReportTemperaturasCalculadas+EM_Pond.ReportProcessamentoEstatistico
        return r

