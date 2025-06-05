import os, uuid, secrets
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user


from db import db
from models import TransactionLog, BillingInfo, User

payment = Blueprint('payment', __name__)

@payment.route('/billing', methods=['GET', 'POST'])
@login_required
def billing():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        currency = request.form.get('currency', 'USD')
        desc = request.form.get('desc', 'Nạp tiền thủ công')

        transaction = TransactionLog(
            user_id=current_user.id,
            amount=amount,
            currency=currency,
            description=desc
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Nạp tiền thành công!', 'success')
        return redirect(url_for('payment.billing'))

    transactions = TransactionLog.query.filter_by(user_id=current_user.id).order_by(TransactionLog.timestamp.desc()).all()
    return render_template('billing.html', transactions=transactions)
