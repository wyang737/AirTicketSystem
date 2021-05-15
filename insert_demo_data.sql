INSERT INTO airline VALUES('United');
-- e2fc714c4727ee9395f324cd2e7f331f is 'abcd' after being hashed
INSERT INTO staff VALUES('admin', 'e2fc714c4727ee9395f324cd2e7f331f', 'Roe Jones', '1978-05-25', 11122223333, 'United');
INSERT INTO staffphones VALUES ('admin', 11122223333);
INSERT INTO staffphones VALUES ('admin',  44455556666);
INSERT INTO airplane VALUES (1, 4, 'United');
INSERT INTO airplane VALUES (2, 4, 'United');
INSERT INTO airplane VALUES (3, 50, 'United');
INSERT INTO airport VALUES ('JFK', 'NYC');
INSERT INTO airport VALUES ('BOS', 'Boston');
INSERT INTO airport VALUES ('PVG', 'Shanghai');
INSERT INTO airport VALUES ('BEI', 'Beijing');
INSERT INTO airport VALUES ('SHEN', 'Shenzhen');
INSERT INTO airport VALUES ('SFO', 'San Francisco');
INSERT INTO airport VALUES ('LAX', 'Los Angeles');
INSERT INTO airport VALUES ('HKA', 'Hong Kong');
-- aa9b780d550932a87de6e1a6f539d1bc is 'abcd1234' after being hashed
-- initial commission values for the purchases given
INSERT INTO bookingagent VALUES ('ctrip@agent.com', 'aa9b780d550932a87de6e1a6f539d1bc', 1, 245);
INSERT INTO bookingagent VALUES ('expedia@agent.com', 'aa9b780d550932a87de6e1a6f539d1bc', 2, 330);
-- 68b201de9f4f68771aec0094b04005c5 is '1234' after being hashed
INSERT INTO customer VALUES ('Test Customer 1', 'testcustomer@nyu.edu', '68b201de9f4f68771aec0094b04005c5', 1555, 'Jay Street', 'Brooklyn', 'New York', 12343214321, 54321, '2025-12-24', 'USA', '1999-12-19');
INSERT INTO customer VALUES ('User 1', 'user1@nyu.edu', '68b201de9f4f68771aec0094b04005c5', 5405, 'Jay Street', 'Brooklyn', 'New York', 12343224322, 54322, '2025-12-25', 'USA', '1999-11-19');
INSERT INTO customer VALUES ('User 2', 'user2@nyu.edu', '68b201de9f4f68771aec0094b04005c5', 1702, 'Jay Street', 'Brooklyn', 'New York', 12343214321, 54323, '2025-10-24', 'USA', '1999-10-19');
INSERT INTO customer VALUES ('User 3', 'user3@nyu.edu', '68b201de9f4f68771aec0094b04005c5', 1890, 'Jay Street', 'Brooklyn', 'New York', 12343214321, 54324, '2025-09-24', 'USA', '1999-09-19');
INSERT INTO flight VALUES ('United', 'On Time', 102, 'SFO', '2021-04-12', '13:25:00', 'LAX', '2021-04-12', '16:50:00', 300, 3);
INSERT INTO flight VALUES ('United', 'On Time', 104, 'PVG', '2021-05-14', '13:25:00', 'BEI', '2021-05-14', '16:50:00', 300, 3);
INSERT INTO flight VALUES ('United', 'Delayed', 106, 'SFO', '2021-03-12', '13:25:00', 'LAX', '2021-03-12', '16:50:00', 350, 3);
INSERT INTO flight VALUES ('United', 'On Time', 206, 'SFO', '2021-06-12', '13:25:00', 'LAX', '2021-06-12', '16:50:00', 400, 2);
INSERT INTO flight VALUES ('United', 'On Time', 207, 'LAX', '2021-07-12', '13:25:00', 'SFO', '2021-07-12', '16:50:00', 300, 2);
INSERT INTO flight VALUES ('United', 'Delayed', 134, 'JFK', '2021-02-12', '13:25:00', 'BOS', '2021-02-12', '16:50:00', 300, 3);
INSERT INTO flight VALUES ('United', 'On Time', 296, 'PVG', '2021-06-01', '13:25:00', 'SFO', '2021-06-01', '16:50:00', 3000, 1);
INSERT INTO flight VALUES ('United', 'Delayed', 715, 'PVG', '2021-04-28', '10:25:00', 'BEI', '2021-04-28', '13:50:00', 500, 1);
INSERT INTO flight VALUES ('United', 'On Time', 839, 'SHEN', '2020-07-12', '13:25:00', 'BEI', '2020-07-12', '16:50:00', 800, 3);
INSERT INTO ticket VALUES (1, 'United', 102);
INSERT INTO ticket VALUES (2, 'United', 102);
INSERT INTO ticket VALUES (3, 'United', 102);
INSERT INTO ticket VALUES (4, 'United', 104);
INSERT INTO ticket VALUES (5, 'United', 104);
INSERT INTO ticket VALUES (6, 'United', 106);
INSERT INTO ticket VALUES (7, 'United', 106);
INSERT INTO ticket VALUES (8, 'United', 839);
INSERT INTO ticket VALUES (9, 'United', 102);
INSERT INTO ticket VALUES (11, 'United', 134);
INSERT INTO ticket VALUES (12, 'United', 715);
INSERT INTO ticket VALUES (14, 'United', 206);
INSERT INTO ticket VALUES (15, 'United', 206);
INSERT INTO ticket VALUES (16, 'United', 206);
INSERT INTO ticket VALUES (17, 'United', 207);
INSERT INTO ticket VALUES (18, 'United', 207);
INSERT INTO ticket VALUES (19, 'United', 296);
INSERT INTO ticket VALUES (20, 'United', 296);

