import datetime
from sqlalchemy import or_, and_, func, case
import sqlalchemy
from sqlalchemy.sql.expression import cast, extract
from sqlalchemy.sql import text
from app.models.loan_case.loan_case_model import LoanCase
from app.models.monitoring_case.hybrid_letter_model import HybridLetters
from app.models.problems_case.problem_state_chain_model import ProblemStateChain
from app.models.problems_case.problem_states_model import ProblemStates
from ...models.kad_case.kad_case_model import KADCase
from ...models.brief_case.loan_portfolio import Loan_Portfolio
from ...models.users.users import Users as users_model
from ...models.brief_case.directories.loan_product import loan_product
from ...models.brief_case.directories.currency import currency
from ...common.commit import flush_object, commit_object
from ...models.brief_case.directories.local_code import local_code
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import cast
from ...common.dictionaries.monitoring_case_dictionary import loan_case
from ...common.dictionaries.general_tasks_dictionary import KGT
from ...models.brief_case.loan_portfolio_schedule import LoanPortfolioSchedule
from ..loan_monitoring.monitoring_case.script_date_holidays import define_is_the_date_holiday_or_weekend


def create_kad_case_with_append_task(task, data,from_type, db_session):#used
    new_loan_case = KADCase(loan_portfolio_id = data.loan_portfolio_id,
                                 main_responsible_id = data.main_responsible_id,
                                 deadline_extension_status_id = 1,
                                 from_type_id = from_type,
                                 second_responsible_id = data.second_responsible_id,
                                 kad_case_status_id = loan_case['Новый'],
                                 task_manager_id = task.id,
                                 created_at = datetime.datetime.now(),
                                 updated_at = datetime.datetime.now()
                                 )
    db_session.add(new_loan_case)
    flush_object(db_session)
    return new_loan_case





