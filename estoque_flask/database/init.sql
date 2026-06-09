CREATE DATABASE almoxarifado;

USE almoxarifado;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user VARCHAR(50),
    password VARCHAR(50),
    permissao VARCHAR(20)
);

CREATE TABLE estoque (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    quantidade INT,
    estoque_minimo INT,
    descricao VARCHAR(255),
    preco DECIMAL(10,2),
    foto VARCHAR(255),
    categoria VARCHAR(30)
);

CREATE TABLE movimentacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT,
    usuario_id INT,
    quantidade INT,
    tipo VARCHAR(20),
    finalidade VARCHAR(100),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO usuarios
(user,password,permissao)
VALUES
('admin','admin123','admin');