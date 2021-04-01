# Overview
Project for Intro to Databases (CS-UY 3083) by Brian Guo & Winston Yang. This project aims to simulate an online Air Ticket Reservation System. The system has 3 types of users - customers, booking agents, and airline staff. 

## Functional Requirements

1. **View Public Info:** All users, whether logged in or not, can:
     * Search for future flights based on source city/airport name, destination city/airport name, departure date for one way (departure and return dates for round trip).
     * Will be able to see the flights status based on airline name, flight number, arrival/departure
date. 
2. **Register:**   3 types of user registrations (Customer, Booking Agent and Airline Staff) option via forms.
3. **Login:** Users enters their username
(email address will be used as username), x, and password, y, via forms on login page. This data is sent
as POST parameters to the login-authentication component, which checks whether there is a tuple in
the corresponding user’s table with username=x and the password = md5(y).
### Customer 

1. **View My flights:** Provide various ways for the user to see flights information which he/she purchased.
The default should be showing for the future flights.
2. **Search for flights:** Search for future flights (one way or round trip) based on source city/airport name,
destination city/airport name, dates (departure or return).
3. **Purchase tickets:** Customer chooses a flight and purchase ticket for this flight, providing all the
needed data, via forms. You may find it easier to implement this along with a use case to search for
flights. 
4. **Give Ratings and Comment on previous flights:** Customer will be able to rate and comment on their
previous flights (for which he/she purchased tickets and already took that flight) for the airline they
logged in.
5. **Track My Spending:** Default view will be total amount of money spent in the past year and a bar
chart showing month wise money spent for last 6 months. He/she will also have option to specify a
range of dates to view total amount of money spent within that range and a bar chart showing month
wise money spent within that range.
6. **Logout:** The session is destroyed and a “goodbye” page or the login page is displayed

### Booking Agent

1. **View My flights:** Provide various ways for the booking agents to see flights information for which
he/she purchased on behalf of customers. The default should be showing for the future flights.
Optionally you may include a way for the user to specify a range of dates, specify destination and/or
source airport name and/or city name etc to show all the flights for which he/she purchased tickets.
2. **Search for flights:** Search for future flights (one way or round trip) based on source city/airport name,
destination city/airport name, dates (departure or arrival).
3. **Purchase tickets:** Booking agent chooses a flight and purchases tickets for other customers giving
customer information and payment information, providing all the needed data, via forms. You may find
it easier to implement this along with a use case to search for flights. 
4. **View my commission:** Default view will be total amount of commission received in the past 30 days
and the average commission he/she received per ticket booked in the past 30 days and total
number of tickets sold by him in the past 30 days. He/she will also have option to specify a range of
dates to view total amount of commission received and total numbers of tickets sold.
5. **View Top Customers:** Top 5 customers based on number of tickets bought from the booking agent in
the past 6 months and top 5 customers based on amount of commission received in the last year. Show
a bar chart showing each of these 5 customers in x-axis and number of tickets bought in y-axis. Show
another bar chart showing each of these 5 customers in x-axis and amount commission received in yaxis.
6. **Logout:** The session is destroyed and a “goodbye” page or the login page is displayed.

### Airline Staff

1. **View flights:** Defaults will be showing all the future flights operated by the airline he/she works for
the next 30 days. He/she will be able to see all the current/future/past flights operated by the airline
he/she works for based range of dates, source/destination airports/city etc. He/she will be able to see
all the customers of a particular flight.
2. **Create new flights:** He or she creates a new flight, providing all the needed data, via forms. The
application should prevent unauthorized users from doing this action. Defaults will be showing all the
future flights operated by the airline he/she works for the next 30 days.
3. **Change Status of flights:** He or she changes a flight status (from on-time to delayed or vice versa) via
forms.
4. **Add airplane in the system:** He or she adds a new airplane, providing all the needed data, via forms.
The application should prevent unauthorized users from doing this action. In the confirmation page,
she/he will be able to see all the airplanes owned by the airline he/she works for.
5. **Add new airport in the system:** He or she adds a new airport, providing all the needed data, via
forms. The application should prevent unauthorized users from doing this action.
6. **View flight ratings:** Airline Staff will be able to see each flight’s average ratings and all the comments
and ratings of that flight given by the customers.
7. **View all the booking agents:** Top 5 booking agents based on number of tickets sales for the past
month and past year. Top 5 booking agents based on the amount of commission received for the last
year.
8. **View frequent customers:** Airline Staff will also be able to see the most frequent customer within
the last year. In addition, Airline Staff will be able to see a list of all flights a particular Customer has
taken only on that particular airline.
9. **View reports:** Total amounts of ticket sold based on range of dates/last year/last month etc. Month
wise tickets sold in a bar chart.
10. **Comparison of Revenue earned:** Draw a pie chart for showing total amount of revenue earned from
direct sales (when customer bought tickets without using a booking agent) and total amount of revenue
earned from indirect sales (when customer bought tickets using booking agents) in the last month and
last year.
11. **View Top destinations:** Find the top 3 most popular destinations for last 3 months and last year
(based on tickets already sold).
12. **Logout:** The session is destroyed and a “goodbye” page or the login page is displayed.
