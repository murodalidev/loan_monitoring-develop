from sqlalchemy.sql import text
from fastapi import HTTPException
from app.models.brief_case.directories.client_region import client_region
from app.models.brief_case.directories.local_code import local_code
from app.models.users.attached_branches import attached_branches



def get_all_regions(db_session):
    regions = db_session.query(client_region).all()
    data = []
    
    for region in regions:
        data.append({"id":region.id,
                     "code":region.code and region.code or None,
                     "region_name":region.name})
    return data



def get_attached_regions(user, main_responsible, attached_type, db_session):
    attached_regions = []
    get_attached = None
    # if user.roles[0].level == 30:
    #     get_attached = get_region_for_superviser(user.local_code, db_session)
    if user.roles[0].level == 20:
        get_attached = get_region_for_main_user(user.id, attached_type, db_session)
    elif user.roles[0].level <= 40 and user.roles[0].level > 30:
        get_attached = get_region_for_main_superviser(main_responsible, attached_type, db_session)
    
    if get_attached is not None:
        for attached in get_attached:       
            attached_regions.append({"id":attached.id,
                                    "name":attached.region_name})

    return attached_regions



def get_region_for_main_user(user_id, attached_type, db_session):
    
    
    return db_session.execute(text(f'''
                                                  SELECT
                                                    distinct cr.name as region_name,
                                                    cr.id
                                                FROM
                                                    CLIENT_REGION CR
                                                    JOIN LOCAL_CODE LC ON LC.REGION_ID = CR.ID
                                                    JOIN ATTACHED_BRANCHES AB ON AB.LOCAL_CODE_ID = LC.ID
                                                WHERE
                                                    AB.USER_ID = {user_id} AND
                                                     AB.ATTACHED_TYPE_ID = {attached_type}
                                                  
                                                  ''')).fetchall() 
    


def get_region_for_superviser(user_local, db_session):
    
    
    return db_session.execute(text(f'''
                                                  SELECT
                                                    distinct cr.name as region_name,
                                                    cr.id
                                                FROM
                                                    CLIENT_REGION CR
                                                    JOIN LOCAL_CODE LC ON LC.REGION_ID = CR.ID
                                                    
                                                WHERE
                                                    LC.ID = {user_local}
                                                  
                                                  ''')).fetchall() 




def get_region_for_main_superviser(main_responsible, attached_type, db_session):
    
    main_responsible_script = ''
    if main_responsible is not None:
        main_responsible_script = f'AND AB.USER_ID = {main_responsible}'
    
    return db_session.execute(text(f''' SELECT DISTINCT
                                                    CR.ID,
                                                    CR.NAME AS REGION_NAME
                                                FROM
                                                    CLIENT_REGION CR
                                                    JOIN LOCAL_CODE LC ON LC.REGION_ID = CR.ID
                                                    JOIN ATTACHED_BRANCHES AB ON AB.LOCAL_CODE_ID = LC.ID
                                                WHERE
                                                     AB.ATTACHED_TYPE_ID = {attached_type}
                                                    {main_responsible_script}
                                                  ''')).fetchall() 



def get_region(region_id, db_session):
    return db_session.query(client_region).filter(client_region.id == region_id).first()
    
    
    
