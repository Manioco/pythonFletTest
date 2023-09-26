id_0 = 100000000000


def create_new_id(bigger_id):
    if bigger_id <= id_0:
        return id_0 + 1
    
    return bigger_id + 1
