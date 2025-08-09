# main.py
# A simple Flask web application to collect user contact information
# and send it as an email.

# docker build -t us-east1-docker.pkg.dev/surfn-peru/serviceform/service-form:v1 .
# docker push us-east1-docker.pkg.dev/surfn-peru/serviceform/service-form:v1
import os
import smtplib
import ssl
from email.message import EmailMessage
from flask import Flask, request, render_template_string

# Initialize Flask app
app = Flask(__name__)

# --- Configuration from Environment Variables ---
# It is a security best practice to store sensitive information
# in environment variables, not in the code.
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 465))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

# HTML for the web form. We're keeping it simple and self-contained.
HTML_FORM = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Contact Form</title>
  <style>
    body {
      font-family: sans-serif;
      background-color: #f4f7f6;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
    }
    .container {
      background-color: #ffffff;
      padding: 2rem;
      border-radius: 8px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      width: 100%;
      max-width: 500px;
    }
    h1 {
      text-align: center;
      color: #333;
    }
    label {
      display: block;
      margin-bottom: 0.5rem;
      color: #555;
      font-weight: bold;
    }
    input[type="text"], input[type="email"], textarea {
      width: 95%;
      padding: 10px;
      margin-bottom: 1rem;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 16px;
    }
    textarea {
      resize: vertical;
      height: 100px;
    }
    button {
      width: 100%;
      padding: 12px;
      border: none;
      background-color: #007bff;
      color: white;
      font-size: 18px;
      font-weight: bold;
      border-radius: 4px;
      cursor: pointer;
      transition: background-color 0.2s;
    }
    button:hover {
      background-color: #0056b3;
    }
  </style>
</head>
<body>
<div class="container">
  <h1>Contact Us</h1>
  <form action="/submit" method="post">
    <label for="name">Name</label>
    <input type="text" id="name" name="name" required>

    <label for="phone">Phone</label>
    <input type="text" id="phone" name="phone">

    <label for="email">Email</label>
    <input type="email" id="email" name="email" required>

    <label for="comments">Comments</label>
    <textarea id="comments" name="comments" rows="4"></textarea>

    <button type="submit">Submit</button>
  </form>
</div>
</body>
</html>
"""

# HTML for a simple success message
SUCCESS_PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Success</title>
  <style>
    body {
      font-family: sans-serif;
      background-color: #e9f5e9;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
      text-align: center;
    }
    .success-container {
      background-color: #ffffff;
      padding: 2rem;
      border-radius: 8px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    h1 {
      color: #28a745;
    }
    p {
      color: #333;
    }
    a {
      display: inline-block;
      margin-top: 1rem;
      padding: 10px 20px;
      background-color: #007bff;
      color: white;
      text-decoration: none;
      border-radius: 4px;
    }
    a:hover {
      background-color: #0056b3;
    }
  </style>
</head>
<body>
<div class="success-container">
  <h1>Success!</h1>
  <p>Your information has been submitted and an email has been sent.</p>
  <a href="/">Submit another response</a>
</div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    """Renders the contact form."""
    return render_template_string(HTML_FORM)


@app.route('/submit', methods=['POST'])
def submit():
    """Handles form submission and sends data via email."""
    try:
        # Get data from the form
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        comments = request.form.get('comments')

        if not all([SMTP_USERNAME, SMTP_PASSWORD, EMAIL_RECEIVER]):
            raise ValueError("Email credentials not set in environment variables.")

        # Create the email message
        msg = EmailMessage()
        msg['Subject'] = 'New Contact Form Submission'
        msg['From'] = SMTP_USERNAME
        msg['To'] = EMAIL_RECEIVER
        
        body = (f"Name: {name}\n"
                f"Phone: {phone}\n"
                f"Email: {email}\n"
                f"Comments: {comments}")
        msg.set_content(body)

        # Send the email using SSL
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        # Return a success message
        return render_template_string(SUCCESS_PAGE)

    except Exception as e:
        # Log the error and return a friendly error message
        app.logger.error(f"An error occurred: {e}")
        return "An error occurred while sending the email. Please check your credentials.", 500


# The Cloud Run environment will set the PORT environment variable.
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)