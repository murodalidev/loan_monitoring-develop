from datetime import datetime, timedelta
from app.models.brief_case.directories.bank_mfo import bank_mfo

from app.models.brief_case.directories.client_region import client_region
from app.models.brief_case.loan_portfolio_schedule import LoanPortfolioSchedule
from app.models.problems_case.problem_state_chain_model import ProblemStateChain
from app.models.problems_case.problem_states_model import ProblemStates
from ....models.brief_case.directories.local_code import local_code
from ....models.brief_case.loan_portfolio import Loan_Portfolio
from ....models.loan_case.loan_case_model import LoanCase
from ....models.brief_case.directories.dis_reg_post_codes import post_codes
from ....models.brief_case.directories.client_district import client_district

from ....common.commit import commit_object, flush_object


def get_problem_states(db_session):
    
    get_states = db_session.query(ProblemStates).all()
    
    states = []
    
    for state in get_states:
        
        states.append({"id":state.id,
                       "name":state.name,
                       "code": state.code})
    return states
    





def set_chain_state_for_letter(general_task_id, loan_id, db_session):
    set_chain = db_session.query(ProblemStateChain).filter(ProblemStateChain.loan_id== loan_id).first()
    
    
    if general_task_id==7:
        state_type=1
        if set_chain is None:
        
            new_chain = ProblemStateChain(loan_id=loan_id,
                                        letter_35_id = state_type,
                                        letter_35_date =datetime.now(),
                                        last_state_id = state_type,
                                        created_at = datetime.now())
            db_session.add(new_chain)
            flush_object(db_session)
    
        else:
            if set_chain.last_state_id !=state_type:
                set_chain.letter_35_id = state_type
                set_chain.letter_35_date = datetime.now()
                set_chain.last_state_id = state_type
                set_chain.updated_at = datetime.now()
            
            flush_object(db_session)
    else:
        state_type=2
        if set_chain is None:
        
            new_chain = ProblemStateChain(loan_id=loan_id,
                                        letter_45_id = state_type,
                                        letter_45_date =datetime.now(),
                                        last_state_id = state_type,
                                        created_at = datetime.now())
            db_session.add(new_chain)
            flush_object(db_session)
    
        else:
            if set_chain.last_state_id !=state_type:
                set_chain.letter_45_id = state_type
                set_chain.letter_45_date = datetime.now()
                set_chain.last_state_id = state_type
                set_chain.updated_at = datetime.now()
            
            flush_object(db_session)
            
            
            
            
            
            
            
            
            
def set_chain_state_for_ssp(loan_id, db_session):
    set_chain = db_session.query(ProblemStateChain).filter(ProblemStateChain.loan_id== loan_id).first()
    
    
    
    if set_chain is None:
    
        new_chain = ProblemStateChain(loan_id=loan_id,
                                    ssp_id = 3,
                                    ssp_date =datetime.now(),
                                    last_state_id = 3,
                                    created_at = datetime.now())
        db_session.add(new_chain)
        commit_object(db_session)

    else:
        if set_chain.last_state_id !=3:
            set_chain.ssp_id = 3
            set_chain.ssp_date = datetime.now()
            set_chain.last_state_id = 3
            set_chain.updated_at = datetime.now()
        
        commit_object(db_session)
 
 
 
 
def set_chain_state_for_judicial_proccess(loan_id, db_session):
    set_chain = db_session.query(ProblemStateChain).filter(ProblemStateChain.loan_id== loan_id).first()
    
    
    
    if set_chain is None:
    
        new_chain = ProblemStateChain(loan_id=loan_id,
                                    judicial_process_id = 4,
                                    judicial_process_date =datetime.now(),
                                    last_state_id = 4,
                                    created_at = datetime.now())
        db_session.add(new_chain)
        commit_object(db_session)

    else:
        if set_chain.last_state_id !=4:
            set_chain.judicial_process_id = 4
            set_chain.judicial_process_date = datetime.now()
            set_chain.last_state_id = 4
            set_chain.updated_at = datetime.now()
        
        commit_object(db_session)
 
 
 
 
 

