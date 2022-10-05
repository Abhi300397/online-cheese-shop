
from flask import Flask, render_template, request, json, redirect,flash,url_for
from flaskext.mysql import MySQL
from flask import session
import config as cn
from werkzeug.security import generate_password_hash, check_password_hash
from flask_paginate import Pagination, get_page_parameter
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = cn.cred['MYSQL_DATABASE_USER']
app.config['MYSQL_DATABASE_PASSWORD'] = cn.cred['MYSQL_DATABASE_PASSWORD']
app.config['MYSQL_DATABASE_DB'] = cn.cred['MYSQL_DATABASE_DB']
app.config['MYSQL_DATABASE_HOST'] = cn.cred['MYSQL_DATABASE_HOST']
app.config['MYSQL_DATABASE_PORT'] = cn.cred['MYSQL_DATABASE_PORT']
mysql.init_app(app)

app.secret_key = cn.skey


@app.route("/")
def main():
    return redirect('/Home')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')

@app.route('/employeeSignin')
def empSignin():
    return render_template('employeeSignin.html')
@app.route("/employeeSignup")
def empSignup():
    return render_template('employeeSignup.html')



@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user',None)
    elif session.get('employee'):
        session.pop('employee',None)
    
    flash('Logged out successfully','success')
    return redirect('/')



@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        con = mysql.connect()
        cursor = con.cursor()
        

        cursor.execute("SELECT * FROM customer WHERE email = %s", (_email))

        data = cursor.fetchall()



        if len(data) > 0:
            if check_password_hash(str(data[0][3]),_password):
                session['user'] = data[0][0]
                flash('Logged in successfully. Welcome '+data[0][1]+'!', 'success')
                return redirect('/Home')
            else:
                flash('Wrong Email address or Password.','danger')
                return redirect('/showSignin')
        else:
            flash('User does not exist','danger')
            return redirect('/showSignin')

    except Exception as e:
        flash(str(e),'danger')
        return redirect('/showSignin')
    finally:
        cursor.close()
        con.close()
@app.route('/employeeValidatelogin',methods=["POST"])
def empValidation():
    try:
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        con = mysql.connect()
        cursor = con.cursor()
        

        cursor.execute("SELECT * FROM employee WHERE email = %s", (_email))

        data = cursor.fetchall()



        if len(data) > 0:
            if check_password_hash(str(data[0][3]),_password):
                session['employee'] = data[0][0]
                flash('Logged in successfully. Welcome '+data[0][1]+'!', 'success')
                return redirect('/Home')
            else:
                flash('Wrong Email address or Password.','danger')
                return redirect('/employeeSignin')


    except Exception as e:
        flash(str(e),'danger')
        return redirect('/employeeSignin')
    finally:
        cursor.close()
        con.close()


@app.route('/signUp',methods=['POST'])
def signUp():

    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
    
    _hashpwd = generate_password_hash(_password)
 
    # validate the received values
    if _name and _email and _password:

        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM customer WHERE name=%s or email=%s",(_name,_email))
        data1= cursor.fetchall()
        if len(data1)==0:


            cursor.execute("INSERT INTO customer(name, email, password) VALUES (%s, %s, %s)", (_name, _email, _hashpwd))
            

            data = cursor.fetchall()

            if len(data) == 0:
                con.commit()
                cursor.close()
                con.close()
                text = "User registered successfully."
                return text
            else:
                return json.dumps({'error':str(data[0])})
        else:
            text = 'User already exists!! Try a different name or email id.'
            return text

    else:
        return 'Enter the required fields!'

@app.route('/employeeSignUp',methods=['POST'])
def employeeSignUp():

    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
    _hashpwd = generate_password_hash(_password)
 
    # validate the received values
    if _name and _email and _password:

        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM employee WHERE name=%s or email=%s",(_name,_email))
        data1= cursor.fetchall()
        if len(data1)==0:


            cursor.execute("INSERT INTO employee(name, email, password) VALUES (%s, %s, %s)", (_name, _email, _hashpwd))
            

            data = cursor.fetchall()

            if len(data) == 0:
                con.commit()
                cursor.close()
                con.close()
                text = "Employee registered successfully."
                return text
            else:
                return json.dumps({'error':str(data[0])})
        else:
            text = 'Employee already exists!! Try a different name or email id.'
            return text

    else:
        return 'Enter the required fields!'



