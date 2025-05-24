import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import re
from datetime import datetime
import pandas as pd
from ttkthemes import ThemedTk
from sistema import SistemaSeguros
from usuarios_window import UsuariosWindow
from cliente import Cliente
from seguro import SeguroAutomovel, SeguroResidencial, SeguroVida

class SeguroApp:
    def __init__(self, root, usuario_manager):
        self.root = root
        self.root.title("Sistema de Seguros Hierapolis - Apólices")
        self.root.geometry("950x700")
        self.root.configure(background='white')
        
        # Gerenciador de usuários
        self.usuario_manager = usuario_manager
        
        # Inicializa o armazenamento de dados
        self.sistema = SistemaSeguros()
        self.lista_de_clientes_pessoais = []
        self.lista_de_apolices = []
        self.lista_de_sinistros = []
        self.proximo_numero_apolice = 1  # Inicializa o contador do número da apólice
        self.carregar_dados()  # Carrega dados do arquivo
        self.indice_edicao = None  # Para rastrear a apólice em edição
        
        # Configurar Estilo Global para a Aplicação
        style = ttk.Style(self.root)
        # Configurações de fonte padrão
        default_font = ("Arial", 10)
        header_font = ("Arial", 11, "bold")
        title_font = ("Arial", 12, "bold")

        # Cores
        primary_color = "#007bff" # Azul Hierapolis
        secondary_color = "#6c757d" # Cinza para ações secundárias
        danger_color = "#dc3545" # Vermelho para perigo/cancelar
        light_bg_color = "#f8f9fa" # Um cinza bem claro para alguns fundos
        text_color = "black" # Preto para texto com alto contraste em fundos claros
        white_color = "white"

        style.configure("TFrame", background=white_color)
        style.configure("TLabel", background=white_color, foreground=text_color, font=default_font)
        style.configure("Header.TLabel", background=white_color, foreground=primary_color, font=title_font, padding=(0,5,0,5))
        style.configure("TLabelframe", background=white_color, bordercolor="#dee2e6", relief=tk.SOLID, borderwidth=1)
        style.configure("TLabelframe.Label", background=white_color, foreground=primary_color, font=header_font, padding=(5,2,5,2))
        
        style.configure("TEntry", font=default_font, padding=5)
        style.configure("TCombobox", font=default_font, padding=5)
        style.map("TCombobox", fieldbackground=[('readonly', white_color)])

        # Botão Primário - Texto Preto
        style.configure("TButton", 
                        font=default_font, 
                        padding=(10,5,10,5), 
                        width=15,
                        foreground=text_color,  # Texto PRETO no estado normal
                        background=primary_color)
        style.map("TButton",
                  background=[('pressed', '#004085'), ('active', '#0056b3')],
                  foreground=[('pressed', text_color), ('active', text_color)]
                  )
        
        # Botão Secundário - Texto Preto (já estava, mas garantindo)
        style.configure("Secondary.TButton", 
                        font=default_font, 
                        padding=(10,5,10,5), 
                        width=15,
                        foreground=text_color, 
                        background=secondary_color)
        style.map("Secondary.TButton",
                  background=[('pressed', '#545b62'), ('active', '#5a6268')],
                  foreground=[('pressed', text_color), ('active', text_color)]
                  )

        # Botão de Perigo - Texto Preto
        style.configure("Danger.TButton", 
                        font=default_font, 
                        padding=(10,5,10,5), 
                        width=15,
                        foreground=text_color, # Texto PRETO no estado normal
                        background=danger_color)
        style.map("Danger.TButton",
                  background=[('pressed', '#bd2130'), ('active', '#c82333')],
                  foreground=[('pressed', text_color), ('active', text_color)]
                  )

        style.configure("Treeview.Heading", font=header_font, background=light_bg_color, foreground=text_color, padding=5)
        style.configure("Treeview", font=default_font, rowheight=28, background=white_color, fieldbackground=white_color)
        style.map("Treeview", background=[('selected', primary_color)], foreground=[('selected', white_color)])
        
        style.configure("TNotebook", background=white_color, tabmargins=[2, 5, 2, 0])
        style.configure("TNotebook.Tab", font=default_font, padding=[10, 5], background=light_bg_color, foreground=secondary_color)
        style.map("TNotebook.Tab",
                  background=[("selected", white_color), ('active', light_bg_color)],
                  foreground=[("selected", primary_color), ('active', primary_color)])

        # Configurar menu
        self.criar_menu()
        
        # Criação das abas
        self.tab_control = ttk.Notebook(self.root, style="TNotebook")
        
        # Aba para cadastro de clientes
        self.tab_cadastro = ttk.Frame(self.tab_control, style="TFrame", padding=(10,10,10,10))
        
        # Aba para visualização e exportação
        self.tab_visualizacao = ttk.Frame(self.tab_control, style="TFrame", padding=(10,10,10,10))
        
        self.tab_control.add(self.tab_cadastro, text="  Nova Apólice  ")
        self.tab_control.add(self.tab_visualizacao, text="  Visualizar Apólices  ")
        
        self.tab_control.pack(expand=1, fill="both", padx=10, pady=(5,10))
        
        # Configuração da aba de cadastro
        self.setup_cadastro_tab()
        
        # Configuração da aba de visualização
        self.setup_visualizacao_tab()
        
        # Configurar acesso baseado no tipo de usuário
        self.configurar_acesso()
    
    def criar_menu(self):
        """Cria a barra de menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Exportar para Excel", command=self.exportar_excel)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        
        # Menu Usuário
        user_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Usuário", menu=user_menu)
        user_menu.add_command(label=f"Logado como: {self.usuario_manager.get_usuario_atual()}", state="disabled")
        
        # Adicionar opções apenas para administradores
        if self.usuario_manager.is_admin():
            user_menu.add_command(label="Gerenciar Usuários", command=self.abrir_gerenciamento_usuarios)
            # Adicionar menu de relatórios
            reports_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Relatórios", menu=reports_menu)
            reports_menu.add_command(label="Abrir Relatórios", command=self.abrir_relatorios)
        
        user_menu.add_command(label="Logout", command=self.fazer_logout)
    
    def configurar_acesso(self):
        """Configura o acesso aos elementos da interface baseado no tipo de usuário"""
        is_admin = self.usuario_manager.is_admin()
        
        # Configurar acesso à aba de cadastro
        if not is_admin:
            self.tab_control.hide(0)  # Esconde a aba de cadastro para usuários comuns
        
        # Configurar acesso aos botões de ação
        if not is_admin:
            self.btn_editar.configure(state="disabled")
            self.btn_salvar.configure(state="disabled")
            self.btn_limpar.configure(state="disabled")
            self.btn_exportar.configure(state="disabled")
            self.btn_cancelar.configure(state="disabled")
            self.btn_sinistro.configure(state="disabled")
        else:
            self.btn_editar.configure(state="normal")
            self.btn_salvar.configure(state="normal")
            self.btn_limpar.configure(state="normal")
            self.btn_exportar.configure(state="normal")
            self.btn_cancelar.configure(state="normal")
            self.btn_sinistro.configure(state="normal")
        
        # Atualizar título da janela com o tipo de usuário
        tipo_usuario = "Administrador" if is_admin else "Cliente"
        usuario_atual = self.usuario_manager.get_usuario_atual()
        self.root.title(f"Sistema de Cadastro de Apólices de Seguro - {tipo_usuario}: {usuario_atual}")
    
    def fazer_logout(self):
        """Realiza o logout e fecha a aplicação"""
        self.usuario_manager.logout()
        self.root.quit()
    
    def carregar_dados(self):
        """Carrega dados dos arquivos JSON separados (clientes, apolices, sinistros).
           Realiza uma migração única do antigo seguros.json, se necessário."""
        
        clientes_file = "clientes.json"
        apolices_file = "apolices.json"
        sinistros_file = "sinistros.json"
        seguros_antigo_file = "seguros.json"
        seguros_migrado_file = "seguros.json.migrated"

        # Tenta carregar os arquivos novos
        try:
            if os.path.exists(clientes_file):
                with open(clientes_file, "r", encoding="utf-8") as f:
                    self.lista_de_clientes_pessoais = json.load(f)
            else:
                self.lista_de_clientes_pessoais = []

            if os.path.exists(apolices_file):
                with open(apolices_file, "r", encoding="utf-8") as f:
                    self.lista_de_apolices = json.load(f)
            else:
                self.lista_de_apolices = []

            if os.path.exists(sinistros_file):
                with open(sinistros_file, "r", encoding="utf-8") as f:
                    self.lista_de_sinistros = json.load(f)
            else:
                self.lista_de_sinistros = []
            
            print(f"Dados carregados: {len(self.lista_de_clientes_pessoais)} clientes, "
                  f"{len(self.lista_de_apolices)} apólices, {len(self.lista_de_sinistros)} sinistros.")

        except Exception as e:
            messagebox.showerror("Erro ao Carregar Dados", f"Erro ao ler arquivos JSON: {e}")
            # Inicializa listas como vazias em caso de erro grave na leitura
            self.lista_de_clientes_pessoais = []
            self.lista_de_apolices = []
            self.lista_de_sinistros = []

        # Lógica de Migração Única do antigo seguros.json
        # Condição para migração: apolices.json não existe ou está vazio E seguros.json antigo existe
        if (not os.path.exists(apolices_file) or not self.lista_de_apolices) and os.path.exists(seguros_antigo_file):
            print(f"Arquivo {apolices_file} não encontrado ou vazio. Tentando migrar de {seguros_antigo_file}...")
            try:
                with open(seguros_antigo_file, "r", encoding="utf-8") as f_antigo:
                    dados_antigos_completos = json.load(f_antigo)
                
                print(f"Iniciando migração de {len(dados_antigos_completos)} registros de {seguros_antigo_file}.")
                
                cpfs_clientes_processados = set() # Para evitar duplicatas de clientes
                novos_clientes = []
                novas_apolices = []
                novos_sinistros = []

                for registro_antigo in dados_antigos_completos:
                    # 1. Processar Cliente
                    cpf_cliente = registro_antigo.get("cpf")
                    if cpf_cliente and cpf_cliente not in cpfs_clientes_processados:
                        cliente_data = {
                            "cpf": cpf_cliente,
                            "nome": registro_antigo.get("nome"),
                            "data_nascimento": registro_antigo.get("data_nascimento"),
                            "endereco": registro_antigo.get("endereco"),
                            "telefone": registro_antigo.get("telefone"),
                            "email": registro_antigo.get("email")
                        }
                        novos_clientes.append(cliente_data)
                        cpfs_clientes_processados.add(cpf_cliente)
                    
                    # 2. Processar Apólice
                    numero_apolice_atual = registro_antigo.get("numero_apolice")
                    if numero_apolice_atual is not None: # Apólice deve ter um número
                        apolice_data = {
                            "numero_apolice": numero_apolice_atual,
                            "cpf_cliente": cpf_cliente,
                            "tipo_seguro": registro_antigo.get("tipo_seguro"),
                            "status_apolice": registro_antigo.get("status_apolice", "Ativa"),
                            "data_inicio_apolice": registro_antigo.get("data_inicio_apolice"),
                            "data_fim_apolice": registro_antigo.get("data_fim_apolice"),
                            "valor_assegurado": registro_antigo.get("valor_assegurado"),
                            "dados_especificos": registro_antigo.get("dados_especificos", {}),
                            # Campos de cancelamento, se existirem
                            "data_cancelamento": registro_antigo.get("data_cancelamento"),
                            "motivo_cancelamento": registro_antigo.get("motivo_cancelamento")
                        }
                        # Remover chaves None para não salvar campos vazios desnecessariamente
                        apolice_data = {k: v for k, v in apolice_data.items() if v is not None}
                        novas_apolices.append(apolice_data)

                        # 3. Processar Sinistro (se existir na apólice antiga)
                        if registro_antigo.get("data_sinistro"):
                            sinistro_data = {
                                "numero_apolice": numero_apolice_atual,
                                "data_sinistro": registro_antigo.get("data_sinistro"),
                                "descricao_sinistro": registro_antigo.get("descricao_sinistro"),
                                "status_sinistro": registro_antigo.get("status_sinistro")
                            }
                            novos_sinistros.append(sinistro_data)
                
                # Atualizar listas da instância com os dados migrados
                self.lista_de_clientes_pessoais = novos_clientes
                self.lista_de_apolices = novas_apolices
                self.lista_de_sinistros = novos_sinistros

                # Salvar os dados migrados nos novos arquivos
                self._salvar_lista_em_json(self.lista_de_clientes_pessoais, clientes_file)
                self._salvar_lista_em_json(self.lista_de_apolices, apolices_file)
                self._salvar_lista_em_json(self.lista_de_sinistros, sinistros_file)

                # Renomear o arquivo antigo para evitar nova migração
                try:
                    os.rename(seguros_antigo_file, seguros_migrado_file)
                    print(f"Arquivo {seguros_antigo_file} migrado e renomeado para {seguros_migrado_file}.")
                    messagebox.showinfo("Migração de Dados", 
                                        f"Os dados do arquivo {seguros_antigo_file} foram migrados para a nova estrutura.")
                except OSError as e_rename:
                    print(f"Erro ao renomear {seguros_antigo_file}: {e_rename}")
                    messagebox.showwarning("Migração de Dados", 
                                          f"Os dados foram migrados, mas houve um erro ao renomear o arquivo antigo {seguros_antigo_file}. Recomenda-se renomeá-lo manualmente para {seguros_migrado_file} para evitar futuras migrações.")

            except Exception as e_migracao:
                messagebox.showerror("Erro na Migração", f"Ocorreu um erro durante a migração de dados de {seguros_antigo_file}: {e_migracao}")
                # Em caso de falha na migração, tentamos carregar os novos arquivos como estão (ou vazios)
        
        # Determinar o próximo número de apólice com base nas apólices carregadas/migradas
        if self.lista_de_apolices:
            max_numero = 0
            for apolice in self.lista_de_apolices:
                if "numero_apolice" in apolice and isinstance(apolice["numero_apolice"], int):
                    if apolice["numero_apolice"] > max_numero:
                        max_numero = apolice["numero_apolice"]
            self.proximo_numero_apolice = max_numero + 1
        else:
            self.proximo_numero_apolice = 1
        
        # A lógica antiga de popular/atualizar clientes.json a partir de self.dados_clientes é removida
        # pois a migração e o novo processo de salvamento cuidarão disso.

    def salvar_dados(self):
        """Salva os dados em um arquivo JSON"""
        try:
            with open("seguros.json", "w", encoding="utf-8") as file:
                json.dump(self.dados_clientes, file, ensure_ascii=False, indent=4)
            print(f"Dados salvos com sucesso. Total de apólices: {len(self.dados_clientes)}")
        except Exception as e:
            print(f"Erro ao salvar dados: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível salvar os dados")
    
    def setup_cadastro_tab(self):
        """Configura os elementos da aba de cadastro com novo estilo"""
        # Frame para dados do cliente
        self.frame_cliente = ttk.LabelFrame(self.tab_cadastro, text="Dados do Cliente", style="TLabelframe", padding=(10, 10))
        self.frame_cliente.pack(fill="x", expand=False, padx=10, pady=(0,10))

        # Layout em Grid para melhor alinhamento
        self.frame_cliente.columnconfigure(1, weight=1) # Coluna do Entry expande
        self.frame_cliente.columnconfigure(3, weight=1)

        ttk.Label(self.frame_cliente, text="CPF:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.cpf_entry = ttk.Entry(self.frame_cliente, width=30)
        self.cpf_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.cpf_entry.bind("<FocusOut>", self.preencher_dados_por_cpf)
        self.cpf_entry.bind("<KeyRelease>", lambda event, widget=self.cpf_entry: self._formatar_cpf_entry(event, widget))

        ttk.Label(self.frame_cliente, text="Nome Completo:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.nome_entry = ttk.Entry(self.frame_cliente, width=40)
        self.nome_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(self.frame_cliente, text="Data de Nascimento (dd/mm/yyyy):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.data_nascimento_entry = ttk.Entry(self.frame_cliente, width=20)
        self.data_nascimento_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        self.data_nascimento_entry.bind("<KeyRelease>", lambda event, widget=self.data_nascimento_entry: self._formatar_data_entry(event, widget))

        ttk.Label(self.frame_cliente, text="Telefone:").grid(row=2, column=2, sticky=tk.W, padx=(20,5), pady=5)
        self.telefone_entry = ttk.Entry(self.frame_cliente, width=20)
        self.telefone_entry.grid(row=2, column=3, padx=5, pady=5, sticky=tk.EW)
        self.telefone_entry.bind("<KeyRelease>", lambda event, widget=self.telefone_entry: self._formatar_telefone_entry(event, widget))

        ttk.Label(self.frame_cliente, text="Endereço:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.endereco_entry = ttk.Entry(self.frame_cliente, width=40)
        self.endereco_entry.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(self.frame_cliente, text="E-mail:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.email_entry = ttk.Entry(self.frame_cliente, width=40)
        self.email_entry.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky=tk.EW)

        # Frame para tipo de seguro
        self.frame_tipo_seguro_main = ttk.LabelFrame(self.tab_cadastro, text="Tipo de Seguro", style="TLabelframe", padding=(10,10))
        self.frame_tipo_seguro_main.pack(fill="x", expand=False, padx=10, pady=(0,10))
        self.frame_tipo_seguro_main.columnconfigure(1, weight=1)

        ttk.Label(self.frame_tipo_seguro_main, text="Selecione o tipo:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.tipo_seguro = ttk.Combobox(self.frame_tipo_seguro_main, values=["Automóvel", "Residencial", "Vida"], state="readonly", width=28)
        self.tipo_seguro.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.tipo_seguro.bind("<<ComboboxSelected>>", self.mostrar_campos_seguro)

        # Frame para dados gerais da apólice
        self.frame_dados_apolice = ttk.LabelFrame(self.tab_cadastro, text="Dados Gerais da Apólice", style="TLabelframe", padding=(10,10))
        self.frame_dados_apolice.pack(fill="x", expand=False, padx=10, pady=(0,10))
        self.frame_dados_apolice.columnconfigure(1, weight=1)
        self.frame_dados_apolice.columnconfigure(3, weight=1)

        ttk.Label(self.frame_dados_apolice, text="Data Início (dd/mm/yyyy):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.data_inicio_apolice_entry = ttk.Entry(self.frame_dados_apolice, width=20)
        self.data_inicio_apolice_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.data_inicio_apolice_entry.bind("<KeyRelease>", lambda event, widget=self.data_inicio_apolice_entry: self._formatar_data_entry(event, widget))

        ttk.Label(self.frame_dados_apolice, text="Data Fim (dd/mm/yyyy):").grid(row=0, column=2, sticky=tk.W, padx=(20,5), pady=5)
        self.data_fim_apolice_entry = ttk.Entry(self.frame_dados_apolice, width=20)
        self.data_fim_apolice_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.EW)
        self.data_fim_apolice_entry.bind("<KeyRelease>", lambda event, widget=self.data_fim_apolice_entry: self._formatar_data_entry(event, widget))

        ttk.Label(self.frame_dados_apolice, text="Valor Assegurado (R$):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.valor_assegurado_entry = ttk.Entry(self.frame_dados_apolice, width=20)
        self.valor_assegurado_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.valor_assegurado_entry.bind("<KeyRelease>", lambda event, widget=self.valor_assegurado_entry: self._formatar_valor_monetario_entry(event, widget))

        ttk.Label(self.frame_dados_apolice, text="Status da Apólice:").grid(row=1, column=2, sticky=tk.W, padx=(20,5), pady=5)
        self.status_apolice_combobox = ttk.Combobox(self.frame_dados_apolice, values=["Ativa", "Inativa", "Pendente", "Cancelada"], state="readonly", width=18)
        self.status_apolice_combobox.grid(row=1, column=3, padx=5, pady=5, sticky=tk.EW)
        self.status_apolice_combobox.current(0) # Padrão para "Ativa"

        # Frame para campos específicos do seguro (será preenchido dinamicamente)
        self.frame_especifico = ttk.LabelFrame(self.tab_cadastro, text="Dados Específicos do Seguro", style="TLabelframe", padding=(10,10))
        self.frame_especifico.pack(fill="both", expand=True, padx=10, pady=(0,10))
        # Inicialmente vazio, será populado por mostrar_campos_seguro
        self.campos_especificos = {}
        self.mostrar_campos_seguro() # Chamar para exibir campos do tipo padrão selecionado (se houver)

        # Frame para botões de ação
        self.frame_botoes_cadastro = ttk.Frame(self.tab_cadastro, style="TFrame", padding=(0,10,0,0))
        self.frame_botoes_cadastro.pack(fill="x", expand=False, padx=10, pady=(5,0))

        self.btn_salvar = ttk.Button(self.frame_botoes_cadastro, text="Salvar Apólice", command=self.salvar_apolice, style="TButton")
        self.btn_salvar.pack(side=tk.RIGHT, padx=(5,0))

        self.btn_limpar = ttk.Button(self.frame_botoes_cadastro, text="Limpar Campos", command=self.limpar_campos, style="Secondary.TButton")
        self.btn_limpar.pack(side=tk.RIGHT, padx=(0,5))
    
    def preencher_dados_por_cpf(self, event=None):
        """Preenche automaticamente os dados do cliente se o CPF já existir na lista de clientes."""
        cpf = self.cpf_entry.get()
        # Remover formatação do CPF para busca e validação
        cpf_numerico = re.sub(r'\D', '', cpf)

        if not self.validar_cpf(cpf_numerico): # Validar o CPF numérico
            # Limpar campos se o CPF digitado (mesmo incompleto) não for encontrado
            # e não for um CPF válido ainda.
            # Isso evita manter dados de um cliente anterior se um novo CPF inválido for digitado.
            # self.limpar_campos_cliente() # Função auxiliar se quiser limpar apenas campos do cliente
            return

        cliente_encontrado = None
        # Procurar o cliente em self.lista_de_clientes_pessoais
        for cliente_data in self.lista_de_clientes_pessoais:
            if cliente_data.get("cpf") == cpf_numerico:
                cliente_encontrado = cliente_data
                break
        
        # Limpar campos de dados pessoais antes de preencher ou se não encontrar
        # para garantir que não haja dados de um cliente anterior.
        self.nome_entry.delete(0, tk.END)
        self.data_nascimento_entry.delete(0, tk.END)
        self.endereco_entry.delete(0, tk.END)
        self.telefone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)

        if cliente_encontrado:
            self.nome_entry.insert(0, cliente_encontrado.get("nome", ""))
            self.data_nascimento_entry.insert(0, cliente_encontrado.get("data_nascimento", ""))
            self.endereco_entry.insert(0, cliente_encontrado.get("endereco", ""))
            self.telefone_entry.insert(0, cliente_encontrado.get("telefone", ""))
            self.email_entry.insert(0, cliente_encontrado.get("email", ""))
            # Ao preencher, tornar campos readonly exceto se explicitamente permitido
            # self.nome_entry.config(state='readonly') # Exemplo
        # else: 
            # Se não encontrou, os campos já foram limpos acima.
            # O usuário pode então preencher um novo cliente.
            # self.cpf_entry.focus() # Focar no CPF para nova entrada se necessário
            # Nenhuma ação adicional é necessária aqui, pois os campos já estão limpos.

    def setup_visualizacao_tab(self):
        """Configura os elementos da aba de visualização com novo estilo"""
        # Frame principal da aba de visualização
        # self.tab_visualizacao já tem padding e estilo TFrame do __init__

        # Frame para a lista de apólices (Treeview e Scrollbar)
        self.frame_lista = ttk.LabelFrame(self.tab_visualizacao, text="Apólices Cadastradas", style="TLabelframe", padding=(10,10))
        self.frame_lista.pack(fill="both", expand=True, padx=0, pady=(0,10)) # Removido padx daqui, já está no frame da aba

        # Treeview para exibir as apólices
        colunas = ("numero_apolice", "nome", "cpf", "tipo_seguro", "status_apolice", "valor_assegurado")
        self.tree = ttk.Treeview(self.frame_lista, columns=colunas, show="headings", style="Treeview", selectmode="browse")

        self.tree.heading("numero_apolice", text="Nº Apólice")
        self.tree.heading("nome", text="Cliente")
        self.tree.heading("cpf", text="CPF Cliente")
        self.tree.heading("tipo_seguro", text="Tipo de Seguro")
        self.tree.heading("status_apolice", text="Status")
        self.tree.heading("valor_assegurado", text="Valor (R$)")

        # Ajustar a largura das colunas e alinhamento
        self.tree.column("numero_apolice", width=80, anchor=tk.CENTER)
        self.tree.column("nome", width=200)
        self.tree.column("cpf", width=120, anchor=tk.CENTER)
        self.tree.column("tipo_seguro", width=120, anchor=tk.CENTER)
        self.tree.column("status_apolice", width=80, anchor=tk.CENTER)
        self.tree.column("valor_assegurado", width=100, anchor=tk.E) # Alinhado à direita para valor

        scrollbar = ttk.Scrollbar(self.frame_lista, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        # Frame para botões de ação, organizado horizontalmente
        self.frame_acoes = ttk.Frame(self.tab_visualizacao, style="TFrame")
        self.frame_acoes.pack(fill="x", pady=(5,0))

        # Botões com o novo estilo e um pouco mais de padding interno no texto se necessário
        # Usar um frame interno para agrupar botões e centralizá-los ou alinhá-los
        botoes_group_frame = ttk.Frame(self.frame_acoes, style="TFrame")
        # Para centralizar o grupo de botões:
        # botoes_group_frame.pack(anchor=tk.CENTER, pady=5) 
        # Ou para alinhar à esquerda (padrão do pack sem side)
        botoes_group_frame.pack(pady=5)

        self.btn_atualizar = ttk.Button(botoes_group_frame, text="Atualizar", command=self.atualizar_lista, style="Secondary.TButton", width=12)
        self.btn_atualizar.pack(side=tk.LEFT, padx=3)

        self.btn_exportar = ttk.Button(botoes_group_frame, text="Exportar XLS", command=self.exportar_excel, style="Secondary.TButton", width=12)
        self.btn_exportar.pack(side=tk.LEFT, padx=3)

        self.btn_detalhes = ttk.Button(botoes_group_frame, text="Ver Detalhes", command=self.ver_detalhes, style="TButton", width=12)
        self.btn_detalhes.pack(side=tk.LEFT, padx=3)

        self.btn_editar = ttk.Button(botoes_group_frame, text="Editar", command=self.editar_apolice, style="TButton", width=10)
        self.btn_editar.pack(side=tk.LEFT, padx=3)

        self.btn_cancelar = ttk.Button(botoes_group_frame, text="Cancelar Apólice", command=self.cancelar_apolice, style="Danger.TButton", width=15) # Estilo de perigo
        self.btn_cancelar.pack(side=tk.LEFT, padx=3)

        self.btn_sinistro = ttk.Button(botoes_group_frame, text="Gerenciar Sinistro", command=self.gerenciar_sinistro, style="TButton", width=15)
        self.btn_sinistro.pack(side=tk.LEFT, padx=3)

        self.atualizar_lista() # Carregar dados na treeview ao iniciar
    
    def mostrar_campos_seguro(self, event=None):
        """Exibe os campos específicos de acordo com o tipo de seguro selecionado, com estilo."""
        for widget in self.frame_especifico.winfo_children():
            widget.destroy()

        self.campos_especificos = {}
        tipo = self.tipo_seguro.get()

        # Usar grid para alinhar os campos dentro de self.frame_especifico
        self.frame_especifico.columnconfigure(1, weight=1) # Coluna do widget de entrada expande

        row_counter = 0

        def add_campo_especifico(label_text, tipo_widget, widget_kwargs=None, grid_options=None):
            nonlocal row_counter
            if widget_kwargs is None: widget_kwargs = {}
            if grid_options is None: grid_options = {}

            label = ttk.Label(self.frame_especifico, text=label_text, style="TLabel")
            label.grid(row=row_counter, column=0, sticky=tk.W, padx=5, pady=(5,2))
            
            widget = None
            if tipo_widget == "Entry":
                widget = ttk.Entry(self.frame_especifico, **widget_kwargs)
            elif tipo_widget == "Combobox":
                widget = ttk.Combobox(self.frame_especifico, state="readonly", **widget_kwargs)
            elif tipo_widget == "Text":
                # Para Text, criamos um frame com scrollbar, pois Text não é um widget ttk nativo com estilo fácil
                text_frame = ttk.Frame(self.frame_especifico, style="TFrame") # Usar TFrame para consistência
                text_frame.grid(row=row_counter, column=1, sticky=tk.NSEW, padx=5, pady=2, **grid_options)
                text_frame.rowconfigure(0, weight=1)
                text_frame.columnconfigure(0, weight=1)
                
                widget = tk.Text(text_frame, relief=tk.SOLID, borderwidth=1, font=("Arial", 10), **widget_kwargs) # Estilo básico para Text
                scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=widget.yview)
                widget.configure(yscrollcommand=scrollbar.set)
                
                widget.grid(row=0, column=0, sticky=tk.NSEW)
                scrollbar.grid(row=0, column=1, sticky=tk.NS)
                self.frame_especifico.rowconfigure(row_counter, weight=1 if tipo_widget == "Text" and widget_kwargs.get("height",0) > 1 else 0)

            if widget and tipo_widget != "Text": # Text já foi colocado no grid dentro de seu próprio frame
               widget.grid(row=row_counter, column=1, sticky=tk.EW, padx=5, pady=2, **grid_options)
            
            # Adicionar ao dicionário de campos específicos
            # A chave será o label_text simplificado (ex: "Marca" -> "marca")
            chave_campo = label_text.lower().replace(" ", "_").replace(":", "").replace("(","").replace(")","")
            self.campos_especificos[chave_campo] = widget
            row_counter += 1
            return widget

        if tipo == "Automóvel":
            add_campo_especifico("Marca:", "Entry", {"width": 40})
            add_campo_especifico("Modelo:", "Entry", {"width": 40})
            add_campo_especifico("Ano:", "Entry", {"width": 10})
            add_campo_especifico("Placa:", "Entry", {"width": 15})
            add_campo_especifico("Estado de Conservação:", "Combobox", {"values": ["Novo", "Semi novo", "Usado"], "width": 20})
            add_campo_especifico("Uso Principal:", "Combobox", {"values": ["Pessoal", "Comercial", "Misto"], "width": 20})
            add_campo_especifico("Condutores (separar por vírgula se mais de um):", "Entry", {"width": 50})
            
        elif tipo == "Residencial":
            add_campo_especifico("Endereço do Imóvel:", "Entry", {"width": 50})
            add_campo_especifico("Área Construída (m²):", "Entry", {"width": 15})
            add_campo_especifico("Valor Venal (R$):", "Entry", {"width": 20})
            add_campo_especifico("Tipo de Construção:", "Combobox", {"values": ["Alvenaria", "Madeira", "Mista"], "width": 20})
            add_campo_especifico("Coberturas Adicionais (separar por vírgula):", "Entry", {"width": 50})

        elif tipo == "Vida":
            add_campo_especifico("Beneficiários (separar por vírgula):", "Text", {"height": 3, "width": 50})
            # Para Checkbuttons, a abordagem é um pouco diferente, vamos usar TCheckbutton
            # e precisaremos de variáveis tk.BooleanVar para cada um.
            self.coberturas_vars = {}
            coberturas_vida = [
                "Morte (natural ou acidental)", 
                "Invalidez permanente (total ou parcial) por acidente", 
                "Doenças graves", 
                "Assistência Funeral"
            ]
            ttk.Label(self.frame_especifico, text="Coberturas Desejadas:", style="TLabel").grid(row=row_counter, column=0, columnspan=2, sticky=tk.W, padx=5, pady=(10,2))
            row_counter += 1
            for cob in coberturas_vida:
                var = tk.BooleanVar()
                chk = ttk.Checkbutton(self.frame_especifico, text=cob, variable=var, style="TCheckbutton")
                chk.grid(row=row_counter, column=0, columnspan=2, sticky=tk.W, padx=15, pady=1)
                chave_cobertura = cob.split(" (")[0].lower().replace(" ", "_") + "_var"
                self.coberturas_vars[chave_cobertura] = var
                self.campos_especificos[chave_cobertura] = chk # Adicionar checkbutton aos campos para referência se necessário
                row_counter += 1
        
        # Garantir que o último LabelFrame (frame_especifico) tenha algum espaço abaixo se for o último elemento visível antes dos botões
        # Isso é mais uma questão de layout geral da aba do que desta função específica.

    def validar_cpf(self, cpf):
        """Valida o formato do CPF"""
        cpf = ''.join(filter(str.isdigit, cpf))
        if len(cpf) != 11:
            return False
        return True
    
    def validar_data(self, data):
        """Valida o formato da data"""
        try:
            datetime.strptime(data, "%d/%m/%Y")
            return True
        except ValueError:
            return False
    
    def validar_email(self, email):
        """Valida o formato do email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def salvar_apolice(self):
        """Coleta dados do formulário, valida, separa em dados de cliente e apólice,
           e salva/atualiza em suas respectivas listas e arquivos JSON."""
        
        # Validações (mantidas como antes)
        if not self.nome_entry.get() or not self.cpf_entry.get() or not self.data_nascimento_entry.get() or not self.tipo_seguro.get():
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios (Nome, CPF, Nascimento, Tipo de Seguro)")
            return
        
        cpf_cliente = self.cpf_entry.get()
        if not self.validar_cpf(cpf_cliente):
            messagebox.showerror("Erro", "CPF inválido. Deve conter 11 dígitos.")
            return
        if not self.validar_data(self.data_nascimento_entry.get()):
            messagebox.showerror("Erro", "Data de nascimento inválida. Use o formato dd/mm/yyyy.")
            return
        
        if self.email_entry.get() and not self.validar_email(self.email_entry.get()):
            messagebox.showerror("Erro", "E-mail inválido.")
            return
        
        data_inicio_str = self.data_inicio_apolice_entry.get()
        data_fim_str = self.data_fim_apolice_entry.get()
        valor_assegurado_str = self.valor_assegurado_entry.get()

        if not data_inicio_str or not self.validar_data(data_inicio_str):
            messagebox.showerror("Erro", "Data de início da apólice inválida ou não preenchida. Use o formato dd/mm/yyyy.")
            return
        if not data_fim_str or not self.validar_data(data_fim_str):
            messagebox.showerror("Erro", "Data final da apólice inválida ou não preenchida. Use o formato dd/mm/yyyy.")
            return
        try:
            data_inicio_obj = datetime.strptime(data_inicio_str, "%d/%m/%Y")
            data_fim_obj = datetime.strptime(data_fim_str, "%d/%m/%Y")
            if data_fim_obj <= data_inicio_obj:
                messagebox.showerror("Erro", "Data final da apólice deve ser posterior à data de início.")
                return
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido para comparação.")
            return
        if not valor_assegurado_str:
            messagebox.showerror("Erro", "Valor assegurado não preenchido.")
            return
        try:
            valor_assegurado_float = float(valor_assegurado_str.replace(".", "").replace(",", "."))
            if valor_assegurado_float <= 0:
                messagebox.showerror("Erro", "Valor assegurado deve ser um número positivo.")
                return
        except ValueError:
            messagebox.showerror("Erro", "Valor assegurado inválido. Deve ser um número.")
            return

        # 1. Preparar dados do Cliente
        dados_cliente_pessoais = {
            "cpf": cpf_cliente,
            "nome": self.nome_entry.get(),
            "data_nascimento": self.data_nascimento_entry.get(),
            "endereco": self.endereco_entry.get(),
            "telefone": self.telefone_entry.get(),
            "email": self.email_entry.get()
        }

        # 2. Preparar dados da Apólice
        dados_nova_apolice = {
            # numero_apolice será definido abaixo (novo ou existente)
            "cpf_cliente": cpf_cliente, # Link para o cliente
            "tipo_seguro": self.tipo_seguro.get(),
            "status_apolice": self.status_apolice_combobox.get(), # Usar o novo combobox
            "data_inicio_apolice": data_inicio_str,
            "data_fim_apolice": data_fim_str,
            "valor_assegurado": valor_assegurado_float,
            "dados_especificos": {}
        }
        for campo, widget in self.campos_especificos.items():
            if hasattr(widget, 'get'):
                if isinstance(widget, tk.Text):
                    dados_nova_apolice["dados_especificos"][campo] = widget.get("1.0", tk.END).strip()
                else:
                    dados_nova_apolice["dados_especificos"][campo] = widget.get()

        mensagem_sucesso = ""
        numero_apolice_final = None

        # 3. Lógica de Edição vs. Nova Apólice
        if self.indice_edicao is not None: # Editando apólice existente
            apolice_existente = self.lista_de_apolices[self.indice_edicao]
            numero_apolice_final = apolice_existente.get("numero_apolice")
            dados_nova_apolice["numero_apolice"] = numero_apolice_final
            
            # Campos de cancelamento são parte da apólice, podem ser atualizados na edição
            dados_nova_apolice["data_cancelamento"] = apolice_existente.get("data_cancelamento") 
            dados_nova_apolice["motivo_cancelamento"] = apolice_existente.get("motivo_cancelamento")

            self.lista_de_apolices[self.indice_edicao] = dados_nova_apolice
            
            # Atualizar dados do cliente em lista_de_clientes_pessoais
            cliente_atualizado = False
            for i, cliente in enumerate(self.lista_de_clientes_pessoais):
                if cliente["cpf"] == cpf_cliente:
                    self.lista_de_clientes_pessoais[i] = dados_cliente_pessoais
                    cliente_atualizado = True
                    break
            if not cliente_atualizado: # Deveria existir, mas por segurança
                self.lista_de_clientes_pessoais.append(dados_cliente_pessoais)
            
            mensagem_sucesso = "Apólice atualizada com sucesso!"
        
        else: # Nova apólice
            numero_apolice_final = self.proximo_numero_apolice
            dados_nova_apolice["numero_apolice"] = numero_apolice_final
            self.proximo_numero_apolice += 1
            self.lista_de_apolices.append(dados_nova_apolice)

            # Adicionar ou atualizar cliente em lista_de_clientes_pessoais
            cliente_existia = False
            for i, cliente in enumerate(self.lista_de_clientes_pessoais):
                if cliente["cpf"] == cpf_cliente:
                    self.lista_de_clientes_pessoais[i] = dados_cliente_pessoais # Atualiza se já existe
                    cliente_existia = True
                    break
            if not cliente_existia:
                self.lista_de_clientes_pessoais.append(dados_cliente_pessoais)
            
            # Lógica de cadastro de usuário (mantida como antes)
            try:
                # Determinar o tipo de usuário. Se for CPF do cliente, tipo "Cliente".
                # Administradores são cadastrados manualmente ou por outra interface.
                tipo_usuario_cadastro = "Cliente" 
                self.usuario_manager.cadastrar_usuario(cpf_cliente, "12345", tipo_usuario_cadastro)
                print(f"Usuário {cpf_cliente} (tipo: {tipo_usuario_cadastro}) cadastrado/verificado com sucesso.")
            except ValueError as e_user:
                if "Usuário já existe" in str(e_user) or "Nome de usuário já cadastrado" in str(e_user):
                    print(f"Usuário {cpf_cliente} já existe, continuando com cadastro da apólice.")
                else:
                    messagebox.showerror("Erro ao criar usuário associado", str(e_user))
                    return
            except Exception as e_user_inesperado:
                messagebox.showerror("Erro inesperado ao criar usuário", str(e_user_inesperado))
                return
            mensagem_sucesso = "Apólice cadastrada com sucesso!"

        # 4. Salvar listas atualizadas nos arquivos JSON
        self._salvar_lista_em_json(self.lista_de_clientes_pessoais, "clientes.json")
        self._salvar_lista_em_json(self.lista_de_apolices, "apolices.json")
        # Sinistros são salvos separadamente pela função gerenciar_sinistro

        self.atualizar_lista() # Esta função precisará ser refatorada depois
        messagebox.showinfo("Sucesso", mensagem_sucesso)
        self.limpar_campos() # Esta função também precisará ser refatorada

    def limpar_campos(self, limpar_indice_edicao=True):
        """Limpa todos os campos do formulário"""
        # Não limpa mais usuario_entry e senha_entry
        # self.tipo_seguro.current(0) # Não definir current(0) aqui, set('') é melhor
        
        # Limpar campo Número Apólice e atualizar para o próximo se não estiver editando
        self.data_inicio_apolice_entry.delete(0, tk.END)
        self.data_fim_apolice_entry.delete(0, tk.END)
        self.valor_assegurado_entry.delete(0, tk.END)
        
        # Limpar campos pessoais
        self.nome_entry.delete(0, tk.END)
        self.cpf_entry.delete(0, tk.END)
        self.cpf_entry.config(state='normal') # Garantir que o CPF esteja editável
        self.data_nascimento_entry.delete(0, tk.END)
        self.endereco_entry.delete(0, tk.END)
        self.telefone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        
        self.status_apolice_combobox.current(0) # Reset para "Ativa"
        self.tipo_seguro.set('') # Limpa a seleção do combobox de tipo de seguro
        
        # Limpar campos específicos (isso vai disparar mostrar_campos_seguro com tipo vazio)
        self.mostrar_campos_seguro() 
        
        # Resetar o modo de edição, se aplicável
        if limpar_indice_edicao:
            self.indice_edicao = None
            self.btn_salvar.config(text="Salvar Apólice")
            # Habilitar edição do CPF se saiu do modo de edição
            self.cpf_entry.config(state='normal')
    
    def _salvar_lista_em_json(self, lista, arquivo):
        """Salva uma lista em um arquivo JSON"""
        try:
            with open(arquivo, "w", encoding="utf-8") as f:
                json.dump(lista, f, ensure_ascii=False, indent=4)
            print(f"Dados salvos com sucesso em {arquivo}")
        except Exception as e:
            print(f"Erro ao salvar dados em {arquivo}: {e}")
            messagebox.showerror("Erro ao Salvar Dados", f"Não foi possível salvar os dados em {arquivo}: {e}")

    def atualizar_lista(self):
        """Atualiza a lista de apólices na aba de visualização, buscando dados do cliente em lista_de_clientes_pessoais."""
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            print(f"Atualizando lista. Total de apólices: {len(self.lista_de_apolices)}, Total de clientes: {len(self.lista_de_clientes_pessoais)}")
            
            # Criar um dicionário de clientes para busca rápida por CPF
            clientes_dict = {cliente.get("cpf"): cliente for cliente in self.lista_de_clientes_pessoais}

            for i, apolice in enumerate(self.lista_de_apolices):
                numero_apolice = apolice.get("numero_apolice", "N/A")
                cpf_cliente_da_apolice = apolice.get("cpf_cliente")
                tipo_seguro = apolice.get("tipo_seguro", "N/A")
                status_apolice = apolice.get("status_apolice", "N/A")

                nome_cliente_display = "Cliente não encontrado"
                cpf_cliente_display_formatado = cpf_cliente_da_apolice if cpf_cliente_da_apolice else "N/A"

                if cpf_cliente_da_apolice and cpf_cliente_da_apolice in clientes_dict:
                    cliente_obj = clientes_dict[cpf_cliente_da_apolice]
                    nome_cliente_display = cliente_obj.get("nome", "N/A")
                    # Formatar CPF do cliente para exibição
                    cpf_original = cliente_obj.get("cpf", "")
                    if cpf_original.isdigit() and len(cpf_original) == 11:
                        cpf_cliente_display_formatado = f"{cpf_original[:3]}.{cpf_original[3:6]}.{cpf_original[6:9]}-{cpf_original[9:]}"
                    else:
                        cpf_cliente_display_formatado = cpf_original
                elif cpf_cliente_da_apolice:
                    print(f"Aviso: Cliente com CPF {cpf_cliente_da_apolice} não encontrado para a apólice {numero_apolice}.")
                
                valores = (
                    numero_apolice,
                    nome_cliente_display,
                    cpf_cliente_display_formatado,
                    tipo_seguro,
                    status_apolice
                )
                # print(f"Inserindo na Treeview: {valores}") # Descomente para depuração detalhada
                self.tree.insert("", tk.END, values=valores)
            
            self.tree.update()
            
        except Exception as e:
            print(f"Erro ao atualizar lista: {str(e)}")
            import traceback
            print(traceback.format_exc()) # Imprime o traceback completo para depuração
            messagebox.showerror("Erro", f"Erro ao atualizar lista: {str(e)}")
    
    def ver_detalhes(self):
        """Mostra os detalhes da apólice selecionada em uma nova janela estilizada."""
        item_selecionado = self.tree.selection()
        if not item_selecionado:
            messagebox.showwarning("Atenção", "Selecione uma apólice para ver os detalhes.", parent=self.root)
            return

        # Obter o número da apólice da coluna correta
        numero_apolice_selecionado = self.tree.item(item_selecionado[0], "values")[0]
        apolice_obj = None
        for ap in self.lista_de_apolices:
            if str(ap.get("numero_apolice")) == str(numero_apolice_selecionado):
                apolice_obj = ap
                break
        
        if not apolice_obj:
            messagebox.showerror("Erro", "Apólice não encontrada.", parent=self.root)
            return

        details_window = tk.Toplevel(self.root)
        details_window.title(f"Detalhes da Apólice - Nº {numero_apolice_selecionado}")
        details_window.geometry("700x550")
        details_window.configure(background="white")
        details_window.transient(self.root)
        details_window.grab_set()
        # Centralizar Toplevel
        self.root.eval(f'tk::PlaceWindow {str(details_window)} center')

        # Estilo para esta Toplevel (pode herdar, mas é bom ser explícito para Toplevels)
        style = ttk.Style(details_window)
        style.configure("Details.TFrame", background="white")
        style.configure("Details.TLabel", background="white", foreground="black", font=("Arial", 10))
        style.configure("Section.TLabel", background="white", foreground="#007bff", font=("Arial", 11, "bold"), padding=(0,5,0,5))
        style.configure("Details.Text", font=("Arial", 10), relief=tk.FLAT, background="#f0f0f0", padding=5)

        main_frame = ttk.Frame(details_window, style="Details.TFrame", padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(main_frame, wrap=tk.WORD, relief=tk.FLAT, 
                              font=("Arial", 10), spacing1=2, spacing2=2, spacing3=2,
                              padx=10, pady=10, background="#fdfdfd", borderwidth=1)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0,10), padx=(0,5))
        text_widget.pack(fill=tk.BOTH, expand=True, pady=(0,10), padx=(5,0))

        # Adicionar conteúdo ao Text widget
        def add_detail_section(title):
            text_widget.insert(tk.END, title + "\n", ("section_title",))
            text_widget.insert(tk.END, "=" * 60 + "\n", ("separator",))
        
        def add_detail_field(label, value):
            if isinstance(value, float) and "valor" in label.lower():
                value_str = f"R$ {value:,.2f}"
            elif value is None or str(value).strip() == "":
                value_str = "N/A"
            else:
                value_str = str(value)
            text_widget.insert(tk.END, f"{label}: ", ("field_label",))
            text_widget.insert(tk.END, f"{value_str}\n", ("field_value",))

        # Configurar tags de estilo para o Text widget
        text_widget.tag_configure("section_title", font=("Arial", 12, "bold"), foreground="#0056b3", spacing1=5, spacing3=5)
        text_widget.tag_configure("separator", font=("Courier", 10), foreground="#cccccc")
        text_widget.tag_configure("field_label", font=("Arial", 10, "bold"), foreground="#333333")
        text_widget.tag_configure("field_value", font=("Arial", 10), foreground="#555555")

        add_detail_section("DADOS DO CLIENTE")
        cliente_cpf = apolice_obj.get("cpf_cliente")
        cliente_info = next((c for c in self.lista_de_clientes_pessoais if c.get("cpf") == cliente_cpf), None)
        if cliente_info:
            add_detail_field("Nome", cliente_info.get("nome"))
            add_detail_field("CPF", cliente_info.get("cpf"))
            add_detail_field("Data de Nascimento", cliente_info.get("data_nascimento"))
            add_detail_field("Endereço", cliente_info.get("endereco"))
            add_detail_field("Telefone", cliente_info.get("telefone"))
            add_detail_field("E-mail", cliente_info.get("email"))
        else:
            add_detail_field("Informações do Cliente", "Não encontradas (CPF: " + str(cliente_cpf) + ")")
        text_widget.insert(tk.END, "\n")

        add_detail_section("DADOS DA APÓLICE")
        add_detail_field("Número da Apólice", apolice_obj.get("numero_apolice"))
        add_detail_field("Tipo de Seguro", apolice_obj.get("tipo_seguro"))
        add_detail_field("Status da Apólice", apolice_obj.get("status_apolice"))
        add_detail_field("Data Início Vigência", apolice_obj.get("data_inicio_apolice"))
        add_detail_field("Data Fim Vigência", apolice_obj.get("data_fim_apolice"))
        add_detail_field("Valor Assegurado", apolice_obj.get("valor_assegurado"))
        if apolice_obj.get("status_apolice") == "Cancelada":
            add_detail_field("Data de Cancelamento", apolice_obj.get("data_cancelamento"))
            add_detail_field("Motivo do Cancelamento", apolice_obj.get("motivo_cancelamento"))
        text_widget.insert(tk.END, "\n")

        dados_especificos = apolice_obj.get("dados_especificos", {})
        if dados_especificos:
            add_detail_section("DADOS ESPECÍFICOS DO SEGURO")
            for campo, valor in dados_especificos.items():
                campo_formatado = campo.replace("_", " ").title()
                # Para coberturas de seguro de vida (que são booleanos/checkbuttons)
                if isinstance(valor, bool) and "_var" in campo.lower():
                    add_detail_field(campo_formatado.replace("_Var",""), "Sim" if valor else "Não")
                elif isinstance(valor, list): # Caso de beneficiários ou condutores como lista
                     add_detail_field(campo_formatado, ", ".join(valor) if valor else "N/A")
                else:
                    add_detail_field(campo_formatado, valor)
            text_widget.insert(tk.END, "\n")
        
        # Buscar e exibir dados do sinistro, se houver
        sinistro_relacionado = next((s for s in self.lista_de_sinistros if str(s.get("numero_apolice")) == str(apolice_obj.get("numero_apolice"))), None)
        if sinistro_relacionado:
            add_detail_section("DADOS DO SINISTRO")
            add_detail_field("Data do Sinistro", sinistro_relacionado.get("data_sinistro"))
            add_detail_field("Descrição", sinistro_relacionado.get("descricao_sinistro"))
            add_detail_field("Status do Sinistro", sinistro_relacionado.get("status_sinistro"))

        text_widget.config(state=tk.DISABLED) # Tornar somente leitura

        # Botão Fechar
        btn_fechar_frame = ttk.Frame(details_window, style="Details.TFrame")
        btn_fechar_frame.pack(fill=tk.X, padx=15, pady=(0,10))
        btn_fechar = ttk.Button(btn_fechar_frame, text="Fechar", command=details_window.destroy, style="Secondary.TButton", width=10)
        btn_fechar.pack(side=tk.RIGHT)

    def editar_apolice(self):
        """Carrega os dados de uma apólice selecionada para edição"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Aviso", "Selecione uma apólice para editar.")
            return

        item_id = selection[0]
        item_values = self.tree.item(item_id, "values")
        if not item_values: # Verificar se item_values não está vazio
            messagebox.showerror("Erro", "Não foi possível obter os valores da apólice selecionada.")
            return
            
        numero_apolice_selecionado = str(item_values[0]) # Nº Apólice é a primeira coluna

        apolice_para_editar = None
        indice_encontrado = -1
        for i, apolice_data in enumerate(self.lista_de_apolices):
            if str(apolice_data.get("numero_apolice")) == numero_apolice_selecionado:
                apolice_para_editar = apolice_data
                indice_encontrado = i
                break
        
        if apolice_para_editar is None:
            messagebox.showerror("Erro", "Apólice não encontrada nos dados.")
            return
        
        # Verificar se a apólice está cancelada
        if apolice_para_editar.get("status_apolice") == "Cancelada":
            messagebox.showinfo("Aviso", "Não é possível editar uma apólice cancelada.")
            return

        # Limpar campos ANTES de preencher, mas sem resetar o indice_edicao ainda
        self.limpar_campos(limpar_indice_edicao=False) 
        
        self.indice_edicao = indice_encontrado # Definir o índice de edição AGORA
        self.btn_salvar.config(text="Atualizar Apólice")

        # Preencher dados do cliente associado à apólice
        cpf_cliente_apolice = apolice_para_editar.get("cpf_cliente")
        cliente_info = next((c for c in self.lista_de_clientes_pessoais if c.get("cpf") == cpf_cliente_apolice), None)

        if cliente_info:
            self.cpf_entry.insert(0, cliente_info.get("cpf", ""))
            self.cpf_entry.config(state='readonly') # CPF não deve ser editado ao editar apólice
            self.nome_entry.insert(0, cliente_info.get("nome", ""))
            self.data_nascimento_entry.insert(0, cliente_info.get("data_nascimento", ""))
            self.endereco_entry.insert(0, cliente_info.get("endereco", ""))
            self.telefone_entry.insert(0, cliente_info.get("telefone", ""))
            self.email_entry.insert(0, cliente_info.get("email", ""))
        else:
            # Se não encontrar dados do cliente, permitir edição ou alertar
            messagebox.showwarning("Aviso", f"Dados do cliente com CPF {cpf_cliente_apolice} não encontrados. Preencha manualmente.")
            self.cpf_entry.insert(0, cpf_cliente_apolice if cpf_cliente_apolice else "")
            self.cpf_entry.config(state='normal') # Permitir edição se não encontrou

        # Preencher dados gerais da apólice
        self.data_inicio_apolice_entry.insert(0, apolice_para_editar.get("data_inicio_apolice", ""))
        self.data_fim_apolice_entry.insert(0, apolice_para_editar.get("data_fim_apolice", ""))
        
        valor_assegurado_str = str(apolice_para_editar.get("valor_assegurado", ""))
        if '.' in valor_assegurado_str: # Presumir que se tem ponto, é formato float puro
             try:
                 valor_assegurado_float = float(valor_assegurado_str)
                 self.valor_assegurado_entry.insert(0, f"{valor_assegurado_float:,.2f}".replace(",", "TEMP").replace(".", ",").replace("TEMP", "."))
             except ValueError:
                 self.valor_assegurado_entry.insert(0, valor_assegurado_str) # Insere como está se falhar
        else: # Se não tem ponto, pode ser já formatado ou inteiro
            self.valor_assegurado_entry.insert(0, valor_assegurado_str.replace(".", ","))

        status_apolice_valor = apolice_para_editar.get("status_apolice", "Ativa")
        if status_apolice_valor in self.status_apolice_combobox['values']:
            self.status_apolice_combobox.set(status_apolice_valor)
        elif self.status_apolice_combobox['values']: # Se valor não está na lista, seleciona o primeiro
            self.status_apolice_combobox.current(0)

        tipo_seguro_valor = apolice_para_editar.get("tipo_seguro", "")
        if tipo_seguro_valor in self.tipo_seguro['values']:
            self.tipo_seguro.set(tipo_seguro_valor)
        # else: self.tipo_seguro.set('') # Já feito em limpar_campos

        # Chamar mostrar_campos_seguro DEPOIS de definir o tipo de seguro
        # para que os widgets corretos sejam criados
        self.mostrar_campos_seguro() 

        # Preencher campos específicos DEPOIS que eles foram criados por mostrar_campos_seguro
        dados_especificos = apolice_para_editar.get("dados_especificos", {})
        for campo_key, widget_obj in self.campos_especificos.items():
            valor_especifico = dados_especificos.get(campo_key)

            # Lógica para Checkbuttons de seguro de vida (self.coberturas_vars)
            if "_var" in campo_key and isinstance(widget_obj, ttk.Checkbutton) and campo_key in self.coberturas_vars:
                if isinstance(valor_especifico, bool):
                     self.coberturas_vars[campo_key].set(valor_especifico)
                elif isinstance(valor_especifico, str): # Se estiver salvo como string "True"/"False"
                     self.coberturas_vars[campo_key].set(valor_especifico.lower() == "true")
                continue # Próximo campo

            # Lógica para outros widgets (Entry, Combobox, Text)
            if valor_especifico is not None: # Apenas preencher se houver valor
                if isinstance(widget_obj, tk.Text):
                    widget_obj.delete("1.0", tk.END)
                    widget_obj.insert("1.0", str(valor_especifico))
                elif isinstance(widget_obj, ttk.Combobox):
                    if str(valor_especifico) in widget_obj['values']:
                        widget_obj.set(str(valor_especifico))
                    # elif widget_obj['values']: widget_obj.current(0) # Opcional: definir padrão se valor não encontrado
                elif hasattr(widget_obj, 'insert'): # Para ttk.Entry
                    widget_obj.delete(0, tk.END)
                    widget_obj.insert(0, str(valor_especifico))
        
        # Mudar para a aba de cadastro
        self.tab_control.select(self.tab_cadastro)
    
    def exportar_excel(self):
        """Exporta os dados para um arquivo Excel"""
        if not self.lista_de_apolices:
            messagebox.showinfo("Aviso", "Não há dados para exportar")
            return
        
        # Pedir ao usuário onde salvar o arquivo
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Salvar dados como"
        )
        
        if not file_path:
            return  # Usuário cancelou
        
        try:
            # Criar DataFrame e exportar
            df = pd.DataFrame(self.lista_de_apolices)
            
            # Lidar com os dados específicos que estão aninhados
            # Primeiro vamos expandir os dados específicos em colunas separadas
            specific_data = pd.json_normalize(df['dados_especificos'].to_dict())
            
            # Remover a coluna de dados específicos e juntar com os dados específicos expandidos
            df = df.drop('dados_especificos', axis=1)
            df = pd.concat([df, specific_data], axis=1)
            
            # Exportar para Excel
            df.to_excel(file_path, index=False)
            
            messagebox.showinfo("Sucesso", f"Dados exportados com sucesso para {file_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar dados: {str(e)}")

    def abrir_gerenciamento_usuarios(self):
        """Abre a janela de gerenciamento de usuários"""
        UsuariosWindow(self.root, self.usuario_manager)

    def cancelar_apolice(self):
        """Cancela a apólice selecionada"""
        try:
            selection = self.tree.selection()
            if not selection:
                messagebox.showinfo("Aviso", "Selecione uma apólice para cancelar")
                return
            
            item = self.tree.item(selection[0])
            valores = item.get("values", [])
            
            if not valores: # Verificar se valores não está vazio
                messagebox.showerror("Erro", "Erro ao obter dados da apólice selecionada.")
                return
            
            numero_apolice_selecionado = str(valores[0])  # Nº Apólice é a primeira coluna
            
            apolice_encontrada = None
            for i, apolice_data in enumerate(self.lista_de_apolices):
                if str(apolice_data.get("numero_apolice")) == numero_apolice_selecionado:
                    apolice_encontrada = apolice_data
                    break
            
            if not apolice_encontrada:
                messagebox.showerror("Erro", "Apólice não encontrada")
                return
            
            # Verificar se a apólice já está cancelada
            if apolice_encontrada.get("status_apolice") == "Cancelada":
                messagebox.showinfo("Aviso", "Esta apólice já está cancelada")
                return
            
            # Confirmar cancelamento
            if not messagebox.askyesno("Confirmar Cancelamento", 
                                     "Tem certeza que deseja cancelar esta apólice? Esta ação não pode ser desfeita."):
                return
            
            # Atualizar status da apólice
            apolice_encontrada["status_apolice"] = "Cancelada"
            apolice_encontrada["data_cancelamento"] = datetime.now().strftime("%d/%m/%Y")
            apolice_encontrada["motivo_cancelamento"] = "Cancelamento solicitado pelo usuário"
            
            # Salvar alterações
            self.salvar_dados()
            self.atualizar_lista()
            messagebox.showinfo("Sucesso", "Apólice cancelada com sucesso!")
            
        except Exception as e:
            print(f"Erro ao cancelar apólice: {str(e)}")
            import traceback
            print(f"Traceback completo: {traceback.format_exc()}")
            messagebox.showerror("Erro", f"Erro ao cancelar apólice: {str(e)}")
    
    def gerenciar_sinistro(self):
        """Abre janela estilizada para gerenciar sinistro da apólice selecionada."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atenção", "Selecione uma apólice para gerenciar o sinistro.", parent=self.root)
            return

        item_values = self.tree.item(selection[0], "values")
        if not item_values:
            messagebox.showerror("Erro", "Não foi possível obter os valores da apólice selecionada.", parent=self.root)
            return
            
        numero_apolice_selecionado = str(item_values[0])
        
        apolice_obj = next((ap for ap in self.lista_de_apolices if str(ap.get("numero_apolice")) == numero_apolice_selecionado), None)
        if not apolice_obj:
            messagebox.showerror("Erro", "Apólice não encontrada.", parent=self.root)
            return

        cliente_obj = next((cli for cli in self.lista_de_clientes_pessoais if cli.get("cpf") == apolice_obj.get("cpf_cliente")), None)
        sinistro_existente = next((sin for sin in self.lista_de_sinistros if str(sin.get("numero_apolice")) == numero_apolice_selecionado), None)

        sinistro_window = tk.Toplevel(self.root)
        sinistro_window.title(f"Gerenciar Sinistro - Apólice {numero_apolice_selecionado}")
        sinistro_window.geometry("450x420") # Ajuste de tamanho
        sinistro_window.configure(background="white")
        sinistro_window.transient(self.root)
        sinistro_window.grab_set()
        self.root.eval(f'tk::PlaceWindow {str(sinistro_window)} center') # Centralizar

        # Estilo para esta Toplevel
        style = ttk.Style(sinistro_window)
        style.configure("Sinistro.TFrame", background="white")
        style.configure("Sinistro.TLabel", background="white", foreground="black", font=("Arial", 10))
        style.configure("Sinistro.Header.TLabel", background="white", foreground="#007bff", font=("Arial", 11, "bold"))
        style.configure("Sinistro.Info.TLabel", background="white", foreground="#555555", font=("Arial", 9))
        style.configure("Sinistro.TButton", foreground="white", background="#007bff", font=("Arial", 10, "bold"), padding=5)
        style.map("Sinistro.TButton", background=[('active', '#0056b3')])
        style.configure("Sinistro.Secondary.TButton", foreground="#333", background="#e0e0e0", font=("Arial", 10))
        style.map("Sinistro.Secondary.TButton", background=[('active', '#cccccc')])

        main_frame = ttk.Frame(sinistro_window, style="Sinistro.TFrame", padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        ttk.Label(main_frame, text=f"Apólice Nº: {numero_apolice_selecionado}", style="Sinistro.Header.TLabel").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0,5))
        nome_cliente_display = cliente_obj.get("nome", "N/A") if cliente_obj else "Cliente não encontrado"
        ttk.Label(main_frame, text=f"Cliente: {nome_cliente_display}", style="Sinistro.Info.TLabel").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0,2))
        ttk.Label(main_frame, text=f"Tipo de Seguro: {apolice_obj.get('tipo_seguro', 'N/A')}", style="Sinistro.Info.TLabel").grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0,15))

        ttk.Label(main_frame, text="Data do Sinistro (dd/mm/yyyy):", style="Sinistro.TLabel").grid(row=3, column=0, sticky=tk.W, padx=5, pady=3)
        data_sinistro_entry = ttk.Entry(main_frame, width=25)
        data_sinistro_entry.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=3)
        data_sinistro_entry.bind("<KeyRelease>", lambda event, widget=data_sinistro_entry: self._formatar_data_entry(event, widget))
        if sinistro_existente: data_sinistro_entry.insert(0, sinistro_existente.get("data_sinistro", ""))

        ttk.Label(main_frame, text="Descrição do Sinistro:", style="Sinistro.TLabel").grid(row=4, column=0, sticky=tk.NW, padx=5, pady=3)
        # Usando tk.Text com um frame para scrollbar, pois ttk.Text não existe
        desc_frame = ttk.Frame(main_frame, style="Sinistro.TFrame") # Usar TFrame para consistência
        desc_frame.grid(row=4, column=1, sticky=tk.NSEW, padx=5, pady=3)
        desc_frame.rowconfigure(0, weight=1)
        desc_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1) # Permitir que a linha da descrição expanda

        descricao_sinistro_text = tk.Text(desc_frame, height=5, width=30, relief=tk.SOLID, borderwidth=1, font=("Arial", 10))
        desc_scrollbar = ttk.Scrollbar(desc_frame, orient=tk.VERTICAL, command=descricao_sinistro_text.yview)
        descricao_sinistro_text.configure(yscrollcommand=desc_scrollbar.set)
        descricao_sinistro_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        if sinistro_existente: descricao_sinistro_text.insert("1.0", sinistro_existente.get("descricao_sinistro", ""))

        ttk.Label(main_frame, text="Status do Sinistro:", style="Sinistro.TLabel").grid(row=5, column=0, sticky=tk.W, padx=5, pady=3)
        status_sinistro_combobox = ttk.Combobox(main_frame, values=["Em Análise", "Aprovado", "Negado"], state="readonly", width=23)
        status_sinistro_combobox.grid(row=5, column=1, sticky=tk.EW, padx=5, pady=3)
        if sinistro_existente and sinistro_existente.get("status_sinistro"):
            status_sinistro_combobox.set(sinistro_existente.get("status_sinistro"))
        else:
            status_sinistro_combobox.current(0)

        btn_frame = ttk.Frame(main_frame, style="Sinistro.TFrame")
        btn_frame.grid(row=6, column=0, columnspan=2, pady=(15,0), sticky=tk.E) # Alinhar botões à direita
        
        def salvar_sinistro_local():
            data_sin_str = data_sinistro_entry.get()
            if not data_sin_str or not self.validar_data(data_sin_str):
                messagebox.showerror("Erro", "Data do Sinistro inválida ou não preenchida. Use dd/mm/yyyy.", parent=sinistro_window)
                return
            
            dados_novo_sinistro = {
                "numero_apolice": numero_apolice_selecionado,
                "data_sinistro": data_sin_str,
                "descricao_sinistro": descricao_sinistro_text.get("1.0", tk.END).strip(),
                "status_sinistro": status_sinistro_combobox.get()
            }
            
            sinistro_idx_para_atualizar = -1
            for i, sin in enumerate(self.lista_de_sinistros):
                if str(sin.get("numero_apolice")) == numero_apolice_selecionado:
                    sinistro_idx_para_atualizar = i
                    break
            
            if sinistro_idx_para_atualizar != -1:
                self.lista_de_sinistros[sinistro_idx_para_atualizar] = dados_novo_sinistro
            else:
                self.lista_de_sinistros.append(dados_novo_sinistro)
            
            self._salvar_lista_em_json(self.lista_de_sinistros, "sinistros.json")
            messagebox.showinfo("Sucesso", "Informações do sinistro salvas com sucesso!", parent=sinistro_window)
            self.atualizar_lista() # Atualiza a Treeview principal
            sinistro_window.destroy()
        
        ttk.Button(btn_frame, text="Salvar Sinistro", command=salvar_sinistro_local, style="Sinistro.TButton").pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(btn_frame, text="Cancelar", command=sinistro_window.destroy, style="Sinistro.Secondary.TButton").pack(side=tk.LEFT)

        self.root.wait_window(sinistro_window)

    def abrir_relatorios(self):
        """Abre a janela de relatórios"""
        from relatorios import RelatoriosWindow
        RelatoriosWindow(self.root)

    def _formatar_data_entry(self, event, entry_widget):
        """Formata a entrada de data para dd/mm/yyyy automaticamente."""
        text = entry_widget.get()
        text_sem_barra = text.replace("/", "")
        
        # Ignorar teclas não numéricas exceto Backspace e Delete
        if event.keysym not in ['BackSpace', 'Delete'] and not event.char.isdigit():
            return "break" # Impede a inserção do caractere

        novo_texto = ""
        if len(text_sem_barra) > 0:
            novo_texto += text_sem_barra[:2]
        if len(text_sem_barra) >= 2:
            if len(text_sem_barra) > 2 or (len(text_sem_barra) == 2 and event.keysym not in ['BackSpace', 'Delete']):
                 novo_texto += "/"
        if len(text_sem_barra) > 2:
            novo_texto += text_sem_barra[2:4]
        if len(text_sem_barra) >= 4:
             if len(text_sem_barra) > 4 or (len(text_sem_barra) == 4 and event.keysym not in ['BackSpace', 'Delete']):
                novo_texto += "/"
        if len(text_sem_barra) > 4:
            novo_texto += text_sem_barra[4:8]

        # Limitar o comprimento total
        if len(novo_texto) > 10:
            novo_texto = novo_texto[:10]

        # Atualizar o widget apenas se o texto mudou para evitar loops de cursor
        if entry_widget.get() != novo_texto:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, novo_texto)
            # Manter o cursor no final
            entry_widget.icursor(len(novo_texto))
        return None # Permite a propagação do evento, se necessário

    def _formatar_cpf_entry(self, event, entry_widget):
        """Formata a entrada de CPF para xxx.xxx.xxx-xx automaticamente."""
        text = entry_widget.get()
        text_sem_formatacao = re.sub(r'\D', '', text) # Remove não dígitos
        
        if event.keysym not in ['BackSpace', 'Delete'] and not event.char.isdigit():
            return "break" # Impede a inserção do caractere se não for dígito, backspace ou delete

        novo_texto = ""
        if len(text_sem_formatacao) > 0:
            novo_texto += text_sem_formatacao[:3]
        if len(text_sem_formatacao) >= 3:
            if len(text_sem_formatacao) > 3 or (len(text_sem_formatacao) == 3 and event.keysym not in ['BackSpace', 'Delete']):
                novo_texto += "."
        if len(text_sem_formatacao) > 3:
            novo_texto += text_sem_formatacao[3:6]
        if len(text_sem_formatacao) >= 6:
            if len(text_sem_formatacao) > 6 or (len(text_sem_formatacao) == 6 and event.keysym not in ['BackSpace', 'Delete']):
                novo_texto += "."
        if len(text_sem_formatacao) > 6:
            novo_texto += text_sem_formatacao[6:9]
        if len(text_sem_formatacao) >= 9:
            if len(text_sem_formatacao) > 9 or (len(text_sem_formatacao) == 9 and event.keysym not in ['BackSpace', 'Delete']):
                novo_texto += "-"
        if len(text_sem_formatacao) > 9:
            novo_texto += text_sem_formatacao[9:11]

        # Limitar o comprimento total
        if len(novo_texto) > 14:
            novo_texto = novo_texto[:14]

        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, novo_texto)
        entry_widget.icursor(len(novo_texto)) # Manter o cursor no final
        return "break" # Evitar que o evento padrão de tecla insira o caractere novamente

    def _formatar_telefone_entry(self, event, entry_widget):
        """Formata a entrada de telefone para (xx) xxxxx-xxxx ou (xx) xxxx-xxxx."""
        text = entry_widget.get()
        text_sem_formatacao = re.sub(r'\D', '', text)

        if event.keysym not in ['BackSpace', 'Delete'] and not event.char.isdigit():
            return "break"

        novo_texto = ""
        if len(text_sem_formatacao) > 0:
            novo_texto += "(" + text_sem_formatacao[:2]
        if len(text_sem_formatacao) >= 2:
            if len(text_sem_formatacao) > 2 or (len(text_sem_formatacao) == 2 and event.keysym not in ['BackSpace', 'Delete']):
                novo_texto += ") "
        if len(text_sem_formatacao) > 2:
            # Decide entre 8 ou 9 dígitos para o número principal
            if len(text_sem_formatacao) > 10: # Celular com 9 dígitos + DDD
                novo_texto += text_sem_formatacao[2:7]
                if len(text_sem_formatacao) >= 7:
                    if len(text_sem_formatacao) > 7 or (len(text_sem_formatacao) == 7 and event.keysym not in ['BackSpace', 'Delete']):
                        novo_texto += "-"
                if len(text_sem_formatacao) > 7:
                    novo_texto += text_sem_formatacao[7:11]
            else: # Fixo ou celular com 8 dígitos + DDD
                novo_texto += text_sem_formatacao[2:6]
                if len(text_sem_formatacao) >= 6:
                    if len(text_sem_formatacao) > 6 or (len(text_sem_formatacao) == 6 and event.keysym not in ['BackSpace', 'Delete']):
                        novo_texto += "-"
                if len(text_sem_formatacao) > 6:
                    novo_texto += text_sem_formatacao[6:10]
        
        # Limitar o comprimento total (xx) xxxxx-xxxx -> 15 chars
        if len(novo_texto) > 15:
            novo_texto = novo_texto[:15]

        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, novo_texto)
        entry_widget.icursor(len(novo_texto))
        return "break"

    def _formatar_valor_monetario_entry(self, event, entry_widget):
        """Formata a entrada de valor monetário para R$ xxx.xxx,xx."""
        text = entry_widget.get()
        # Permite apenas dígitos e uma vírgula ou ponto como separador decimal
        text_numerico = re.sub(r'[^0-9,.]', '', text)
        
        # Substitui ponto por vírgula para consistência decimal
        text_numerico = text_numerico.replace('.', ',')

        # Impede múltiplas vírgulas
        if text_numerico.count(',') > 1:
            # Mantém apenas a primeira vírgula
            partes = text_numerico.split(',', 1)
            text_numerico = partes[0] + ',' + partes[1].replace(',', '')

        # Bloqueia entrada não numérica, exceto Backspace, Delete, vírgula, ponto e setas
        if event.keysym not in ['BackSpace', 'Delete', 'Left', 'Right', 'Home', 'End'] and not event.char.isdigit() and event.char not in [ ',', '.']:
            return "break"

        # Se o evento for vírgula ou ponto e já existe uma vírgula, impede nova inserção
        if event.char in [ ',', '.'] and ',' in text[:-1]: # text[:-1] para não considerar o char atual
            return "break"

        # Limitar a duas casas decimais
        if ',' in text_numerico:
            parte_inteira, parte_decimal = text_numerico.split(',', 1)
            parte_decimal = parte_decimal[:2]
            text_formatado_final = parte_inteira + ',' + parte_decimal
        else:
            text_formatado_final = text_numerico
        
        # Atualiza o widget sem formatação de R$ ou milhar por enquanto, focando na entrada correta do número
        # A formatação completa para exibição (com R$ e pontos de milhar) pode ser feita ao salvar ou exibir o valor
        current_cursor_pos = entry_widget.index(tk.INSERT)
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, text_formatado_final)
        
        # Tenta restaurar a posição do cursor
        if current_cursor_pos > len(text_formatado_final):
            entry_widget.icursor(len(text_formatado_final))
        else:
            # Ajuste se o caractere digitado foi bloqueado/alterado e o comprimento mudou
            if event.char in [ ',', '.'] and text_formatado_final.endswith(',') and not text.endswith(','):
                 entry_widget.icursor(current_cursor_pos)
            elif len(text) > len(text_formatado_final) or len(text) < len(text_formatado_final):
                 entry_widget.icursor(current_cursor_pos - (len(text) - len(text_formatado_final)) if current_cursor_pos > 0 else 0 )
            else:
                 entry_widget.icursor(current_cursor_pos)
        return "break"

def main():
    """Função principal removida pois agora o login é feito pela LoginWindow"""
    pass

if __name__ == "__main__":
    print("Este módulo não deve ser executado diretamente. Execute main.py")
