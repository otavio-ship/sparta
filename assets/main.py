from flask import Flask, render_template, request, redirect, url_for, flash, session
import fdb
app = Flask(__name__)
# Certifique-se de que a SECRET_KEY é forte!
app.secret_key = 'sua_chave_secreta_MUITO_MAIS_FORTE'

# --- Configurações do Banco de Dados ---
DB_CONFIG = {
    'host': 'localhost',
    # Use barras duplas para caminhos ou r'string' para evitar problemas com backslash
    'database': r'C:\Users\Aluno\Desktop\Sparta\BANCO.FDB',
    'user': 'SYSDBA',
    'password': 'sysdba'
}


# --- FUNÇÃO AUXILIAR DE CONEXÃO ---
def get_db_connection():
    """Tenta estabelecer e retornar uma nova conexão FDB."""
    try:
        return fdb.connect(**DB_CONFIG)
    except fdb.Error as e:
        print(f"ERRO DE CONEXÃO COM FIREBIRD: {e}")
        # Em uma aplicação real, você deve lidar com isso de forma mais robusta
        return None


# ----------------------------------------------------
# AQUI TERMINAM AS CONFIGURAÇÕES E COMEÇAM AS ROTAS
# ----------------------------------------------------


# --- Página inicial ---
@app.route('/')
def index():
    return redirect(url_for("login"))


# --- Login (AGORA INTEGRA COM O FIREBIRD) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')  # Mudei para 'email' ou 'usuario' dependendo da sua tabela
        senha = request.form.get('senha')

        con = get_db_connection()
        if con is None:
            flash('Erro de conexão com o banco de dados.', 'danger')
            return render_template('login.html')

        try:
            cursor = con.cursor()

            # ATENÇÃO: Verifique os nomes das colunas na sua tabela USUARIO.
            # Se você armazena a senha em texto plano (não recomendado), use:
            sql = "SELECT EMAIL, CARGO FROM USUARIO WHERE EMAIL = ? AND SENHA = ?"
            cursor.execute(sql, (email, senha))

            # Se a senha estiver hasheada (RECOMENDADO), você precisaria de um passo extra:
            # sql = "SELECT SENHA_HASH, EMAIL, CARGO FROM USUARIO WHERE EMAIL = ?"
            # cursor.execute(sql, (email,))
            # resultado = cursor.fetchone()
            # if resultado and verificar_hash(senha, resultado[0]):
            #     email, cargo = resultado[1], resultado[2]

            resultado = cursor.fetchone()

            if resultado:
                # O resultado será (EMAIL, CARGO)
                usuario_db, cargo = resultado

                flash('Login realizado com sucesso!', 'success')
                session['usuario'] = usuario_db
                session['cargo'] = cargo.strip()  # .strip() remove espaços em branco se for CHAR/VARCHAR fixo

                if cargo.strip() == 'aluno':
                    return redirect(url_for('paginaaluno'))
                elif cargo.strip() == 'professor':
                    return redirect(url_for('PaginaProfessorAulas'))
                elif cargo.strip() == 'admin':
                    return redirect(url_for('PaginaAdminRelatorios'))
                else:
                    flash('Cargo desconhecido no sistema.', 'danger')

            else:
                flash('Email ou senha inválidos.', 'danger')

        except fdb.Error as e:
            print(f"Erro de login no banco de dados: {e}")
            flash('Erro durante a verificação de login.', 'danger')

        finally:
            # SEMPRE feche a conexão no final da requisição!
            con.close()

    return render_template('login.html')


# --- Logout ---
@app.route('/logout')
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for('login'))


# --- Cadastro (CONEXÃO MELHORADA) ---
@app.route('/cadastro', methods=['GET', 'POST'])
def Cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        cpf = request.form.get('cpf')
        telefone = request.form.get('telefone')

        # Define um cargo padrão (ex: 'aluno') para novos cadastros
        cargo_novo = 'aluno'

        # --- INÍCIO DA INTEGRAÇÃO COM FIREBIRD ---
        con = get_db_connection()
        if con is None:
            flash('Erro de conexão com o banco de dados.', 'danger')
            return render_template('cadastro.html')

        try:
            cursor = con.cursor()

            # Lembre-se de incluir o campo 'CARGO' na sua inserção,
            # para que o login possa funcionar corretamente!
            sql = """
            INSERT INTO USUARIO (NOME, EMAIL, SENHA, CPF, TELEFONE,) 
            VALUES (?, ?, ?, ?, ?, ?)
            """
            # Certifique-se de que a ordem dos campos no SQL bate com a ordem aqui:
            cursor.execute(sql, (nome, email, senha, cpf, telefone, cargo_novo))

            con.commit()

            flash(f'Usuário {nome} cadastrado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))

        except fdb.Error as e:
            con.rollback()
            print(f"Erro ao cadastrar: {e}")
            # Verifica erros comuns (ex: violação de PK/UNIQUE)
            if 'violation of PRIMARY or UNIQUE KEY constraint' in str(e):
                flash('Email ou CPF já cadastrados.', 'danger')
            else:
                flash('Erro ao realizar o cadastro. Tente novamente.', 'danger')
            return render_template('cadastro.html')

        finally:
            # Sempre feche o cursor e a CONEXÃO
            if 'cursor' in locals() and cursor:
                cursor.close()
            con.close()
        # --- FIM DA INTEGRAÇÃO COM FIREBIRD ---

    return render_template('cadastro.html')


# --- Rotas restritas (não precisam de mudança, mas incluídas por contexto) ---
@app.route('/aluno')
def paginaaluno():
    if 'usuario' in session and session.get('cargo') == 'aluno':
        return render_template("paginaaluno.html", usuario=session['usuario'])
    else:
        flash("Acesso negado. Área exclusiva para alunos.", "danger")
        return redirect(url_for("login"))


@app.route('/professor')
def PaginaProfessorAulas():
    if 'usuario' in session and session.get('cargo') == 'professor':
        return render_template("PaginaProfessorAulas.html", usuario=session['usuario'])
    else:
        flash("Acesso negado. Área exclusiva para professores.", "danger")
        return redirect(url_for("login"))


@app.route('/admin')
def PaginaAdminRelatorios():
    if 'usuario' in session and session.get('cargo') == 'admin':
        return render_template("PaginaAdminRelatorios.html", usuario=session['usuario'])
    else:
        flash("Acesso negado. Área exclusiva para administradores.", "danger")
        return redirect(url_for("login"))


@app.route('/home')
def homesemusuario():
    return render_template("homesemusuario.html")


if __name__ == "__main__":
    app.run(debug=True)