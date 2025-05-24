import json
import os

class UsuarioManager:
    def __init__(self):
        self.arquivo_usuarios = "usuarios.json"
        self.usuarios = self.carregar_usuarios()
        self.usuario_atual = None
        self.tipo_usuario_atual = None
    
    def carregar_usuarios(self):
        """Carrega os usuários do arquivo JSON"""
        usuarios_padrao = {
            "admin": ("admin123", "administrador"),
            "user1": ("user123", "usuario"),
            "user2": ("user456", "usuario")
        }
        
        if os.path.exists(self.arquivo_usuarios):
            try:
                with open(self.arquivo_usuarios, "r", encoding="utf-8") as file:
                    return json.load(file)
            except:
                return usuarios_padrao
        return usuarios_padrao
    
    def salvar_usuarios(self):
        """Salva os usuários no arquivo JSON"""
        with open(self.arquivo_usuarios, "w", encoding="utf-8") as file:
            json.dump(self.usuarios, file, ensure_ascii=False, indent=4)
    
    def cadastrar_usuario(self, usuario, senha, tipo):
        """Cadastra um novo usuário"""
        if not usuario or not senha:
            raise ValueError("Usuário e senha são obrigatórios")
        
        if usuario in self.usuarios:
            raise ValueError("Usuário já existe")
        
        if tipo not in ["administrador", "usuario"]:
            raise ValueError("Tipo de usuário inválido")
        
        self.usuarios[usuario] = (senha, tipo)
        self.salvar_usuarios()
    
    def remover_usuario(self, usuario):
        """Remove um usuário"""
        if usuario == "admin":
            raise ValueError("Não é possível remover o usuário admin")
        
        if usuario not in self.usuarios:
            raise ValueError("Usuário não encontrado")
        
        del self.usuarios[usuario]
        self.salvar_usuarios()
    
    def listar_usuarios(self):
        """Retorna lista de usuários cadastrados"""
        return [(usuario, tipo) for usuario, (_, tipo) in self.usuarios.items()]
    
    def autenticar(self, usuario, senha):
        """Autentica um usuário"""
        if usuario in self.usuarios:
            senha_correta, tipo = self.usuarios[usuario]
            if senha == senha_correta:
                self.usuario_atual = usuario
                self.tipo_usuario_atual = tipo
                return True
        return False
    
    def logout(self):
        """Realiza o logout do usuário"""
        self.usuario_atual = None
        self.tipo_usuario_atual = None
    
    def is_admin(self):
        """Verifica se o usuário atual é administrador"""
        return self.tipo_usuario_atual == "administrador"
    
    def is_autenticado(self):
        """Verifica se há um usuário autenticado"""
        return self.usuario_atual is not None
    
    def get_usuario_atual(self):
        """Retorna o nome do usuário atual"""
        return self.usuario_atual 