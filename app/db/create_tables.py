from ..db.connect_db import Base, engine
from ..models.brief_case.directories.bank_mfo import bank_mfo
from ..models.brief_case.directories.client_region import client_region
from ..models.brief_case.directories.client_district import client_district
from ..models.brief_case.directories.currency import currency
from ..models.brief_case.directories.term_type import term_type
from ..models.brief_case.directories.quality_class import quality_class
from ..models.brief_case.directories.loan_security import loan_security
from ..models.brief_case.directories.credit_satus import status
from ..models.brief_case.directories.checked_status import checked_status
from ..models.brief_case.directories.dis_reg_post_codes import post_codes
from ..models.brief_case.directories.credit_rating import credit_rating
from ..models.brief_case.directories.funds_sources import funds_sources
from ..models.brief_case.directories.loan_product import loan_product
from ..models.brief_case.directories.loan_product_type import loan_product_type
from ..models.brief_case.directories.lending_type import lending_type
from ..models.brief_case.directories.mahalla_name import mahalla_name
from ..models.brief_case.directories.loan_industry import loan_industry
from ..models.brief_case.directories.local_code import local_code
from ..models.brief_case.directories.client_parent_org import client_parent_org
from ..models.brief_case.directories.borrower_type import borrower_type
from ..models.brief_case.directories.loan_goal import loan_goal
from ..models.brief_case.directories.gender import gender
from ..models.brief_case.loan_portfolio_schedule import LoanPortfolioSchedule
from ..models.brief_case.loan_portfolio import Loan_Portfolio
from ..models.brief_case.loan_portfolio import Loan_Portfolio_Date


from ..models.structure.departments import Departments
from ..models.users.user_tg_bot_auth import UserTgBotAuth
from ..models.structure.positions import Positions
from ..models.users.user_status import user_status
from ..models.users.users import user_role
from ..models.users.users import Users
from ..models.statuses.attached_type_model import AttachedType
from ..models.users.attached_branches import attached_branches
from ..models.users.attached_regions import attached_regions
from ..models.rbac.permission_category import permission_category
from ..models.rbac.permission import permission
from ..models.rbac.roles import roles
from ..models.rbac.roles import role_permissions



from ..models.statuses.monitoring_case_status_model import MonitoringCaseStatus
from ..models.statuses.montoring_status_model import MonitoringStatus
from ..models.statuses.monitoring_frequency_period_model import MonitoringFrequencyPeriod
from ..models.monitoring_case.monitoring_case_model import MonitoringCase
from ..models.statuses.financial_analysis_status_model import FinancialAnalysisStatus
from ..models.monitoring_case.financial_analysis_model import FinancialAnalysis
from ..models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_model import unscheduled_monitoring_files
from ..models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_model import UnscheduledMonitoring
from ..models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_history import UnscheduledMonitoringHistory
from ..models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_expiration_model import UnscheduledMonitoringExpiration
from ..models.monitoring_case.extension_history_model import scheduled_extension_files, target_extension_files, unscheduled_extension_files, TargetDeadlineExtensionMonitoringHistory, ScheduledDeadlineExtensionMonitoringHistory, UnscheduledDeadlineExtensionMonitoringHistory
from ..models.statuses.scheduled_monitoring_status_model import ScheduledMonitoringStatus
from ..models.monitoring_case.scheduled_monitoring_model import ScheduledMonitoring
from ..models.monitoring_case.scheduled_monitoring_expiration_model import ScheduledMonitoringExpiration
from ..models.statuses.target_monitoring_result_model import TargetMonitoringResult

from ..models.statuses.target_monitoring_status_model import TargetMonitoringStatus
from ..models.monitoring_case.target_monitoring_expiration_model import TargetMonitoringExpiration
from ..models.files.file_types import FTypes
from ..models.files.files_types import FilesTypes
from ..models.files.monitoring_files_model import MonitoringFiles
from ..models.monitoring_case.target_monitoring_history_model import TargetMonitoringHistory
from ..models.monitoring_case.target_monitoring_model import TargetMonitoring
from ..models.monitoring_case.reslut_reason_model import ResultReason
from ..models.statuses.loan_case_status import LoanCaseStatus
from ..models.statuses.deadline_extension_model import DeadlineExtension
from ..models.statuses.case_history_type_model import CaseHistoryType
from ..models.loan_case.holidays_model import Holidays
from ..models.loan_case.loan_case_model import LoanCase
from ..models.loan_case.loan_case_history_model import LoanCaseHistory

from ..models.statuses.kad_case_status_model import KADCaseStatus
from ..models.statuses.kad_monitoring_result import KADMonitoringResult
from ..models.statuses.kad_monitoring_status import KADMonitoringStatus
from ..models.kad_case.kad_monitoring import KADMonitoring
from ..models.kad_case.kad_case_model import KADCase
from ..models.kad_case.kad_case_history import KADCaseHistory


