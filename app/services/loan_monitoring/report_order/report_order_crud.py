from datetime import datetime, timedelta
from ....models.files.monitoring_files_model import MonitoringFiles
from fastapi import HTTPException
from ....models.monitoring_case.monitoring_excel_report import ReportOrder
from ....models.statuses.report_order_status import ReportOrderStatus, ReportBy
from ....models.statuses.target_monitoring_result_model import TargetMonitoringResult
from ....common.is_empty import is_empty, is_empty_list, is_exists
from ....common.commit import commit_object, flush_object
from ....config.logs_config import info_logger
from ....common.dictionaries.monitoring_case_dictionary import report_order_status, report_order_type
from ....common.dictionaries.general_tasks_dictionary import JGT, MGT, PGT, GTCAT, MAIN_DUE_DATE, CASE_HISTORY, DEADLINE_EXT


def report_order(user_id, path, report_type, report_by, db_session):
    new_order = ReportOrder(user_id = user_id,
                            path = path,
                            status = report_order_status['ordered'],
                            type = report_type,
                            report_by_id = report_by,
                            created_at = datetime.now())
    db_session.add(new_order)
    commit_object(db_session)
    info_logger.info('report has been ordered')
    return {"OK"}



def check_if_report_exists(user_id, report_type, report_by, db_session):
    info_logger.info('check if report exists')
    get_report = db_session.query(ReportOrder).filter(ReportOrder.user_id == user_id).filter(ReportOrder.type == report_type)\
        .filter(ReportOrder.report_by_id == report_by).order_by(ReportOrder.id.desc()).first()
    
    if get_report is None or get_report.status == report_order_status['ready']:
        info_logger.info('ok')
        return 0
    
    if get_report.status == report_order_status['error']:
        info_logger.info('error while creating report')
        raise HTTPException(status_code=401, detail='Проблема в процессе создания отчета')
    info_logger.info('report has not ready yet')
    raise HTTPException(status_code=403, detail='Отчет в процессе создания')



def change_report_status_to_ready(user_id, report_type, report_by, db_session):
    get_report = db_session.query(ReportOrder).filter(ReportOrder.user_id == user_id).filter(ReportOrder.type == report_type)
    
    if report_by is not None:
        get_report = get_report.filter(ReportOrder.report_by_id == report_by)
    
    get_report = get_report.order_by(ReportOrder.id.desc()).first()
    
    get_report.status = report_order_status['ready']
    get_report.updated_at = datetime.now()
    info_logger.info('report status has changed to ready')
    flush_object(db_session)

def change_report_status_to_error(user_id, report_type, report_by, db_session):
    get_report = db_session.query(ReportOrder).filter(ReportOrder.user_id == user_id).filter(ReportOrder.type == report_type)
    
    if report_by is not None:
        get_report = get_report.filter(ReportOrder.report_by_id == report_by)
    
    get_report = get_report.order_by(ReportOrder.id.desc()).first()
    
    get_report.status = report_order_status['error']
    get_report.updated_at = datetime.now()
    flush_object(db_session)  
    
    
    
    
    
def get_report_for_user(user_id, report_type, db_session):
    get_reports = db_session.query(ReportOrder).filter(ReportOrder.user_id == user_id).filter(ReportOrder.type == report_type).order_by(ReportOrder.id.desc()).limit(5).all()
    
    reports = []
    if get_reports is not None:
        for report in get_reports:
            
            reports.append({"id": report.id,
                        "path": report.path,
                        "status": report.report_status,
                        "report_by": report.report_by,
                        "created_at": report.created_at})
    
    
    return reports 

def get_report_by(db_session):
    get_report_by = db_session.query(ReportBy).all()
    reports = []
    if get_report_by is not None:
        for report in get_report_by:
            
            reports.append({"id": report.id,
                        "code": report.code,
                        "name": report.name})
    
    
    return reports 


def delete_report_for_user(report_id, db_session):
    get_report = db_session.query(ReportOrder).filter(ReportOrder.id == report_id).first()
    
    db_session.delete(get_report)
    
    commit_object(db_session)
    
    return 'OK' 