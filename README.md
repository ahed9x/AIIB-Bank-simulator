![Apache License 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
# AIIB Bank Web Application

AIIB Bank is a simple web application built with Flask that allows users to create accounts, log in, manage their balances, and transfer funds to other users. It also features secure data handling with encryption and QR code authentication.

## Features

- User account creation
- Secure login with password and QR code
- Balance management
- Fund transfer between users
- Transaction history
- Password reset
- Account deletion

## Technologies Used

- Python
- Flask
- Flask-SSLify
- Cryptography (Fernet)
- QRCode
- HTML/CSS

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/aiib-bank.git
   cd aiib-bank
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

## Usage

1. Open a web browser and navigate to `https://localhost:5000`.

2. **Home Page:**
   - Register or log in with a username and password.
   - Optionally, log in using a QR code.

3. **Dashboard:**
   - View your account balance.
   - Transfer funds to other users by entering the amount and recipient ID.
   - Access account settings.

4. **Settings:**
   - View your transaction history.
   - Reset your password.
   - Delete your account.
   - View your QR code.

## Security

- User data is encrypted using the `cryptography` library.
- QR code login is implemented for convenience and security.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a pull request.

## Credits

All credentials go to Ahmed Omar Zein.

## License

This project is licensed under the MIT License.

---

## Contact

If you have any questions or suggestions, please feel free to contact me.

email: ahmed.omar.zeinelabdin@gmail.com

linkden: www.linkedin.com/in/ahmed-omar-9x

---

- The application uses self-signed SSL for development purposes (`ssl_context='adhoc'`). For production, you should use a proper SSL certificate.