def get_all_kad_case(size, page, region_id, local_code_id, loan_id, client_name, product_type, state_chain, second_responsible, client_type, \
    currency_id, client_code, current_state, user_id, department, db_session):
    main_user = aliased(users_model)
    second_user = aliased(users_model)
    loan_portfolio2 = aliased(Loan_Portfolio)
    loan_portfolio3 = aliased(Loan_Portfolio)
    loan_portfolio4 = aliased(Loan_Portfolio)
    period = datetime.date.today()
    overdue_max_date_case = case(
                        [
                            (and_(Loan_Portfolio.overdue_start_date != None, Loan_Portfolio.date_overdue_percent != None,
                                  Loan_Portfolio.overdue_start_date <= Loan_Portfolio.date_overdue_percent), Loan_Portfolio.overdue_start_date),
                            (and_(Loan_Portfolio.overdue_start_date != None, Loan_Portfolio.date_overdue_percent != None,
                                  Loan_Portfolio.overdue_start_date > Loan_Portfolio.date_overdue_percent), Loan_Portfolio.date_overdue_percent),
                           (and_(Loan_Portfolio.overdue_start_date != None, Loan_Portfolio.date_overdue_percent == None), Loan_Portfolio.overdue_start_date),
                           (and_(Loan_Portfolio.overdue_start_date == None, Loan_Portfolio.date_overdue_percent != None), Loan_Portfolio.date_overdue_percent)
                        ], else_=None).label("overdue_max_date")
    all_duty = case([
        (and_(Loan_Portfolio.overdue_balance != None, Loan_Portfolio.balance_16377 != None), 
         cast(Loan_Portfolio.overdue_balance, sqlalchemy.FLOAT) + cast(Loan_Portfolio.balance_16377, sqlalchemy.FLOAT)),
        (and_(Loan_Portfolio.overdue_balance != None, Loan_Portfolio.balance_16377 == None), 
         cast(Loan_Portfolio.overdue_balance, sqlalchemy.FLOAT)),
        (and_(Loan_Portfolio.overdue_balance == None, Loan_Portfolio.balance_16377 != None), 
         cast(Loan_Portfolio.balance_16377, sqlalchemy.FLOAT)),
        ], else_=None).label('all_duty')
    
    schedule_sum = case([(func.sum(cast(LoanPortfolioSchedule.summ_red, sqlalchemy.FLOAT))==None, 0)], else_=func.sum(cast(LoanPortfolioSchedule.summ_red, sqlalchemy.FLOAT))).label('schedule_sum')
    
    sub_query_schedule_sum = db_session.query(schedule_sum).join(loan_portfolio2, loan_portfolio2.loan_id==LoanPortfolioSchedule.loan_id, isouter=True)\
        .filter(loan_portfolio2.loan_id==Loan_Portfolio.loan_id)\
        .filter(loan_portfolio2.status==1)\
        .filter(LoanPortfolioSchedule.date_red>=datetime.datetime.now()).scalar_subquery()
    
        
    main_user_case = case([(KADCase.main_responsible_id == user_id, second_user.full_name)], else_=None).label("full_name")
    kad_case = db_session.query(
                            KADCase.id,
                            main_user_case,
                            overdue_max_date_case,
                            LoanCase.monitoring_case_id.label("monitoring_case_id"),
                            ProblemStates.name.label('state_chain_name'),
                            Loan_Portfolio.id.label('loan_portfolio_id'),
                            Loan_Portfolio.loan_id,
                            Loan_Portfolio.client_name,
                            Loan_Portfolio.borrower_type,
                            Loan_Portfolio.total_overdue,
                            all_duty,
                            Loan_Portfolio.overdue_balance,
                            Loan_Portfolio.overdue_start_date,
                            Loan_Portfolio.balance_16377,
                            Loan_Portfolio.date_overdue_percent,
                            sub_query_schedule_sum.label('total_overdue_by_graph'),
                            local_code.code.label('local_code'),
                            currency.code.label('currency_code'),
                            KADCase.created_at
                            )\
        .join(Loan_Portfolio, KADCase.loan_portfolio_id == Loan_Portfolio.id, isouter=False)\
        .join(LoanCase, LoanCase.loan_portfolio_id == KADCase.loan_portfolio_id)\
        .join(main_user, KADCase.main_responsible_id == main_user.id, isouter=True)\
        .join(second_user, KADCase.second_responsible_id == second_user.id, isouter=True)\
        .join(local_code, Loan_Portfolio.local_code_id == local_code.id, isouter=True)\
        .join(currency, Loan_Portfolio.currency_id == currency.id, isouter=True)\
        .join(ProblemStateChain, ProblemStateChain.loan_id == Loan_Portfolio.loan_id, isouter = True)\
        .join(ProblemStates, ProblemStates.id == ProblemStateChain.last_state_id, isouter = True)\
        .join(HybridLetters, HybridLetters.kad_case_id == KADCase.id, isouter = True)\
            .filter(or_(KADCase.main_responsible_id == user_id, KADCase.second_responsible_id == user_id))\
            .filter((or_(Loan_Portfolio.overdue_balance!=None, Loan_Portfolio.balance_16377!=None)))\
            .filter(Loan_Portfolio.status==1)\
            .filter(Loan_Portfolio.is_taken_kad == True)\
            .filter(and_(all_duty!=None,all_duty!=0))\
            
    
    if current_state is not None:
        kad_case = kad_case.filter(ProblemStateChain.last_state_id == current_state)
    
    
    
    if currency_id is not None:
        kad_case = kad_case.filter(Loan_Portfolio.currency_id == currency_id)
    
    if region_id is not None:
        kad_case = kad_case.filter(Loan_Portfolio.client_region == region_id)
    
    if local_code_id is not None:
        kad_case = kad_case.filter(Loan_Portfolio.local_code_id == local_code_id)
    
    if loan_id is not None or client_name is not None:
        kad_case = kad_case.filter(or_(cast(Loan_Portfolio.loan_id, sqlalchemy.Text).like(f'{loan_id}%'), Loan_Portfolio.client_name.ilike(f'%{client_name}%')))
    
    if second_responsible is not None:
        kad_case = kad_case.filter(KADCase.second_responsible_id == second_responsible)
    
    
    if product_type is not None:
        kad_case = kad_case.join(loan_product, loan_product.name == Loan_Portfolio.loan_product)\
        .filter(loan_product.type == product_type) 
    
    if state_chain is not None:
        kad_case = kad_case.filter(ProblemStates.id == state_chain)
    
    
    if client_type is not None:    
        if client_type != '11' and client_type != '08':
            kad_case = kad_case.filter(Loan_Portfolio.borrower_type.regexp_match('^(?!08|11).*'))
        else:
            kad_case = kad_case.filter(Loan_Portfolio.borrower_type.regexp_match(f'^({client_type}).*'))
    
    
    count = kad_case.count()
    kad_case = kad_case.limit(size).offset((page-1)*size).all()
    
    kad_case_list = []
    for kad in kad_case:
        recommended_amount = 0
        repayment_date = 0
        get_schedules = db_session.execute(text(f'''
                                               select * from loan_portfolio_schedule where loan_id = {kad.loan_id} order by date_red
                                               ''')).fetchall()
        if get_schedules[0].date_red > datetime.datetime.now():
                repayment_date = None
                recommended_amount = None
        elif get_schedules[-1].date_red < datetime.datetime.now():
                repayment_date = None
                recommended_amount = None
        else:
            for schedule in get_schedules:
                if period.year == schedule.date_red.year and period.month == schedule.date_red.month:
                    repayment_date = schedule.date_red
                    recommended_amount = schedule.summ_red
        
        if kad.overdue_max_date is not None:
            overdue_days = (datetime.datetime.now().date() - kad.overdue_max_date).days
        recommended_amount = recommended_amount and float(recommended_amount)/100 or None
        loan_client = kad.loan_id
        if kad.client_name is not None:
            loan_client = str(kad.loan_id) +' : '+ kad.client_name
        total_overdue = 0
        total_overdue_by_graph = 0
        if kad.total_overdue is not None and  kad.total_overdue !='0':
            total_overdue= kad.total_overdue
        if kad.total_overdue_by_graph is not None and kad.total_overdue_by_graph!=0:
            total_overdue_by_graph = kad.total_overdue_by_graph/100
        if float(total_overdue) < total_overdue_by_graph:
            recommended_amount = 0
        if (kad.all_duty == 0 or kad.all_duty is None) and recommended_amount == 0:
            continue
        kad_case_list.append({"id":kad.id,
                              'state_chain_name':kad.state_chain_name,
                              "monitoring_case_id":kad.monitoring_case_id,
                               "loan_portfolio": {"id":kad.loan_portfolio_id,
                                                  "local_code": kad.local_code,
                                                  "total_overdue": kad.total_overdue,
                                                  "loan_client":loan_client,
                                                  "loan_id":kad.loan_id,
                                                  "client_name":kad.client_name,
                                                  "all_duty": kad.all_duty,
                                                  "overdue_balance": kad.overdue_balance,
                                                  "overdue_max_date": kad.overdue_max_date,
                                                  "overdue_days":overdue_days,
                                                  "overdue_start_date": kad.overdue_start_date,
                                                  "balance_16377": kad.balance_16377,
                                                  "date_overdue_percent": kad.date_overdue_percent,
                                                  "total_overdue_by_graph": kad.total_overdue_by_graph,
                                                  },
                               "loan_portfolio_schedule": {
                                   "repayment_date":repayment_date,
                                   "recommended_amount":recommended_amount,
                                   "currency_code":kad.currency_code
                               },
                               "responsible": {"full_name":kad.full_name},
                               "kad_letter_35":KGT.SEND_1_LETTER.value,
                               "kad_letter_45":KGT.SEND_2_LETTER.value,
                               "created_at":kad.created_at})
    return {"items": kad_case_list,
            "total":count,
            "page":page,
            "size":size}  





