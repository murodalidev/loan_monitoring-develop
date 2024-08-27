
def flush_object(db_session):
    try:
        db_session.flush()
    except:
        db_session.rollback()
        raise


def commit_object(db_session):
    try:
        db_session.commit()
    except:
        db_session.rollback()
        raise