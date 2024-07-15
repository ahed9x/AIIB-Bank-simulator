# All Credential go to Ahmed Omar Zein 
from flask import Flask, request, render_template_string, redirect, url_for, session, jsonify
from flask_sslify import SSLify
from cryptography.fernet import Fernet
import os
import uuid
import json
import qrcode
import base64

app = Flask(__name__)
app.secret_key = 'supersecretkey'
sslify = SSLify(app)

# Generate a key for encryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Save the key to a file
try:
    with open('secret.key', 'rb') as key_file:
        key2 = key_file.read()
        cipher_suite = Fernet(key2)
except:
    with open('secret.key', 'wb') as key_file:
        key_file.write(key)

# Load the key from the file
def load_key():
    return open('secret.key', 'rb').read()

# Create user_data directory if it doesn't exist
if not os.path.exists('user_data'):
    os.makedirs('user_data')

# Inline CSS for styling
css = """
<style>
    body {
        font-family: Arial, sans-serif;
        background-color: #f4f4f9;
        margin: 0;
        padding: 20px;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        background: linear-gradient(to right, #6a11cb, #2575fc);
    }
    .container {
        background-color: #fff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        width: 100%;
        max-width: 400px;
        text-align: center;
    }
    h1, h2, h3 {
        color: #333;
    }
    label {
        display: block;
        margin-top: 10px;
        font-weight: bold;
    }
    input[type="text"], input[type="password"], input[type="number"], select {
        width: calc(100% - 22px);
        padding: 10px;
        margin-top: 5px;
        margin-bottom: 15px;
        border: 1px solid #ccc;
        border-radius: 4px;
    }
    input[type="submit"] {
        background-color: #6a11cb;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 16px;
    }
    input[type="submit"]:hover {
        background-color: #5a0dbd;
    }
    a {
        display: inline-block;
        margin-top: 10px;
        color: #6a11cb;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
</style>
"""

# Utility function to read encrypted user data
def read_user_data(username):
    try:
        with open(f'user_data/{username}.json', 'rb') as file:
            encrypted_data = file.read()
            decrypted_data = cipher_suite.decrypt(encrypted_data).decode()
            return json.loads(decrypted_data)
    except FileNotFoundError:
        return None

# Utility function to write encrypted user data
def write_user_data(username, data):
    json_data = json.dumps(data).encode()
    encrypted_data = cipher_suite.encrypt(json_data)
    with open(f'user_data/{username}.json', 'wb') as file:
        file.write(encrypted_data)

# Utility function to generate QR code
def generate_qr_code(username, password):
    enc_password = cipher_suite.encrypt(password.encode())
    qr_data = f"{username},{enc_password.decode()}"
    img = qrcode.make(qr_data)
    img.save(f'user_data/{username}.png')


@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    
    return css + """
    <div class="container">
        <h1>Welcome to AIIB Bank</h1>
        <form action="/action" method="post">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required><br><br>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required><br><br>
            <input type="submit" value="Submit">
        </form>
        <form action="/login_qr" method="post">
            <input type="submit" value="Login with QR">
        </form>
    </div>
    """

@app.route('/action', methods=['POST'])
def action():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not password:
        return css + """
        <div class="container">
            <h3>Password is required.</h3><a href='/'>Try again</a>
        </div>
        """
    
    user_data = read_user_data(username)

    if user_data and user_data['password'] == password:
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        if user_data:
            return css + f"""
            <div class="container">
                <h3>User {username} already exists or wrong password.</h3><a href='/'>Try again</a>
            </div>
            """
        else:
            account_id = str(uuid.uuid4())
            new_user = {
                'account_id': account_id,
                'password': password,
                'balance': 0,
                'transactions': []
            }
            write_user_data(username, new_user)
            generate_qr_code(username, password)
            session['username'] = username
            return css + f"""
            <div class="container">
                <h2>Account created for {username}</h2>
                <p>Your account ID is: {account_id}</p>
                <h3>Your QR</h3>
                <img src='user_data/{username}.png'>
                <a href='/'>Go to Home</a>
            </div>
            """

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    username = session['username']
    user_data = read_user_data(username)

    if user_data:
        return render_template_string(css + """
        <div class="container">
            <h2>Welcome {{ username }}</h2>
            <p>Your balance is: {{ balance }}</p>
            <form action="/transaction" method="post">
                <label for="amount">Transfer Amount:</label>
                <input type="number" id="amount" name="amount" required><br><br>
                <label for="recipient_id">Recipient ID (for transfer only):</label>
                <select id="recipient_id" name="recipient_id"></select><br><br>
                <input type="submit" value="Submit">
            </form>
            <a href="/settings">Settings</a>
            <form action="/signout" method="post">
                <input type="submit" value="Sign Out">
            </form>
        </div>

        <script>
            function populateRecipientDropdown() {
                fetch('/users')
                .then(response => response.json())
                .then(data => {
                    const recipientDropdown = document.getElementById('recipient_id');
                    recipientDropdown.innerHTML = '<option value="">Select a recipient</option>';
                    data.users.forEach(user => {
                        const option = document.createElement('option');
                        option.value = user.id;
                        option.textContent = `Username: ${user.username}, ID: ${user.id}`;
                        recipientDropdown.appendChild(option);
                    });
                });
            }

            document.addEventListener('DOMContentLoaded', populateRecipientDropdown);
        </script>
        """, username=username, balance=user_data['balance'])
    else:
        return css + """
        <div class="container">
            <h3>Account does not exist.</h3><a href='/'>Go back</a>
        </div>
        """

