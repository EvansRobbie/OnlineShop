from flask import *
import pymysql

import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth


app = Flask(__name__)
app.secret_key = 'A1_445T_@!jhf5gH'
connection = pymysql.connect(host='localhost',user='root', password='', database='onlineShop_db')

@app.route('/')
def index():
# create your Query
    sql = 'Select * from product_tbl'

    #execute query
    # create a cursor used to execute sql
    cursor = connection.cursor()
    #now use the cursor to execute your sql
    cursor.execute(sql)

    # check how many rows are returned
    if cursor.rowcount == 0:
        # return no. of rows
        return render_template('index.htm', msg = 'Out of Stock')
    else:
        #get all rows
        rows = cursor.fetchall()
        return render_template('index.html', rows= rows)



# 2nd route
# this route will display a single shoe
# This route willneed a product_id
@app.route('/product/<product_id>')
def single(product_id):
    # create your query, provide a placeholder
    sql = 'SELECT * FROM product_tbl WHERE product_id = %s'
    # execute /run your
    # create a cursor used to execute sql
    cursor = connection.cursor()
    # now use the cursor to execute your sql
    # below you provide id to replace the %s
    cursor.execute(sql, (product_id))

    if cursor.rowcount == 0:
        # return all rows
        return render_template('product.html', msg = 'Product does not exist')
        # fetch one row
    else:
        row = cursor.fetchone()
        return render_template('product.html', row =row)

@app.route('/action1', methods = ['POST', 'GET'])
def action1():
    if request.method == 'POST':
        customer_fname = request.form['customer_fname']
        customer_lname = request.form['customer_lname']
        customer_surname = request.form['customer_surname']
        customer_email = request.form['customer_email']
        customer_phone = request.form['customer_phone']
        customer_password = request.form['customer_password']
        customer_password2 = request.form['customer_password2']
        customer_gender = request.form['customer_gender']
        customer_address = request.form['customer_address']


        # validations
        import re
        if customer_password != customer_password2:
            flash("password do not match")
            return render_template('index.html',password= 'password do not match')

        elif len(customer_password)< 8:
            flash("password must have 8 characters")
            return render_template('index.html',password= 'password must have 8 characters')

        elif not re.search("[a-z]", customer_password):
            flash("must have a small letter")
            return render_template('index.html',password='must have a small letter')

        elif not re.search("[A-Z]", customer_password):
            flash("must have a capital letter")
            return render_template('index.html',password='must have a capital letter')

        elif not re.search("[0-9]", customer_password):
            flash("must have a number")
            return render_template('index.html',password='must have a number')

        elif not re.search("[!@#$%^&*]", customer_password):
            flash("must have a symbol")
            return render_template('index.html',password='must have a symbol')
        else:
            sql = "INSERT INTO customers(customer_fname,customer_lname,customer_surname,customer_email,customer_phone,customer_password,customer_gender,customer_address) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor= connection.cursor()
            try:
                cursor.execute(sql, (customer_fname, customer_lname, customer_surname, customer_email, customer_phone, customer_password,
                customer_gender, customer_address))
                connection.commit()
                flash("saved successfully.Please Login")
                return render_template('index.html')

            except:
                flash("failed")
                return render_template('index.html', error='failed')

    else:
        flash("Request Failed")
        return render_template('index.html')

@app.route('/action', methods = ['POST','GET'])
def action():
    if request.method == 'POST':
        # receive the posted username and password variables
        customer_surname = request.form['customer_surname']
        password = request.form['password']

        # We now move to the db and confirm if above details exists
        sql = "SELECT * FROM customers where customer_surname = %s and customer_password = %s"
        # create a cursor an d execute above sql
        cursor = connection.cursor()
        # execute the sql,provide email and password to fit %s placeholders
        cursor.execute(sql, (customer_surname, password))

    # Check if match was found
        if cursor.rowcount == 0:
            flash("Wrong credentials")
            return render_template('index.html', error='Wrong credentials')
        elif cursor.rowcount == 1:
            # create a user to track who is logged in
            # Attach user email to the session
            session['user'] = customer_surname
            flash("Login Successfull")
            return redirect('/')
        else:
            flash("Error Occured,Try later")
            return render_template('index.html', error='Error Occured,Try later')

    else:
        return render_template('index.html')
@app.route('/logout')
def logout():
    session.pop('user')
    flash("Your session has ended.See you later")
    return redirect('/') #clear session
@app.route('/mpesa_payment', methods=['POST', 'GET'])
def mpesa_payment():
    if request.method == 'POST':
        phone = str(request.form['phone'])
        amount = str(request.form['amount'])
        # capture the session of paying client
        email = session['user']

        quantity = str(request.form['quantity'])
        product_id = str(request.form['product_id'])

        # multiply quantity * amount
        total_pay = float(quantity) * float(amount)

        # sql to insert
        # create a table named payment_info
        # pay_id INT PK AI
        # product_id INT 50
        # phone VARCHAR 50
        # email VARCHAR 50
        # quantity INT 50
        # total_pay
        # pay_date timestamp current time stamp
        sql = 'insert into payment_info(phone,email,quantity,total_pay,product_id) values(%s,%s,%s,%s,%s)'
        cursor = connection.cursor()
        cursor.execute(sql, (phone, email, quantity, total_pay, product_id))
        connection.commit()

        # GENERATING THE ACCESS TOKEN
        consumer_key = "6G3GmLHwEIjxn8dmlGaJjkq23ajSpTVM"
        consumer_secret = "uLWM2zZHJOtx9V3C"

        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

        data = r.json()
        access_token = "Bearer" + ' ' + data['access_token']

        #  GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        business_short_code = "174379"
        data = business_short_code + passkey + timestamp
        encoded = base64.b64encode(data.encode())
        password = encoded.decode('utf-8')

        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password": "{}".format(password),
            "Timestamp": "{}".format(timestamp),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": total_pay,  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://modcom.co.ke/job/confirmation.php",
            "AccountReference": email,
            "TransactionDesc": 'quantity:' + 'ID' + product_id
        }

        # POPULAING THE HTTP HEADER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  # C2B URL

        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        flash("Please Complete Payment in Your Phone.Thank you for shopping With Us")
        return render_template('index.html')
    else:
        return render_template('index.html')
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)