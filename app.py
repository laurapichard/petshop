import os
from decimal import Decimal
from functools import wraps

import psycopg2
from flask import (Flask, abort, flash, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from db import run, transaction

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")


# ---------- utilitários ----------

def nz(valor):
    """Converte texto vazio em None."""
    if valor is None:
        return None
    valor = valor.strip()
    return valor or None


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "funcionario_id" not in session:
            flash("Faça login para acessar o sistema.", "aviso")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


@app.template_filter("reais")
def formatar_reais(valor):
    texto = f"{float(valor or 0):,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


@app.errorhandler(psycopg2.Error)
def erro_banco(erro):
    if isinstance(erro, psycopg2.IntegrityError):
        mensagem = "Não foi possível concluir: o registro já existe ou está vinculado a outros dados."
    else:
        mensagem = "Erro ao acessar o banco de dados."
    flash(mensagem, "erro")
    return redirect(request.referrer or url_for("painel"))


# ---------- autenticação ----------

@app.route("/")
def index():
    if "funcionario_id" in session:
        return redirect(url_for("painel"))
    return redirect(url_for("login"))


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = nz(request.form.get("nome"))
        cargo = nz(request.form.get("cargo"))
        telefone = nz(request.form.get("telefone"))
        login_usuario = nz(request.form.get("login"))
        senha = request.form.get("senha", "")

        if not (nome and cargo and login_usuario):
            flash("Preencha nome, cargo e login.", "erro")
            return render_template("cadastro.html")
        if len(senha) < 6:
            flash("A senha precisa ter ao menos 6 caracteres.", "erro")
            return render_template("cadastro.html")

        with transaction() as cur:
            cur.execute(
                "INSERT INTO funcionario (nome, cargo, telefone) VALUES (%s, %s, %s) "
                "RETURNING codigo_funcionario",
                (nome, cargo, telefone),
            )
            funcionario_id = cur.fetchone()["codigo_funcionario"]
            cur.execute(
                "INSERT INTO usuario (login, senha_hash, codigo_funcionario) VALUES (%s, %s, %s)",
                (login_usuario, generate_password_hash(senha), funcionario_id),
            )
        flash("Cadastro realizado! Agora faça login.", "sucesso")
        return redirect(url_for("login"))

    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = run(
            """SELECT u.senha_hash, f.codigo_funcionario, f.nome, f.cargo
               FROM usuario u
               JOIN funcionario f ON f.codigo_funcionario = u.codigo_funcionario
               WHERE u.login = %s""",
            (request.form.get("login", "").strip(),),
            one=True,
        )
        if usuario and check_password_hash(usuario["senha_hash"], request.form.get("senha", "")):
            session.clear()
            session["funcionario_id"] = usuario["codigo_funcionario"]
            session["nome"] = usuario["nome"]
            session["cargo"] = usuario["cargo"]
            return redirect(url_for("painel"))
        flash("Login ou senha inválidos.", "erro")

    return render_template("login.html")


@app.route("/sair")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "sucesso")
    return redirect(url_for("login"))


# ---------- painel ----------

@app.route("/painel")
@login_required
def painel():
    totais = run(
        """SELECT
             (SELECT COUNT(*) FROM cliente)       AS clientes,
             (SELECT COUNT(*) FROM pet)           AS pets,
             (SELECT COUNT(*) FROM atendimento)   AS atendimentos,
             (SELECT COALESCE(SUM(valor_total), 0) FROM atendimento) AS faturamento""",
        one=True,
    )
    recentes = run(
        """SELECT a.numero_atendimento, a.data_atendimento, a.horario, a.valor_total,
                  p.nome AS pet, f.nome AS funcionario
           FROM atendimento a
           JOIN pet p ON p.codigo_pet = a.codigo_pet
           JOIN funcionario f ON f.codigo_funcionario = a.codigo_funcionario
           ORDER BY a.data_atendimento DESC, a.horario DESC
           LIMIT 5"""
    )
    return render_template("painel.html", totais=totais, recentes=recentes)


# ---------- clientes ----------