@app.route('/Home')

def userHome():
    perpage=9
    page = request.args.get(get_page_parameter(),type=int,default=1)
    offset = page*perpage-perpage
    con = mysql.connect()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM products WHERE isDeleted=0")
    total = cursor.fetchall()
    cursor.execute("SELECT * FROM products WHERE isDeleted=0 LIMIT %s OFFSET %s",(perpage,offset))
    data = cursor.fetchall()
    categ1=()
    pagination = Pagination(page=page, per_page=perpage, total=len(total), record_name='products')
    return render_template('userHome.html',data = data,pagination=pagination,categ=categ1)


@app.route('/searchItem',methods=['post'])
def search():
    item = request.form.get('product')
    if item:
        return redirect(url_for('searchItem',item = item))  
    else:
        return redirect(url_for('userHome')) 

@app.route('/Home/filterItem',methods=['get'])
def filterItems():
    item = request.args.get('item')
    if item:
        
        categ1=request.args.getlist('categoryMilk')
        
        if len(categ1)>0:
                categ1=tuple(categ1)
                perpage = 9
                page = request.args.get(get_page_parameter(),type=int,default=1)
                offset = page*perpage-perpage
                
                      
                _product  = item
                _product = _product+'%'

                con = mysql.connect()
                cursor = con.cursor()
                cursor.execute("SELECT * FROM products WHERE isDeleted=0 and name LIKE %s and categoryMilk in %s",(_product,categ1))
                total = cursor.fetchall()
                cursor.execute("SELECT * FROM products WHERE isDeleted=0 and name LIKE %s and categoryMilk in %s LIMIT %s OFFSET %s",(_product,categ1,perpage,offset) )

                data = cursor.fetchall()
                pagination = Pagination(page=page, per_page=perpage, total=len(total), record_name='products')
                return render_template('userHome.html',data = data,pagination=pagination,item=item,categ = categ1)
        elif len(categ1)==0:
            return redirect(url_for('searchItem',item=item))
        
    else:
        
        categ1=request.args.getlist('categoryMilk')
        if len(categ1)>0:
                categ1=tuple(categ1)
                perpage = 9
                page = request.args.get(get_page_parameter(),type=int,default=1)
                offset = page*perpage-perpage

                con = mysql.connect()
                cursor = con.cursor()
                cursor.execute("SELECT * FROM products WHERE isDeleted=0 and categoryMilk in %s",(categ1,))
                total = cursor.fetchall()
                cursor.execute("SELECT * FROM products WHERE isDeleted=0 and categoryMilk in %s LIMIT %s OFFSET %s",(categ1,perpage,offset) )

                data = cursor.fetchall()
                pagination = Pagination(page=page, per_page=perpage, total=len(total), record_name='products')
                return render_template('userHome.html',data = data,pagination=pagination,item=item,categ = categ1)
        elif len(categ1)==0:
            return redirect('/Home')



    

@app.route('/Home/<item>',methods=['get','post'])

def searchItem(item):

    
        perpage = 9
        page = request.args.get(get_page_parameter(),type=int,default=1)
        offset = page*perpage-perpage
        
              
        _product  = item
        _product = _product+'%'

        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM products WHERE name LIKE %s and isDeleted=0",(_product))
        total = cursor.fetchall()
        cursor.execute("SELECT * FROM products WHERE name LIKE %s and isDeleted=0 LIMIT %s OFFSET %s",(_product,perpage,offset) )

        data = cursor.fetchall()
        pagination = Pagination(page=page, per_page=perpage, total=len(total), record_name='products')
        return render_template('userHome.html',data = data,pagination=pagination,item=item,categ=())
        




@app.route('/showAddProd')
def prodPage():
    return render_template('addProducts.html')