def set_chain_state_for_bpi(loan_id, db_session):
    set_chain = db_session.query(ProblemStateChain).filter(ProblemStateChain.loan_id== loan_id).first()
    
    
    
    if set_chain is None:
    
        new_chain = ProblemStateChain(loan_id=loan_id,
                                    bpi_id = 5,
                                    bpi_date =datetime.now(),
                                    last_state_id = 5,
                                    created_at = datetime.now())
        db_session.add(new_chain)
        commit_object(db_session)

    else:
        if set_chain.last_state_id !=5:
            set_chain.bpi_id = 5
            set_chain.bpi_date = datetime.now()
            set_chain.last_state_id = 5
            set_chain.updated_at = datetime.now()
        
        commit_object(db_session)
        
        
        
        

def set_chain_state_for_problems_assets(loan_id, db_session):
    set_chain = db_session.query(ProblemStateChain).filter(ProblemStateChain.loan_id== loan_id).first()
    
    
    
    if set_chain is None:
    
        new_chain = ProblemStateChain(loan_id=loan_id,
                                    problem_state_id = 6,
                                    problem_state_date =datetime.now(),
                                    last_state_id = 6,
                                    created_at = datetime.now())
        db_session.add(new_chain)
        commit_object(db_session)

    else:
        if set_chain.last_state_id !=6:
            set_chain.problem_state_id = 6
            set_chain.problem_state_date = datetime.now()
            set_chain.last_state_id = 6
            set_chain.updated_at = datetime.now()
        
        commit_object(db_session)
        
        
        
        
        
        
        
        
def set_chain_state_for_out_of_balance(loan_id, db_session):
    set_chain = db_session.query(ProblemStateChain).filter(ProblemStateChain.loan_id== loan_id).first()
    
    
    
    if set_chain is None:
    
        new_chain = ProblemStateChain(loan_id=loan_id,
                                    out_of_balance_id = 7,
                                    out_of_balance_date =datetime.now(),
                                    last_state_id = 7,
                                    created_at = datetime.now())
        db_session.add(new_chain)
        commit_object(db_session)

    else:
        if set_chain.last_state_id !=7:
            set_chain.out_of_balance_id = 7
            set_chain.out_of_balance_date = datetime.now()
            set_chain.last_state_id = 7
            set_chain.updated_at = datetime.now()
        
        commit_object(db_session)
        
        
        
        
        
def set_chain_state_for_auction(loan_id, db_session):
    set_chain = db_session.query(ProblemStateChain).filter(ProblemStateChain.loan_id== loan_id).first()
    
    
    
    if set_chain is None:
    
        new_chain = ProblemStateChain(loan_id=loan_id,
                                    auction_id = 8,
                                    auction_date =datetime.now(),
                                    last_state_id = 8,
                                    created_at = datetime.now())
        db_session.add(new_chain)
        commit_object(db_session)

    else:
        if set_chain.last_state_id !=8:
            set_chain.auction_id = 8
            set_chain.auction_date = datetime.now()
            set_chain.last_state_id = 8
            set_chain.updated_at = datetime.now()
        
        commit_object(db_session)
        
        


def set_chain_state_for_bpi_ended(loan_id, db_session):
    set_chain = db_session.query(ProblemStateChain).filter(ProblemStateChain.loan_id== loan_id).first()
    
    
    
    if set_chain is None:
    
        new_chain = ProblemStateChain(loan_id=loan_id,
                                    bpi_ended_id = 9,
                                    bpi_ended_date =datetime.now(),
                                    last_state_id = 9,
                                    created_at = datetime.now())
        db_session.add(new_chain)
        commit_object(db_session)

    else:
        if set_chain.last_state_id !=9:
            set_chain.bpi_ended_id = 9
            set_chain.bpi_ended_date = datetime.now()
            set_chain.last_state_id = 9
            set_chain.updated_at = datetime.now()
        
        commit_object(db_session)