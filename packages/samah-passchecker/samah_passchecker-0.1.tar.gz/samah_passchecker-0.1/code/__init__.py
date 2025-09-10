def check_strength(password):
    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False
    special_chars = "!@#$%^&*()-_+="

    if len(password) < 8:
        return "weak ❌: at least 8 letters"

    for char in password:
        if char.isupper():
            has_upper = True
        elif char.islower():
            has_lower = True
        elif char.isdigit():
            has_digit = True
        elif char in special_chars:
            has_special = True

    errors = []
    if not has_upper:
        errors.append("at least one upper case letter")
    if not has_lower:
        errors.append("at least one lower case letter")
    if not has_digit:
        errors.append("at least one number")
    if not has_special:
        errors.append("at least one char")

    if errors:
        return "weak ❌: " + ", ".join(errors)
    else:
        return "strong ✅"

# تجربة الكود
password = input("enter password")
print(check_strength(password))