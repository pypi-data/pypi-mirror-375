
from django.contrib.auth import get_user_model 
 
def set_full_name(strategy, details, user=None, *args, **kwargs): 
    print("************** Set Full Name")

    first = details.get("first_name") or "" 
    last = details.get("last_name") or "" 
    fullname = (details.get("fullname") or "").strip() 
 
    if not fullname: 
        if first or last: 
            fullname = f"{first} {last}".strip() 
        else:
            fullname = "Custome FUllanme"
    details["fullname"] = fullname
    details["full_name"] = fullname
 
