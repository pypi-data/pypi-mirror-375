from anpseisearch import SeiRegisterSearcher

# Cria a instância do buscador
searcher = SeiRegisterSearcher()

# Define filtros de pesquisa (form-data do SEI)
filters = {
    "numero_protocolo_sei": "5288361",
    "texto_pesquisa": "",
    "incluir_processos": True,
    "incluir_documentos_gerados": True,
    "incluir_documentos_recebidos": False,
    "tipo_processo": "",    
    "tipo_documento": "",
    "data_inicio": "",
    "data_fim": "",
}

searcher.set_filters(filters)

# Executa a busca
registers = searcher.execute_search()

# Itera sobre os registros encontrados
print(registers)