# Full-Stack Flight Reservation System

A high-concurrency, full-stack flight booking engine designed to handle real-time ticket reservations, secure payment processing, and dynamic flight discovery. 
This project was built to tackle complex backend architectural challenges—such as preventing race conditions during simultaneous seat bookings—while delivering a seamless, state-driven Single Page Application on the frontend.

# Key Features

* **Concurrency Control & Seat Locking:** Implemented row-level database locking (`select_for_update`) to temporarily lock seats and prevent double-booking race conditions when multiple users attempt to reserve the same seat simultaneously.
* **Secure Payment Integration:** Integrated the Razorpay payment gateway with server-side cryptographic signature verification (HMAC SHA-256) to ensure ACID-compliant, secure ticket transactions.
* **Automated Data Pipeline:** Engineered a custom Django management command to mathematically generate and seed a rolling 90-day window of realistic flight routes and seat layouts.
* **Chronological Route Discovery:** Built an interactive React UI featuring intelligent data grouping, chronological date dropdowns, and an interactive, visually responsive 60-seat mapping interface.

## Tech Stack

**Frontend:**
* React.js (Vite)
* React Router (SPA Navigation)
* Tailwind CSS
* Axios

**Backend & Database:**
* Python
* Django & Django REST Framework (DRF)
* PostgreSQL
* Razorpay SDK


## Local Setup & Installation

# Prerequisites
* Node.js & npm installed
* Python 3.10+ installed
* PostgreSQL installed and running locally

# 1. Backend Setup (Django)
Navigate to the backend directory and set up your virtual environment:
```bash
cd backend
python -m venv venv
source venv\Scripts\activate
