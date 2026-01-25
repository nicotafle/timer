

def user_schema(user) -> dict:
    """ Transform Pydantic schemta to BD schema """
    return {
        'id' : str(user['_id']),
        'name' : user['name'],
        'email' : user['email']
    }

def users_schema(users) -> list:

    return [user_schema(user) for user in users]