CREATE TABLE IF NOT EXISTS `Patient_table` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`age` int,
	`gender` varchar(255),
	`height` float,
	`weight` float,
	`frame` varchar(255),
	`waist` float,
	`hip` float,
	`location` varchar(255),
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `medical_history` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`pregnancies` int,
	`glucose` int,
	`bloodpressure` float,
	`skinthickness` float,
	`insulin` float,
	`bmi` float,
	`diabetespedigreefunction` float,
	`glyhb` float,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `cholesterol_bp` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`chol` float,
	`stab.glu` float,
	`hdl` float,
	`ratio` float,
	`bp.1s` float,
	`bp.1d` float,
	`bp.2s` float,
	`bp.2d` float,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `diabetes_diagnosis` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`outcome` boolean NOT NULL,
	`diabete` varchar(255) NOT NULL,
	PRIMARY KEY (`id`)
);


ALTER TABLE `medical_history` ADD CONSTRAINT `medical_history_fk0` FOREIGN KEY (`id`) REFERENCES `Patient_table`(`id`);
ALTER TABLE `cholesterol_bp` ADD CONSTRAINT `cholesterol_bp_fk0` FOREIGN KEY (`id`) REFERENCES `Patient_table`(`id`);
ALTER TABLE `diabetes_diagnosis` ADD CONSTRAINT `diabetes_diagnosis_fk0` FOREIGN KEY (`id`) REFERENCES `Patient_table`(`id`);