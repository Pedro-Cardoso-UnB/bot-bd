CREATE TABLE "Cargo" (
  "id_cargo" integer PRIMARY KEY AUTOINCREMENT,
  "cor" varchar,
  "nome" varchar,
  "prioridade" integer
);

CREATE TABLE "UsuarioCargo" (
  "id_usuariocargo" integer PRIMARY KEY AUTOINCREMENT,
  "fk_id_usuario" integer NOT NULL,
  "fk_id_cargo" integer NOT NULL,
  CONSTRAINT "fk_usuario" FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario"),
  CONSTRAINT "fk_cargo" FOREIGN KEY ("fk_id_cargo") REFERENCES "Cargo" ("id_cargo")
);

CREATE TABLE "Servidor" (
  "id_servidor" integer PRIMARY KEY,
  "nome" varchar
);

CREATE TABLE "UsuarioServidor" (
  "fk_id_usuario" integer NOT NULL,
  "fk_id_servidor" integer NOT NULL,
  PRIMARY KEY ("fk_id_usuario", "fk_id_servidor"),
  CONSTRAINT "fk_usuario" FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario"),
  CONSTRAINT "fk_servidor" FOREIGN KEY ("fk_id_servidor") REFERENCES "Servidor" ("id_servidor")
);

CREATE TABLE "Estatistica" (
  "acertos" integer,
  "total" integer,
  "streak" integer,
  "streak_max" integer,
  "fk_id_usuario" integer NOT NULL UNIQUE,
  CONSTRAINT "fk_usuario" FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario")
);

CREATE TABLE "ComandoLog" (
  "parametro" text,
  "comando_data" timestamp,
  "fk_id_usuario" integer NOT NULL,
  "fk_id_comando" integer NOT NULL,
  PRIMARY KEY ("fk_id_usuario", "fk_id_comando"),
  CONSTRAINT "fk_usuario" FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario"),
  CONSTRAINT "fk_comando" FOREIGN KEY ("fk_id_comando") REFERENCES "Comando" ("id_comando")
);

CREATE TABLE "Comando" (
  "id_comando" integer PRIMARY KEY AUTOINCREMENT,
  "nome" varchar,
  "descricao" text,
  "requerimento" integer
);

CREATE TABLE "UsuarioConquista" (
  "completo" boolean DEFAULT false,
  "completo_em" timestamp,
  "fk_id_conquista" integer NOT NULL,
  "fk_id_usuario" integer NOT NULL,
  PRIMARY KEY ("fk_id_usuario", "fk_id_conquista"),
  CONSTRAINT "fk_usuario" FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario"),
  CONSTRAINT "fk_conquista" FOREIGN KEY ("fk_id_conquista") REFERENCES "Conquista" ("id_conquista")
);

CREATE TABLE "Conquista" (
  "id_conquista" integer PRIMARY KEY AUTOINCREMENT,
  "nome" varchar,
  "descricao" text,
  "recompensa" integer
);

CREATE TABLE "Modificador" (
  "fk_id_item" integer NOT NULL,
  "tipo" boolean,
  "valor" float,
  "alvo" boolean,
  "acumulador" integer DEFAULT 0,
  CONSTRAINT "fk_modificador_item" FOREIGN KEY ("fk_id_item") REFERENCES "Item" ("id_item") ON DELETE CASCADE
);

CREATE TABLE "Item" (
  "id_item" integer PRIMARY KEY AUTOINCREMENT,
  "nome" varchar,
  "comprado" boolean DEFAULT false,
  "descricao" text,
  "preco" integer,
  "aquisicao_data" timestamp DEFAULT NULL
);

CREATE TABLE "UsuarioItem" (
  "fk_id_usuario" integer NOT NULL,
  "fk_id_item" integer NOT NULL,
  PRIMARY KEY ("fk_id_usuario", "fk_id_item"),
  CONSTRAINT "fk_usuario" FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario"),
  CONSTRAINT "fk_item" FOREIGN KEY ("fk_id_item") REFERENCES "Item" ("id_item")
);

CREATE TABLE "Mensagem" (
  "id_mensagem" integer PRIMARY KEY AUTOINCREMENT,
  "fk_id_usuario" integer,
  "tipo_evento" varchar,
  "texto" text,
  "media_blob" blob,
  CONSTRAINT "fk_usuario" FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario")
);

CREATE TABLE "Usuario" (
  "id_usuario" integer PRIMARY KEY,
  "nome" varchar,
  "pontos" integer,
  "saldo" integer
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

-- REGISTROS DE MENSAGENS