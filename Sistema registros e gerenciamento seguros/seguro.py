from datetime import datetime

class Seguro:
    def __init__(self, id_seguro, valor_cobertura, data_inicio, data_fim, tipo_seguro="Seguro"):
        self.id = id_seguro
        self.valor_cobertura = valor_cobertura
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.tipo = tipo_seguro
    
    def calcular_premio(self):
        """Método abstrato para cálculo do prêmio do seguro"""
        raise NotImplementedError("Método deve ser implementado nas subclasses")
    
    def validar_datas(self):
        """Valida as datas de início e fim do seguro"""
        try:
            inicio = datetime.strptime(self.data_inicio, "%d/%m/%Y")
            fim = datetime.strptime(self.data_fim, "%d/%m/%Y")
            return fim > inicio
        except ValueError:
            return False
    
    def to_dict(self):
        """Converte os dados do seguro para um dicionário"""
        return {
            "id": self.id,
            "tipo": self.tipo,
            "valor_cobertura": self.valor_cobertura,
            "data_inicio": self.data_inicio,
            "data_fim": self.data_fim
        }

    @classmethod
    def from_dict(cls, data):
        # Este método será mais útil nas subclasses para instanciar o tipo correto.
        # Para a classe base, pode não ser chamado diretamente se sempre usamos subclasses.
        return cls(
            data["id"],
            data["valor_cobertura"],
            data["data_inicio"],
            data["data_fim"]
        )

class SeguroAutomovel(Seguro):
    def __init__(self, id_seguro, valor_cobertura, data_inicio, data_fim, marca, modelo, ano, placa, estado_conservacao, uso_veiculo, num_condutores):
        super().__init__(id_seguro, valor_cobertura, data_inicio, data_fim, tipo_seguro="Automóvel")
        self.marca = marca
        self.modelo = modelo
        self.ano = ano
        self.placa = placa
        self.estado_conservacao = estado_conservacao
        self.uso_veiculo = uso_veiculo
        self.num_condutores = num_condutores
    
    def calcular_premio(self):
        """Calcula o prêmio do seguro baseado nas características do veículo"""
        premio_base = self.valor_cobertura * 0.05  # 5% do valor de cobertura
        
        # Ajustes baseados no estado de conservação
        multiplicadores_estado = {
            "Novo": 1.0,
            "Semi novo": 1.2,
            "Usado": 1.4
        }
        
        # Ajustes baseados no uso do veículo
        multiplicadores_uso = {
            "Pessoal": 1.0,
            "Compartilhado": 1.3,
            "Profissional": 1.5
        }
        
        premio = premio_base * multiplicadores_estado.get(self.estado_conservacao, 1.4)
        premio *= multiplicadores_uso.get(self.uso_veiculo, 1.5)
        premio *= (1 + (self.num_condutores - 1) * 0.1)  # +10% por condutor adicional
        
        if self.uso_veiculo == "Comercial":
            premio *= 1.2
        
        return premio
    
    def to_dict(self):
        """Converte os dados do seguro de automóvel para um dicionário"""
        dados_base = super().to_dict()
        dados_base.update({
            "marca": self.marca,
            "modelo": self.modelo,
            "ano": self.ano,
            "placa": self.placa,
            "estado_conservacao": self.estado_conservacao,
            "uso_veiculo": self.uso_veiculo,
            "num_condutores": self.num_condutores
        })
        return dados_base

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["id"],
            data["valor_cobertura"],
            data["data_inicio"],
            data["data_fim"],
            data["marca"],
            data["modelo"],
            data["ano"],
            data["placa"],
            data["estado_conservacao"],
            data["uso_veiculo"],
            data["num_condutores"]
        )

class SeguroResidencial(Seguro):
    def __init__(self, id_seguro, valor_cobertura, data_inicio, data_fim, endereco_imovel, area, valor_venal, tipo_construcao):
        super().__init__(id_seguro, valor_cobertura, data_inicio, data_fim, tipo_seguro="Residencial")
        self.endereco_imovel = endereco_imovel
        self.area = area
        self.valor_venal = valor_venal
        self.tipo_construcao = tipo_construcao
    
    def calcular_premio(self):
        """Calcula o prêmio do seguro baseado nas características do imóvel"""
        premio_base = self.valor_cobertura * 0.02  # 2% do valor de cobertura
        
        # Ajustes baseados no tipo de construção
        multiplicadores_construcao = {
            "Alvenaria": 1.0,
            "Madeira": 1.5,
            "Modular": 1.2
        }
        
        # Ajuste baseado na área
        fator_area = 1 + (self.area / 1000)  # +0.1% a cada 10m²
        
        premio = premio_base * multiplicadores_construcao.get(self.tipo_construcao, 1.5)
        premio *= fator_area
        
        if self.tipo_construcao == "Madeira":
            premio *= 1.3
        
        return premio
    
    def to_dict(self):
        """Converte os dados do seguro residencial para um dicionário"""
        dados_base = super().to_dict()
        dados_base.update({
            "endereco_imovel": self.endereco_imovel,
            "area": self.area,
            "valor_venal": self.valor_venal,
            "tipo_construcao": self.tipo_construcao
        })
        return dados_base

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["id"],
            data["valor_cobertura"],
            data["data_inicio"],
            data["data_fim"],
            data["endereco_imovel"],
            data["area"],
            data["valor_venal"],
            data["tipo_construcao"]
        )

class SeguroVida(Seguro):
    def __init__(self, id_seguro, valor_cobertura, data_inicio, data_fim, beneficiarios, tipos_cobertura):
        super().__init__(id_seguro, valor_cobertura, data_inicio, data_fim, tipo_seguro="Vida")
        self.beneficiarios = beneficiarios
        self.tipos_cobertura = tipos_cobertura
    
    def calcular_premio(self):
        """Calcula o prêmio do seguro baseado nas coberturas selecionadas"""
        premio_base = self.valor_cobertura * 0.03  # 3% do valor de cobertura
        
        # Ajuste baseado no número de tipos de cobertura
        fator_coberturas = 1 + (len(self.tipos_cobertura) * 0.1)  # +10% por tipo de cobertura
        
        premio = premio_base * fator_coberturas
        
        return premio * 1.1
    
    def to_dict(self):
        """Converte os dados do seguro de vida para um dicionário"""
        dados_base = super().to_dict()
        dados_base.update({
            "beneficiarios": self.beneficiarios,
            "tipos_cobertura": self.tipos_cobertura
        })
        return dados_base

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["id"],
            data["valor_cobertura"],
            data["data_inicio"],
            data["data_fim"],
            data["beneficiarios"],
            data["tipos_cobertura"]
        ) 