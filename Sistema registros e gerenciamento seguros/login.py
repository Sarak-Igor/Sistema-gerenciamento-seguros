import tkinter as tk
from tkinter import ttk, messagebox
from auth import UsuarioManager
from cadastro_usuario_window import CadastroUsuarioWindow
from ttkthemes import ThemedTk
import Interface_Python

class LoginWindow:
    def __init__(self):
        self.root = ThemedTk(theme="adapta")
        self.root.title("Login - Sistema de Seguros")
        self.root.geometry("350x300")
        
        # Configurar cor de fundo da janela principal
        self.root.configure(background='white')
        
        # Centralizar a janela
        window_width = 350
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Gerenciador de usuários
        self.usuario_manager = UsuarioManager()
        
        # Configurar estilo ttk
        style = ttk.Style()
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white", foreground="black", font=("Arial", 10))
        style.configure("Header.TLabel", background="white", foreground="#007bff", font=("Arial", 14, "bold"))
        
        # Botão de Login Principal - Texto Preto
        style.configure("TButton", 
                        foreground="black", # Texto PRETO
                        background="#007bff", 
                        font=("Arial", 10, "bold"), 
                        padding=5)
        style.map("TButton",
                  background=[('active', '#0056b3'), ('pressed', '#004085')],
                  foreground=[('active', 'black'), ('pressed', 'black')]) # Texto PRETO
                  
        # Botão de Cadastro como Link - Texto Preto
        style.configure("Link.TButton", 
                        foreground="black", # Texto PRETO
                        background="white", 
                        font=("Arial", 9), 
                        borderwidth=0)
        style.map("Link.TButton",
                  foreground=[('active', 'black'), ('hover', 'black')], # Texto PRETO
                  # background não precisa mudar para Link.TButton nos estados active/hover
                  )
        
        # Frame principal com fundo branco
        self.frame = ttk.Frame(self.root, padding="20 20 20 20", style="TFrame")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(self.frame, text="Bem-vindo!", style="Header.TLabel").pack(pady=(0, 25))
        
        # Campos de entrada
        ttk.Label(self.frame, text="Usuário:").pack(anchor=tk.W, padx=5)
        self.usuario_entry = ttk.Entry(self.frame, font=("Arial", 10), width=30)
        self.usuario_entry.pack(fill=tk.X, pady=(0, 10), padx=5, ipady=4)
        
        ttk.Label(self.frame, text="Senha:").pack(anchor=tk.W, padx=5)
        self.senha_entry = ttk.Entry(self.frame, show="*", font=("Arial", 10), width=30)
        self.senha_entry.pack(fill=tk.X, pady=(0, 20), padx=5, ipady=4)
        
        # Botão de login
        self.btn_login = ttk.Button(self.frame, text="Login", command=self.fazer_login, style="TButton")
        self.btn_login.pack(fill=tk.X, padx=5, pady=(0,10))
        
        # Botão de cadastro como link
        self.btn_cadastro = ttk.Button(self.frame, text="Não tem uma conta? Cadastre-se",
                                       command=self.abrir_cadastro_usuario_event, style="Link.TButton")
        self.btn_cadastro.pack(pady=(5,0))
        
        # Vincular tecla Enter ao login
        self.root.bind("<Return>", self.fazer_login_event)
    
    def fazer_login_event(self, event=None):
        self.fazer_login()
    
    def fazer_login(self):
        usuario = self.usuario_entry.get()
        senha = self.senha_entry.get()
        
        if self.usuario_manager.autenticar(usuario, senha):
            messagebox.showinfo("Login", "Login bem-sucedido!")
            self.abrir_aplicacao_principal()
        else:
            messagebox.showerror("Erro de Login", "Usuário ou senha incorretos.")
    
    def abrir_aplicacao_principal(self):
        self.root.destroy()
        app_root = ThemedTk(theme="adapta")
        app = Interface_Python.SeguroApp(app_root, self.usuario_manager)
        app_root.mainloop()
    
    def abrir_cadastro_usuario_event(self, event=None):
        self.abrir_cadastro()
    
    def abrir_cadastro(self):
        CadastroUsuarioWindow(self.root, self.usuario_manager)
    
    def executar(self):
        self.root.mainloop()

if __name__ == "__main__":
    login_window = LoginWindow()
    login_window.executar() 