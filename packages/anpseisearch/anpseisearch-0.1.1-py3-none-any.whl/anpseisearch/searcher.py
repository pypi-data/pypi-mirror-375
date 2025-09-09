import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings
from pathlib import Path
import json


class SeiProcessSearchError(Exception):
    pass


class SeiRegisterSearcher:
    BASE_URL = (
        "https://sei.anp.gov.br/sei/modulos/pesquisa/md_pesq_controlador_ajax_externo.php"
        "?acao_ajax_externo=protocolo_pesquisar&id_orgao_acesso_externo=0"
        "&isPaginacao=true"
    )

    DEFAULT_FORM_DATA = {
        "txtProtocoloPesquisa": "",
        "q": "",
        "chkSinProcessos": "P",
        "chkSinDocumentosGerados": "",
        "chkSinDocumentosRecebidos": "",
        "txtParticipante": "",
        "hdnIdParticipante": "",
        "txtUnidade": "",
        "hdnIdUnidade": "",
        "selTipoProcedimentoPesquisa": "",
        "selSeriePesquisa": "",
        "txtDataInicio": "",
        "txtDataFim": "",
        "txtInfraCaptcha": "2MI42G",
        "hdnInfraCaptcha": "1",
        "txtNumeroDocumentoPesquisa": "",
        "txtAssinante": "",
        "hdnIdAssinante": "",
        "txtDescricaoPesquisa": "",
        "txtAssunto": "",
        "hdnIdAssunto": "",
        "txtSiglaUsuario1": "",
        "txtSiglaUsuario2": "",
        "txtSiglaUsuario3": "",
        "txtSiglaUsuario4": "",
        "hdnSiglasUsuarios": "",
        "hdnCId": "PESQUISA_PUBLICA1757167558039",
        "partialfields": "",
        "requiredfields": "",
        "as_q": "",
        "hdnFlagPesquisa": "1",
    }

    FILTER_TO_SEI_MAP = {
        "numero_protocolo_sei": "txtProtocoloPesquisa",
        "texto_pesquisa": "q",
        "incluir_processos": "chkSinProcessos",
        "incluir_documentos_gerados": "chkSinDocumentosGerados",
        "incluir_documentos_recebidos": "chkSinDocumentosRecebidos",
        "tipo_processo": "selTipoProcedimentoPesquisa",
        "tipo_documento": "selSeriePesquisa",
        "data_inicio": "txtDataInicio",
        "data_fim": "txtDataFim",
    }

    def __init__(self):
        self.search_params = dict(self.DEFAULT_FORM_DATA)
        self.PROCESS_ID = self._load_mapping("process_ids.json")
        self.DOCUMENT_ID = self._load_mapping("document_ids.json")

    def _load_mapping(self, filename):
        path = Path(__file__).parent / "data" / filename
        with path.open(encoding="utf-8") as f:
            return json.load(f)

    def set_filters(self, filters):
        handlers = {
            "incluir_processos": lambda v: "P" if v else "",
            "incluir_documentos_gerados": lambda v: "G" if v else "",
            "incluir_documentos_recebidos": lambda v: "R" if v else "",
            "tipo_processo": lambda v: self.PROCESS_ID.get(v, ""),
            "tipo_documento": lambda v: self.DOCUMENT_ID.get(v, ""),
        }
        for filtro, valor in filters.items():
            chave_sei = self.FILTER_TO_SEI_MAP.get(filtro)
            if not chave_sei:
                continue
            self.search_params[chave_sei] = handlers.get(filtro, lambda v: v)(valor)
        return self.search_params

    def _build_partialfields(self):
        partes = []

        if self.search_params["txtProtocoloPesquisa"]:
            partes.append(f"prot_pesq:*{self.search_params['txtProtocoloPesquisa']}*")

        if self.search_params["selTipoProcedimentoPesquisa"]:
            partes.append(f"id_tipo_proc:{self.search_params['selTipoProcedimentoPesquisa']}")

        if self.search_params["selSeriePesquisa"]:
            partes.append(f"id_serie:{self.search_params['selSeriePesquisa']}")

        flags = ";".join(
            filter(None, [
                self.search_params["chkSinProcessos"],
                self.search_params["chkSinDocumentosGerados"],
                self.search_params["chkSinDocumentosRecebidos"],
            ])
        )
        if flags:
            partes.append(f"sta_prot:{flags}")

        data_inicio = self.search_params["txtDataInicio"]
        data_fim = self.search_params["txtDataFim"]
        if data_inicio and data_fim:
            intervalo = f"[{data_inicio}T00:00:00Z TO {data_fim}T00:00:00Z]"
            partes.append(f"(dta_ger:{intervalo} OR dta_inc:{intervalo})")

        self.search_params["partialfields"] = " AND ".join(partes)

    def execute_search(self, page=0, rows_per_page=50):
        self._build_partialfields()
        inicio = page * rows_per_page
        url = f"{self.BASE_URL}&inicio={inicio}&rowsSolr={rows_per_page}"
        try:
            response = requests.post(url, data=self.search_params)
            response.raise_for_status()
        except requests.RequestException as e:
            raise SeiProcessSearchError(f"Erro na requisição ao SEI: {e}")
        return self._parse_response(response.text)

    @staticmethod
    def _parse_response(raw_response):
        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
        soup = BeautifulSoup(raw_response, "lxml")
        if soup.find("consultavazia"):
            return []
        resultados = []
        registros = soup.find_all("tr", class_="pesquisaTituloRegistro")
        for reg in registros:
            link = reg.find("a", class_="protocoloNormal")
            if not link:
                continue
            protocolo = link.text.strip()
            descricao = reg.get_text(" ", strip=True).replace(protocolo, "").replace("Registro:", "").strip()
            url_processo = link.get("href")
            tr_next = reg.find_next_sibling("tr")
            unidade = tr_next.find("a", class_="ancoraSigla")
            unidade = unidade.text.strip() if unidade else ""
            data = ""
            for td in tr_next.find_all("td"):
                if "Data:" in td.get_text():
                    data = td.get_text().replace("Data:", "").strip()
            resultados.append({
                "protocolo": protocolo,
                "descricao": descricao,
                "unidade": unidade,
                "data": data,
                "link": url_processo
            })
        return resultados