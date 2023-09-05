from flask import Flask, render_template, request, current_app,redirect,url_for
from flask_mail import Mail, Message
import requests
from bs4 import BeautifulSoup
import os
import threading  

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'kashyapkr4147@gmail.com'
app.config['MAIL_PASSWORD'] = 'skyteihxtbswrlze'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

#Dictionary to save url info
tracking_info = {}

#Function to scrape price and title
def scrape_price(url, desired_price, recipient_email):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    try:
        while True:  
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            product_title = soup.find(id='productTitle').get_text().strip()
            product_prices = soup.find('span', class_='a-price-whole').get_text()
            product_price = float(product_prices.replace(",", "").replace(".", ""))
            print(product_title)
            print(product_price)

            if product_price <= desired_price:
                send_email("Price Drop Alert!!", recipient_email, product_title, product_price)
                # tracking_info[url] = "Price met" 
                print(f"Price met for {product_title}")
                break 

    except Exception as e:
        print(f"Error occurred while scraping: {e}")
      
#Functio to send mail
def send_email(subject, recipient, product_name, product_price):
    try:
        message_body = f"Product: {product_name}\n Current Price: Rs{product_price}\n\nThe product price has dropped below your desired price.\nPurchase Now!!"
        with app.app_context():
            msg = Message(subject, sender='kashyapkr4147@gmail.com', recipients=[recipient])
            msg.body = message_body
            mail.send(msg)
        return True 
    except Exception as e:
        print(f"Error sending email: {e}")
        return False 

@app.route('/', methods=['GET', 'POST'])
def home_page():
    if request.method == 'POST':
        url = request.form['url']
        desired_price = float(request.form['desired_price'])
        recipient_email = request.form['email']

        if url not in tracking_info:
            tracking_thread = threading.Thread(target=scrape_price, args=(url, desired_price, recipient_email))
            tracking_thread.daemon = True
            tracking_thread.start()
       
        #     tracking_info[url] = "Tracking in progress..."
        #     flash(tracking_info[url])
        # else:
        #     if tracking_info[url] == "Price met":
        #          flash("Price met")
        #     else:
        #         flash("Product is already being tracked")
        return redirect(url_for('track_page'))

    return render_template('home.html')


@app.route('/track')
def track_page():
    return render_template('track.html')

if __name__ == '__main__':
    app.run(debug=True)