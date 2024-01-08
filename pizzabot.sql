create database if not exists pizzabot;
use pizzabot;

create table pizzas (
	pizza_id INT NOT NULL AUTO_INCREMENT,
    pizza_type VARCHAR(50),
    price DECIMAL (10, 2),
    preparation_time INT, 
    PRIMARY KEY (pizza_id)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INT NOT NULL,
    pizza_id INT,
    quantity INT,
    total_price DECIMAL(10, 2),
    order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    preparation_time INT,  -- Add a foreign key reference to the pizzas table
    transit_time INT,
    status ENUM('Being Prepared', 'In Transit', 'Delivered') DEFAULT 'Being Prepared',
    PRIMARY KEY (order_id, pizza_id),
    FOREIGN KEY (pizza_id) REFERENCES pizzas(pizza_id),
    FOREIGN KEY (preparation_time) REFERENCES pizzas(preparation_time)
);

-- UNIQUE KEY unique_order_pizza (order_id, pizza_id), -> no duplicate entries for the same pizza in the same order

create table locations (
	location_id INT NOT NULL AUTO_INCREMENT,
    location_name VARCHAR(40),
    time_taken INT
);

select * from orders;
-- DELETE FROM orders WHERE order_id = 1;

drop table orders;
drop table pizzas;