@app.route('/users')
def users():
    users = []
    for file in os.listdir("user_data"):
        if file.endswith(".json"):
            username = file.rsplit('.', 1)[0]
            user_data = read_user_data(username)
            users.append({'username': username, 'id': user_data['account_id']})
    return jsonify({'users': users})

@app.route('/transaction', methods=['POST'])
def transaction():
    username = session['username']
    amount = int(request.form.get('amount'))
    recipient_id = request.form.get('recipient_id')

    if amount <= 0:
        return css + """
        <div class="container">
            <h3>Transfer amount must be positive.</h3><a href='/dashboard'>Go back</a>
        </div>
        """

    user_data = read_user_data(username)

    if user_data and user_data['balance'] >= amount and recipient_id:
        recipient_data = None
        for file in os.listdir("user_data"):
            if file.endswith(".json"):
                potential_recipient_data = read_user_data(file.rsplit('.', 1)[0])
                if potential_recipient_data['account_id'] == recipient_id:
                    recipient_data = potential_recipient_data
                    recipient_username = file.rsplit('.', 1)[0]
                    break

        if recipient_data:
            user_data['balance'] -= amount
            recipient_data['balance'] += amount

            user_data['transactions'].append({
                'type': 'transfer',
                'amount': amount,
                'recipient_id': recipient_id
            })
            recipient_data['transactions'].append({
                'type': 'received',
                'amount': amount,
                'sender_id': user_data['account_id']
            })

            write_user_data(username, user_data)
            write_user_data(recipient_username, recipient_data)

            return redirect(url_for('dashboard'))
        else:
            return css + """
            <div class="container">
                <h3>Recipient not found.</h3><a href='/dashboard'>Go back</a>
            </div>
            """
    else:
        return css + """
        <div class="container">
            <h3>Insufficient balance or invalid transaction.</h3><a href='/dashboard'>Go back</a>
        </div>
        """

@app.route('/settings')
def settings():
    if 'username' not in session:
        return redirect(url_for('home'))

    username = session['username']
    user_data = read_user_data(username)

    if user_data:
        return render_template_string(css + """
        <div class="container">
            <h2>Settings</h2>
            <h3>Transaction History</h3>
            <ul>
                {% for transaction in transactions %}
                <li>{{ transaction }}</li>
                {% endfor %}
            </ul>
            <form action="/reset_password" method="post">
                <label for="new_password">New Password:</label>
                <input type="password" id="new_password" name="new_password" required><br><br>
                <input type="submit" value="Reset Password">
            </form>
            <form action="/delete_account" method="post">
                <input type="submit" value="Delete Account">
            </form>
            <form action="/show_qr" method="get">
                <input type="submit" value="Show QR Code">
            </form>
            <a href="/dashboard">Back to Dashboard</a>
        </div>
        """, transactions=user_data['transactions'])
    else:
        return css + """
        <div class="container">
            <h3>Account does not exist.</h3><a href='/'>Go back</a>
        </div>
        """

@app.route('/reset_password', methods=['POST'])
def reset_password():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    username = session['username']
    new_password = request.form.get('new_password')
    user_data = read_user_data(username)

    if user_data:
        user_data['password'] = new_password
        write_user_data(username, user_data)
        return redirect(url_for('dashboard'))
    else:
        return css + """
        <div class="container">
            <h3>Account does not exist.</h3><a href='/'>Go back</a>
        </div>
        """

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    username = session['username']

    if os.path.exists(f'user_data/{username}.json'):
        os.remove(f'user_data/{username}.json')
        os.remove(f'user_data/{username}.png')
        session.pop('username', None)
        return css + """
        <div class="container">
            <h3>Account deleted successfully.</h3><a href='/'>Go to Home</a>
        </div>
        """
    else:
        return css + """
        <div class="container">
            <h3>Account does not exist.</h3><a href='/'>Go back</a>
        </div>
        """

@app.route('/login_qr', methods=['POST'])
def login_qr():
    return css + """
    <div class="container">
        <h2>Login with QR Code</h2>
        <div id="qr-reader" style="width:300px;"></div>
        <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
        <script>
            function openQRScanner() {
                let html5QrCode = new Html5Qrcode("qr-reader");
                html5QrCode.start(
                    { facingMode: "environment" },
                    {
                        fps: 10,
                        qrbox: { width: 250, height: 250 }
                    },
                    (decodedText, decodedResult) => {
                        fetch(`/qr_login_action?username=${decodedText}`)
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                window.location.href = "/dashboard";
                            } else {
                                alert("Login failed");
                            }
                        });
                    },
                    (errorMessage) => {
                        console.warn(`QR Code no match: ${errorMessage}`);
                    }
                ).catch((err) => {
                    console.error(`Unable to start scanning, error: ${err}`);
                });
            }

            document.addEventListener('DOMContentLoaded', openQRScanner);
        </script>
    </div>
    """

@app.route('/qr_login_action')
def qr_login_action():
    qr_data = request.args.get('username')
    username, encrypted_password = qr_data.split(",")
    
    # Ensure the encoded encrypted password is properly formatted
    encrypted_password = encrypted_password.encode()
    
    try:
        decrypted_password = cipher_suite.decrypt(encrypted_password).decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return jsonify({'success': False})
    
    user_data = read_user_data(username)
    
    if user_data and user_data['password'] == decrypted_password:
        session['username'] = username
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})


@app.route('/show_qr')
def show_qr():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    username = session['username']
    return css + f"""
    <div class="container">
        <h2>Your QR Code</h2>
        <img src='user_data/{username}.png'>
        <a href='/settings'>Back to Settings</a>
    </div>
    """

@app.route('/signout', methods=['POST'])
def signout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(ssl_context='adhoc', debug=True, host='0.0.0.0', port=5000)
