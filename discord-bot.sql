CREATE TABLE "Cargo" (
  "id_cargo" INTEGER PRIMARY KEY AUTOINCREMENT,
  "cor" VARCHAR,
  "nome" VARCHAR,
  "prioridade" INTEGER
);

CREATE TABLE "UsuarioCargo" (
  "id_usuariocargo" INTEGER PRIMARY KEY AUTOINCREMENT,
  "fk_id_usuario" INTEGER NOT NULL,
  "fk_id_cargo" INTEGER NOT NULL,
  CONSTRAINT "fk_usuario" FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario") ON DELETE CASCADE,
  CONSTRAINT "fk_cargo" FOREIGN KEY ("fk_id_cargo") REFERENCES "Cargo" ("id_cargo") ON DELETE CASCADE
);

CREATE TABLE "Servidor" (
  "id_servidor" INTEGER PRIMARY KEY,
  "nome" VARCHAR
);

CREATE TABLE "UsuarioServidor" (
  "fk_id_usuario" INTEGER NOT NULL,
  "fk_id_servidor" INTEGER NOT NULL,
  PRIMARY KEY ("fk_id_usuario", "fk_id_servidor"),
  CONSTRAINT "fk_usuario" FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario") ON DELETE CASCADE,
  CONSTRAINT "fk_servidor" FOREIGN KEY ("fk_id_servidor") REFERENCES "Servidor" ("id_servidor") ON DELETE CASCADE
);

CREATE TABLE "Estatistica" (
  "acertos" INTEGER,
  "total" INTEGER,
  "streak" INTEGER,
  "streak_max" INTEGER,
  "fk_id_usuario" INTEGER NOT NULL UNIQUE,
  CONSTRAINT "fk_usuario" FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario") ON DELETE CASCADE
);

CREATE TABLE "ComandoLog" (
  "parametro" TEXT,
  "comando_data" TIMESTAMP,
  "fk_id_usuario" INTEGER NOT NULL,
  "fk_id_comando" INTEGER NOT NULL,
  PRIMARY KEY ("fk_id_usuario", "fk_id_comando"),
  CONSTRAINT "fk_usuario" FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario") ON DELETE CASCADE,
  CONSTRAINT "fk_comando" FOREIGN KEY ("fk_id_comando") REFERENCES "Comando" ("id_comando") ON DELETE CASCADE
);

CREATE TABLE "Comando" (
  "id_comando" INTEGER PRIMARY KEY AUTOINCREMENT,
  "nome" VARCHAR,
  "descricao" TEXT,
  "requerimento" INTEGER
);

CREATE TABLE "UsuarioConquista" (
  "completo" BOOLEAN DEFAULT FALSE,
  "completo_em" TIMESTAMP,
  "fk_id_conquista" INTEGER NOT NULL,
  "fk_id_usuario" INTEGER NOT NULL,
  PRIMARY KEY ("fk_id_usuario", "fk_id_conquista"),
  CONSTRAINT "fk_usuario" FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario") ON DELETE CASCADE,
  CONSTRAINT "fk_conquista" FOREIGN KEY ("fk_id_conquista") REFERENCES "Conquista" ("id_conquista") ON DELETE CASCADE
);

CREATE TABLE "Conquista" (
  "id_conquista" INTEGER PRIMARY KEY AUTOINCREMENT,
  "nome" VARCHAR,
  "descricao" TEXT,
  "recompensa" INTEGER
);

CREATE TABLE "Modificador" (
  "fk_id_item" INTEGER NOT NULL,
  "tipo" BOOLEAN,
  "valor" FLOAT,
  "alvo" BOOLEAN,
  "acumulador" INTEGER DEFAULT 0,
  CONSTRAINT "fk_modificador_item" FOREIGN KEY ("fk_id_item") REFERENCES "Item" ("id_item") ON DELETE CASCADE
);