@app.route('/addProd',methods=['POST'])
def addProd():

    try:
        if session['employee']:

            _name = request.form.get('inputName')
            file = request.files.get('inputImg')
            milk = request.form.get('milk')
            country = request.form.get('country')
            _type = request.form.get('type')
            price = request.form.get('price')
            qty100=request.form.get('qty100')
            qty200=request.form.get('qty200')
            qty300=request.form.get('qty300')
            qty500=request.form.get('qty500')
            if file:
                file.save(os.path.join('static/images',file.filename))
            con = mysql.connect()
            cursor = con.cursor()
            cursor.execute("INSERT INTO products(name, img,categoryMilk,origin,type,price,qty100,qty200,qty300,qty500) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (_name,file.filename,milk,country,_type,price,qty100,qty200,qty300,qty500))
            data = cursor.fetchall()
            if len(data)==0:
                con.commit()
                cursor.close()
                con.close()
                flash('Product added successfully','success')
                return render_template('addProducts.html')
    except:
        flash('Fill all the details','danger')
        return render_template('addProducts.html')



@app.route('/updateProd',methods=['POST','GET'])
def updateProd():
    if session['employee']:

        if request.method == 'POST' :
            _id = request.form.get('id')
            _name = request.form.get('inputName')
            file = request.files.get('inputImg')
            milk = request.form.get('milk')
            country = request.form.get('country')
            _type = request.form.get('type')
            price = request.form.get('price')
            qty100=request.form.get('qty100')
            qty200=request.form.get('qty200')
            qty300=request.form.get('qty300')
            qty500=request.form.get('qty500')
            if file:
                file.save(os.path.join('static/images',file.filename))
            con = mysql.connect()
            cursor = con.cursor()
            cursor.execute('''UPDATE products 
                SET name=%s,img=%s,categoryMilk=%s,origin=%s,type=%s,price=%s,qty100=%s,qty200=%s,qty300=%s,qty500=%s
                WHERE productId=%s''', (_name,file.filename,milk,country,_type,price,qty100,qty200,qty300,qty500,_id))
            data = cursor.fetchall()
            

            if len(data)==0:
                con.commit()
                cursor.close()
                con.close()
                flash('Product updated successfully','success')
                return redirect('/updateProd?id='+str(_id))
        else:
            _id = request.args.get('id')
            con = mysql.connect()
            cursor = con.cursor()
            cursor.execute("SELECT * FROM products WHERE isDeleted=0 and productId=%s",(_id,))
            data = cursor.fetchall()
            return render_template('updateProduct.html',data=data)

@app.route('/deleteProd',methods=["GET"])
def deleteProd():
    if session['employee']:

        _id=request.args.get('id')
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute('''UPDATE products 
                SET isDeleted=1
                WHERE productId=%s''',(_id,))
        data = cursor.fetchall()
        if len(data)==0:
            con.commit()
            cursor.close()
            con.close()
            flash('Deleted the product successfully','success')
            return redirect('/Home')




    


@app.route('/addtoCart',methods=["POST"])
def addtoCart():
    if session.get('user'):
        _user = session.get('user')
        _prodId = request.form.get('prodId')
        _size = request.form.get('size')
        _qty = request.form.get('qty')
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute("SELECT qty100,qty200,qty300,qty500,price from products WHERE productId=%s",_prodId)
        stock=cursor.fetchone()
        if _size==str(100) and int(_qty)<=stock[0]:
            cursor.execute("SELECT * FROM cart WHERE customerId=%s and productId=%s and size=%s",(_user,_prodId,_size))
            exist = cursor.fetchall()
            price = str(stock[4]*float(_qty)*1)
            if len(exist)>0:
                cursor.execute("UPDATE cart SET qty=qty+%s,price=price+%s WHERE customerId=%s and productId=%s and size=%s",(_qty,price,_user,_prodId,_size))
            else:
                
                cursor.execute("INSERT INTO cart(customerId,productId,size,qty,price) VALUES (%s, %s,%s,%s,%s)", (_user,_prodId,_size,_qty,price))

            data = cursor.fetchall()
            if len(data)==0:
                con.commit()
                cursor.close()
                con.close()
                flash('Item added to the cart successfully','success')
                return redirect('/Home')
        elif _size==str(200) and int(_qty)<=stock[1]:
            cursor.execute("SELECT * FROM cart WHERE customerId=%s and productId=%s and size=%s",(_user,_prodId,_size))
            exist = cursor.fetchall()
            price = str(stock[4]*float(_qty)*2)
            if len(exist)>0:
                cursor.execute("UPDATE cart SET qty=qty+%s,price=price+%s WHERE customerId=%s and productId=%s and size=%s",(_qty,price,_user,_prodId,_size))
            else:
                cursor.execute("INSERT INTO cart(customerId,productId,size,qty,price) VALUES (%s, %s,%s,%s,%s)", (_user,_prodId,_size,_qty,price))
            data = cursor.fetchall()
            if len(data)==0:
                con.commit()
                cursor.close()
                con.close()
                flash('Item added to the cart successfully','success')
                return redirect('/Home')
        elif _size==str(300) and int(_qty)<=stock[2]:
            cursor.execute("SELECT * FROM cart WHERE customerId=%s and productId=%s and size=%s",(_user,_prodId,_size))
            exist = cursor.fetchall()
            price = str(stock[4]*float(_qty)*3)
            if len(exist)>0:
                cursor.execute("UPDATE cart SET qty=qty+%s,price=price+%s WHERE customerId=%s and productId=%s and size=%s",(_qty,price,_user,_prodId,_size))
            else:
                cursor.execute("INSERT INTO cart(customerId,productId,size,qty,price) VALUES (%s, %s,%s,%s,%s)", (_user,_prodId,_size,_qty,price))
            data = cursor.fetchall()
            if len(data)==0:
                con.commit()
                cursor.close()
                con.close()
                flash('Item added to the cart successfully','success')
                return redirect('/Home')
        elif _size==str(500) and int(_qty)<=stock[3]:
            cursor.execute("SELECT * FROM cart WHERE customerId=%s and productId=%s and size=%s",(_user,_prodId,_size))
            exist = cursor.fetchall()
            price = str(stock[4]*float(_qty)*5)
            if len(exist)>0:
                cursor.execute("UPDATE cart SET qty=qty+%s,price=price+%s WHERE customerId=%s and productId=%s and size=%s",(_qty,price,_user,_prodId,_size))
            else:
                cursor.execute("INSERT INTO cart(customerId,productId,size,qty,price) VALUES (%s, %s,%s,%s,%s)", (_user,_prodId,_size,_qty,price))
            data = cursor.fetchall()
            if len(data)==0:
                con.commit()
                cursor.close()
                con.close()
                flash('Item added to the cart successfully','success')
                return redirect('/Home')
        else:
            flash('Could not add item to the cart due to low/no stock','danger')
            return redirect('/Home')
    else:
        flash('Login to add to the cart','danger')
        return redirect('/Home')


@app.route('/Home/viewCart',methods=["GET","POST"])
def viewCart():
    if session.get('user'):
        _user = session.get('user')
        if request.method=="POST":
            if request.form.get('remove'):
                con = mysql.connect()
                cursor = con.cursor()
                _id = request.form.get("id")
                cursor.execute("DELETE FROM cart WHERE id=%s",_id)
                con.commit()
                flash('Item removed from the cart successfully',"success")
                return redirect('/Home/viewCart')
            elif request.form.get('edit'):
                con = mysql.connect()
                cursor = con.cursor()
                _id = request.form.get("id")
                _size = request.form.get('size')
                _qty = request.form.get('qty')
                cursor.execute("SELECT products.price from cart JOIN products ON cart.productId=products.productId WHERE cart.id=%s",_id)
                price = cursor.fetchone()
                total = (float(price[0])*float(_size)*float(_qty))/100
                cursor.execute("UPDATE cart SET size=%s,qty=%s,price=%s WHERE id=%s",(_size,_qty,total,_id))
                con.commit()
                flash('Updated item successfully','success')
                return redirect('/Home/viewCart')



        
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute("""SELECT cart.* , products.name FROM cart 
            INNER JOIN products 
            ON cart.productId = products.productId 
            WHERE cart.customerId=%s""",_user)
        data = cursor.fetchall()
        return render_template('cart.html',data= data)
    else:
        flash('Login to view the cart','danger')
        return redirect('/Home')

@app.route('/Home/checkout', methods=['GET'])
def checkOut():
    if session.get('user'):
        _user = session.get('user')
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute("SELECT productId,size,qty FROM cart WHERE customerId=%s",_user)
        items = cursor.fetchall()
        
        no_stock =[]
        for i in items:
            cursor.execute("SELECT qty100,qty200,qty300,qty500,name from products WHERE productId=%s",i[0])
            stock = cursor.fetchone()
            if i[1]==100 and i[2]>stock[0]:
                    no_stock.append((stock[4],'100gm'))
                
            if i[1]==200 and i[2]>stock[1]:
                    no_stock.append((stock[4],'200gm'))
                
            if i[1]==300 and i[2]>stock[2]:
                    no_stock.append((stock[4],'300gm'))
                
            if i[1]==500 and i[2]>stock[3]:
                    no_stock.append((stock[4],'500gm'))
               

        if len(no_stock)==0:
            cursor.execute("SELECT SUM(price) FROM cart WHERE customerId=%s",_user)
            t = cursor.fetchone()

            total= t[0]
            cursor.execute('INSERT INTO orderdetails(customerId,total) VALUES(%s,%s)',(_user,total))
            cursor.execute('SELECT MAX(id) from orderdetails')
            orderid = cursor.fetchall()

            cursor.execute('''INSERT INTO orderitems(orderId,productId,size,qty,price) SELECT orderdetails.id,cart.productId,cart.size,cart.qty,cart.price FROM cart
                JOIN orderdetails ON cart.customerId = orderdetails.customerId WHERE orderdetails.id=%s''',orderid)
           
            for item in items:
                cursor.execute("SELECT qty100,qty200,qty300,qty500 from products WHERE productId=%s",item[0])
                current_stock = cursor.fetchone()

                if item[1]==100:
                    updated_stock = current_stock[0]-item[2]
                    cursor.execute("UPDATE products SET qty100=%s WHERE productId=%s",(updated_stock,item[0]))
                    con.commit()
                if item[1]==200:
                    updated_stock = current_stock[1]-item[2]
                    cursor.execute("UPDATE products SET qty200=%s WHERE productId=%s",(updated_stock,item[0]))
                    con.commit()
                if item[1]==300:
                    updated_stock = current_stock[2]-item[2]
                    cursor.execute("UPDATE products SET qty300=%s WHERE productId=%s",(updated_stock,item[0]))
                    con.commit()
                if item[1]==500:
                    updated_stock = current_stock[3]-item[2]
                    cursor.execute("UPDATE products SET qty500=%s WHERE productId=%s",(updated_stock,item[0]))
                    con.commit()

                     
            cursor.execute('DELETE FROM cart WHERE customerId =%s',_user)
            data = cursor.fetchall()
            if len(data)==0:
                con.commit()
                flash('Order placed successfully. Our team will mail you once the order is ready for pickup. It should take no more than 2 days to finish a order.','success')
                return redirect('/Home')
        else:
            flash('Could not place the order as the following items are of low/out of stock\n'+str(no_stock)+'\n Remove or modify these items to place order','danger')
            return redirect('/Home/viewCart')
        
    else:
        flash('Login to place the order','danger')
        return redirect('/Home')

@app.route('/Home/myOrders')
def myOrders():
    if session.get('user'):
        _user = session.get('user')
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute('SELECT id,datePlaced,total FROM orderdetails WHERE customerId=%s',_user)
        data = cursor.fetchall()
        return render_template('orders.html',data=data)
    else:
        flash('Login to view your orders','danger')
        return redirect('/Home')


@app.route('/Home/myOrders/orderItems',methods=['POST'])
def orderItems():
    if session.get('user'):
        orderId = request.form.get('OrderId')
        con = mysql.connect()
        cursor =con.cursor()
        cursor.execute('''SELECT products.name,size,qty,orderitems.price FROM orderitems 
            JOIN  products 
            ON orderitems.productId=products.productId 
            WHERE orderId=%s''',orderId)
        data = cursor.fetchall() 
        return render_template('orderitems.html',data = data)
    else:
        flash('Login to view the orderitems','danger')
        return redirect('/Home')




        

if __name__ == "__main__":
    app.run()   




