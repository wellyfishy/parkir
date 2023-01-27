from django import template 
from parkiran.models import *

register = template.Library()

@register.filter
def jumlah_parkiran_count(user):
    if user.is_authenticated:
        return Struk.objects.filter(status=1).count() 
    return 0