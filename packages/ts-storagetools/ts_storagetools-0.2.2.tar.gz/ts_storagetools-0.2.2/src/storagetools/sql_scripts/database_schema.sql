CREATE TABLE association (
  child GUID NOT NULL,
  parent GUID NOT NULL,
  UNIQUE(child, parent)
);

CREATE TABLE experiment (
  guid GUID PRIMARY KEY
);

CREATE TABLE sensor (
  guid GUID PRIMARY KEY
);

CREATE TABLE channel (
  guid GUID PRIMARY KEY
);

CREATE TABLE sensor_capture (
  guid GUID PRIMARY KEY,
  capture_of GUID NOT NULL,
  FOREIGN KEY (capture_of) REFERENCES sensor (guid)
);

CREATE TABLE channel_capture (
  guid GUID PRIMARY KEY,
  capture_of GUID NOT NULL,
  FOREIGN KEY (capture_of) REFERENCES channel (guid)
);

CREATE TABLE ts_representation (
  guid GUID PRIMARY KEY,
  name TEXT,
  type TEXT
);

CREATE TABLE container (
  guid GUID PRIMARY KEY,
  name TEXT NOT NULL,
  info TEXT 
);