INSERT INTO purchases VALUES (1, 'testcustomer@nyu.edu', 1, 300, '2021-03-12', '11:55:55', 'Credit', 1111222233334444, 'Test Customer 1', '2023-03-01');
INSERT INTO purchases VALUES (2, 'user1@nyu.edu', NULL, 300, '2021-03-11', '11:55:55', 'Credit', 1111222233335555, 'User 1', '2023-03-01');
INSERT INTO purchases VALUES (3, 'user2@nyu.edu', NULL, 300, '2021-04-11', '11:55:55', 'Credit', 1111222233334444, 'User 2', '2023-03-01');
INSERT INTO purchases VALUES (4, 'user1@nyu.edu', NULL, 300, '2021-03-21', '11:55:55', 'Credit', 1111222233334444, 'User 1', '2023-03-01');
INSERT INTO purchases VALUES (5, 'testcustomer@nyu.edu', 1, 300, '2021-04-28', '11:55:55', 'Credit', 1111222233334444, 'Test Customer 1', '2023-03-01');
INSERT INTO purchases VALUES (6, 'testcustomer@nyu.edu', 1, 350, '2021-03-05', '11:55:55', 'Credit', 1111222233334444, 'Test Customer 1', '2023-03-01');
INSERT INTO purchases VALUES (7, 'user3@nyu.edu', NULL, 350, '2021-02-03', '11:55:55', 'Credit', 1111222233335555, 'User 3', '2023-03-01');
INSERT INTO purchases VALUES (8, 'user3@nyu.edu', NULL, 300, '2020-07-03', '11:55:55', 'Credit', 1111222233335555, 'User 3', '2023-03-01');
INSERT INTO purchases VALUES (9, 'user3@nyu.edu', NULL, 360, '2021-02-03', '11:55:55', 'Credit', 1111222233335555, 'User 3', '2023-03-01');
INSERT INTO purchases VALUES (11, 'user3@nyu.edu', 2, 300, '2020-07-23', '11:55:55', 'Credit', 1111222233335555, 'User 3', '2023-03-01');
INSERT INTO purchases VALUES (12, 'testcustomer@nyu.edu', 1, 500, '2021-03-05', '11:55:55', 'Credit', 1111222233334444, 'Test Customer 1', '2023-03-01');
INSERT INTO purchases VALUES (14, 'user3@nyu.edu', 1, 400, '2021-05-05', '11:55:55', 'Credit', 1111222233335555, 'User 3', '2023-03-01');
INSERT INTO purchases VALUES (15, 'user1@nyu.edu', NULL, 400, '2021-06-06', '11:55:55', 'Credit', 1111222233335555, 'User 1', '2023-03-01');
INSERT INTO purchases VALUES (16, 'user2@nyu.edu', NULL, 400, '2021-04-19', '11:55:55', 'Credit', 1111222233335555, 'User 2', '2023-03-01');
INSERT INTO purchases VALUES (17, 'user1@nyu.edu', 1, 300, '2021-03-11', '11:55:55', 'Credit', 1111222233335555, 'User 1', '2023-03-01');
INSERT INTO purchases VALUES (18, 'testcustomer@nyu.edu', 1, 300, '2021-04-25', '11:55:55', 'Credit', 1111222233334444, 'Test Customer 1', '2023-03-01');
INSERT INTO purchases VALUES (19, 'user1@nyu.edu', 2, 3000, '2021-05-04', '11:55:55', 'Credit', 1111222233335555, 'User 1', '2023-03-01');
INSERT INTO purchases VALUES (20, 'testcustomer@nyu.edu', NULL, 3000, '2021-02-12', '11:55:55', 'Credit', 1111222233334444, 'Test Customer 1', '2023-03-01');

-- converting /5 rating scale to 100
INSERT INTO rates VALUES ('testcustomer@nyu.edu', 102, 'Very Comfortable', 80);
INSERT INTO rates VALUES ('user1@nyu.edu', 102, 'Relaxing, check-in and onboarding very professional', 100);
INSERT INTO rates VALUES ('user3@nyu.edu', 102, 'Satisfied and will use same flight again', 60);
INSERT INTO rates VALUES ('testcustomer@nyu.edu', 104, 'Customer Care services are not good', 20);
INSERT INTO rates VALUES ('user1@nyu.edu', 104, 'Comfortable journey and Professional', 100);