CREATE TABLE "Item" (
  "id_item" INTEGER PRIMARY KEY AUTOINCREMENT,
  "nome" VARCHAR,
  "comprado" BOOLEAN DEFAULT FALSE,
  "descricao" TEXT,
  "preco" INTEGER,
  "aquisicao_data" TIMESTAMP DEFAULT NULL
);

CREATE TABLE "UsuarioItem" (
  "fk_id_usuario" INTEGER NOT NULL,
  "fk_id_item" INTEGER NOT NULL,
  PRIMARY KEY ("fk_id_usuario", "fk_id_item"),
  CONSTRAINT "fk_usuario" FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario") ON DELETE CASCADE,
  CONSTRAINT "fk_item" FOREIGN KEY ("fk_id_item") REFERENCES "Item" ("id_item") ON DELETE CASCADE
);

CREATE TABLE "Mensagem" (
  "id_mensagem" INTEGER PRIMARY KEY AUTOINCREMENT,
  "fk_id_usuario" INTEGER,
  "tipo_evento" VARCHAR,
  "texto" TEXT,
  "media_blob" BLOB,
  CONSTRAINT "fk_usuario" FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario") ON DELETE CASCADE
);

CREATE TABLE "Usuario" (
  "id_usuario" INTEGER PRIMARY KEY,
  "nome" VARCHAR,
  "pontos" INTEGER DEFAULT 0,
  "saldo" INTEGER DEFAULT 0
);

-- REGISTROS DE ITENS
-- A: aditivo, ponto
INSERT INTO Item (nome, descricao, preco)
VALUES ('A', 'Item 1.', 10);
INSERT INTO Modificador (fk_id_item, tipo, valor, alvo)
VALUES (last_insert_rowid(), FALSE, 20, FALSE);
-- B: aditivo, moeda
INSERT INTO Item (nome, descricao, preco)
VALUES ('B', 'Item 2.', 10);
INSERT INTO Modificador (fk_id_item, tipo, valor, alvo)
VALUES (last_insert_rowid(), FALSE, 20, TRUE);
-- C: multiplicativo, ponto
INSERT INTO Item (nome, descricao, preco)
VALUES ('C', 'Item 3.', 10);
INSERT INTO Modificador (fk_id_item, tipo, valor, alvo)
VALUES (last_insert_rowid(), TRUE, 0.1, FALSE);
-- D: multiplicativo, moeda
INSERT INTO Item (nome, descricao, preco)
VALUES ('D', 'Item 4.', 10);
INSERT INTO Modificador (fk_id_item, tipo, valor, alvo)
VALUES (last_insert_rowid(), TRUE, 0.2, TRUE);
-- E: aditivo, ponto
INSERT INTO Item (nome, descricao, preco)
VALUES ('E', 'Item 5.', 50);
INSERT INTO Modificador (fk_id_item, tipo, valor, alvo)
VALUES (last_insert_rowid(), FALSE, 20, FALSE);

-- REGISTROS DE CARGOS
INSERT INTO Cargo (cor, nome, prioridade)
VALUES ('#FFD700', 'Administrador', 5);
INSERT INTO Cargo (cor, nome, prioridade)
VALUES ('#00BFFF', 'Moderador', 4);
INSERT INTO Cargo (cor, nome, prioridade)
VALUES ('#32CD32', 'Membro VIP', 3);
INSERT INTO Cargo (cor, nome, prioridade)
VALUES ('#FFA500', 'Membro', 2);
INSERT INTO Cargo (cor, nome, prioridade)
VALUES ('#808080', 'Visitante', 1);

-- REGISTROS DE CONQUISTAS
INSERT INTO Conquista (nome, descricao, recompensa)
VALUES 
    ('Primeiro Problema', 'Resolva o primeiro problema.', 10),
    ('5 Corretos', 'Resolva 5 problemas corretamente.', 50),
    ('10 Corretos', 'Resolva 10 problemas corretamente.', 100),
    ('Sequencia de 5', 'Resolva 5 problemas corretamente em sequência.', 75),
    ('Sequencia de 10', 'Resolva 10 problemas corretamente em sequência.', 150);