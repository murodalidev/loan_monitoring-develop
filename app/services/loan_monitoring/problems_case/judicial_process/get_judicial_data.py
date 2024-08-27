from app.models.problems_case.judicial_process.judicial_authority_type import JudicialAuthorityType
from .....models.problems_case.judicial_process.judicial_process_data_model import JudicialData
from .....models.problems_case.judicial_process.judicial_authority import JudicialAuthority        
from .....common.is_empty import is_empty, is_exists
from .....common.commit import commit_object
    
def get_judicial_details(problem_case_id, judicial_type_id, authority_id, db_session):
    judicial_datas = {}
    judicial_data = db_session.query(JudicialData)\
            .filter(JudicialData.problems_case_id == problem_case_id).filter(JudicialData.type_id == judicial_type_id).first()
    
    if judicial_data is not None:
        judicial_datas ={"id":judicial_data.id,
                            "type" : judicial_data.type_id and judicial_data.type or None,
                            "region": judicial_data.region_id and judicial_data.region or None,
                            "authority": judicial_data.authority_id and judicial_data.authority or None,
                            
                            "receipt_date": judicial_data.receipt_date and judicial_data.receipt_date or None,
                            "decision_date_on_admission": judicial_data.decision_date_on_admission and judicial_data.decision_date_on_admission or None,
                            "decision_date_to_set": judicial_data.decision_date_to_set and judicial_data.decision_date_to_set or None,
                            "decision_date_in_favor_of_bank": judicial_data.decision_date_in_favor_of_bank and judicial_data.decision_date_in_favor_of_bank or None,
                            "date_to_set": judicial_data.date_to_set and judicial_data.date_to_set or None,
                            
                            "register_num":judicial_data.register_num and judicial_data.register_num or None,
                            "decision_on_admission_num": judicial_data.decision_on_admission_num and judicial_data.decision_on_admission_num or None,
                            "decision_to_set_num": judicial_data.decision_to_set_num and judicial_data.decision_to_set_num or None,
                            "decision_in_favor_of_bank_num": judicial_data.decision_in_favor_of_bank_num and judicial_data.decision_in_favor_of_bank_num or None,
                            
                            "claim_amount": judicial_data.claim_amount and judicial_data.claim_amount or None,
                            
                            "judicial_status": judicial_data.judicial_status_id and judicial_data.status or None,
                            "created_at":judicial_data.created_at and judicial_data.created_at or None,
                            "updated_at":judicial_data.updated_at and judicial_data.updated_at or None,
                            "files": judicial_data.files}
    
    return {"judicial_data":judicial_datas}













def get_judicial_all_existing(problem_case_id, db_session):
    judicial_authorities = []
    
    judicial_authority = db_session.query(JudicialData).filter(JudicialData.problems_case_id == problem_case_id).all()
    
    for authority in judicial_authority:
        judicial_authorities.append({
                            "type_id": authority.type_id,
                            "authority_type_id": authority.authority_id and authority.authority.type.id})
        
    return {"judicial":judicial_authorities}









def get_judicial_authorities(region_id, authority_type_id, db_session):
    judicial_authorities = []
    
    judicial_authority = db_session.query(JudicialAuthority).filter(JudicialAuthority.region_id == region_id).filter(JudicialAuthority.type_id == authority_type_id).all()
    
    for authority in judicial_authority:
        judicial_authorities.append({"id":authority.id,
                                     
                            "name": authority.name,
                            "code": authority.code})
        
    return {"judicial_data":judicial_authorities}



def create_judicial_authority(request, db_session):
    get_authority = db_session.query(JudicialAuthority).filter(JudicialAuthority.name == request.judicial_authority_name)\
        .filter(JudicialAuthority.type_id == request.type_id).first()
    is_empty(get_authority, 400, 'Authority has already created!')
    
    new_authority = JudicialAuthority(name=request.judicial_authority_name,
                                    region_id=request.region_id,
                                    type_id = request.type_id,
                                    code = request.code)
    db_session.add(new_authority)
    commit_object(db_session)
            
            
    
    return {"result":"OK"}



def get_all_judicial_authorities(name, region_id, type_id, code, page, size, db_session):
    get_authorities = db_session.query(JudicialAuthority).order_by(JudicialAuthority.id.asc())
    
    if name is not None:
        get_authorities = get_authorities.filter(JudicialAuthority.name.like(f"%{name}%"))
        
    if region_id is not None:
        get_authorities = get_authorities.filter(JudicialAuthority.region_id == region_id)
        
        
    if type_id is not None:
        get_authorities = get_authorities.filter(JudicialAuthority.type_id == type_id)
        
    if code is not None:
        get_authorities = get_authorities.filter(JudicialAuthority.code == code)
        
    count = get_authorities.count()
    get_authorities = get_authorities.limit(size).offset((page-1)*size).all()
    
    authorities = []
    for authority in get_authorities:
        authorities.append({"id":authority.id,
                            "name":authority.name,
                            "region":authority.region_id and {"id":authority.region.id,
                                                    "name":authority.region.name} or None,
                            "type":authority.type_id and {"id": authority.type.id,
                                                          "name":authority.type.name,
                                                          "name_full":authority.type.name_full},
                            "code": authority.code})
        
        
    return {"items":authorities,
            "total":count,
            "page":page,
            "size":size}
    
    
    
    
    
    
    
    
def get_judicial_authority_type(db_session):
    get_type = db_session.query(JudicialAuthorityType).all()
    product_type = []
    for type in get_type:
        product_type.append({"id":type.id,
                             "name_full":type.name_full,
               "name":type.name})
    return product_type




def get_one_judicial_authority(judicial_authority_id, db_session):
    authority =  db_session.query(JudicialAuthority).filter(JudicialAuthority.id == judicial_authority_id).first()
        
        
    return {"id":authority.id,
                            "name":authority.name,
                            "region":authority.region_id and {"id":authority.region.id,
                                                    "name":authority.region.name} or None,
                            "type":authority.type_id and {"id": authority.id,
                                                          "name":authority.name,
                                                          "name_full":authority.type.name_full},
                            "code": authority.code}
    
    
    
    
    
    
    
    
def update_judicial_authority(id, request, db_session):
    get_judicial_authority = db_session.query(JudicialAuthority).filter(JudicialAuthority.id == id).first()
    
    if request.judicial_authority_name:
        get_judicial_authority.name=request.judicial_authority_name
    
    if request.region_id:
        get_judicial_authority.region_id = request.region_id
    
    if request.type_id:
        get_judicial_authority.type_id = request.type_id
        
    if request.code is not None:
        get_judicial_authority.code= request.code
    
    commit_object(db_session)
    
    return {"result":"OK"}



def delete_judicial_authority(id, db_session):
    get_judicial_authority = db_session.query(JudicialAuthority).filter(JudicialAuthority.id == id).first()
    is_exists(get_judicial_authority, 400, 'judicial authority not found')
    db_session.delete(get_judicial_authority)
    commit_object(db_session)
    return {"result":"OK"}