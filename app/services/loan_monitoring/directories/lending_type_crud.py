from ....models.brief_case.directories.lending_type import lending_type









def get_lending_type(db_session):
    lending = db_session.query(lending_type).all()
    lending_types =[]
    for dir in lending:
        lending_types.append({"id": dir.id,
                       "code":dir.code,
                       "name":dir.name})
        
    return lending_types
        