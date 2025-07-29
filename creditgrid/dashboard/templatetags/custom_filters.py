from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try: 
        return float(value) * float(arg/100)
    except (ValueError, TypeError):
        return 0
    
@register.filter
def sum(value,arg):
    try: 
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return 0