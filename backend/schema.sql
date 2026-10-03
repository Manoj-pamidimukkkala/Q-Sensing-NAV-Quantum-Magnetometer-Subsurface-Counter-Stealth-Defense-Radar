CREATE DATABASE IF NOT EXISTS drdo_qnav_db;
USE drdo_qnav_db;

CREATE TABLE IF NOT EXISTS magnetic_anomalies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,
    flux_density_nT FLOAT NOT NULL,
    target_classification VARCHAR(100) DEFAULT 'UNIDENTIFIED_SUB_SURFACE'
);