@app.route("/clientes", methods=["GET", "POST"])
@login_required
def clientes():
    if request.method == "POST":
        f = request.form
        nome = nz(f.get("nome"))
        if not nome:
            flash("Informe o nome do cliente.", "erro")
        else:
            run(
                "INSERT INTO cliente (nome, telefone, email, endereco) VALUES (%s, %s, %s, %s)",
                (nome, nz(f.get("telefone")), nz(f.get("email")), nz(f.get("endereco"))),
            )
            flash("Cliente cadastrado.", "sucesso")
        return redirect(url_for("clientes"))

    lista = run("SELECT * FROM cliente ORDER BY nome")
    return render_template("clientes.html", clientes=lista)


@app.route("/clientes/<int:codigo>/excluir", methods=["POST"])
@login_required
def excluir_cliente(codigo):
    run("DELETE FROM cliente WHERE codigo_cliente = %s", (codigo,))
    flash("Cliente excluído.", "sucesso")
    return redirect(url_for("clientes"))


# ---------- pets ----------

@app.route("/pets", methods=["GET", "POST"])
@login_required
def pets():
    if request.method == "POST":
        f = request.form
        run(
            """INSERT INTO pet (nome, especie, raca, data_nascimento, codigo_cliente)
               VALUES (%s, %s, %s, %s, %s)""",
            (nz(f.get("nome")), nz(f.get("especie")), nz(f.get("raca")),
             nz(f.get("data_nascimento")), f.get("codigo_cliente")),
        )
        flash("Pet cadastrado.", "sucesso")
        return redirect(url_for("pets"))

    lista = run(
        """SELECT p.codigo_pet, p.nome, p.especie, p.raca, p.data_nascimento,
                  c.nome AS dono
           FROM pet p
           JOIN cliente c ON c.codigo_cliente = p.codigo_cliente
           ORDER BY p.nome"""
    )
    donos = run("SELECT codigo_cliente, nome FROM cliente ORDER BY nome")
    return render_template("pets.html", pets=lista, donos=donos)


@app.route("/pets/<int:codigo>/excluir", methods=["POST"])
@login_required
def excluir_pet(codigo):
    run("DELETE FROM pet WHERE codigo_pet = %s", (codigo,))
    flash("Pet excluído.", "sucesso")
    return redirect(url_for("pets"))


# ---------- serviços ----------

@app.route("/servicos", methods=["GET", "POST"])
@login_required
def servicos():
    if request.method == "POST":
        f = request.form
        run(
            """INSERT INTO servico (nome, descricao, preco, duracao_minutos)
               VALUES (%s, %s, %s, %s)""",
            (nz(f.get("nome")), nz(f.get("descricao")),
             Decimal(f.get("preco") or "0"), int(f.get("duracao_minutos") or 30)),
        )
        flash("Serviço cadastrado.", "sucesso")
        return redirect(url_for("servicos"))

    lista = run("SELECT * FROM servico ORDER BY nome")
    return render_template("servicos.html", servicos=lista)


@app.route("/servicos/<int:codigo>/excluir", methods=["POST"])
@login_required
def excluir_servico(codigo):
    run("DELETE FROM servico WHERE codigo_servico = %s", (codigo,))
    flash("Serviço excluído.", "sucesso")
    return redirect(url_for("servicos"))


# ---------- atendimentos ----------

@app.route("/atendimentos")
@login_required
def atendimentos():
    lista = run(
        """SELECT a.numero_atendimento, a.data_atendimento, a.horario, a.valor_total,
                  p.nome AS pet, f.nome AS funcionario
           FROM atendimento a
           JOIN pet p ON p.codigo_pet = a.codigo_pet
           JOIN funcionario f ON f.codigo_funcionario = a.codigo_funcionario
           ORDER BY a.data_atendimento DESC, a.horario DESC"""
    )
    return render_template("atendimentos.html", atendimentos=lista)


