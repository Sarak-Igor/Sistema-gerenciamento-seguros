import tkinter as tk
from tkinter import ttk, messagebox

class CadastroUsuarioWindow:
    def __init__(self, parent, usuario_manager):
        self.window = tk.Toplevel(parent)
        self.window.title("Cadastro de Novo Usuário")
        self.window.geometry("400x350") # Ajustar tamanho se necessário

        # Configurar cor de fundo da janela
        self.window.configure(background='white')

        # Centralizar a janela
        window_width = 400
        window_height = 350
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.usuario_manager = usuario_manager

        # Estilo (pode herdar do pai, mas podemos definir especificidades)
        style = ttk.Style(self.window) # Pegar o estilo da Toplevel
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white", foreground="black", font=("Arial", 10))
        style.configure("Header.TLabel", background="white", foreground="#007bff", font=("Arial", 12, "bold"))
        style.configure("TButton", foreground="white", background="#007bff", font=("Arial", 10, "bold"), padding=5)
        style.map("TButton",
                  background=[('active', '#0056b3'), ('pressed', '#004085')],
                  foreground=[('active', 'white')])
        style.configure("TCombobox", font=("Arial", 10), padding=3)
        style.configure("TEntry", font=("Arial", 10), padding=3)

        # Frame principal
        self.frame = ttk.Frame(self.window, padding="20", style="TFrame")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Título
        ttk.Label(self.frame, text="Criar Nova Conta", style="Header.TLabel").pack(pady=(0, 20))

        # Campos de cadastro
        ttk.Label(self.frame, text="Nome de Usuário:").pack(anchor=tk.W, padx=5)
        self.usuario_entry = ttk.Entry(self.frame, width=40)
        self.usuario_entry.pack(fill=tk.X, pady=(0, 10), padx=5, ipady=2)

        ttk.Label(self.frame, text="Senha:").pack(anchor=tk.W, padx=5)
        self.senha_entry = ttk.Entry(self.frame, width=40, show="*")
        self.senha_entry.pack(fill=tk.X, pady=(0, 10), padx=5, ipady=2)

        ttk.Label(self.frame, text="Confirmar Senha:").pack(anchor=tk.W, padx=5)
        self.confirmar_senha_entry = ttk.Entry(self.frame, width=40, show="*")
        self.confirmar_senha_entry.pack(fill=tk.X, pady=(0, 10), padx=5, ipady=2)

        ttk.Label(self.frame, text="Tipo de Usuário:").pack(anchor=tk.W, padx=5)
        self.tipo_usuario_combobox = ttk.Combobox(self.frame, values=["usuario", "administrador"], state="readonly", width=37)
        self.tipo_usuario_combobox.current(0)
        self.tipo_usuario_combobox.pack(fill=tk.X, pady=(0, 20), padx=5, ipady=2)

        # Frame para botões
        self.btn_frame = ttk.Frame(self.frame, style="TFrame") # Fundo branco para o frame dos botões
        self.btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.btn_cadastrar = ttk.Button(self.btn_frame, text="Cadastrar", command=self.cadastrar, style="TButton")
        self.btn_cadastrar.pack(side=tk.RIGHT, padx=(5,0)) # Alinhar à direita

        self.btn_cancelar = ttk.Button(self.btn_frame, text="Cancelar", command=self.window.destroy, style="TButton") 
        # Poderia ter um estilo diferente para cancelar, ex: "Secondary.TButton"
        self.btn_cancelar.pack(side=tk.RIGHT, padx=(0,5))

        # Vincular tecla Enter
        self.window.bind("<Return>", lambda e: self.cadastrar())

        # Tornar a janela modal e focar
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_set()
        # self.window.wait_window() # Não necessário se o fluxo de login espera

    def cadastrar(self):
        """Realiza o cadastro do usuário"""
        usuario = self.usuario_entry.get()
        senha = self.senha_entry.get()
        confirmar_senha = self.confirmar_senha_entry.get()
        tipo = self.tipo_usuario_combobox.get()
        
        # Validações
        if not usuario or not senha or not confirmar_senha:
            messagebox.showerror("Erro de Cadastro", "Todos os campos são obrigatórios.", parent=self.window)
            return
        
        if senha != confirmar_senha:
            messagebox.showerror("Erro de Cadastro", "As senhas não coincidem.", parent=self.window)
            return
        
        try:
            self.usuario_manager.cadastrar_usuario(usuario, senha, tipo)
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!", parent=self.window)
            self.window.destroy()
        except ValueError as e:
            messagebox.showerror("Erro de Cadastro", str(e), parent=self.window) 