import datetime
from ....models.loan_case.holidays_model import Holidays
from ....common.is_empty import is_empty, is_exists
from ....common.commit import commit_object
from ....config.logs_config import info_logger



def add_holiday(request, db_session):
    date = datetime.datetime.strptime(request.holiday, '%m-%d-%Y')
    day = date.day
    month = date.month
    holiday = str(month) +'-'+ str(day)
    
    get_date = db_session.query(Holidays).filter(Holidays.month_day == holiday).first()
   
    is_empty(get_date, 403, f'Date has already exists.')
    
    
    new_holiday = Holidays(month_day=holiday)
    db_session.add(new_holiday)
    commit_object(db_session)
    info_logger.info('Added holiday day %s', holiday)
    return {"result":"OK"}



def get_all_holidays(db_session):
    get_day_month = db_session.query(Holidays).all()
    holidays = []
    for day_month in get_day_month:
        date = make_date_from_day_and_month(day_month.month_day)
        holidays.append({"id":day_month.id,
               "day_month":date})
    return holidays







def get_holiday(holiday_id, db_session):
    day_month = db_session.query(Holidays).filter(Holidays.id == holiday_id).first()
    return make_date_from_day_and_month(day_month.month_day)



# def update_holiday(id, request, db_session):
#     get_holiday = db_session.query(Holidays).filter(Holidays.id == id).first()
#     is_exists(get_holiday, 400, 'holiday doesn`t not exists.')
    
#     if request.date:
#         get_holiday.date= request.date
#     commit_object(db_session)
#     return {"result":"OK"}



def delete_holiday(id, db_session):
    get_holiday = db_session.query(Holidays).filter(Holidays.id == id).first()
    is_exists(get_holiday, 400, 'Holiday not found')
    db_session.delete(get_holiday)
    commit_object(db_session)
    info_logger.info('Deleted holiday day %s', get_holiday.month_day)
    return {"result":"OK"}





def get_business_days(start_date, num_days, db_session):
    get_holiday = db_session.query(Holidays).all()
    holidays = [make_date_from_day_and_month(holiday.month_day) for holiday in get_holiday]
    
    # Определение рабочих дней без выходных и праздников
    current_date = start_date
    count = 0
    while count < num_days:
        if current_date.weekday() < 5 and current_date not in holidays:
            count += 1
        current_date += datetime.timedelta(days=1)

    return current_date - datetime.timedelta(days=1)


def make_date_from_day_and_month(day_month):
    year = datetime.datetime.now().year
    day_mon = str(day_month) + '-' + str(year)
    return datetime.datetime.strptime(day_mon, '%m-%d-%Y').date()





def define_is_the_date_holiday_or_weekend(date, db_session):
    get_holiday = db_session.query(Holidays).all()
    holidays = [make_date_from_day_and_month(holiday.month_day) for holiday in get_holiday]
    for _ in range(len(holidays)):
        if date.weekday() > 4 or date in holidays:
            return False
    return True