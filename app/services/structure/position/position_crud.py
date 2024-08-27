from app.models.structure.positions import Positions
from ....common.is_empty import is_empty, is_exists
from ....common.commit import commit_object


def create_position(request, db_session):
    get_position = db_session.query(Positions).filter(Positions.name == request.position_name).first()
    is_empty(get_position, 400, 'position has already created!')
    new_position = Positions(name=request.position_name)
    db_session.add(new_position)
    commit_object(db_session)
    return {"result":"OK"}



def get_all_positions(db_session):
    get_positions = db_session.query(Positions).all()
    positions = []
    for pos in get_positions:
        positions.append({"id":pos.id,
               "position_name":pos.name})
    return positions



def get_position(position, db_session):
    return db_session.query(Positions).filter(Positions.id == position).first()



def update_position(id, request, db_session):
    get_dep = db_session.query(Positions).filter(Positions.name == request.position_name).filter(Positions.id == id).first()
    is_empty(get_dep, 400, 'position_name has already created!')
    get_dep = db_session.query(Positions).filter(Positions.id == id).first()
    get_dep.name=request.position_name
    commit_object(db_session)
    return {"result":"OK"}



def delete_position(id, db_session):
    get_dep = db_session.query(Positions).filter(Positions.id == id).first()
    is_exists(get_dep, 400, 'position not found')
    db_session.delete(get_dep)
    commit_object(db_session)
    return {"result":"OK"}
