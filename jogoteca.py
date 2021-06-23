from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_mysqldb import MySQL

from dao import JogoDao, UsuarioDao

import config


app = Flask(__name__)
app.secret_key = 'alura'

app.config["MYSQL_USER"] = config.MYSQL_USER
app.config["MYSQL_PASSWORD"] = config.MYSQL_PASSWORD
app.config["MYSQL_HOST"] = config.MYSQL_HOST
app.config["MYSQL_PORT"] = config.MYSQL_PORT
app.config["MYSQL_DB"] = config.MYSQL_DB
db = MySQL(app)

jogo_dao = JogoDao(db)
usuario_dao = UsuarioDao(db)

from models import Jogo, Usuario

@app.route('/')
def index():
	lista = jogo_dao.listar()
	return render_template('lista.html', titulo='Jogos', jogos = lista)

@app.route('/novo')
def novo():
	if 'usuario_logado' not in session or session['usuario_logado'] == None:
		return redirect(url_for('login', proxima=url_for('novo')))
	return render_template('novo.html', titulo='Novo Jogo')

@app.route('/criar', methods=['POST',])
def criar():
	nome = request.form['nome']
	categoria = request.form['categoria']
	console = request.form['console']
	jogo = Jogo(nome, categoria, console)
	jogo_dao.salvar(jogo)
	return redirect(url_for('index'))

@app.route('/editar/<int:id>')
def editar(id):
	if 'usuario_logado' not in session or session['usuario_logado'] == None:
		return redirect(url_for('login', proxima=url_for('editar')))
	jogo = jogo_dao.busca_por_id(id)
	return render_template('editar.html', titulo='Editar Jogo', jogo=jogo)

@app.route('/atualizar', methods=['POST',])
def atualizar():
	id = request.form['id']
	nome = request.form['nome']
	categoria = request.form['categoria']
	console = request.form['console']
	jogo = Jogo(nome, categoria, console, id)
	jogo_dao.salvar(jogo)
	return redirect(url_for('index'))

@app.route('/deletar/<int:id>')
def deletar(id):
	jogo_dao.deletar(id)
	flash('Jogo removido com sucesso!')
	return redirect(url_for('index'))

@app.route('/login')
def login():
	proxima = request.args.get('proxima')
	return render_template('login.html', proxima=proxima)


@app.route('/autenticar', methods=['POST', ])
def autenticar():
	usuario = usuario_dao.buscar_por_id(request.form['usuario'])
	if usuario:
		if usuario.senha == request.form['senha']:
			session['usuario_logado'] = usuario.id
			flash(usuario.nome + ' logou com sucesso!')
			proxima_pagina = request.form['proxima']
			return redirect(proxima_pagina)
	else:
		flash('Não logado, tente novamente!')
		return redirect(url_for('login'))


@app.route('/logout')
def logout():
	session['usuario_logado'] = None
	flash('Nenhum usuário logado!')
	return redirect(url_for('index'))


app.run(debug=True)
