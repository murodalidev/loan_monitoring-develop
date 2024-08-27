

from sqlalchemy.sql import text

from app.common.commit import flush_object, commit_object
from app.models.brief_case.loan_portfolio import Loan_Portfolio
from app.models.kad_case.kad_case_model import KADCase
from app.models.loan_case.loan_case_model import LoanCase
from app.models.problems_case.problems_case_model import ProblemsCase
from app.models.users.attached_regions import attached_regions




def gateway_to_back(db_session):
    print('for local admins started')
    script = 'R.ID IN (3, 9)'
    give_back_own_locals(LoanCase, script, db_session)
    print('LoanCase finished')
    give_back_own_locals(KADCase, script, db_session)
    print('KAD finished')
    script = 'R.ID = 12'
    give_back_own_locals(ProblemsCase, script, db_session)
    print('Problems finished')
    print('for local admins finished')
    
    # print('for main admins started')
    # script = 'R.ID IN (4, 8)'
    # give_back_own_region(LoanCase, script, 3, db_session)
    # print('LoanCase finished')
    # give_back_own_region(KADCase, script, 2, db_session)
    # print('KAD finished')
    # script = 'R.ID = 11'
    # give_back_own_region(ProblemsCase, script, 4, db_session)
    # print('Problems finished')
    # print('for main admins finished')
    

def give_back_own_locals(case, script, db_session):
    get_local_admins = db_session.execute(text(f'''
                                                SELECT DISTINCT
                                                    U.ID AS USER_ID,
                                                    U.LOCAL_CODE
                                                FROM
                                                    USERS U
                                                    JOIN USER_ROLE UR ON UR.USER_ID = U.ID
                                                    JOIN ROLES R ON UR.ROLE_ID = R.ID
                                                WHERE
                                                    {script}
                                               ''')).fetchall()
    
    
    
    for locals in get_local_admins:
        
        get_loan_cases = db_session.query(case).join(Loan_Portfolio, Loan_Portfolio.id==case.loan_portfolio_id)\
            .filter(Loan_Portfolio.local_code_id == locals.local_code).filter(Loan_Portfolio.status==1).all()
        
        for loans in get_loan_cases:
            if loans.second_responsible_id != locals.user_id:
                loans.second_responsible_id = locals.user_id
                
            flush_object(db_session)
            
    
    commit_object(db_session)
    
    
    
 
 
def give_back_own_region(case, script, type_id, db_session):
    get_main_admins = db_session.execute(text(f'''
                                                SELECT
                                                    AR.USER_ID,
                                                    U.DEPARTMENT
                                                FROM
                                                    ATTACHED_REGIONS AR
                                                    JOIN USERS U ON U.ID = AR.USER_ID
                                                    JOIN USER_ROLE UR ON UR.USER_ID = U.ID
                                                    JOIN ROLES R ON UR.ROLE_ID = R.ID
                                                WHERE
                                                    {script}
                                                GROUP BY
                                                    AR.USER_ID,
                                                    U.DEPARTMENT
                                                    
                                               ''')).fetchall()
    
    
    
    for main in get_main_admins:
        
        get_attached_regions = db_session.query(attached_regions.region_id).filter(attached_regions.user_id==main.user_id)\
            .filter(attached_regions.attached_type_id == type_id).all()
        
        if get_attached_regions is not None:
            for attached in get_attached_regions:
                
        
                get_loan_cases = db_session.query(case).join(Loan_Portfolio, Loan_Portfolio.id==case.loan_portfolio_id)\
                    .filter(Loan_Portfolio.client_region == attached.region_id).filter(Loan_Portfolio.status==1).all()
                
                for loans in get_loan_cases:
                    if loans.main_responsible_id != main.user_id:
                        loans.main_responsible_id = main.user_id
                        
                    flush_object(db_session)
            
    
    commit_object(db_session)