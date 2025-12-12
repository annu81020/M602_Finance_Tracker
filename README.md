# Personal Finance Tracker with Multi-Currency Support

## Project Overview
This is a Python-based desktop application designed to help users track their income and expenses efficiently. Built as part of a university Software Engineering assessment, this tool addresses the challenge of managing finances in a globalized world by offering **real-time currency conversion**.

Users can input transactions in major global currencies (EUR, GBP, JPY, etc.), and the application automatically standardizes them into a user-selected "Base Currency" (e.g., USD) using a live API. This ensures an accurate total balance regardless of where the money was spent.

## Key Features
* **Object-Oriented Design:** structured using modular classes (`Transaction`, `FinanceManager`) for maintainability.
* **Live Currency Conversion:** Integrates with **ExchangeRate-API** to fetch real-time rates.
* **Dynamic Base Currency:** Users can switch their home currency (e.g., from USD to EUR) and the entire dashboard recalculates instantly.
* **Data Persistence:** Uses JSON file handling to save and load transactions and user settings.
* **Visual Analytics:** Generates a Pie Chart using `matplotlib` to visualize expense distribution.
* **CRUD Functionality:** Full support to Create, Read, Update, and Delete transactions.

## Technologies Used
* **Language:** Python 3.x
* **GUI:** Tkinter (Standard Library)
* **API Handling:** `requests` library
* **Visualization:** `matplotlib` library
* **Data Storage:** JSON

## Installation & Setup

### Prerequisites
Ensure you have Python 3.x installed. You will also need the following external libraries:

```bash
pip install -r requirements.txt
