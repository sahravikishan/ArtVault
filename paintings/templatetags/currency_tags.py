from django import template

register = template.Library()

@register.filter
def inr(value):
    """
    Formats a number to Indian Rupee format (e.g., 1,00,000.00).
    Adds the ₹ symbol.
    """
    if value is None:
        return ''
        
    try:
        # Convert to float to handle decimals
        f_value = float(value)
        # Format to 2 decimal places
        str_val = f"{f_value:.2f}"
        
        # Split into integer and decimal parts
        if '.' in str_val:
            int_part, dec_part = str_val.split('.')
        else:
            int_part, dec_part = str_val, '00'
            
        # Add commas according to Indian numbering system
        # Last 3 digits, then every 2 digits
        res = ""
        length = len(int_part)
        
        if length > 3:
            res = "," + int_part[-3:]
            int_part = int_part[:-3]
            while len(int_part) > 2:
                res = "," + int_part[-2:] + res
                int_part = int_part[:-2]
            res = int_part + res
        else:
            res = int_part
            
        # Return without decimal if it's .00 to keep UI clean, or keep it if requested
        if dec_part == '00':
            return f"₹{res}"
        return f"₹{res}.{dec_part}"
        
    except (ValueError, TypeError):
        return value
