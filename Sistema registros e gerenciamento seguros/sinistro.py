from datetime import datetime
# from apolice import Apolice # Removido para evitar dependência circular, será ajustado na classe SistemaSeguros

class Sinistro:
    def __init__(self, id_sinistro, data_ocorrencia, descricao, valor_prejuizo, status="Em Análise"):
        self.id = id_sinistro
        self.data_ocorrencia = data_ocorrencia
        self.descricao = descricao
        self.valor_prejuizo = float(valor_prejuizo)
        self.status = status
        self.data_registro = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    def __str__(self):
        return f"Sinistro ID: {self.id} - {self.data_ocorrencia}: {self.descricao} - Prejuízo: R${self.valor_prejuizo:.2f} - Status: {self.status}"
    
    def aprovar(self):
        """Aprova o sinistro"""
        self.status = "Aprovado"
    
    def recusar(self):
        """Recusa o sinistro"""
        self.status = "Recusado"
    
    def validar_data_ocorrencia(self, apolice):
        """Verifica se a data de ocorrência não é futura e está dentro da vigência da apólice."""
        try:
            data_ocorr_obj = datetime.strptime(self.data_ocorrencia, "%d/%m/%Y")
            # Verifica se a data de ocorrência não é futura
            if data_ocorr_obj.date() > datetime.now().date():
                print("Erro: Data de ocorrência do sinistro não pode ser uma data futura.")
                return False
        except ValueError as e:
            print(f"Erro: Formato da data de ocorrência do sinistro inválido ({self.data_ocorrencia}). Use DD/MM/AAAA.")
            return False
        
        if not hasattr(apolice, 'seguro') or not apolice.seguro: 
            print("Aviso: Objeto seguro não encontrado na apólice para validação completa de data do sinistro.")
            # Se o seguro não está carregado, não podemos validar contra a vigência da apólice.
            # Dependendo da política, pode-se retornar True aqui (assumindo que será validado depois) ou False.
            # Por ora, retornamos True para não bloquear o registro apenas por isso, mas com aviso.
            return True 

        try:
            # data_ocorr_obj já foi convertida e validada acima
            data_inicio_apolice = datetime.strptime(apolice.seguro.data_inicio, "%d/%m/%Y")
            data_fim_apolice = datetime.strptime(apolice.seguro.data_fim, "%d/%m/%Y")
            
            if not (data_inicio_apolice <= data_ocorr_obj <= data_fim_apolice):
                print(f"Erro: Data de ocorrência ({self.data_ocorrencia}) fora da vigência da apólice ({apolice.seguro.data_inicio} - {apolice.seguro.data_fim}).")
                return False
            return True
        except ValueError as e:
            # Este erro de ValueError seria para as datas da apólice, o que é menos provável se já foram validadas antes.
            print(f"Erro ao converter datas da apólice para validação do sinistro: {e}")
            return False
        except AttributeError as e:
            print(f"Erro ao acessar atributos de data da apólice/seguro durante validação do sinistro: {e}")
            return False
    
    def to_dict(self):
        """Converte os dados do sinistro para um dicionário"""
        return {
            "id": self.id,
            "data_ocorrencia": self.data_ocorrencia,
            "descricao": self.descricao,
            "valor_prejuizo": self.valor_prejuizo,
            "status": self.status,
            "data_registro": self.data_registro
        }

    @classmethod
    def from_dict(cls, data):
        sinistro = cls(
            data["id"],
            data["data_ocorrencia"],
            data["descricao"],
            data["valor_prejuizo"],
            data.get("status", "Em Análise") # .get para retrocompatibilidade se status não existir
        )
        sinistro.data_registro = data.get("data_registro", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        return sinistro 