# forum/templatetags/forms_extras.py
from django import template

register = template.Library()

@register.filter
def add_class(value, arg):
    """
    Ajoute une classe CSS à un champ de formulaire.
    Usage : {{ form.field|add_class:"ma-classe" }}
    """
    return value.as_widget(attrs={"class": arg})
