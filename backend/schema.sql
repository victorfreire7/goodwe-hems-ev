CREATE TABLE IF NOT EXISTS simulations (
  simulation_id VARCHAR(64) COLLATE utf8mb4_bin PRIMARY KEY
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS steps (
  simulation_id VARCHAR(64) COLLATE utf8mb4_bin NOT NULL,
  time_ms BIGINT NOT NULL,
  request_hash CHAR(64) NOT NULL,
  payload JSON NOT NULL,
  PRIMARY KEY (simulation_id, time_ms),
  FOREIGN KEY (simulation_id) REFERENCES simulations(simulation_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS readings (
  simulation_id VARCHAR(64) COLLATE utf8mb4_bin NOT NULL,
  house_id VARCHAR(64) COLLATE utf8mb4_bin NOT NULL,
  time_ms BIGINT NOT NULL,
  payload JSON NOT NULL,
  PRIMARY KEY (simulation_id, house_id, time_ms),
  FOREIGN KEY (simulation_id, time_ms) REFERENCES steps(simulation_id, time_ms)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS trades (
  simulation_id VARCHAR(64) COLLATE utf8mb4_bin NOT NULL,
  time_ms BIGINT NOT NULL,
  trade_index INT NOT NULL,
  payload JSON NOT NULL,
  PRIMARY KEY (simulation_id, time_ms, trade_index),
  FOREIGN KEY (simulation_id, time_ms) REFERENCES steps(simulation_id, time_ms)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ev_targets (
  simulation_id VARCHAR(64) COLLATE utf8mb4_bin NOT NULL,
  house_id VARCHAR(64) COLLATE utf8mb4_bin NOT NULL,
  payload JSON NOT NULL,
  PRIMARY KEY (simulation_id, house_id),
  FOREIGN KEY (simulation_id) REFERENCES simulations(simulation_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS comparisons (
  simulation_id VARCHAR(64) COLLATE utf8mb4_bin PRIMARY KEY,
  payload JSON NOT NULL,
  FOREIGN KEY (simulation_id) REFERENCES simulations(simulation_id)
) ENGINE=InnoDB;
