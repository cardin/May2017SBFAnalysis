/* Though SQLite only has 4 storage types, it's best to write like standard SQL */
/* PRIMARY = UNIQUE is implied */
BEGIN TRANSACTION;
DROP TABLE IF EXISTS Day;
DROP TABLE IF EXISTS Block;
DROP TABLE IF EXISTS Apartment;
DROP TABLE IF EXISTS Lease_Price;
COMMIT;
VACUUM;

/* Indexing Strategies:
    * Offline search, so no. of indices is irrelevant
    * High selectivity (< 1% of total rows)
*/

BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS Day (
    day_id INT(10) UNIQUE NOT NULL,
    year SMALLINT(4) NOT NULL,
    month TINYINT(2),
    day TINYINT(2),
    quarter TINYINT(1),
    months_since SMALLINT(4) NOT NULL,
    PRIMARY KEY(day_id)
);


CREATE TABLE IF NOT EXISTS Block (
    town_name VARCHAR(100) NOT NULL,
    title_name VARCHAR(100) NOT NULL,
    block_id INT(10) UNIQUE NOT NULL,
    flat_type VARCHAR(100) NOT NULL,
    block VARCHAR(5) NOT NULL,
    street VARCHAR(255) NOT NULL,
    postal_code INT(6) NOT NULL,
    lat FLOAT(10) NOT NULL,
    long FLOAT(10) NOT NULL,
    pcd_date INT(10),
    dpd_date INT(10),
    lcd_date INT(10),
    quota_m SMALLINT(4) NOT NULL,
    quota_c SMALLINT(4) NOT NULL,
    quota_o SMALLINT(4) NOT NULL,
    CONSTRAINT flatType_address UNIQUE(flat_type, block, street),
    CONSTRAINT flatType_postal UNIQUE(flat_type, block, postal_code),
    PRIMARY KEY(block_id),
    FOREIGN KEY(pcd_date) REFERENCES Day(day_id),
    FOREIGN KEY(dpd_date) REFERENCES Day(day_id),
    FOREIGN KEY(lcd_date) REFERENCES Day(day_id)
);
CREATE INDEX IF NOT EXISTS Block_title ON Block(title_name);
CREATE INDEX IF NOT EXISTS Block_lat ON Block(lat);
CREATE INDEX IF NOT EXISTS Block_long ON Block(long);
CREATE INDEX IF NOT EXISTS Block_pcd ON Block(pcd_date);
CREATE INDEX IF NOT EXISTS Block_dpd ON Block(dpd_date);
CREATE INDEX IF NOT EXISTS Block_lcd ON Block(lcd_date);


CREATE TABLE IF NOT EXISTS Apartment (
    block_id INT(10) NOT NULL,
    apartment_id INT(10) NOT NULL,
    floor TINYINT(2) NOT NULL,
    unit VARCHAR(5) NOT NULL,
    area FLOAT(10) NOT NULL,
    repurchased BOOLEAN NOT NULL,
    PRIMARY KEY(apartment_id),
    CONSTRAINT block_floor_unit UNIQUE(block_id, floor, unit),
    FOREIGN KEY(block_id) REFERENCES Block(block_id)
);
-- no floor - most queries will target >50%
CREATE INDEX IF NOT EXISTS Apartment_block_id ON Apartment(block_id);
CREATE INDEX IF NOT EXISTS Apartment_area ON Apartment(area);


CREATE TABLE IF NOT EXISTS Lease_Price (
    apartment_id INT(10) NOT NULL,
    lease TINYINT(3) NOT NULL,
    price INT(10) NOT NULL,
    PRIMARY KEY(apartment_id, lease),
    FOREIGN KEY(apartment_id) REFERENCES Apartment(apartment_id)
);
-- no lease - most queries will target >50%
CREATE INDEX IF NOT EXISTS Lease_Price_price ON Lease_Price(price);
COMMIT;