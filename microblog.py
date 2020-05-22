from app import application, db
from app.models import User, Movies

db.create_all()


@application.shell_context_processor
def make_shell_context():
    return {'db': db, 'Movies': Movies}
