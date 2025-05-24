# Sistema-gerenciamento-seguros

## Visão Geral

O Sistema de Gestão de Seguros é uma aplicação desktop desenvolvida em Python com a biblioteca Tkinter (usando `ttk` para widgets temáticos e `ttkthemes` para o tema "Adapta"). Ele permite o cadastro, visualização, edição e gerenciamento de apólices de seguro, clientes e sinistros. A interface busca ser intuitiva, seguindo uma paleta de cores azul e branca, com foco na clareza e usabilidade.

## Funcionalidades Principais

### 1. Autenticação de Usuários
- **Tela de Login**: Interface para que usuários acessem o sistema com nome de usuário e senha.
- **Cadastro de Usuários**: Permite que novos usuários (clientes) sejam cadastrados. Administradores são pré-definidos ou gerenciados internamente.
- **Níveis de Acesso**:
    - **Administrador**: Acesso completo a todas as funcionalidades, incluindo cadastro de apólices, gerenciamento de usuários e visualização de relatórios.
    - **Cliente**: Acesso restrito à visualização de suas próprias apólices e informações (funcionalidade de visualização específica para cliente pode ser implementada futuramente; atualmente, o foco de acesso restrito é na aba de cadastro e botões de ação).

### 2. Gerenciamento de Clientes
- Cadastro e atualização de dados pessoais dos clientes:
    - CPF (com preenchimento automático se o cliente já existir)
    - Nome Completo
    - Data de Nascimento
    - Telefone
    - Endereço
    - E-mail
- Os dados dos clientes são armazenados em `clientes.json`.

### 3. Gerenciamento de Apólices
- **Cadastro de Novas Apólices**:
    - Seleção do tipo de seguro: Automóvel, Residencial ou Vida.
    - Campos específicos são exibidos dinamicamente conforme o tipo de seguro.
    - Definição de datas de início e fim da vigência.
    - Registro do valor assegurado.
    - Atribuição de um número de apólice sequencial e único.
    - Definição do status da apólice (Ativa, Inativa, Pendente, Cancelada).
- **Visualização de Apólices**:
    - Lista tabulada de todas as apólices cadastradas, exibindo informações chave como número da apólice, nome do cliente, CPF, tipo de seguro, status e valor.
    - Funcionalidade de "Ver Detalhes" para uma visualização completa da apólice selecionada, incluindo dados do cliente, da apólice e específicos do seguro, além de informações de sinistro (se houver).
- **Edição de Apólices**:
    - Permite modificar dados de apólices existentes (exceto apólices canceladas).
    - Os campos do formulário de cadastro são preenchidos com os dados da apólice selecionada. O CPF do cliente não é editável durante a alteração de uma apólice.
- **Cancelamento de Apólices**:
    - Permite marcar uma apólice como "Cancelada", registrando a data e um motivo padrão.
- Os dados das apólices são armazenados em `apolices.json`.

### 4. Gerenciamento de Sinistros
- Para cada apólice, é possível registrar e gerenciar um sinistro.
- Campos para registro:
    - Data do Sinistro
    - Descrição Detalhada
    - Status do Sinistro (Em Análise, Aprovado, Negado)
- Os dados dos sinistros são armazenados em `sinistros.json`.

### 5. Relatórios (Acesso de Administrador)
- Geração de relatórios visuais (gráficos) e tabulares:
    - **Distribuição de Apólices por Tipo**: Gráfico de pizza mostrando a proporção de cada tipo de seguro.
    - **Valor Total Segurado por Cliente**: Tabela e gráfico de barras exibindo o valor total que cada cliente possui em apólices ativas.
    - **Ranking de Clientes por Nº de Apólices**: Tabela e gráfico mostrando os clientes com mais apólices.
    - **Sinistros Registrados**: Tabela detalhando os sinistros.
- Os gráficos são gerados utilizando Matplotlib e integrados na interface Tkinter.

### 6. Exportação de Dados
- Funcionalidade para exportar a lista de apólices (incluindo dados específicos expandidos) para um arquivo Excel (`.xlsx`).

### 7. Interface Gráfica (GUI)
- Desenvolvida com Tkinter, `ttk` e `ttkthemes` (tema "Adapta").
- Design com fundo branco, paleta de cores primária azul e fontes pretas para contraste.
- Validação de entrada de dados nos formulários (CPF, datas, e-mail, valores monetários).
- Formatação automática para campos como CPF, data e telefone durante a digitação.
- Janelas de diálogo para confirmações, avisos e erros.

## Estrutura do Projeto (Simplificada)

- `main.py`: Ponto de entrada da aplicação, inicia a tela de login.
- `login.py`: Interface e lógica da tela de login e link para cadastro de usuário.
- `cadastro_usuario_window.py`: Janela para cadastro de novos usuários.
- `Interface_Python.py`: Janela principal da aplicação após o login, contendo as abas de cadastro e visualização de apólices, menus e toda a lógica de negócio relacionada a clientes, apólices e sinistros.
- `relatorios.py`: Janela e lógica para a geração e exibição dos relatórios.
- `usuarios_window.py`: Janela para gerenciamento de usuários (adição, remoção - acessível pelo admin).
- `sistema.py`: Contém classes de modelo (Cliente, SeguroAutomovel, etc.) e a classe `SistemaSeguros` (embora a maior parte da lógica de dados esteja em `Interface_Python.py` atualmente).
- `usuario.py`: Lógica de gerenciamento de usuários (autenticação, cadastro, armazenamento em `usuarios.json`).
- Arquivos JSON:
    - `clientes.json`: Armazena dados dos clientes.
    - `apolices.json`: Armazena dados das apólices.
    - `sinistros.json`: Armazena dados dos sinistros.
    - `usuarios.json`: Armazena credenciais e tipos de usuários.
    - `seguros.json`: Arquivo de dados legado (sistema possui lógica de migração única).

## Como Executar

1.  Certifique-se de ter Python instalado.
2.  Instale as dependências (geralmente listadas em um arquivo `requirements.txt` - *se este arquivo for criado*):
    ```bash
    pip install pandas ttkthemes matplotlib
    ```
3.  Execute o arquivo principal:
    ```bash
    python main.py
    ```

## Próximos Passos e Melhorias Potenciais
- Implementar um arquivo `requirements.txt`.
- Refatorar a persistência de dados para um banco de dados (ex: SQLite) para melhor performance e integridade.
- Aprimorar a gestão de sessões de usuário.
- Expandir as funcionalidades de relatório.
- Testes unitários e de integração.
- Documentação mais detalhada do código. 
