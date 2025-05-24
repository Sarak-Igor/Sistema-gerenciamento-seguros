from datetime import datetime
# Não precisamos mais importar Cliente e Seguro aqui se vamos usar IDs
# from cliente import Cliente 
# from seguro import Seguro

class Apolice:
    def __init__(self, numero, cliente_cpf, seguro_id, status="Ativa"):
        self.numero = numero
        self.cliente_cpf = cliente_cpf # Armazena o CPF do cliente
        self.seguro_id = seguro_id     # Armazena o ID do seguro
        self.data_emissao = datetime.now().strftime("%d/%m/%Y")
        self.status = status  # Ativa, Cancelada, Vencida
        self.sinistros_ids = [] # Lista de IDs de sinistros associados
        # Os objetos Cliente e Seguro serão carregados/associados pelo SistemaSeguros quando necessário
        self.cliente = None # Objeto Cliente carregado
        self.seguro = None  # Objeto Seguro carregado
        self.sinistros = [] # Lista de objetos Sinistro carregados
        self.premio = 0.0 # O prêmio pode ser calculado quando o seguro é associado

    def __str__(self):
        return f"Apólice {self.numero} - Cliente CPF: {self.cliente_cpf} - Seguro ID: {self.seguro_id} - Status: {self.status}"

    def calcular_premio(self):
        if self.seguro: # Calcula apenas se o objeto seguro estiver carregado
            self.premio = self.seguro.calcular_premio()
            return self.premio
        return 0.0

    def adicionar_sinistro_id(self, sinistro_id):
        if sinistro_id not in self.sinistros_ids:
            self.sinistros_ids.append(sinistro_id)
    
    # O método registrar_sinistro(sinistro_obj) pode ser removido ou adaptado
    # se o SistemaSeguros vai gerenciar a adição de sinistros à lista global
    # e apenas vincular por ID aqui.
    # Por ora, vamos manter a lógica de adicionar o objeto sinistro se ele for passado,
    # mas o fluxo principal em SistemaSeguros usará adicionar_sinistro_id.
    def registrar_sinistro(self, sinistro_obj):
        if sinistro_obj and sinistro_obj.id not in self.sinistros_ids:
            self.sinistros_ids.append(sinistro_obj.id)
        if sinistro_obj and sinistro_obj not in self.sinistros:
             self.sinistros.append(sinistro_obj) # Mantém a lista de objetos carregados também

    def cancelar_apolice(self, motivo):
        self.status = "Cancelada"
        self.motivo_cancelamento = motivo
        self.data_cancelamento = datetime.now().strftime("%d/%m/%Y")
        print(f"Apólice {self.numero} cancelada.")

    def to_dict(self):
        # Convertendo objetos Cliente e Seguro para seus IDs para persistência
        return {
            "numero": self.numero,
            "cliente_cpf": self.cliente_cpf,
            "seguro_id": self.seguro_id,
            "data_emissao": self.data_emissao,
            "status": self.status,
            "premio": self.premio,
            "sinistros_ids": self.sinistros_ids, # Salva a lista de IDs de sinistros
            "motivo_cancelamento": getattr(self, 'motivo_cancelamento', None),
            "data_cancelamento": getattr(self, 'data_cancelamento', None)
        }

    @classmethod
    def from_dict(cls, data, cliente_obj, seguro_obj): # Recebe objetos cliente e seguro
        apolice = cls(data["numero"], data["cliente_cpf"], data["seguro_id"], data["status"])
        apolice.data_emissao = data["data_emissao"]
        apolice.premio = data.get("premio", 0.0)
        apolice.cliente = cliente_obj # Associa o objeto cliente carregado
        apolice.seguro = seguro_obj   # Associa o objeto seguro carregado
        # Os sinistros_ids são carregados aqui, e os objetos Sinistro serão vinculados pelo SistemaSeguros
        apolice.sinistros_ids = data.get("sinistros_ids", [])
        apolice.motivo_cancelamento = data.get("motivo_cancelamento")
        apolice.data_cancelamento = data.get("data_cancelamento")
        # A lista apolice.sinistros (objetos) será preenchida pelo SistemaSeguros após carregar todos os sinistros
        return apolice

    def ativar(self):
        """Ativa a apólice"""
        self.status = "Ativa"
    
    def cancelar(self):
        """Cancela a apólice"""
        # Chama o método mais completo para consistência
        self.cancelar_apolice(motivo="Cancelamento solicitado") 
    
    def calcular_valor_indenizacao(self, sinistro):
        """Calcula o valor da indenização para um sinistro"""
        if not self.seguro:
            print("Aviso: Seguro não carregado na apólice para calcular indenização.")
            return 0.0
        if sinistro.valor_prejuizo <= self.seguro.valor_cobertura:
            return sinistro.valor_prejuizo
        return self.seguro.valor_cobertura
    
    # O SEGUNDO MÉTODO to_dict ABAIXO SERÁ REMOVIDO
    # def to_dict(self):
    #     """Converte os dados da apólice para um dicionário"""
    #     return {
    #         "numero": self.numero,
    #         "cliente_cpf": self.cliente_cpf,
    #         "seguro_id": self.seguro_id,
    #         "data_emissao": self.data_emissao,
    #         "status": self.status,
    #         "premio": self.premio,
    #         "sinistros_ids": self.sinistros_ids,
    #         "motivo_cancelamento": getattr(self, 'motivo_cancelamento', None),
    #         "data_cancelamento": getattr(self, 'data_cancelamento', None)
    #     } 