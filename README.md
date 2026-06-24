# 🗂️ Office DTR System

## 📌 Overview

The **Office DTR (Daily Time Record) System** is a lightweight Django-based web application designed to track and manage employee attendance within an office environment. It provides a structured and efficient way to record time-in/time-out data, monitor attendance trends, and support decision-making through real-time dashboards.

---

## 🏗️ System Architecture

The application follows a **three-layer architecture**:

### 1. Data Layer

* Powered by **SQLite**
* Core tables include:

  * Departments
  * Employees
  * Daily Time Records (DTR)

### 2. Business Logic Layer

* Implemented using Django views
* Key functionalities:

  * List and sort employee records (alphabetically by last name)
  * Search and filter by:

    * Employee Name
    * Employee ID
    * Department
  * Edit and update records
  * Time-in and time-out tracking
  * Excel import/export

### 3. Presentation Layer

* Built with **Bootstrap** for responsive UI
* Integrated with **Chart.js** for data visualization
* Features:

  * Dynamic tables
  * Visual dashboards
  * Highlight feedback (edited rows flash yellow for confirmation)

---

## 📊 Dashboard & Analytics

The dashboard acts as a **decision-making assistant**, providing real-time insights:

### 🔄 Data Processing

* A background module (`dtr/dashboard.py`) aggregates:

  * Last 14 days of attendance data
  * Total work hours
  * Attendance status counts
  * Daily trends
  * Department comparisons

### ⚡ Live Updates

* Dashboard fetches data from `/dashboard/data.json` every **5 seconds**
* Uses an **MD5 version hash** to detect changes
* Automatically updates:

  * Chart.js visualizations
  * Insight cards

### 📈 Key Insights Displayed

* Completion Rate
* Top Performer
* Late Leader
* Busiest Day

---

## 🔁 Data Synchronization

All system updates—whether from:

* Web interface edits, or
* Excel uploads

…are stored in the same SQLite database.

➡️ The dashboard reflects changes **automatically within seconds**.

---

## 📥📤 Excel Integration

The system includes a robust Excel import/export feature:

### 📤 Export

* Consistent column format:

  * Employee ID
  * Name
  * Department
  * Date
  * Time In / Time Out
  * Hours Worked
  * Status
  * Remarks

### 📥 Import

* Validates uploaded files against the required header format
* Ensures data consistency before inserting into the database

### 🌉 Purpose

This feature turns Excel into a **portable, editable version of the database**, allowing managers to:

* Work offline
* Modify attendance data
* Re-upload changes seamlessly

---

## ✨ Key Features

* 📋 Employee attendance tracking
* 🔍 Advanced search and filtering
* ⚡ Real-time dashboard updates
* 📊 Data visualization with Chart.js
* 📁 Excel import/export support
* 🎯 Immediate visual feedback on edits

---

## 🚀 Use Case

This system is ideal for:

* Small to medium-sized offices
* Academic or prototype systems
* Attendance monitoring with analytics support

---

## 🛠️ Tech Stack

* **Backend:** Django (Python)
* **Database:** SQLite
* **Frontend:** Bootstrap, HTML/CSS
* **Visualization:** Chart.js
* **Data Exchange:** Excel (XLSX)

---

## 📌 Notes

* The system ensures **data consistency** by using a single source of truth (SQLite database).
* Dashboard updates are **automatic and near real-time**, requiring no manual refresh.
* Excel integration allows **flexible data management outside the system**.

---

## 👨‍💻 Author

Developed as part of a project focused on combining:

* Web development
* Data visualization
* Real-time system feedback

---

## 📄 License

This project is intended for educational and demonstration purposes.
