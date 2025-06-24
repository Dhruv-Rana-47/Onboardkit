from accounts.models import User

def get_subordinates(user):
    def recurse(u):
        children = User.objects.filter(mentor=u)
        result = list(children)
        for child in children:
            result += recurse(child)
        return result
    return recurse(user)