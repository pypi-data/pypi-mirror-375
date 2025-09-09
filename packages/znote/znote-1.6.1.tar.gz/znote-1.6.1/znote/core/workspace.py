import impmagic


@impmagic.loader(
    {'module': '__main__'},
    {'module': 'os'},
    {'module': 'model', 'submodule': ['models']}
)
def list_workspace(user):
    #create_workspace(user)

    with __main__.Session() as session:
        user_db = session.query(models.User).filter_by(username=user).first()
        if user_db:
            return user_db.workspace.split(",")
    return []


@impmagic.loader(
    {'module': '__main__'},
    {'module': 'os'},
    {'module': 'model', 'submodule': ['models']}
)
def create_workspace(user, namespace):
    try:
        with __main__.Session() as session:
            user_db = session.query(models.User).filter_by(username=user).first()
            if user_db:
                user_workspace = user_db.workspace.split(",")

                if namespace not in user_workspace:
                    user_workspace.append(namespace)
                    user_db.workspace = ",".join(user_workspace)

                    session.commit()

                    return True

        return False
    except:
        return False


@impmagic.loader(
    {'module': '__main__'},
    {'module': 'os'},
    {'module': 'shutil'},
    {'module': 'model', 'submodule': ['models']}
)
def remove_workspace(user, namespace):
    try:
        with __main__.Session() as session:
            user_db = session.query(models.User).filter_by(username=user).first()
            if user_db:
                user_workspace = user_db.workspace.split(",")

                if namespace in user_workspace:
                    user_workspace.remove(namespace)
                    user_db.workspace = ",".join(user_workspace)

                    session.commit()

                    return True

        return False
    except:
        return Falselse