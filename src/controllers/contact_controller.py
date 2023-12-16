from flask import Blueprint, jsonify

from database import db
from src.models.contact_model import Contact

contact_controller = Blueprint('contact_controller', __name__)


@contact_controller.route("users/<int:user_id>/contacts")
def get_user_contact(user_id):
    contact = Contact.query.filter_by(user_id=user_id).first()
    if not contact:
        return {}
    else:
        contact_info = {
            "id": contact.id,
            "address": contact.address,
            "github": contact.github,
            "linkedin": contact.linkedin,
            "email": contact.email,
            "phoneNumber": contact.phone_number,
        }
    return contact_info


@contact_controller.route("contacts", methods=['POST'])
def create_or_update_contact_details(contact, user_id):
    contact_db = Contact.query.filter_by(user_id=user_id).first()
    if contact_db:
        contact_db.address = contact.get('address', contact_db.address)
        contact_db.github = contact.get('github', contact_db.github)
        contact_db.linkedin = contact.get('linkedin', contact_db.linkedin)
        contact_db.email = contact.get('email', contact_db.email)
        contact_db.phone_number = contact.get('phoneNumber', contact_db.phone_number)
    else:
        contact_db = Contact(address=contact.get('address'),
                             linkedin=contact.get('linkedin'),
                             github=contact.get('github'),
                             email=contact.get('email'),
                             phone_number=contact.get('phoneNumber'),
                             user_id=user_id)
        db.session.add(contact_db)
    db.session.commit()
