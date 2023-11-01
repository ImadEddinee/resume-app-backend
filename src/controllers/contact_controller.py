from flask import Blueprint, jsonify

from database import db
from src.models.contact_model import Contact

contact_controller = Blueprint('contact_controller', __name__)


@contact_controller.route("users/<int:user_id>/contacts")
def get_user_contact(user_id):
    contact = Contact.query.filter_by(user_id=user_id).first()
    contact_info = {
        "id": contact.id,
        "address": contact.address,
        "github": contact.github,
        "linkedin": contact.linkedin,
        "email": contact.email
    }
    return contact_info


@contact_controller.route("contacts", methods=['POST'])
def create_or_update_contact_details(contact, user_id):
    contact_db = Contact.query.filter_by(user_id=user_id).first()
    if contact_db:
        contact_db.address = contact['address']
        contact_db.github = contact['github']
        contact_db.linkedin = contact['linkedin']
        contact_db.email = contact['email']
    else:
        contact_db = Contact(address=contact['address'],
                             linkedin=contact['linkedin'],
                             github=contact['github'],
                             email=contact['email'],
                             user_id=user_id)
        db.session.add(contact_db)
    db.session.commit()
