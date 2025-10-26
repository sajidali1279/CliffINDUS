def get_visible_users_for(user):
    from cliffindus_backend.users.models import User
    if user.role == "admin":
        return User.objects.all()
    elif user.role == "wholesaler":
        return User.objects.filter(role="retailer")
    elif user.role == "retailer":
        return User.objects.filter(role="consumer")
    elif user.role == "consumer":
        return User.objects.filter(id=user.id)
    return User.objects.none()
