from flask import request, render_template,redirect, url_for, flash, session
from sqlalchemy import asc
import random

from app import app, db
from models.models import Product, Expense, Batch
from datetime import datetime

@app.route('/')
def product():
    return render_template('products.html')

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        quantity = request.form.get('quantity')
        unit = request.form.get('unit')
        price = request.form.get('price')

        added_date_str = datetime.today()

        product = Product(name=name, quantity=quantity, unit=unit, price=price, added_date=added_date_str)
        db.session.add(product)
        db.session.commit()

        batch = Batch(product_id=product.id, quantity=quantity, arrival_date=added_date_str)
        db.session.add(batch)
        db.session.commit()

        return redirect(url_for('add_product'))

    return render_template('products_add.html')


@app.route('/expenses/add', methods=['GET', 'POST'])
def add_expense():
    total_amount = 0

    if request.method == 'POST':
        name = request.form.get('name')
        quantity_to_spent = int(request.form.get('quantity'))
        unit = request.form.get('unit')
        expense_date_str = datetime.today()

        available_quantity = 0
        batches = Batch.query.join(Product).filter(Product.name == name).order_by(asc(Batch.arrival_date))

        for batch in batches:
            available_quantity += batch.quantity

        if available_quantity < quantity_to_spent:
            shortage_quantity = quantity_to_spent - available_quantity
            flash(f'Недостатня кількість товару на складі. Не вистачає {shortage_quantity} одиниць.', 'danger')
            return redirect(url_for('add_expense'))

        # Списання кількості товару за методом FIFO
        remaining_quantity = quantity_to_spent
        expense_form_data = session.get('expense_form_data', [])
        for batch in batches:
            if remaining_quantity > 0:
                if batch.quantity >= remaining_quantity:
                    expense_quantity = remaining_quantity
                else:
                    expense_quantity = batch.quantity

                batch.quantity -= expense_quantity
                remaining_quantity -= expense_quantity

                expense_form_data.append({
                    'invoice_title': name,
                    'invoice_quantity': expense_quantity,
                    'invoice_price': batch.product.price if batch.product else 0,
                })
                expense = Expense(name=name, quantity=expense_quantity, unit=unit, expense_date=expense_date_str)
                db.session.add(expense)

                if 'invoice_number' not in session:
                    session['invoice_number'] = random.randint(100000, 9999999)

        total_amount = sum(data['invoice_quantity'] * data['invoice_price'] for data in expense_form_data if
                           'invoice_quantity' in data and 'invoice_price' in data)

        session['expense_form_data'] = expense_form_data
        db.session.commit()

    elif request.method == 'POST' and 'clear_form' in request.form:
        session.pop('expense_form_data', None)
        session.pop('invoice_number', None)

    else:
        expense_form_data = session.get('expense_form_data', [])

    invoice_number = session.get('invoice_number', None)
    current_datetime = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    return render_template('expenses_add.html', expense_form_data=expense_form_data, total_amount=total_amount, invoice_number=invoice_number, current_datetime=current_datetime)


@app.route('/expenses/clear', methods=['POST'])
def clear_expense_form():
    session.pop('expense_form_data', None)
    return redirect(url_for('add_expense'))

@app.route('/materials')
def materials():
    products = Product.query.all()
    expenses = Expense.query.all()
    batches = Batch.query.all()
    return render_template('materials.html', products=products, expenses=expenses, batches=batches)

@app.route('/generate_report', methods=['GET', 'POST'])
def generate_report():
    if request.method == 'POST':
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        inventory_date_str = request.form.get('inventory_date')
        inventory_date = None
        if start_date_str is not None:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

        if end_date_str is not None:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        if inventory_date_str is not None:
            inventory_date = datetime.strptime(inventory_date_str, '%Y-%m-%d')
        sales = Expense.query.filter(Expense.expense_date.between(start_date, end_date)).all()

        if inventory_date is not None:
            remaining_batches = Batch.query.filter(Batch.arrival_date <= inventory_date).all()
        else:
            remaining_batches = []
        sold_quantity = sum(sale.quantity for sale in sales)
        remaining_quantity = sum(batch.quantity for batch in remaining_batches)
        return render_template('report.html', start_date=start_date, end_date=end_date,
                               inventory_date=inventory_date, sales=sales, sold_quantity=sold_quantity,
                               remaining_quantity=remaining_quantity, remaining_batches=remaining_batches, show_report=True)
    else:
        return render_template('report.html', show_report=False)
