from app.db.connect_db import Base
from sqlalchemy import Integer,Column, Column, Integer, ForeignKey, DateTime, Table, Boolean, String, Text, Date, Float, NUMERIC
from sqlalchemy.orm import relationship





class BalanceTurnover(Base):
    __tablename__='balance_turnover'
    id=Column(Integer, primary_key=True)
    loan_id = Column(Integer, index=True) 
    debt_account_start_state = Column(NUMERIC, nullable=True)
    debt_account_credit_sum = Column(NUMERIC, nullable=True)
    
    account_16377_start_state = Column(NUMERIC, nullable=True)
    account_16377_debit_sum = Column(NUMERIC, nullable=True)
    account_16377_credit_sum = Column(NUMERIC, nullable=True)
    
    account_163xx_start_state = Column(NUMERIC, nullable=True)
    account_163xx_debit_sum = Column(NUMERIC, nullable=True)
    account_163xx_credit_sum = Column(NUMERIC, nullable=True)
    
    account_95413_start_state = Column(NUMERIC, nullable=True)
    account_95413_debit_sum = Column(NUMERIC, nullable=True)
    account_95413_credit_sum = Column(NUMERIC, nullable=True)
    
    account_9150x_start_state = Column(NUMERIC, nullable=True)
    account_9150x_debit_sum = Column(NUMERIC, nullable=True)
    account_9150x_credit_sum = Column(NUMERIC, nullable=True)
    
    lead_last_date = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True
        
class CheckBalanceTurnoverUpdate(Base):
    __tablename__='check_balance_turnover_update'
    id=Column(Integer, primary_key=True)
    is_updated_debt_account = Column(Boolean, default=False)
    is_updated_account_163xx = Column(Boolean, default=False)
    is_updated_account_95413_9150x = Column(Boolean, default=False) 
    
    class Config:
        orm_mode=True


class BalanceTurnoverHistory(Base):
    __tablename__='balance_turnover_history'
    id=Column(Integer, primary_key=True)
    loan_id = Column(Integer, index=True) 
    debt_account_start_state = Column(NUMERIC, nullable=True)
    debt_account_credit_sum = Column(NUMERIC, nullable=True)
    
    account_16377_start_state = Column(NUMERIC, nullable=True)
    account_16377_debit_sum = Column(NUMERIC, nullable=True)
    account_16377_credit_sum = Column(NUMERIC, nullable=True)
    
    account_163xx_start_state = Column(NUMERIC, nullable=True)
    account_163xx_debit_sum = Column(NUMERIC, nullable=True)
    account_163xx_credit_sum = Column(NUMERIC, nullable=True)
    period = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True
        
        
        
        
        
class Accounts(Base):
    __tablename__='accounts'
    id=Column(Integer, primary_key=True)
    loan_type_account = Column(Integer, nullable=True) 
    loan_id = Column(Integer, index=True) 
    coa = Column(Integer, nullable=True) 
    client_id = Column(Integer, nullable=True) 
    code = Column(String(64),  nullable = True) 
    code_filial = Column(String(10), nullable=True) 
    name = Column(Text, nullable=True)  
    saldo_in = Column(String(25),  nullable = True) 
    saldo_out = Column(String(25),  nullable = True) 
    turnover_debit = Column(String(25),  nullable = True) 
    turnover_credit = Column(String(25),  nullable = True) 
    turnover_all_debit = Column(String(25),  nullable = True)
    turnover_all_credit = Column(String(25),  nullable = True)
    lead_last_date = Column(Date, nullable=True)
    client_code = Column(Integer, nullable=True) 
    product_id = Column(Integer, nullable=True) 
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True
        
        


class AccountsHistory(Base):
    __tablename__='accounts_history'
    id=Column(Integer, primary_key=True)
    loan_type_account = Column(Integer, nullable=True) 
    loan_id = Column(Integer, index=True) 
    coa = Column(Integer, nullable=True) 
    client_id = Column(Integer, nullable=True) 
    code = Column(String(64),  nullable = True) 
    code_filial = Column(String(10), nullable=True) 
    name = Column(Text, nullable=True)  
    saldo_in = Column(String(25),  nullable = True) 
    saldo_out = Column(String(25),  nullable = True) 
    turnover_debit = Column(String(25),  nullable = True) 
    turnover_credit = Column(String(25),  nullable = True) 
    turnover_all_debit = Column(String(25),  nullable = True)
    turnover_all_credit = Column(String(25),  nullable = True)
    lead_last_date = Column(DateTime, nullable=True)
    client_code = Column(Integer, nullable=True) 
    product_id = Column(Integer, nullable=True) 
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True
        
        
        
        
        
        
        
        
        
        
    
    
class Saldo(Base):
    __tablename__='saldo'
    id=Column(Integer, primary_key=True)
    loan_type_account = Column(Integer, nullable=True) 
    loan_id = Column(Integer, index=True) 
    coa = Column(Integer, nullable=True) 
    account_code = Column(String(64),  nullable = True) 
    code_filial = Column(String(10), nullable=True) 
    saldo_in = Column(String(25),  nullable = True) 
    saldo_out = Column(String(25),  nullable = True) 
    turnover_debit = Column(String(25),  nullable = True) 
    turnover_credit = Column(String(25),  nullable = True) 
    turnover_all_debit = Column(String(25),  nullable = True)
    turnover_all_credit = Column(String(25),  nullable = True)
    oper_day = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True


class CheckBalanceTurnoverUpdatePerOperDay(Base):
    __tablename__='check_balance_turnover_update_per_operday'
    id=Column(Integer, primary_key=True)
    oper_day = Column(Date)
    is_updated_main_accounts_credit_sums = Column(Boolean, default=False)
    is_updated_16377_accounts_credit_debit_sums = Column(Boolean, default=False)
    is_updated_163xx_accounts_credit_debit_sums = Column(Boolean, default=False)
    is_updated_95413_accounts_credit_debit_sums = Column(Boolean, default=False)
    is_updated_9150x_accounts_credit_debit_sums = Column(Boolean, default=False)
    
    class Config:
        orm_mode=True