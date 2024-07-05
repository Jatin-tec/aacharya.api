def parse_user(user):
    return {
        "email": user["email"],
        "verified_email": user["verified_email"],
        "sid": user["sid"],
        "name": user["name"],
        "given_name": user["given_name"],
        "family_name": user["family_name"],
        "picture": user["picture"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
        "last_login": user["last_login"],
    }
