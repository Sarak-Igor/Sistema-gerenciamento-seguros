from datetime import datetime
import json
import os
from cliente import Cliente
from seguro import Seguro, SeguroAutomovel, SeguroResidencial, SeguroVida
from apolice import Apolice
from sinistro import Sinistro
import uuid # Adicionar para gerar IDs únicos

class SistemaSeguros:
    def __init__(self):
        self.clientes = []
        self.seguros = []  # Adicionado para armazenar seguros
        self.apolices = []
        self.sinistros = [] # Adicionado para armazenar sinistros
        self.carregar_dados()
    
    def cadastrar_cliente(self, nome, cpf, data_nasc, endereco, telefone, email):
        """Cadastra um novo cliente no sistema"""
        # 1. Validação de campos obrigatórios básicos (incluindo se o CPF foi fornecido)
        if not nome or not nome.strip():
            print("Erro: Nome do cliente é obrigatório.")
            return None
        if not cpf or not str(cpf).strip(): # Verifica se o CPF original foi fornecido
            print("Erro: CPF do cliente é obrigatório.")
            return None
        if not data_nasc or not data_nasc.strip():
            print("Erro: Data de nascimento do cliente é obrigatória.")
            return None
        if not endereco or not endereco.strip():
            print("Erro: Endereço do cliente é obrigatório.")
            return None
        if not telefone or not str(telefone).strip():
            print("Erro: Telefone do cliente é obrigatório.")
            return None
        if not email or not email.strip():
            print("Erro: Email do cliente é obrigatório.")
            return None

        # 2. Processar/Limpar o CPF
        cpf_limpo = ''.join(filter(str.isdigit, str(cpf)))

        # 3. Validar o formato do CPF limpo (deve ter 11 dígitos)
        if len(cpf_limpo) != 11:
            print(f"Erro: CPF fornecido ('{cpf}') resulta em um formato inválido ('{cpf_limpo}') após limpeza. Deve conter 11 dígitos numéricos.")
            return None
        
        # 4. Verificar duplicidade usando o CPF limpo
        # c.cpf nos objetos Cliente já está armazenado como string limpa de 11 dígitos
        if any(c.cpf == cpf_limpo for c in self.clientes):
            print(f"Erro: CPF {cpf_limpo} já cadastrado.")
            return None
        
        # 5. Criar uma instância temporária de Cliente APENAS para usar seus métodos de validação mais específicos.
        # Passamos o cpf_limpo para o construtor.
        cliente_para_validacao = Cliente(nome, cpf_limpo, data_nasc, endereco, telefone, email)
        
        if not cliente_para_validacao.validar_cpf(): # Usa o validar_cpf() do Cliente
            print(f"Erro: CPF {cpf_limpo} é inválido (algoritmo).")
            return None
        if not cliente_para_validacao.validar_email():
            print(f"Erro: Email '{email}' é inválido.")
            return None
        if not cliente_para_validacao.validar_data_nascimento():
            # A mensagem de erro específica já é impressa dentro de validar_data_nascimento()
            return None
            
        # 6. Se todas as validações passaram, agora sim criamos o objeto final e adicionamos.
        # (Poderíamos reutilizar cliente_para_validacao, mas recriar é mais explícito se houvesse mais lógica)
        cliente_final = Cliente(nome, cpf_limpo, data_nasc, endereco, telefone, email)
        self.clientes.append(cliente_final)
        
        print(f"Cliente {nome} (CPF: {cpf_limpo}) cadastrado com sucesso!")
        self.salvar_clientes()
        return cliente_final
    
    def criar_seguro_automovel(self, valor_cobertura, data_inicio, data_fim, marca, modelo, 
                             ano, placa, estado_conservacao, uso_veiculo, num_condutores):
        """Cria um novo seguro de automóvel"""
        # Validação de campos obrigatórios e tipos básicos
        try:
            vc = float(valor_cobertura)
            if vc <= 0:
                print("Erro: Valor da cobertura deve ser positivo.")
                return None
        except ValueError:
            print("Erro: Valor da cobertura deve ser um número.")
            return None
        if not data_inicio or not data_inicio.strip():
            print("Erro: Data de início do seguro é obrigatória.")
            return None
        if not data_fim or not data_fim.strip():
            print("Erro: Data de fim do seguro é obrigatória.")
            return None
        if not marca or not marca.strip(): print("Erro: Marca do veículo é obrigatória."); return None
        if not modelo or not modelo.strip(): print("Erro: Modelo do veículo é obrigatório."); return None
        if not ano or not str(ano).strip(): print("Erro: Ano do veículo é obrigatório."); return None # Ano pode ser int
        if not placa or not placa.strip(): print("Erro: Placa do veículo é obrigatória."); return None
        if not estado_conservacao or not estado_conservacao.strip(): print("Erro: Estado de conservação é obrigatório."); return None
        if not uso_veiculo or not uso_veiculo.strip(): print("Erro: Uso do veículo é obrigatório."); return None
        try:
            nc = int(num_condutores)
            if nc <= 0:
                print("Erro: Número de condutores deve ser positivo.")
                return None
        except ValueError:
            print("Erro: Número de condutores deve ser um número inteiro.")
            return None

        seguro = SeguroAutomovel(str(uuid.uuid4()), valor_cobertura, data_inicio, data_fim, marca, modelo, ano, placa, 
                                 estado_conservacao, uso_veiculo, num_condutores)
        if not seguro.validar_datas():
            print("Erro: Datas do seguro inválidas.")
            return None
        self.seguros.append(seguro)
        self.salvar_seguros() # Salva apenas seguros
        return seguro

    def criar_seguro_residencial(self, valor_cobertura, data_inicio, data_fim, 
                               endereco_imovel, area, valor_venal, tipo_construcao):
        """Cria um novo seguro residencial"""
        try:
            vc = float(valor_cobertura)
            if vc <= 0: print("Erro: Valor da cobertura deve ser positivo."); return None
        except ValueError: print("Erro: Valor da cobertura deve ser um número."); return None
        if not data_inicio or not data_inicio.strip(): print("Erro: Data de início do seguro é obrigatória."); return None
        if not data_fim or not data_fim.strip(): print("Erro: Data de fim do seguro é obrigatória."); return None
        if not endereco_imovel or not endereco_imovel.strip(): print("Erro: Endereço do imóvel é obrigatório."); return None
        try:
            a = float(area)
            if a <= 0: print("Erro: Área deve ser positiva."); return None
        except ValueError: print("Erro: Área deve ser um número."); return None
        try:
            vv = float(valor_venal)
            if vv <= 0: print("Erro: Valor venal deve ser positivo."); return None
        except ValueError: print("Erro: Valor venal deve ser um número."); return None
        if not tipo_construcao or not tipo_construcao.strip(): print("Erro: Tipo de construção é obrigatório."); return None
        
        seguro = SeguroResidencial(str(uuid.uuid4()), valor_cobertura, data_inicio, data_fim, endereco_imovel, 
                                   area, valor_venal, tipo_construcao)
        if not seguro.validar_datas():
            print("Erro: Datas do seguro inválidas.")
            return None
        self.seguros.append(seguro)
        self.salvar_seguros() # Salva apenas seguros
        return seguro

    def criar_seguro_vida(self, valor_cobertura, data_inicio, data_fim, beneficiarios, tipos_cobertura):
        """Cria um novo seguro de vida"""
        try:
            vc = float(valor_cobertura)
            if vc <= 0: print("Erro: Valor da cobertura deve ser positivo."); return None
        except ValueError: print("Erro: Valor da cobertura deve ser um número."); return None
        if not data_inicio or not data_inicio.strip(): print("Erro: Data de início do seguro é obrigatória."); return None
        if not data_fim or not data_fim.strip(): print("Erro: Data de fim do seguro é obrigatória."); return None
        # Beneficiários e tipos_cobertura podem ser listas ou strings, verificar se não são vazios
        if not beneficiarios: # Para lista ou string não vazia
            print("Erro: Beneficiários são obrigatórios."); return None
        if isinstance(beneficiarios, str) and not beneficiarios.strip():
             print("Erro: Beneficiários (string) não podem ser vazios."); return None
        if not tipos_cobertura:
            print("Erro: Tipos de cobertura são obrigatórios."); return None
        if isinstance(tipos_cobertura, str) and not tipos_cobertura.strip():
             print("Erro: Tipos de cobertura (string) não podem ser vazios."); return None

        seguro = SeguroVida(str(uuid.uuid4()), valor_cobertura, data_inicio, data_fim, beneficiarios, tipos_cobertura)
        if not seguro.validar_datas():
            print("Erro: Datas do seguro inválidas.")
            return None
        self.seguros.append(seguro)
        self.salvar_seguros() # Salva apenas seguros
        return seguro

    def emitir_apolice(self, cliente, seguro):
        """Emite uma nova apólice de seguro"""
        if not cliente or not seguro:
            print("Erro: Cliente ou Seguro inválido para emitir apólice.")
            return None
        numero_apolice = f"AP-{len(self.apolices) + 1:04d}" 
        apolice = Apolice(numero_apolice, cliente.cpf, seguro.id) # Usar IDs/referências
        self.apolices.append(apolice)
        self.salvar_apolices() # Salva apenas apolices
        print(f"Apólice {numero_apolice} emitida para o cliente {cliente.nome}.")
        return apolice

    def registrar_sinistro(self, apolice, data_ocorrencia, descricao, valor_prejuizo):
        """Registra um novo sinistro para uma apólice"""
        if not apolice: # apolice pode ser o objeto ou número da apólice
            print("Erro: Apólice é obrigatória para registrar sinistro.")
            return None
        if not data_ocorrencia or not data_ocorrencia.strip():
            print("Erro: Data de ocorrência do sinistro é obrigatória.")
            return None
        if not descricao or not descricao.strip():
            print("Erro: Descrição do sinistro é obrigatória.")
            return None
        try:
            vp = float(valor_prejuizo)
            if vp <= 0:
                print("Erro: Valor do prejuízo deve ser positivo.")
                return None
        except (ValueError, TypeError): # TypeError para caso valor_prejuizo seja None
            print("Erro: Valor do prejuízo deve ser um número.")
            return None
        
        sinistro_id = str(uuid.uuid4())
        sinistro = Sinistro(sinistro_id, data_ocorrencia, descricao, valor_prejuizo) # Adicionado ID
        
        # Validação da data de ocorrência do sinistro
        # Precisamos do objeto apolice real, não apenas do número
        apolice_obj = self.buscar_apolice_por_numero(apolice.numero if isinstance(apolice, Apolice) else apolice)
        if not apolice_obj:
            print(f"Erro: Apólice com número {apolice.numero if isinstance(apolice, Apolice) else apolice} não encontrada.")
            return None
            
        seguro_obj = self.buscar_seguro_por_id(apolice_obj.seguro_id)
        if not seguro_obj:
            print(f"Erro: Seguro com ID {apolice_obj.seguro_id} não encontrado para a apólice {apolice_obj.numero}.")
            return None

        # Criar um objeto apolice temporário com seguro para validação, se a validação depender do seguro
        apolice_para_validacao = Apolice(apolice_obj.numero, apolice_obj.cliente_cpf, apolice_obj.seguro_id)
        apolice_para_validacao.seguro = seguro_obj # Atribuir o objeto seguro para validação
        
        if not sinistro.validar_data_ocorrencia(apolice_para_validacao): # Passar a apólice com o seguro carregado
            print("Erro: Data de ocorrência do sinistro fora da vigência da apólice.")
            return None
            
        apolice_obj.adicionar_sinistro_id(sinistro.id) # Adiciona o ID do sinistro à apólice
        self.sinistros.append(sinistro) # Adiciona o sinistro à lista principal de sinistros
        self.salvar_sinistros()
        self.salvar_apolices() # Salvar apólices pois o sinistro_id foi adicionado
        print(f"Sinistro {sinistro_id} registrado para a apólice {apolice_obj.numero}.")
        return sinistro

    def buscar_cliente_por_cpf(self, cpf):
        """Busca um cliente pelo CPF"""
        cpf_filtrado = ''.join(filter(str.isdigit, cpf))
        for cliente in self.clientes:
            if cliente.cpf == cpf_filtrado:
                return cliente
        return None

    def buscar_apolice_por_numero(self, numero):
        """Busca uma apólice pelo número"""
        for apolice in self.apolices:
            if apolice.numero == numero:
                return apolice
        return None

    def buscar_apolices_por_cliente(self, cpf):
        """Busca todas as apólices de um cliente pelo CPF"""
        cliente = self.buscar_cliente_por_cpf(cpf)
        if cliente: # cliente é um objeto Cliente
            # Compara o cliente_cpf armazenado na apólice com o cpf do objeto cliente encontrado
            return [apolice for apolice in self.apolices if apolice.cliente_cpf == cliente.cpf]
        return []

    def buscar_seguro_por_id(self, seguro_id):
        """Busca um seguro pelo ID"""
        for s in self.seguros:
            if s.id == seguro_id:
                return s
        return None

    def buscar_sinistro_por_id(self, sinistro_id):
        """Busca um sinistro pelo ID"""
        for s in self.sinistros:
            if s.id == sinistro_id:
                return s
        return None

    def carregar_dados(self):
        """Carrega os dados de clientes, seguros, apólices e sinistros de arquivos JSON"""
        self._carregar_clientes()
        self._carregar_seguros()
        self._carregar_sinistros() # Carregar sinistros antes de apólices para referência
        self._carregar_apolices() # Apólices referenciam clientes, seguros e sinistros

    def _carregar_clientes(self):
        if os.path.exists("clientes.json"):
            try:
                with open("clientes.json", "r") as f:
                    clientes_data = json.load(f)
                    self.clientes = [Cliente.from_dict(c) for c in clientes_data]
            except json.JSONDecodeError:
                print("Erro ao decodificar clientes.json.")
                self.clientes = []
            except Exception as e:
                print(f"Erro ao carregar clientes.json: {e}")
                self.clientes = []
        else:
            self.clientes = []
            # Criar o arquivo se não existir
            with open("clientes.json", "w") as f:
                json.dump([], f)

    def _carregar_seguros(self):
        if os.path.exists("seguros.json"):
            try:
                with open("seguros.json", "r") as f:
                    seguros_data = json.load(f)
                    temp_seguros = []
                    for s_data in seguros_data:
                        tipo_seguro = s_data.get("tipo")
                        seguro_obj = None
                        if tipo_seguro == "Automóvel":
                            seguro_obj = SeguroAutomovel.from_dict(s_data)
                        elif tipo_seguro == "Residencial":
                            seguro_obj = SeguroResidencial.from_dict(s_data)
                        elif tipo_seguro == "Vida":
                            seguro_obj = SeguroVida.from_dict(s_data)
                        else: 
                            seguro_obj = Seguro.from_dict(s_data)
                        if seguro_obj:
                            temp_seguros.append(seguro_obj)
                    self.seguros = temp_seguros
            except json.JSONDecodeError:
                print("Erro ao decodificar seguros.json.")
                self.seguros = []
            except Exception as e:
                print(f"Erro ao carregar seguros.json: {e}")
                self.seguros = []
        else:
            self.seguros = []
            with open("seguros.json", "w") as f:
                json.dump([], f)

    def _carregar_sinistros(self):
        if os.path.exists("sinistros.json"):
            try:
                with open("sinistros.json", "r") as f:
                    sinistros_data = json.load(f)
                    self.sinistros = [Sinistro.from_dict(s) for s in sinistros_data]
            except json.JSONDecodeError:
                print("Erro ao decodificar sinistros.json.")
                self.sinistros = []
            except Exception as e:
                print(f"Erro ao carregar sinistros.json: {e}")
                self.sinistros = []
        else:
            self.sinistros = []
            with open("sinistros.json", "w") as f:
                json.dump([], f)

    def _carregar_apolices(self):
        if os.path.exists("apolices.json"):
            try:
                with open("apolices.json", "r") as f:
                    apolices_data = json.load(f)
                    temp_apolices = []
                    for ap_data in apolices_data:
                        cliente_cpf = ap_data.get("cliente_cpf")
                        seguro_id = ap_data.get("seguro_id")
                        
                        cliente_obj = self.buscar_cliente_por_cpf(cliente_cpf)
                        seguro_obj = self.buscar_seguro_por_id(seguro_id)

                        if cliente_obj and seguro_obj:
                            # Passar os objetos reais para o from_dict da Apolice, se necessário,
                            # ou apenas os IDs e o from_dict lida com a busca (precisa de acesso ao sistema ou listas)
                            # A abordagem atual do from_dict da Apolice precisará ser ajustada
                            apolice = Apolice.from_dict(ap_data, cliente_obj, seguro_obj) # Ajustar Apolice.from_dict
                            
                            # Recuperar e vincular sinistros
                            sinistros_ids_na_apolice = ap_data.get("sinistros_ids", [])
                            for sinistro_id in sinistros_ids_na_apolice:
                                sinistro_obj = self.buscar_sinistro_por_id(sinistro_id)
                                if sinistro_obj:
                                    # Apolice deve ter um método para adicionar o objeto sinistro, não o ID aqui
                                    if not hasattr(apolice, 'sinistros'): # Garantir que a lista exista
                                        apolice.sinistros = []
                                    if sinistro_obj not in apolice.sinistros: # Evitar duplicatas se já carregado de alguma forma
                                        apolice.sinistros.append(sinistro_obj)
                                else:
                                    print(f"Aviso: Sinistro com ID {sinistro_id} referenciado pela apólice {apolice.numero} não encontrado.")
                            temp_apolices.append(apolice)
                        else:
                            if not cliente_obj:
                                print(f"Cliente CPF {cliente_cpf} não encontrado para apólice {ap_data.get('numero')}. Pulando.")
                            if not seguro_obj:
                                print(f"Seguro ID {seguro_id} não encontrado para apólice {ap_data.get('numero')}. Pulando.")
                    self.apolices = temp_apolices
            except json.JSONDecodeError:
                print("Erro ao decodificar apolices.json.")
                self.apolices = []
            except Exception as e:
                print(f"Erro ao carregar apolices.json: {e}")
                self.apolices = []
        else:
            self.apolices = []
            with open("apolices.json", "w") as f:
                json.dump([], f)

    def salvar_dados(self):
        """Salva todos os dados (clientes, seguros, apólices, sinistros)"""
        self.salvar_clientes()
        self.salvar_seguros()
        self.salvar_apolices()
        self.salvar_sinistros()

    def salvar_clientes(self):
        try:
            with open("clientes.json", "w") as f:
                json.dump([c.to_dict() for c in self.clientes], f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar clientes.json: {e}")

    def salvar_seguros(self):
        try:
            with open("seguros.json", "w") as f:
                json.dump([s.to_dict() for s in self.seguros], f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar seguros.json: {e}")
    
    def salvar_apolices(self):
        try:
            with open("apolices.json", "w") as f:
                # Certifique-se que Apolice.to_dict() usa seguro_id e sinistros_ids
                json.dump([ap.to_dict() for ap in self.apolices], f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar apolices.json: {e}")

    def salvar_sinistros(self):
        try:
            with open("sinistros.json", "w") as f:
                json.dump([s.to_dict() for s in self.sinistros], f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar sinistros.json: {e}") 