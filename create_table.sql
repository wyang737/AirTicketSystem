CREATE TABLE Airport
(
    airport_name varchar(10) not null unique,
    city varchar(20),
    PRIMARY KEY (airport_name)
);

CREATE TABLE Airplane
(
    airplane_id numeric(10, 0) not null unique,
    num_seats int CHECK (num_seats > 0),
    airline_name varchar(20),
    PRIMARY KEY (airplane_id),
    FOREIGN KEY (airline_name) REFERENCES airline(airline_name) on delete set null
);

CREATE TABLE Airline
(
	airline_name varchar(20) not null unique,
    PRIMARY KEY (airline_name)
);

CREATE TABLE Flight
(
	airline_name varchar(20),
	status varchar(10) CHECK (status in ('Delayed', 'On Time')),
	flight_number numeric(9, 0) not null,
	departure_airport varchar(10),
	departure_date date,
	departure_time time,
	arrival_airport varchar(10),
	arrival_date date,
	arrival_time time,
	base_price int,
	airplane_id numeric(10, 0),
	PRIMARY KEY (flight_number, departure_date, departure_time),
	FOREIGN KEY (departure_airport) REFERENCES Airport(airport_name) on delete set null,
	FOREIGN KEY (arrival_airport) REFERENCES Airport(airport_name) on delete set null,
	FOREIGN KEY (airline_name) REFERENCES airline(airline_name) on delete set null,
	FOREIGN KEY (airplane_id) REFERENCES Airplane(airplane_id) on delete set null
);

CREATE TABLE Ticket
(

	ticket_id numeric(8, 0) not null unique,
	airline_name varchar(20),
	flight_number numeric(9, 0),
	PRIMARY KEY (ticket_id),
	FOREIGN KEY (airline_name) REFERENCES flight(airline_name) on delete set null,
	FOREIGN KEY (flight_number) REFERENCES flight(flight_number) on delete set null
);

CREATE TABLE Customer
(
	name varchar(30),
	customer_email varchar(30) not null unique,
	password varchar(40),
	building_number int,
	street varchar(20),
	city varchar(20),
	state varchar(20),
	phone_number numeric(10, 0),
	passport_number numeric(9, 0),
	passport_expiration date,
	passport_country varchar(20),
	date_of_birth date,
	PRIMARY KEY (customer_email)
);

CREATE TABLE Rates
(
	customer_email varchar(30) not null,
	flight_number numeric(9, 0),
	comment varchar(200),
	rating int CHECK (rating >= 1 and rating <= 100), # 1-100 scale
	PRIMARY KEY (customer_email, flight_number),
	FOREIGN KEY (customer_email) REFERENCES customer(customer_email) on delete cascade,
	FOREIGN KEY (flight_number) REFERENCES flight(flight_number) on delete cascade
);

CREATE TABLE BookingAgent
(
	booking_agent_email varchar(30) unique,
	password varchar(40),
	booking_agent_id numeric(5, 0),
	commission int,
	PRIMARY KEY(booking_agent_email)
);

CREATE TABLE Purchases
(
	ticket_id numeric(8, 0) not null unique,
	customer_email varchar(30),
	booking_agent_id varchar(30),
	sold_price int,
	purchase_date date,
	purchase_time time,
	card_type varchar(6) CHECK (card_type in ('credit', 'debit')),
	card_number numeric(16, 0),
	card_name varchar(20),
	card_expiration_date date,
	PRIMARY KEY (ticket_id, customer_email),
	FOREIGN KEY (ticket_id) REFERENCES Ticket(ticket_id) on delete cascade,
	FOREIGN KEY (customer_email) REFERENCES customer(customer_email) on delete set null,
	FOREIGN KEY (booking_agent_id) REFERENCES BookingAgent(booking_agent_id) on delete set null
);

CREATE TABLE StaffPhones
(
	username varchar(20),
	phone_number numeric(10, 0),
	FOREIGN KEY (username) REFERENCES Staff(username) on delete cascade
);

CREATE TABLE Staff
(
	username varchar(20) not null unique,
	password varchar(40),
	name varchar(30),
	date_of_birth date,
	phone_number numeric(10, 0),
	airline_name varchar(20),
	PRIMARY KEY (username),
	FOREIGN KEY (phone_number) REFERENCES StaffPhones(phone_number) on delete set null,
	FOREIGN KEY (airline_name) REFERENCES airline(airline_name) on delete set null
);
