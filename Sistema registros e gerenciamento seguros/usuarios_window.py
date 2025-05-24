import tkinter as tk
from tkinter import ttk, messagebox

class UsuariosWindow:
    def __init__(self, parent, usuario_manager):
        self.window = tk.Toplevel(parent)
        self.window.title("Gerenciamento de Usuários")
        self.window.geometry("600x450") # Ajustar tamanho

        # Configurar cor de fundo da janela
        self.window.configure(background='white')

        # Centralizar a janela
        window_width = 600
        window_height = 450
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.usuario_manager = usuario_manager

        # Estilo
        style = ttk.Style(self.window)
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white", foreground="black", font=("Arial", 10))
        style.configure("Header.TLabel", background="white", foreground="#007bff", font=("Arial", 12, "bold")) # Azul para LabelFrame
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#e0e0e0", foreground="black") # Cabeçalho do Treeview
        style.configure("Treeview", font=("Arial", 10), rowheight=25)
        style.configure("TButton", foreground="white", background="#007bff", font=("Arial", 10, "bold"), padding=5)
        style.map("TButton",
                  background=[('active', '#0056b3'), ('pressed', '#004085')],
                  foreground=[('active', 'white')])
        style.configure("Danger.TButton", foreground="white", background="#dc3545", font=("Arial", 10, "bold"), padding=5) # Botão vermelho para remover
        style.map("Danger.TButton",
                  background=[('active', '#c82333'), ('pressed', '#bd2130')])
        style.configure("TCombobox", font=("Arial", 10), padding=3)
        style.configure("TEntry", font=("Arial", 10), padding=3)
        style.configure("TLabelframe", background="white", bordercolor="#cccccc")
        style.configure("TLabelframe.Label", background="white", foreground="#007bff", font=("Arial", 11, "bold"))


        # Frame principal
        self.main_frame = ttk.Frame(self.window, padding="10", style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame para cadastro
        self.cadastro_frame = ttk.LabelFrame(self.main_frame, text="Adicionar Novo Usuário", padding="10", style="TLabelframe")
        self.cadastro_frame.pack(fill=tk.X, pady=(0, 15))

        # Campos de cadastro
        ttk.Label(self.cadastro_frame, text="Usuário:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        self.usuario_entry = ttk.Entry(self.cadastro_frame, width=30)
        self.usuario_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=3)

        ttk.Label(self.cadastro_frame, text="Senha:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        self.senha_entry = ttk.Entry(self.cadastro_frame, width=30, show="*")
        self.senha_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=3)

        ttk.Label(self.cadastro_frame, text="Tipo:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=3)
        self.tipo_combobox = ttk.Combobox(self.cadastro_frame, values=["usuario", "administrador"], state="readonly", width=27)
        self.tipo_combobox.current(0)
        self.tipo_combobox.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=3)
        
        self.cadastro_frame.columnconfigure(1, weight=1) # Faz a coluna 1 (dos entries) expandir

        # Botão de cadastro
        self.btn_cadastrar = ttk.Button(self.cadastro_frame, text="Adicionar Usuário", command=self.cadastrar_usuario, style="TButton")
        self.btn_cadastrar.grid(row=3, column=0, columnspan=2, pady=10)

        # Frame para lista de usuários
        self.lista_frame = ttk.LabelFrame(self.main_frame, text="Usuários Cadastrados", padding="10", style="TLabelframe")
        self.lista_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview para lista de usuários
        self.tree = ttk.Treeview(self.lista_frame, columns=("usuario", "tipo"), show="headings", style="Treeview")
        self.tree.heading("usuario", text="Usuário")
        self.tree.heading("tipo", text="Tipo")
        self.tree.column("usuario", width=250, stretch=tk.YES)
        self.tree.column("tipo", width=150, stretch=tk.YES)

        # Scrollbar para a lista
        scrollbar = ttk.Scrollbar(self.lista_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botão para remover usuário
        self.btn_remover = ttk.Button(self.main_frame, text="Remover Usuário Selecionado", command=self.remover_usuario, style="Danger.TButton")
        self.btn_remover.pack(pady=10, fill=tk.X, padx=10)

        self.atualizar_lista()
        
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_set()

    def cadastrar_usuario(self):
        """Cadastra um novo usuário"""
        try:
            usuario = self.usuario_entry.get()
            senha = self.senha_entry.get()
            tipo = self.tipo_combobox.get()
            
            self.usuario_manager.cadastrar_usuario(usuario, senha, tipo)
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!", parent=self.window)
            
            # Limpar campos
            self.usuario_entry.delete(0, tk.END)
            self.senha_entry.delete(0, tk.END)
            self.tipo_combobox.current(0)
            
            # Atualizar lista
            self.atualizar_lista()
            
        except ValueError as e:
            messagebox.showerror("Erro", str(e), parent=self.window)
    
    def remover_usuario(self):
        """Remove o usuário selecionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Aviso", "Selecione um usuário para remover", parent=self.window)
            return
        
        usuario_selecionado = self.tree.item(selection[0])["values"][0]
        confirmar = messagebox.askyesno("Confirmar Remoção", 
                                        f"Tem certeza que deseja remover o usuário '{usuario_selecionado}'?",
                                        parent=self.window)
        if confirmar:
            try:
                self.usuario_manager.remover_usuario(usuario_selecionado)
                messagebox.showinfo("Sucesso", "Usuário removido com sucesso!", parent=self.window)
                self.atualizar_lista()
            except ValueError as e:
                messagebox.showerror("Erro", str(e), parent=self.window)
    
    def atualizar_lista(self):
        """Atualiza a lista de usuários"""
        # Limpar lista atual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Adicionar usuários
        for usuario, tipo in self.usuario_manager.listar_usuarios():
            self.tree.insert("", tk.END, values=(usuario, tipo)) 