def get_loan_portfolio_schedule(period, loan_id, db_session):
    return db_session.query(LoanPortfolioSchedule).filter(LoanPortfolioSchedule.loan_id == loan_id)\
        .filter(extract('month', LoanPortfolioSchedule.date_red) == period.month)\
            .filter(extract('year', LoanPortfolioSchedule.date_red) == period.year).first()



def get_kad_data_for_main_page(user_id, db_session):
    
    data = db_session.query(func.count(Loan_Portfolio.id).label('loan_count'), \
                            func.sum(cast(Loan_Portfolio.total_overdue, sqlalchemy.FLOAT)).label('total_overdue'),\
                            func.sum(cast(Loan_Portfolio.overdue_balance, sqlalchemy.FLOAT)).label('overdue_balance'),\
                            func.sum(cast(Loan_Portfolio.balance_16377, sqlalchemy.FLOAT)).label('balance_16377'),\
                            (func.sum(cast(Loan_Portfolio.overdue_balance, sqlalchemy.FLOAT)) + func.sum(cast(Loan_Portfolio.balance_16377, sqlalchemy.FLOAT))).label('all_duty'))\
        .filter(Loan_Portfolio.status == 1).first()
    # TODO: Отправленные письма/Не отправленные письма
    
    sent_letter_count = db_session.query(func.count(cast(HybridLetters.id, sqlalchemy.FLOAT)).label('sent_letter_count'))\
        .filter(or_(HybridLetters.letter_status_id == 2, HybridLetters.letter_status_id == 5)).filter(HybridLetters.kad_case_id == KADCase.id)\
            .filter(or_(KADCase.main_responsible_id == user_id, KADCase.second_responsible_id == user_id)).first()
    unsent_letter_count = db_session.query(func.count(cast(HybridLetters.id, sqlalchemy.FLOAT)).label('unsent_letter_count'))\
        .filter(or_(HybridLetters.letter_status_id == 3, HybridLetters.letter_status_id == 4)).filter(HybridLetters.kad_case_id == KADCase.id)\
            .filter(or_(KADCase.main_responsible_id == user_id, KADCase.second_responsible_id == user_id)).first()
    
    return {"loan_count":data.loan_count,
            "total_overdue":data.total_overdue,
            "overdue_balance":data.overdue_balance,
            "balance_16377":data.balance_16377,
            "all_duty":data.all_duty,
            "sent_letter_count":sent_letter_count.sent_letter_count,
            "unsent_letter_count":unsent_letter_count.unsent_letter_count}
