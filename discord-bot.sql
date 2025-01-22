CREATE TABLE "Cargo" (
  "id_cargo" serial PRIMARY KEY,
  "cor" varchar,
  "nome" varchar,
  "prioridade" integer
);

CREATE TABLE "UsuarioCargo" (
  "id_usuariocargo" serial PRIMARY KEY,
  "fk_id_usuario" integer NOT NULL,
  "fk_id_cargo" integer NOT NULL
);

CREATE TABLE "Servidor" (
  "id_servidor" serial PRIMARY KEY,
  "nome" varchar
);

CREATE TABLE "UsuarioServidor" (
  "fk_id_usuario" integer,
  "fk_id_servidor" integer,
  PRIMARY KEY ("fk_id_usuario", "fk_id_servidor")
);

CREATE TABLE "Estatistica" (
  "id_estatistica" serial,
  "acertos" integer,
  "total" integer,
  "streak" integer,
  "streak_max" integer,
  "fk_id_usuario" integer,
  PRIMARY KEY ("id_estatistica", "fk_id_usuario")
);

CREATE TABLE "ComandoLog" (
  "parametro" text,
  "comando_data" timestamp,
  "fk_id_usuario" integer PRIMARY KEY,
  "fk_id_comando" integer NOT NULL
);

CREATE TABLE "Comando" (
  "id_comando" serial PRIMARY KEY,
  "nome" varchar,
  "descricao" text,
  "requerimento" integer
);

CREATE TABLE "UsuarioConquista" (
  "completo" boolean,
  "completo_em" timestamp,
  "fk_id_conquista" integer NOT NULL,
  "fk_id_usuario" integer PRIMARY KEY
);

CREATE TABLE "Conquista" (
  "id_conquista" serial PRIMARY KEY,
  "nome" varchar,
  "descricao" text,
  "recompensa" integer
);

CREATE TABLE "Modificador" (
  "id_item" serial PRIMARY KEY,
  "fk_id_item" integer NOT NULL,
  "tipo" boolean,
  "valor" float,
  "alvo" boolean,
  "acumulador" integer
);

CREATE TABLE "Item" (
  "id_item" serial PRIMARY KEY,
  "nome" varchar,
  "comprado" boolean,
  "descricao" text,
  "preco" integer,
  "aquisicao_data" timestamp
);

CREATE TABLE "UsuarioItem" (
  "fk_id_usuario" integer,
  "fk_id_item" integer,
  PRIMARY KEY ("fk_id_usuario", "fk_id_item")
);

CREATE TABLE "Mensagem" (
  "id_mensagem" serial PRIMARY KEY,
  "fk_id_usuario" integer,
  "tipo_evento" varchar,
  "texto" text,
  "media_blob" blob
);

CREATE TABLE "Usuario" (
  "id_usuario" serial PRIMARY KEY,
  "nome" varchar,
  "pontos" integer,
  "saldo" integer
);

-- ALTER TABLE "UsuarioServidor" ADD FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario");

-- ALTER TABLE "UsuarioServidor" ADD FOREIGN KEY ("fk_id_servidor") REFERENCES "Servidor" ("id_servidor");

-- ALTER TABLE "Estatistica" ADD FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario");

-- ALTER TABLE "ComandoLog" ADD FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario");

-- ALTER TABLE "UsuarioConquista" ADD FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario");

-- ALTER TABLE "UsuarioItem" ADD FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario");

-- ALTER TABLE "UsuarioItem" ADD FOREIGN KEY ("fk_id_item") REFERENCES "Item" ("id_item");

-- ALTER TABLE "Mensagem" ADD FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario");

-- ALTER TABLE "UsuarioCargo" ADD FOREIGN KEY ("fk_id_usuario") REFERENCES "Usuario" ("id_usuario");

-- ALTER TABLE "UsuarioCargo" ADD FOREIGN KEY ("fk_id_cargo") REFERENCES "Cargo" ("id_cargo");

-- ALTER TABLE "ComandoLog" ADD FOREIGN KEY ("fk_id_comando") REFERENCES "Comando" ("id_comando");

-- ALTER TABLE "UsuarioConquista" ADD FOREIGN KEY ("fk_id_conquista") REFERENCES "Conquista" ("id_conquista");

-- ALTER TABLE "Modificador" ADD FOREIGN KEY ("fk_id_item") REFERENCES "Item" ("id_item");
