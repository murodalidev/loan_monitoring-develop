from enum import Enum

    
class DEP(Enum):
    KAD = 3
    PROBLEM = 4
    JURIDIC = 7
    BUSINESS = 2
    
    
    
class BRANCH(Enum):
    KAD = 3
    PROBLEM = 6
    JURIDIC = 7
    
    
    


class ROLES(Enum):
    superuser = 1
    monitoring_filial_user = 2
    monitoring_filial_admin = 3
    monitoring_main_admin = 4
    business_block_main_admin = 5
    business_block_filial_admin = 6
    business_block_filial_user = 7
    kad_block_main_admin = 8
    kad_block_filial_admin = 9 
    kad_block_filial_user = 10
    promlem_block_main_admin = 11
    problem_block_filial_admin = 12 
    promlem_block_filial_user = 13
    superviser = 14
    main_superviser = 15
    main_superviser_kad = 16
    main_superviser_business = 17
    main_superviser_problem = 18
    main_superviser_kad_with_pledge = 19
    problem_block_lawyer = 20
    problem_block_report_admin = 21
    directory_admin = 22
    has_all_loan_stats = 23