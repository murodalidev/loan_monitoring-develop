import time
from ....models.brief_case.loan_portfolio import Loan_Portfolio
from ....services.loan_monitoring.integrations.iabs_integrations import get_loan_repayment_schedule, get_customer


def get_all_schedule(offset: int, size: int, db_session):
    start_timer = time.time()
    count = 0
    size = 10000
    offset = 0

    while True:
        first_time = time.time()
        portfolio_list = db_session.query(Loan_Portfolio).order_by(Loan_Portfolio.id.asc()).limit(size).offset(offset).all()
        print('portfolio takes: ', time.time() - first_time, " sec")

        if len(portfolio_list) == 0:
            break
        
        another_time = time.time()

        for portfolio in portfolio_list:
            get_loan_repayment_schedule(db_session, portfolio.loan_id)
            count += 1
            if count % 100 == 0:
                print(count, " it's taken: ", time.time() - another_time, " sec")
                another_time = time.time()

        print('el count: ', count)
        offset += size

        # break
        #with break we save only (size) loan_id, without break we write all the portfolio


    end_timer = time.time()
    print('It is taken: ', end_timer - start_timer, " sec")
    return 'OK'


def get_all_phone(offset: int, size: int, db_session):
    start_timer = time.time()
    count = 0
    size = 10000
    # offset = 0

    while True:
        first_time = time.time()
        portfolio_list = db_session.query(Loan_Portfolio).order_by(Loan_Portfolio.id.asc()).limit(size).offset(offset).all()
        print('portfolio takes: ', time.time() - first_time, " sec")

        if len(portfolio_list) == 0:
            break
        
        another_time = time.time()

        for portfolio in portfolio_list:
            if (portfolio.borrower_type is not None and portfolio.inps is not None and portfolio.borrower_type.startswith('08')):
                get_customer(db_session, portfolio.inps, portfolio.id)

            count += 1
            if count % 100 == 0:
                print(count, " it's taken: ", time.time() - another_time, " sec")
                another_time = time.time()

        print('el count: ', count)
        offset += size

        break
        #with break we save only (size) loan_id, without break we write all the portfolio


    end_timer = time.time()
    print('It is taken: ', end_timer - start_timer, " sec")
    return 'OK'