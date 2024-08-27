from enum import Enum

class MGT(Enum):
    NEW = 1
    TARGET_MONITORING = 2
    PLAN_MONITORING = 3
    ON_WORK = 4
    SEND_PORBLEM = 5
    SEND_JURIDIC = 6
    FINAN = 9
    CLOSE = 10
    UNSCHEDULED = 11
    PROBLEMS = 12
    DEADLINE_EXTENSION = 13
    JUDICIAL = 14
    ASSETS_GET = 15
    ASSETS_SELL = 16
    OUT_OF_BALANCE = 17
    MIB_ENDED = 20
    AUCTION = 21
    
class KGT(Enum):
    SEND_1_LETTER = 7
    SEND_2_LETTER = 8
    

class PGT(Enum):
    NEW = 12
    APPOINT_RESPONSIBLE = 13
    SEND_JURIDIC = 17
    REPAID = 18
    
    
class JGT(Enum):
    APPOINT_RESPONSIBLE = 19
    COORDINATE_DOCUMENTS = 12
    PROCURATURA = 21
    CONSEQUENCE = 22
    TPP = 23
    LETTER_FROM_COURT = 24
    COURT = 25
    MIB = 26
    AUCTION = 27
    SEND_TO_ARRIVAL = 28
    CLOSE = 29
    RETURN = 30
    
    
    
class DEP(Enum):
    KAD = 3
    PROBLEM = 6
    JURIDIC = 7
    
    
class GTCAT(Enum):
    MONIT = 1
    PROBLEM = 2
    JURIDIC = 3
    PROBLEMS_ARRIVAL = 4
    JURIDIC_PUNISH = 5
    MONIT_EXTRA = 6
    BUSINESS = 7
    KAD = 8
    
    
    

class MAIN_DUE_DATE(Enum):
    DATE = 3
    
    
class CASE_HISTORY(Enum):
    TARGET = 1
    SCHEDULED = 2
    UNSCHEDULED = 3
    LOAN_CASE = 4
    PROBLEMS = 5
    JUDICIAL = 6
    ASSETS_GET = 7
    ASSETS_SELL = 8
    OUT_OF_BALANCE = 9
    BPI_ENDED = 10
    AUCTION = 11

class TASK_STATUS(Enum):
    STARTED = 1
    IN_PROGRESS = 2
    COMPLETED = 5
    FOR_CHECKING = 6
    REDO = 10

class TARGET_MONITORING_STATUS(Enum):
    STARTED = 1
    FOR_CHECKING = 3
    COMPLETED = 4
    REDO = 5
    
    
    
    
class DEADLINE_EXT(Enum):
    OK = 1
    EXPIRED = 2
    WAITING = 3