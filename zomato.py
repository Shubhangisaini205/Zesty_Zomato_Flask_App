import pickle
import random
import string
from flask import Flask,render_template,request,redirect,url_for

app = Flask(__name__)

# Load menu data from a file using pickle
def load_menu():
    try:
        with open('menu.pickle', 'rb') as file:
            try:
                menu = pickle.load(file)
            except EOFError:  # Handle empty file
                menu = []
    except FileNotFoundError:
        menu = []
    return menu

# Save menu data to a file using pickle
def save_menu(menu):
    with open('menu.pickle', 'wb') as file:
        pickle.dump(menu, file)


def load_orders():
    try:
        with open('orders.pickle', 'rb') as file:
            try:
                menu = pickle.load(file)
            except EOFError:  # Handle empty file
                menu = []
    except FileNotFoundError:
        menu = []
    return menu



def save_orders(orders):
    with open('orders.pickle', 'wb') as file:
        pickle.dump(orders, file)

def validate_order(dish_ids):
    menu = load_menu()
    orders = load_orders()

    for dish_id in dish_ids:
        dish = next((dish for dish in menu if dish['dish_id'] == dish_id), None)
        if dish is None or dish['stock'] == 0:
            print(f"Invalid or unavailable dish: {dish_id}")
            return False

    return True



def generate_order_id():
    menu = load_menu()
    orders = load_orders()
    # Find the maximum order ID in the existing orders
    order_ids = [order['order_id'] for order in orders]
    max_order_id = max(order_ids) if order_ids else 0

    # Generate a new order ID by incrementing the maximum order ID
    new_order_id = max_order_id + 1
    return new_order_id


def update_dish_stock(dish_ids):
    menu = load_menu()
    orders = load_orders()
    for dish_id in dish_ids:
        # Find the dish in the menu
        dish = next((dish for dish in menu if dish['dish_id'] == int(dish_id)), None)
        # print(dish,"xys")
        dish["stock"] = dish["stock"]-1
        # print(dish,"xys")
    save_menu(menu)
           


@app.route('/')
def display_menu():
    # Retrieve the menu data
    menu = load_menu()
    # Render the menu HTML template and pass the menu data to it
    return render_template('menu.html', menu=menu)





@app.route('/add-dish', methods=['GET', 'POST'])
def Add_Dish():
    menu = load_menu()
    if request.method == "POST":

        dish_id = int(request.form["dish_id"])
        dish_name = request.form["dish_name"]
        price = float(request.form["price"])
        stock = int(request.form["stock"])
        
        menu.append({
            'dish_id': dish_id,
            'dish_name': dish_name,
            'price': price,
            'stock': stock
        })

        # Save the updated menu data using pickle
        save_menu(menu) 

        # Redirect the staff to the "Display Menu" page
        return redirect(url_for('display_menu'))

    else:
        # Render the form template for the GET request
        return render_template('add_dish.html')
    

    
@app.route('/take-order', methods=['POST', 'GET'])
def take_order():
    menu = load_menu()
    orders = load_orders()

    if request.method == 'POST':
        customer_name = request.form['customer_name']
        dish_ids = request.form.getlist('dish_ids')
        # print(dish_ids) 
        if not customer_name or not dish_ids:
            return 'Error: Incomplete order information'

        # Validate the order
        for dish_id in dish_ids:
            dish = next((dish for dish in menu if dish['dish_id'] == int(dish_id)), None)
            if dish is None or dish['stock'] == 0:
                return f"Error: Invalid or unavailable dish in the order: {dish_id}"

        # Generate a new order ID
        order_id = generate_order_id()

        # Update the orders list
        new_order = {
            'order_id': order_id,
            'customer_name': customer_name,
            'dish_ids': dish_ids,
            'status': 'received'
        }
        # print(orders,"take order")
        orders.append(new_order)

        # Save the orders
        save_orders(orders)

        # Update the dish stock
        update_dish_stock(dish_ids)

        # Redirect to the review orders page
        return redirect('/review-orders')

    else:
        # Render the form template for the GET request
        return render_template('take_order.html', menu=menu)

@app.route('/review-orders')
def review_orders():
    # Retrieve the orders data
    orders = load_orders()
    menu = load_menu()

    # Update each order with dish names and prices
   
    for order in orders:
        name=[]
        price=0
        dish_ids = order['dish_ids']
        for id in dish_ids:
            for item in menu:
                 if int(id) ==item["dish_id"]:  
                     name.append(item["dish_name"])
                     price+=item["price"]
                     break
        # print(name,price)
        order['total_price'] = price
        order['name'] = name
    # Render the review orders HTML template and pass the orders data to it
    return render_template('review_orders.html', orders=orders,menu=menu)


@app.route('/delete-dish/<int:dish_id>', methods=['POST'])
def delete_dish(dish_id):
    menu = load_menu()

    # Find the dish to delete
    dish = next((dish for dish in menu if dish['dish_id'] == dish_id), None)
    if dish is None:
        return 'Error: Dish not found'

    # Remove the dish from the menu
    menu.remove(dish)

    # Save the updated menu
    save_menu(menu)

    # Redirect to the display menu page
    return redirect('/')
 

@app.route('/order/update_status', methods=['POST'])
def update_status():
    order_id = int(request.form['order_id'])
    status = request.form['status']
    if update_order_status(order_id, status):
        return redirect('/review-orders')
    return 'Invalid order ID'

def update_order_status(order_id, status):
    orders = load_orders()
    for order in orders:
        if order['order_id'] == order_id:
            order['status'] = status

            # Save updated orders data using pickle
            save_orders(orders)

            return True
    return False

@app.route('/update-stock/<int:dish_id>', methods=['POST'])
def update_stock(dish_id):
    # Retrieve the menu data
    menu = load_menu()

    # Find the dish with the given dish_id
    for dish in menu:
        if dish['dish_id'] == dish_id:
            # Update the stock value
            dish['stock'] = int(request.form['stock'])
            break

    # Save the updated menu data using pickle
    save_menu(menu)

    # Redirect the staff to the "Display Menu" page
    return redirect(url_for('display_menu'))







if __name__ == '__main__':
    app.run(debug=True,port=11000)

