import pandas as pd
import datetime
import os
import re


class PlanilhaManager:

    def __init__(self, caminho=None):
        self.caminho = caminho

        # Cache interno para evitar releitura do Excel
        self.cache_df = None
        self.cache_mtime = None

    # -----------------------------------------------------------
    #  CARREGAMENTO INTELIGENTE (CACHE)
    # -----------------------------------------------------------
    def _carregar_planilha(self):
        """Carrega a planilha apenas se ela mudou. Retorna o DataFrame."""
        if not self.caminho:
            raise FileNotFoundError("Nenhum caminho de planilha foi definido.")

        if not os.path.exists(self.caminho):
            raise FileNotFoundError(f"Planilha não encontrada: {self.caminho}")

        mtime = os.path.getmtime(self.caminho)

        if self.cache_df is not None and self.cache_mtime == mtime:
            return self.cache_df

        try:
            df = pd.read_excel(self.caminho, header=1)
        except Exception as exc:
            raise IOError(f"Falha ao ler a planilha: {exc}") from exc

        self.cache_df = df
        self.cache_mtime = mtime
        return df

    # -----------------------------------------------------------
    #  DEFINIR CAMINHO
    # -----------------------------------------------------------
    def set_caminho(self, caminho):
        self.caminho = caminho
        self.cache_df = None  # limpa o cache
        self.cache_mtime = None

    # -----------------------------------------------------------
    #  DATAS DISPONÍVEIS
    # -----------------------------------------------------------
    def obter_datas_disponiveis(self):
        df = self._carregar_planilha()

        colunas = self._encontrar_colunas(df)
        if not colunas["data"]:
            raise ValueError(
                "Coluna de data não encontrada. Procurei por: "
                "'Data/Hora do Agendamento', 'Data', 'Agendamento'."
            )

        df = self._renomear_colunas(df, colunas)

        df["data_agendamento"] = pd.to_datetime(df["data_agendamento"], errors="coerce", dayfirst=True)
        df = df.dropna(subset=["data_agendamento"])

        datas = df["data_agendamento"].dt.date.unique()
        return sorted([d.strftime("%d/%m/%Y") for d in datas])

    # -----------------------------------------------------------
    #  CARREGAR CLIENTES POR DATA
    # -----------------------------------------------------------
    def carregar_clientes_por_data(self, data_selecionada):
        df = self._carregar_planilha()

        colunas = self._encontrar_colunas(df)
        if not colunas["data"]:
            raise ValueError(
                "Coluna de data não encontrada. Procurei por: "
                "'Data/Hora do Agendamento', 'Data', 'Agendamento'."
            )

        df = self._renomear_colunas(df, colunas)

        try:
            df["data_agendamento"] = pd.to_datetime(
                df["data_agendamento"], errors="coerce", dayfirst=True
            )
        except Exception as exc:
            raise ValueError("Erro ao converter datas.") from exc

        df = df.dropna(subset=["data_agendamento"])

        try:
            data_filtro = datetime.datetime.strptime(data_selecionada, "%d/%m/%Y")
        except ValueError as exc:
            raise ValueError(f"Data inválida: {data_selecionada}") from exc

        filtrado = df[df["data_agendamento"].dt.normalize() == data_filtro]

        resultado = []

        for _, row in filtrado.iterrows():
            tel = self._formatar_telefone(row.get("telefone", ""))
            if not tel:
                continue

            endereco = self._montar_endereco(row)

            resultado.append({
                "protocolo": str(row.get("protocolo", "N/A")),
                "nome": str(row.get("nome", "Nome não informado")),
                "endereco": endereco,
                "telefone": tel,
                "data_agendamento": row["data_agendamento"].strftime("%d/%m/%Y %H:%M")
            })

        return resultado

    # -----------------------------------------------------------
    #  COLUNAS
    # -----------------------------------------------------------
    def _encontrar_colunas(self, df):
        colunas_df_norm = {str(c).strip().lower(): c for c in df.columns}

        colunas = {
            "data": None,
            "nome": None,
            "telefone": None,
            "protocolo": None,
            "endereco": None,
            "numero": None
        }

        mapeamento = {
            "data": ["data/hora do agendamento", "data", "agendamento", "data agendamento", "hora"],
            "nome": ["cliente", "nome", "nome cliente", "nome do cliente"],
            "telefone": ["telefone celular", "telefone", "celular", "whatsapp", "contato"],
            "protocolo": ["nº. ordem serviço", "protocolo", "ordem serviço", "os", "nº ordem"],
            "endereco": ["endereço", "endereco", "logradouro", "rua"],
            "numero": ["número", "numero", "num", "nº"]
        }

        for tipo, nomes_possiveis in mapeamento.items():
            for nome in nomes_possiveis:
                if nome in colunas_df_norm:
                    colunas[tipo] = colunas_df_norm[nome]
                    break

        return colunas

    # -----------------------------------------------------------
    #  RENOMEAR
    # -----------------------------------------------------------
    def _renomear_colunas(self, df, colunas):
        novo = {}
        if colunas["data"]: novo[colunas["data"]] = "data_agendamento"
        if colunas["nome"]: novo[colunas["nome"]] = "nome"
        if colunas["telefone"]: novo[colunas["telefone"]] = "telefone"
        if colunas["protocolo"]: novo[colunas["protocolo"]] = "protocolo"
        if colunas["endereco"]: novo[colunas["endereco"]] = "endereco"
        if colunas["numero"]: novo[colunas["numero"]] = "numero"
        return df.rename(columns=novo)

    # -----------------------------------------------------------
    #  TELEFONE
    # -----------------------------------------------------------
    def _formatar_telefone(self, telefone):
        if pd.isna(telefone):
            return None

        tel = str(telefone)

        # Regex para extrair apenas os dígitos
        tel = re.sub(r"\D", "", tel)

        if len(tel) == 0:
            return None

        if len(tel) == 8:  # sem DDD
            tel = "83" + tel
        elif len(tel) == 9:
            tel = "83" + tel

        if len(tel) in (10, 11):  # DDD + número
            tel = "55" + tel

        return tel

    # -----------------------------------------------------------
    #  ENDEREÇO
    # -----------------------------------------------------------
    def _montar_endereco(self, row):
        partes = []

        if "endereco" in row and pd.notna(row["endereco"]):
            partes.append(str(row["endereco"]).strip())

        if "numero" in row and pd.notna(row["numero"]):
            partes.append(f"Nº {row['numero']}")

        return " ".join(partes) if partes else "Endereço não informado"
