import __main__
import impmagic

@impmagic.loader(
    {'module': '__main__'},
    {'module': 'model', 'submodule': ['models']}
)
def get_note(user_id, workspace=None):
    with __main__.Session() as session:
        query = session.query(models.Note).filter_by(creator_id=user_id)

        if workspace:
            query = query.filter_by(workspace=workspace)

        return query.all()