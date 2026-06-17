from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "123456"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

CATEGORIES = ["eletrica", "mecanica", "geral"]
PERMISSIONS = ["admin", "user"]

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="almoxarifado"
    )

def buscar_um(sql, valores=None):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(sql, valores or ())
    resultado = cursor.fetchone()

    cursor.close()
    conexao.close()

    return resultado

def buscar_todos(sql, valores=None):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(sql, valores or ())
    resultado = cursor.fetchall()

    cursor.close()
    conexao.close()

    return resultado

def executar(sql, valores=None):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(sql, valores or ())
    conexao.commit()

    cursor.close()
    conexao.close()

def logado():
    return "user_id" in session

@app.context_processor
def dados_globais():
    return {
        "categories": CATEGORIES,
        "permissions": PERMISSIONS
    }

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form["username"]
        senha = request.form["password"]

        user = buscar_um(
            "SELECT * FROM usuarios WHERE user=%s",
            (usuario,)
        )

        if user and user["password"] == senha:

            session["user_id"] = user["id"]
            session["username"] = user["user"]
            session["permissao"] = user["permissao"]

            return redirect(url_for("home"))

        flash("Login invalido", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/home")
def home():

    if not logado():
        return redirect(url_for("login"))

    itens = buscar_todos(
        "SELECT * FROM estoque ORDER BY nome"
    )

    return render_template(
        "home.html",
        itens=itens
    )

@app.route("/itens/novo", methods=["GET", "POST"])
def novo_item():

    if not logado():
        return redirect(url_for("login"))

    if request.method == "POST":

        nome = request.form["nome"]
        categoria = request.form["categoria"]
        quantidade = int(request.form["quantidade"])
        estoque_minimo = int(request.form["estoque_minimo"])
        preco = float(
            request.form["preco"].replace(",", ".")
        )
        descricao = request.form["descricao"]

        foto = None

        arquivo = request.files.get("foto")

        if arquivo and arquivo.filename:

            foto = arquivo.filename

            os.makedirs(
                app.config["UPLOAD_FOLDER"],
                exist_ok=True
            )

            arquivo.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    foto
                )
            )

        executar(
            """
            INSERT INTO estoque
            (
                nome,
                quantidade,
                estoque_minimo,
                descricao,
                preco,
                foto,
                categoria
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                nome,
                quantidade,
                estoque_minimo,
                descricao,
                preco,
                foto,
                categoria
            )
        )

        return redirect(url_for("home"))

    return render_template("novo_item.html")

@app.route("/movimentacao", methods=["GET", "POST"])
def movimentacao():

    if not logado():
        return redirect(url_for("login"))

    if request.method == "POST":

        item_id = int(request.form["item_id"])
        quantidade = int(request.form["quantidade"])
        tipo = request.form["tipo"]
        finalidade = request.form["finalidade"]

        item = buscar_um(
            "SELECT * FROM estoque WHERE id=%s",
            (item_id,)
        )

        if item:

            if tipo == "entrada":
                nova_qtd = item["quantidade"] + quantidade
            else:
                nova_qtd = item["quantidade"] - quantidade

                if nova_qtd < 0:
                    nova_qtd = 0

            executar(
                "UPDATE estoque SET quantidade=%s WHERE id=%s",
                (nova_qtd, item_id)
            )

            executar(
                """
                INSERT INTO movimentacoes
                (
                    item_id,
                    usuario_id,
                    quantidade,
                    tipo,
                    finalidade
                )
                VALUES (%s,%s,%s,%s,%s)
                """,
                (
                    item_id,
                    session["user_id"],
                    quantidade,
                    tipo,
                    finalidade
                )
            )

        return redirect(url_for("movimentacao"))

    itens = buscar_todos(
        "SELECT * FROM estoque ORDER BY nome"
    )

    historico = buscar_todos(
        """
        SELECT
            m.*,
            e.nome AS item_nome,
            u.user AS usuario
        FROM movimentacoes m
        INNER JOIN estoque e
            ON m.item_id = e.id
        INNER JOIN usuarios u
            ON m.usuario_id = u.id
        ORDER BY m.id DESC
        LIMIT 10
        """
    )

    return render_template(
        "movimentacao.html",
        itens=itens,
        historico=historico
    )

@app.route("/usuarios/novo", methods=["GET", "POST"])
def novo_usuario():

    if not logado():
        return redirect(url_for("login"))

    if session.get("permissao") != "admin":
        return redirect(url_for("home"))

    if request.method == "POST":

        usuario = request.form["username"]
        senha = request.form["password"]
        permissao = request.form["permissao"]

        executar(
            """
            INSERT INTO usuarios
            (
                user,
                password,
                permissao
            )
            VALUES (%s,%s,%s)
            """,
            (
                usuario,
                senha,
                permissao
            )
        )

        return redirect(
            url_for("novo_usuario")
        )

    usuarios = buscar_todos(
        """
        SELECT *
        FROM usuarios
        ORDER BY user
        """
    )

    return render_template(
        "novo_usuario.html",
        usuarios=usuarios
    )

if __name__ == "__main__":

    os.makedirs(
        app.config["UPLOAD_FOLDER"],
        exist_ok=True
    )

    app.run(
        debug=True
    )
