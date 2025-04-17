from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from app.database import get_db
from app.models.models import Customer, Cart, CartItem, Product
from app.services.email_service import EmailService
import os

load_dotenv()

logger = logging.getLogger(__name__)

def send_installment_reminders(db: Session, days_before: int):
    logger.info(f"Running installment reminder job for payments due in {days_before} days")

    target_date = datetime.now() + timedelta(days=days_before)
    target_date_start = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
    target_date_end = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)
    
    try:
        due_items = (db.query(
            CartItem, Cart, Customer, Product
        ).join(
            Cart, CartItem.cart_id == Cart.id
        ).join(
            Customer, Cart.customer_id == Customer.id
        )
        .join(
            Product, CartItem.product_id == Product.id
        )
        .filter(
            and_(
                CartItem.deleted == False,
                Cart.deleted == False,
                CartItem.due > 0,
                CartItem.next_installment_date >= target_date_start,
                CartItem.next_installment_date <= target_date_end
            )
        ).all())

        customer_due_items = {}
        for item, cart, customer, product in due_items:
            if customer.email not in customer_due_items:
                customer_due_items[customer.email] = {
                    'name': customer.name,
                    'items': []
                }
            customer_due_items[customer.email]['items'].append({
                'product_name': product.name,
                'installment_count': item.installment_count,
                'total_installment': item.total_installment,
                'due_amount': item.due,
                'due_date': item.next_installment_date.strftime('%Y-%m-%d')
            })

        email_service = EmailService()
        for email, data in customer_due_items.items():
            if len(data['items']) == 1:
                item = data['items'][0]
                email_service.send_email_for_installment_due(
                    receiver_email=email,
                    customer_name=data['name'],
                    amount=item['due_amount'],
                    due_date=item['due_date'],
                    product_name=item['product_name']
                )
            else:
                email_service.send_multi_product_reminder(
                    receiver_email=email,
                    customer_name=data['name'],
                    items=data['items']
                )
            
            logger.info(f"Sent reminder to {email} for {len(data['items'])} due items")
        
        logger.info(f"Completed sending reminders to {len(customer_due_items)} customers")
        
    except Exception as e:
        logger.error(f"Error in installment reminder job: {str(e)}")


def setup_scheduler():
    scheduler = BackgroundScheduler()
    reminder_days_str = os.getenv('EMAIL_REMINDER_DAYS', '3,1,0')
    reminder_days = [int(days.strip()) for days in reminder_days_str.split(',')]
    
    for days in reminder_days:
        scheduler.add_job(
            send_installment_reminders,
            CronTrigger(hour=9, minute=0),
            args=[next(get_db()), days],
            id=f'installment_reminder_{0}days',
            replace_existing=True
        )
        logger.info(f"Scheduled installment reminder job for {days} days before due date")
    return scheduler


def start_scheduler():
    scheduler = setup_scheduler()
    scheduler.start()
    logger.info("Installment reminder scheduler started")
    return scheduler