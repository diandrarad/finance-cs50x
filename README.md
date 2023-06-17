# C$50 Stock Trader

## Description
C$50 Stock Trader is a web application built using Flask, Python, HTML, JavaScript, Bootstrap, and Bootswatch. It allows users to "buy" and "sell" stocks, look up stock prices, view transaction history, and manage their portfolio. This application serves as a practical implementation of concepts learned in the CS50 course.

## Technologies Used
- Flask: A lightweight web framework used to handle routing, rendering templates, and processing user requests.
- Python: The programming language used to develop the backend logic and interact with the database.
- HTML: The markup language used for creating the structure and content of web pages.
- JavaScript: The scripting language used to add interactivity and dynamic features to the application.
- Bootstrap: A popular CSS framework that provides pre-designed templates and components for responsive web design.
- Bootswatch: A theme library for Bootstrap that enhances the visual appearance of the application.

## Functionality
The C$50 Stock Trader web application provides the following functionality:

1. Register: Users can create an account by providing a unique username and password. Duplicate usernames and empty fields are not allowed.
2. Quote: Users can look up the current price of a stock by entering its symbol. The application retrieves the stock information using an external API.
3. Buy: Users can buy stocks by entering the stock symbol and the number of shares they want to purchase. The application verifies the input, checks the user's available cash balance, and stores the transaction details in the database.
4. Sell: Users can sell shares of stocks they own. They select the stock symbol and enter the number of shares to sell. The application validates the input and updates the user's portfolio accordingly.
5. Index: Users can view a summary of their portfolio, including the stocks they own, the number of shares, the current prices, and the total value of each holding. The user's cash balance is also displayed, along with the overall portfolio value.
6. History: Users can access a transaction history table that lists all their buy and sell transactions. Each row includes information about the stock symbol, transaction type, price, number of shares, and the date and time of the transaction.
7. Change Password: Users can change their account password to enhance security.
8. Add Cash: Users can add additional cash to their account to increase their buying power.

## Installation
To run the CS50 Stock Trader web application, follow these steps:

1. Install Python: Make sure you have Python installed on your machine. You can download it from the official [Python website](https://www.python.org) and follow the installation instructions for your operating system.
2. Install Dependencies: Open a terminal or command prompt and navigate to the project directory. Run the following command to install the required dependencies:

```pip install -r requirements.txt```

3. Start the Application: Run the following command to start the application:

```flask run```

4. Access the Application: Open a web browser and visit http://127.0.0.1:5000 to access the C$50 Stock Trader web application.

## Credits
The C$50 Stock Trader web application was created as part of the CS50 course offered by Harvard University. The initial code and specifications were provided by the course instructors and teaching staff.

- Course website: https://cs50.harvard.edu
- Flask: https://flask.palletsprojects.com
- Python: https://www.python.org
- HTML: https://developer.mozilla.org/en-US/docs/Web/HTML
- JavaScript: https://developer.mozilla.org/en-US/docs/Web/JavaScript
- Bootstrap: https://getbootstrap.com
- Bootswatch: https://bootswatch.com
