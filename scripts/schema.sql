DROP TABLE IF EXISTS "usuario" CASCADE;
CREATE TABLE "usuario" (
  "id" text,
  "nombre" text,
  "dni" text,
  "telefono" text,
  "email" text,
  "pin_hash" text,
  "foto_url" text,
  "rol" text,
  "is_online" text,
  "intentos_fallidos" text,
  "bloqueado_hasta" text,
  "created_at" text
);

DROP TABLE IF EXISTS "linea" CASCADE;
CREATE TABLE "linea" (
  "id" text,
  "nombre" text,
  "origen" text,
  "destino" text,
  "corredor" text,
  "color_hex" text,
  "created_at" text
);

DROP TABLE IF EXISTS "unidad" CASCADE;
CREATE TABLE "unidad" (
  "id" text,
  "numero_padron" text,
  "placa" text,
  "linea_id" text,
  "estado" text,
  "created_at" text
);

DROP TABLE IF EXISTS "punto_control" CASCADE;
CREATE TABLE "punto_control" (
  "id" text,
  "linea_id" text,
  "nombre" text,
  "orden" text,
  "radio_tolerancia_metros" text,
  "tolerancia_minutos" text,
  "created_at" text
);

DROP TABLE IF EXISTS "usuario_linea" CASCADE;
CREATE TABLE "usuario_linea" (
  "usuario_id" text,
  "linea_id" text
);

DROP TABLE IF EXISTS "solicitud_registro" CASCADE;
CREATE TABLE "solicitud_registro" (
  "id" text,
  "tipo" text,
  "dni" text,
  "nombre_completo" text,
  "telefono" text,
  "email" text,
  "placa_numero" text,
  "ruta_trabajo" text,
  "usuario_id" text,
  "linea_solicitada_id" text,
  "pin_hash" text,
  "estado" text,
  "usuario_asignado" text,
  "creado_en" text,
  "actualizado_en" text
);