@app.route("/atendimentos/novo", methods=["GET", "POST"])
@login_required
def novo_atendimento():
    if request.method == "POST":
        f = request.form
        ids_servicos = [int(s) for s in f.getlist("servicos")]
        if not ids_servicos:
            flash("Selecione ao menos um serviço.", "erro")
            return redirect(url_for("novo_atendimento"))

        # Tudo em uma única transação: cabeçalho + itens com preço praticado
        with transaction() as cur:
            cur.execute(
                "SELECT codigo_servico, preco FROM servico WHERE codigo_servico = ANY(%s)",
                (ids_servicos,),
            )
            itens = cur.fetchall()
            total = sum((item["preco"] for item in itens), Decimal("0"))

            cur.execute(
                """INSERT INTO atendimento
                       (data_atendimento, horario, valor_total, codigo_pet, codigo_funcionario)
                   VALUES (%s, %s, %s, %s, %s)
                   RETURNING numero_atendimento""",
                (f["data_atendimento"], f["horario"], total, f["codigo_pet"], f["codigo_funcionario"]),
            )
            numero = cur.fetchone()["numero_atendimento"]

            for item in itens:
                cur.execute(
                    """INSERT INTO item_atendimento
                           (numero_atendimento, codigo_servico, preco_praticado)
                       VALUES (%s, %s, %s)""",
                    (numero, item["codigo_servico"], item["preco"]),
                )

        flash(f"Atendimento nº {numero} registrado.", "sucesso")
        return redirect(url_for("detalhe_atendimento", numero=numero))

    pets_ = run(
        """SELECT p.codigo_pet, p.nome, c.nome AS dono
           FROM pet p JOIN cliente c ON c.codigo_cliente = p.codigo_cliente
           ORDER BY p.nome"""
    )
    funcionarios = run("SELECT codigo_funcionario, nome, cargo FROM funcionario ORDER BY nome")
    servicos_ = run("SELECT codigo_servico, nome, preco FROM servico ORDER BY nome")
    return render_template("atendimento_novo.html", pets=pets_,
                           funcionarios=funcionarios, servicos=servicos_)


@app.route("/atendimentos/<int:numero>")
@login_required
def detalhe_atendimento(numero):
    at = run(
        """SELECT a.numero_atendimento, a.data_atendimento, a.horario, a.valor_total,
                  p.nome AS pet, c.nome AS cliente, f.nome AS funcionario
           FROM atendimento a
           JOIN pet p ON p.codigo_pet = a.codigo_pet
           JOIN cliente c ON c.codigo_cliente = p.codigo_cliente
           JOIN funcionario f ON f.codigo_funcionario = a.codigo_funcionario
           WHERE a.numero_atendimento = %s""",
        (numero,),
        one=True,
    )
    if not at:
        abort(404)
    itens = run(
        """SELECT s.nome, ia.preco_praticado
           FROM item_atendimento ia
           JOIN servico s ON s.codigo_servico = ia.codigo_servico
           WHERE ia.numero_atendimento = %s
           ORDER BY s.nome""",
        (numero,),
    )
    return render_template("atendimento_detalhe.html", at=at, itens=itens)


# ---------- relatórios ----------

@app.route("/relatorios")
@login_required
def relatorios():
    mais_realizados = run(
        """SELECT s.codigo_servico, s.nome,
                  COUNT(ia.codigo_servico) AS quantidade_realizada,
                  COALESCE(SUM(ia.preco_praticado), 0) AS receita_gerada
           FROM servico s
           LEFT JOIN item_atendimento ia ON s.codigo_servico = ia.codigo_servico
           GROUP BY s.codigo_servico, s.nome
           ORDER BY quantidade_realizada DESC"""
    )
    faturamento = run(
        """SELECT c.codigo_cliente, c.nome AS cliente,
                  COUNT(DISTINCT a.numero_atendimento) AS total_atendimentos,
                  COALESCE(SUM(a.valor_total), 0.00) AS valor_total_gasto
           FROM cliente c
           LEFT JOIN pet p ON c.codigo_cliente = p.codigo_cliente
           LEFT JOIN atendimento a ON p.codigo_pet = a.codigo_pet
           GROUP BY c.codigo_cliente, c.nome
           ORDER BY valor_total_gasto DESC"""
    )
    return render_template("relatorios.html", mais_realizados=mais_realizados,
                           faturamento=faturamento)


if __name__ == "__main__":
    app.run(debug=True)