from ..models.statuses.business_monitoring_result import BusinessMonitoringResult
from ..models.statuses.business_monitoring_status import BusinessMonitoringStatus
from ..models.statuses.business_case_status_model import BusinessCaseStatus
from ..models.business_case.business_case_model import BusinessCase
from ..models.business_case.business_monitoring import BusinessMonitoring
from ..models.business_case.business_case_history import BusinessCaseHistory

from ..models.statuses.problems_monitoring_status_model import ProblemsMonitoringStatus
from ..models.problems_case.problems_monitoring_model import ProblemsMonitoring
from ..models.statuses.problems_case_status_model import ProblemsCaseStatus
from ..models.problems_case.problems_case_model import ProblemsCase
from ..models.problems_case.problems_case_history import ProblemsCaseHistory
from ..models.problems_case.problems_monitoring_expiration_model import ProblemsMonitoringExpiration
from ..models.statuses.letter_status_model import LetterStatus
from ..models.statuses.letter_receiver_type_model import LetterReceiverType
from ..models.monitoring_case.hybrid_letter_model import HybridLetters

from ..models.statuses.juridical_case_status_model import JuridicalCaseStatus
from ..models.statuses.intended_overdue_type_model import IntendedOverdueType
from ..models.juridical_case.overdue_result_model import OverdueResult
from ..models.juridical_case.juridical_intended_overdue_model import JuridicalIntendedOverdue
from ..models.statuses.juridical_punishment_status_model import JuridicalPunishmentStatus
from ..models.juridical_case.juridical_punishment_model import JuridicalPunishment
from ..models.juridical_case.juridical_case_model import  juridical_case_files
from ..models.juridical_case.juridical_case_model import JuridicalCase
from ..models.juridical_case.juridical_case_history_model import JuridicalCaseHistory

from ..models.notification.monitoring_notification_type_model import MonitoringNotificationType
from ..models.notification.monitoring_notification_model import MonitoringNotification

from ..models.monitoring_task_manager.general_tasks_category_model import GeneralTasksCategory
from ..models.monitoring_task_manager.general_tasks_model import GeneralTasks
from ..models.statuses.task_status_model import TaskStatus
from ..models.monitoring_task_manager.task_manager_comments import TaskManagerComments
from ..models.monitoring_task_manager.task_manager_model import TaskManager

from ..models.monitoring_case.monitoring_excel_report import ReportOrder
from ..models.statuses.report_order_status import ReportOrderStatus, ReportBy

from ..models.balance_turnover.balance_turnover_model import BalanceTurnover, CheckBalanceTurnoverUpdate, CheckBalanceTurnoverUpdatePerOperDay
from ..models.balance_turnover.balance_turnover_model import BalanceTurnoverHistory
from ..models.balance_turnover.balance_turnover_model import Accounts, Saldo
from ..models.balance_turnover.account_prefix_model import AccountPrefix
from ..models.statuses.from_type_model import FromType

from ..models.integrations.ssp_integrations import SSP_integrations, SSPFiles
from ..models.integrations.integrations_service import Integrations_service
from ..models.integrations.integrations_service_api import Integrations_service_api
from ..models.integrations.integrations_log import Integrations_log
from ..models.integrations.currency_model import CurrencyRate

from ..models.problems_case.problem_states_model import ProblemStates
from ..models.problems_case.problem_state_chain_model import ProblemStateChain
from ..models.problems_case.non_target_state.non_target_letters_model import NonTargetLetters

from ..models.problems_case.non_target_state.non_target_type_model import NonTargetType
from ..models.problems_case.non_target_state.non_target_state_model import NonTargetState
from ..models.problems_case.non_target_state.non_target_files_model import NonTargetStateFiles

from ..models.problems_case.auction.auction_type_model import ProblemsAuctionType
from ..models.problems_case.auction.auction_model import ProblemsAuction
from ..models.problems_case.auction.auction_files_model import ProblemsAuctionFiles


from ..models.problems_case.mib_ended.mib_type_model import ProblemsMibType
from ..models.problems_case.mib_ended.mib_model import ProblemsMib
from ..models.problems_case.mib_ended.mib_files_model import ProblemsMibFiles

from ..models.problems_case.problems_assets.problems_assets_status_model import ProblemsAssetsStatus
from ..models.problems_case.problems_assets.problems_assets_type_model import ProblemsAssetsType
from ..models.problems_case.problems_assets.problems_assets_model import problems_assets_files, ProblemsAssets

from ..models.problems_case.problems_assets.problems_assets_notification_model import ProblemsStateNotification

from ..models.problems_case.judicial_process.judicial_process_type_model import JudicialType
from ..models.problems_case.judicial_process.judicial_authority_type import JudicialAuthorityType
from ..models.problems_case.judicial_process.judicial_authority import JudicialAuthority
from ..models.problems_case.judicial_process.judicial_process_data_model import judicial_data_files, JudicialData 




def create_table():
    print("Creating db...")
    return Base.metadata.create_all(engine)