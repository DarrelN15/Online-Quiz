from django import template

register = template.Library()

@register.filter
def num_to_letter(num):
    # Converts number to ASCII letter, starting from 'A'
    return chr(64 + num) if 1 <= num <= 26 else num
