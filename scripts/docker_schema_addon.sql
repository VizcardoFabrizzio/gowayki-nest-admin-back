-- Tablas que el backend Django espera y que el esquema compartido de Spring Boot no tiene.
-- Aditivo: NO modifica ni borra ninguna tabla existente (seguro para la API Java).
-- Ejecutar sobre la BD gowayki_db del contenedor postgis.

CREATE TABLE IF NOT EXISTS usuario_linea (
  usuario_id uuid PRIMARY KEY,
  linea_id   integer
);

CREATE TABLE IF NOT EXISTS solicitud_registro (
  id                  bigserial PRIMARY KEY,
  tipo                varchar(20)  NOT NULL DEFAULT 'CHOFER',
  dni                 varchar(8)   NOT NULL,
  nombre_completo     varchar(100) NOT NULL,
  telefono            varchar(9),
  email               varchar(120),
  placa_numero        varchar(10),
  ruta_trabajo        varchar(100),
  usuario_id          uuid,
  linea_solicitada_id integer,
  pin_hash            varchar(255),
  estado              varchar(20)  NOT NULL DEFAULT 'PENDIENTE',
  usuario_asignado    varchar(50),
  creado_en           timestamptz  NOT NULL DEFAULT now(),
  actualizado_en      timestamptz
);

-- Columnas que los modelos Django consultan y que pueden faltar en instalaciones
-- anteriores. Aditivo: ninguna sentencia elimina datos.
ALTER TABLE usuario_linea ADD COLUMN IF NOT EXISTS subruta_id integer;
ALTER TABLE unidad ADD COLUMN IF NOT EXISTS subruta_id integer;
ALTER TABLE solicitud_registro ADD COLUMN IF NOT EXISTS subruta_solicitada_id integer;
ALTER TABLE usuario ADD COLUMN IF NOT EXISTS activo boolean NOT NULL DEFAULT true;
ALTER TABLE usuario ADD COLUMN IF NOT EXISTS token_version integer NOT NULL DEFAULT 0;
ALTER TABLE usuario ADD COLUMN IF NOT EXISTS eliminado_en timestamptz;
ALTER TABLE usuario ADD COLUMN IF NOT EXISTS reactivado_en timestamptz;

-- Subrutas: tabla compartida con la API Java, solo lectura desde el panel.
CREATE TABLE IF NOT EXISTS subruta (
  id            integer PRIMARY KEY,
  codigo        varchar(50)  NOT NULL,
  nombre        varchar(255) NOT NULL,
  linea_codigo  varchar(20),
  activa        boolean      NOT NULL DEFAULT true
);

-- Historial consultado al intentar borrar una combi.
CREATE TABLE IF NOT EXISTS asignacion_turno (
  id         bigserial PRIMARY KEY,
  unidad_id  integer
);

CREATE TABLE IF NOT EXISTS alerta_incidencia (
  id         bigserial PRIMARY KEY,
  unidad_id  integer
);
