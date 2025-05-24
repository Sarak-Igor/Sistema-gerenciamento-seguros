from datetime import datetime
import re

class Cliente:
    def __init__(self, nome, cpf, data_nasc, endereco, telefone, email):
        self.nome = nome
        self.cpf = ''.join(filter(str.isdigit, str(cpf)))
        self.data_nasc = data_nasc
        self.endereco = endereco
        self.telefone = telefone
        self.email = email
    
    def validar_cpf(self):
        """Valida o CPF utilizando o algoritmo oficial brasileiro."""
        cpf_str = str(self.cpf).replace('.', '').replace('-', '')

        if not cpf_str.isdigit() or len(cpf_str) != 11:
            return False

        # Verifica CPFs inválidos conhecidos (todos os dígitos iguais)
        if cpf_str == cpf_str[0] * 11:
            return False

        # Cálculo do primeiro dígito verificador
        soma = 0
        for i in range(9):
            soma += int(cpf_str[i]) * (10 - i)
        resto = soma % 11
        dv1 = 0 if resto < 2 else 11 - resto
        if dv1 != int(cpf_str[9]):
            return False

        # Cálculo do segundo dígito verificador
        soma = 0
        for i in range(10):
            soma += int(cpf_str[i]) * (11 - i)
        resto = soma % 11
        dv2 = 0 if resto < 2 else 11 - resto
        return dv2 == int(cpf_str[10])
    
    def validar_email(self):
        """Valida o formato do email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(self.email)))
    
    def validar_data_nascimento(self):
        """Valida o formato da data de nascimento e se não é uma data futura."""
        try:
            data_nasc_obj = datetime.strptime(self.data_nasc, "%d/%m/%Y")
            if data_nasc_obj.date() >= datetime.now().date():
                print("Erro: Data de nascimento não pode ser hoje ou uma data futura.")
                return False
            return True
        except ValueError:
            print("Erro: Formato de data de nascimento inválido. Use DD/MM/AAAA.")
            return False
    
    def to_dict(self):
        """Converte os dados do cliente para um dicionário"""
        return {
            "nome": self.nome,
            "cpf": self.cpf,
            "data_nascimento": self.data_nasc,
            "endereco": self.endereco,
            "telefone": self.telefone,
            "email": self.email
        }
    
    @staticmethod
    def from_dict(data):
        """Cria uma instância de Cliente a partir de um dicionário"""
        return Cliente(
            nome=data["nome"],
            cpf=data["cpf"],
            data_nasc=data["data_nascimento"],
            endereco=data["endereco"],
            telefone=data["telefone"],
            email=data["email"]
        ) 