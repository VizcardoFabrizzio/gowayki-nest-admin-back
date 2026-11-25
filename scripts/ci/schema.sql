-- Esquema minimo para CI: solo se aplica en el workflow, nunca en la BD real.
-- Aditivo e idempotente: no borra tablas ni columnas.

CREATE TABLE IF NOT EXISTS "usuario" (
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
ALTER TABLE "usuario" ADD COLUMN IF NOT EXISTS "activo" boolean NOT NULL DEFAULT true;
ALTER TABLE "usuario" ADD COLUMN IF NOT EXISTS "token_version" integer NOT NULL DEFAULT 0;
ALTER TABLE "usuario" ADD COLUMN IF NOT EXISTS "eliminado_en" timestamptz;
ALTER TABLE "usuario" ADD COLUMN IF NOT EXISTS "reactivado_en" timestamptz;

CREATE TABLE IF NOT EXISTS "linea" (
  "id" text,
  "nombre" text,
  "origen" text,
  "destino" text,
  "corredor" text,
  "color_hex" text,
  "created_at" text
);

CREATE TABLE IF NOT EXISTS "unidad" (
  "id" text,
  "numero_padron" text,
  "placa" text,
  "linea_id" text,
  "estado" text,
  "created_at" text
);
ALTER TABLE "unidad" ADD COLUMN IF NOT EXISTS "subruta_id" integer;

CREATE TABLE IF NOT EXISTS "punto_control" (
  "id" text,
  "linea_id" text,
  "nombre" text,
  "orden" text,
  "radio_tolerancia_metros" text,
  "tolerancia_minutos" text,
  "created_at" text
);

CREATE TABLE IF NOT EXISTS "usuario_linea" (
  "usuario_id" text,
  "linea_id" text
);
ALTER TABLE "usuario_linea" ADD COLUMN IF NOT EXISTS "subruta_id" integer;

CREATE TABLE IF NOT EXISTS "solicitud_registro" (
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
ALTER TABLE "solicitud_registro" ADD COLUMN IF NOT EXISTS "subruta_solicitada_id" integer;

CREATE TABLE IF NOT EXISTS "subruta" (
  "id" integer PRIMARY KEY,
  "codigo" varchar(50) NOT NULL,
  "nombre" varchar(255) NOT NULL,
  "linea_codigo" varchar(20),
  "activa" boolean NOT NULL DEFAULT true
);

-- Consultadas por has_registros al borrar una unidad.
CREATE TABLE IF NOT EXISTS "asignacion_turno" (
  "id" bigserial PRIMARY KEY,
  "unidad_id" integer
);

CREATE TABLE IF NOT EXISTS "alerta_incidencia" (
  "id" bigserial PRIMARY KEY,
  "unidad_id" integer
);
