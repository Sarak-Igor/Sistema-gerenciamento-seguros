import tkinter as tk
from tkinter import ttk
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox

class RelatoriosWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Relatórios do Sistema")
        self.window.geometry("800x600")
        
        # Carregar dados
        self.carregar_dados()
        
        # Criar notebook para abas
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Criar abas para cada tipo de relatório
        self.criar_aba_valor_segurado()
        self.criar_aba_apolices_tipo()
        self.criar_aba_sinistros()
        self.criar_aba_ranking_clientes()
    
    def carregar_dados(self):
        """Carrega os dados dos arquivos JSON necessários (apolices, clientes, sinistros)"""
        self.dados_apolices = []
        self.dados_clientes = []
        self.dados_sinistros = []

        try:
            with open("apolices.json", "r", encoding="utf-8") as file:
                self.dados_apolices = json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Erro", "Arquivo apolices.json não encontrado!")
        except json.JSONDecodeError:
            messagebox.showerror("Erro", "Erro ao decodificar o arquivo apolices.json!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao carregar apolices.json: {e}")

        try:
            with open("clientes.json", "r", encoding="utf-8") as file:
                self.dados_clientes = json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Erro", "Arquivo clientes.json não encontrado!")
        except json.JSONDecodeError:
            messagebox.showerror("Erro", "Erro ao decodificar o arquivo clientes.json!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao carregar clientes.json: {e}")

        try:
            with open("sinistros.json", "r", encoding="utf-8") as file:
                self.dados_sinistros = json.load(file)
        except FileNotFoundError:
            # Não é um erro crítico se não houver sinistros, apenas exibir mensagem informativa
            print("Arquivo sinistros.json não encontrado. Relatório de sinistros pode estar vazio.")
        except json.JSONDecodeError:
            messagebox.showerror("Erro", "Erro ao decodificar o arquivo sinistros.json!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao carregar sinistros.json: {e}")

        # Para compatibilidade temporária, self.dados pode apontar para apólices,
        # mas o ideal é refatorar as abas para usar as listas específicas.
        self.dados = self.dados_apolices
    
    def criar_aba_valor_segurado(self):
        """Cria aba com relatório de valor total segurado por cliente"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Valor Segurado por Cliente")

        # Frame principal para a aba, que será dividido em duas linhas
        main_content_frame = ttk.Frame(tab)
        main_content_frame.pack(fill="both", expand=True)
        main_content_frame.rowconfigure(0, weight=1) # Linha da tabela
        main_content_frame.rowconfigure(1, weight=1) # Linha do gráfico
        main_content_frame.columnconfigure(0, weight=1)

        # Frame para a Treeview (tabela) - ocupará a primeira linha
        tree_frame = ttk.Frame(main_content_frame)
        # Usar grid para posicionar na primeira linha
        tree_frame.grid(row=0, column=0, sticky="nsew", pady=(5, 2))

        # Frame para o gráfico - ocupará a segunda linha
        graph_frame = ttk.Frame(main_content_frame)
        # Usar grid para posicionar na segunda linha
        graph_frame.grid(row=1, column=0, sticky="nsew", pady=(2, 5))

        # Criar Treeview com Scrollbar
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree = ttk.Treeview(tree_frame, columns=("cliente", "valor"), show="headings", yscrollcommand=tree_scrollbar.set)
        tree_scrollbar.config(command=tree.yview)

        tree.heading("cliente", text="Cliente")
        tree.heading("valor", text="Valor Total Segurado")
        
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill="both", expand=True, padx=(10,0), pady=5) # padx para não colar na scrollbar

        # Mapear CPF para nome do cliente para facilitar a busca
        clientes_map = {cliente["cpf"]: cliente["nome"] for cliente in self.dados_clientes if "cpf" in cliente and "nome" in cliente}

        # Calcular valores
        valores_por_cliente = {}
        for apolice in self.dados_apolices:
            cpf_cliente = apolice.get("cpf_cliente")
            nome_cliente = clientes_map.get(cpf_cliente, f"Cliente (CPF: {cpf_cliente})") # Mostrar CPF se nome não encontrado
            valor = float(apolice.get("valor_assegurado", 0))
            
            if nome_cliente in valores_por_cliente:
                valores_por_cliente[nome_cliente] += valor
            else:
                valores_por_cliente[nome_cliente] = valor
        
        # Inserir dados na tabela
        if valores_por_cliente:
            for cliente, valor_total in valores_por_cliente.items():
                tree.insert("", "end", values=(cliente, f"R$ {valor_total:,.2f}"))
        else:
            tree.insert("", "end", values=("Não há dados para exibir.", ""))

        # Criar gráfico
        if valores_por_cliente:
            # Ajustar o figsize para o novo layout
            fig, ax = plt.subplots(figsize=(8, 5)) # Aumentar altura um pouco
            nomes_clientes_grafico = list(valores_por_cliente.keys())
            valores_grafico = list(valores_por_cliente.values())
            
            ax.bar(nomes_clientes_grafico, valores_grafico, color='#007bff') # Cor primária
            ax.set_title("Valor Total Segurado por Cliente", fontsize=12)
            ax.set_xlabel("Clientes", fontsize=10)
            ax.set_ylabel("Valor (R$)", fontsize=10)
            plt.xticks(rotation=45, ha='right', fontsize=9)
            plt.yticks(fontsize=9)
            fig.tight_layout() # Usar fig.tight_layout() para melhor ajuste
            
            canvas = FigureCanvasTkAgg(fig, graph_frame) # Adicionar ao graph_frame
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)
        else:
            label_sem_dados = ttk.Label(graph_frame, text="Não há dados suficientes para gerar o gráfico.")
            label_sem_dados.pack(pady=20, padx=10)
    
    def criar_aba_apolices_tipo(self):
        """Cria aba com relatório de apólices por tipo de seguro"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Apólices por Tipo")

        main_content_frame = ttk.Frame(tab)
        main_content_frame.pack(fill="both", expand=True)
        main_content_frame.rowconfigure(0, weight=1)
        main_content_frame.rowconfigure(1, weight=1)
        main_content_frame.columnconfigure(0, weight=1)

        tree_frame = ttk.Frame(main_content_frame)
        tree_frame.grid(row=0, column=0, sticky="nsew", pady=(5,2))

        graph_frame = ttk.Frame(main_content_frame)
        graph_frame.grid(row=1, column=0, sticky="nsew", pady=(2,5))
        
        # Contar apólices por tipo
        contagem = {"Automóvel": 0, "Residencial": 0, "Vida": 0}
        for apolice in self.dados_apolices: 
            tipo = apolice.get("tipo_seguro")
            if tipo in contagem:
                contagem[tipo] = contagem.get(tipo, 0) + 1
        
        # Criar Treeview com Scrollbar
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree = ttk.Treeview(tree_frame, columns=("tipo", "quantidade"), show="headings", yscrollcommand=tree_scrollbar.set)
        tree_scrollbar.config(command=tree.yview)

        tree.heading("tipo", text="Tipo de Seguro")
        tree.heading("quantidade", text="Quantidade")
        
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill="both", expand=True, padx=(10,0), pady=5)
        
        if any(contagem.values()):
            for tipo, qtd in contagem.items():
                tree.insert("", "end", values=(tipo, qtd))
        else:
            tree.insert("", "end", values=("Não há dados para exibir.", ""))
        
        # Criar gráfico de pizza apenas se houver dados
        if any(contagem.values()):
            fig, ax = plt.subplots(figsize=(6, 5.5)) # Ajustar tamanho
            cores_pizza = ['#007bff', '#17a2b8', '#28a745'] # Azul, Ciano, Verde
            ax.pie(contagem.values(), labels=contagem.keys(), autopct='%1.1f%%', startangle=90, colors=cores_pizza, textprops={'fontsize': 10})
            ax.set_title("Distribuição de Apólices por Tipo", fontsize=12)
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)
        else:
            label_sem_dados = ttk.Label(graph_frame, text="Não há dados de apólices para gerar este relatório.")
            label_sem_dados.pack(pady=20, padx=10)
    
    def criar_aba_sinistros(self):
        """Cria aba com relatório de sinistros"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Sinistros")

        main_content_frame = ttk.Frame(tab)
        main_content_frame.pack(fill="both", expand=True)
        main_content_frame.rowconfigure(0, weight=1)
        main_content_frame.rowconfigure(1, weight=1)
        main_content_frame.columnconfigure(0, weight=1)

        tree_frame = ttk.Frame(main_content_frame)
        tree_frame.grid(row=0, column=0, sticky="nsew", pady=(5,2))

        graph_frame = ttk.Frame(main_content_frame)
        graph_frame.grid(row=1, column=0, sticky="nsew", pady=(2,5))
        
        sinistros_por_status = {"Em Análise": 0, "Aprovado": 0, "Negado": 0}
        total_sinistros = 0
        
        for sinistro in self.dados_sinistros:
            status = sinistro.get("status_sinistro")
            if status in sinistros_por_status:
                sinistros_por_status[status] += 1
            total_sinistros += 1
        
        # Criar Treeview com Scrollbar
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree = ttk.Treeview(tree_frame, columns=("status", "quantidade", "percentual"), show="headings", yscrollcommand=tree_scrollbar.set)
        tree_scrollbar.config(command=tree.yview)

        tree.heading("status", text="Status")
        tree.heading("quantidade", text="Quantidade")
        tree.heading("percentual", text="Percentual")
        
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill="both", expand=True, padx=(10,0), pady=5)
        
        if total_sinistros > 0:
            for status, qtd in sinistros_por_status.items():
                percentual = (qtd / total_sinistros * 100) if total_sinistros > 0 else 0
                tree.insert("", "end", values=(status, qtd, f"{percentual:.1f}%"))
        else:
            tree.insert("", "end", values=("Não há dados para exibir.", "", ""))
        
        if total_sinistros > 0:
            fig, ax = plt.subplots(figsize=(6, 5)) # Ajustar tamanho
            ax.bar(sinistros_por_status.keys(), sinistros_por_status.values(), color='#007bff')
            ax.set_title("Quantidade de Sinistros por Status", fontsize=12)
            ax.set_xlabel("Status", fontsize=10)
            ax.set_ylabel("Quantidade", fontsize=10)
            plt.xticks(fontsize=9)
            plt.yticks(fontsize=9)
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)
        else:
            label_sem_dados = ttk.Label(graph_frame, text="Não há dados de sinistros para gerar o relatório.")
            label_sem_dados.pack(pady=20, padx=10)
    
    def criar_aba_ranking_clientes(self):
        """Cria aba com ranking de clientes por número de apólices"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Ranking de Clientes")

        main_content_frame = ttk.Frame(tab)
        main_content_frame.pack(fill="both", expand=True)
        main_content_frame.rowconfigure(0, weight=1)
        main_content_frame.rowconfigure(1, weight=1)
        main_content_frame.columnconfigure(0, weight=1)

        tree_frame = ttk.Frame(main_content_frame)
        tree_frame.grid(row=0, column=0, sticky="nsew", pady=(5,2))

        graph_frame = ttk.Frame(main_content_frame)
        graph_frame.grid(row=1, column=0, sticky="nsew", pady=(2,5))

        clientes_map = {cliente["cpf"]: cliente["nome"] for cliente in self.dados_clientes if "cpf" in cliente and "nome" in cliente}

        apolices_por_cpf = {}
        for apolice in self.dados_apolices:
            cpf_cliente = apolice.get("cpf_cliente")
            if cpf_cliente:
                apolices_por_cpf[cpf_cliente] = apolices_por_cpf.get(cpf_cliente, 0) + 1
        
        ranking_com_nomes = []
        for cpf, qtd in apolices_por_cpf.items():
            nome_cliente = clientes_map.get(cpf, f"Cliente (CPF: {cpf})")
            ranking_com_nomes.append((nome_cliente, qtd))

        ranking_ordenado = sorted(ranking_com_nomes, key=lambda x: x[1], reverse=True)
        
        # Criar Treeview com Scrollbar
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree = ttk.Treeview(tree_frame, columns=("posicao", "cliente", "quantidade"), show="headings", yscrollcommand=tree_scrollbar.set)
        tree_scrollbar.config(command=tree.yview)
        
        tree.heading("posicao", text="Posição")
        tree.heading("cliente", text="Cliente")
        tree.heading("quantidade", text="Quantidade de Apólices")
        
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill="both", expand=True, padx=(10,0), pady=5)
        
        if ranking_ordenado:
            for i, (cliente, qtd) in enumerate(ranking_ordenado, 1):
                tree.insert("", "end", values=(f"{i}º", cliente, qtd))
        else:
            tree.insert("", "end", values=("", "Não há dados para exibir.", ""))
        
        if ranking_ordenado:
            fig, ax = plt.subplots(figsize=(8, 5)) # Ajustar tamanho
            top_n = ranking_ordenado[:10] # Limitar ao top N para o gráfico
            clientes_grafico = [x[0] for x in top_n][::-1] # Inverter para o barh
            quantidades_grafico = [x[1] for x in top_n][::-1] # Inverter para o barh
            
            ax.barh(clientes_grafico, quantidades_grafico, color='#007bff')
            ax.set_title(f"Top {len(top_n)} Clientes por Número de Apólices", fontsize=12)
            ax.set_xlabel("Quantidade de Apólices", fontsize=10)
            plt.xticks(fontsize=9)
            plt.yticks(fontsize=9)
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)
        else:
            label_sem_dados = ttk.Label(graph_frame, text="Não há dados para gerar o ranking de clientes.")
            label_sem_dados.pack(pady=20, padx=10) 