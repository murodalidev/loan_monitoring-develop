
from app.models.problems_case.problems_assets.problems_assets_history_model import ProblemsAssetsHistory
from app.models.problems_case.problems_assets.problems_assets_model import ProblemsAssets
from app.models.problems_case.problems_case_model import ProblemsCase
from ......services.monitoring_files import files_crud

    
def get_problems_assets_sell_details(problem_case_id, problems_assets_type_id, db_session):
    problems_assets_datas = {}
    problems_assets = db_session.query(ProblemsAssets).filter(ProblemsAssets.problems_case_id == problem_case_id)\
        .filter(ProblemsAssets.type_id == problems_assets_type_id).first()
    
    
    if problems_assets is not None:
        problems_assets_datas ={"id":problems_assets.id,
                            "type" : problems_assets.type_id and problems_assets.type or None,
                            "main_responsible": problems_assets.main_responsible_id and {"id":problems_assets.main_responsible.id,
                                                                                         "full_name":problems_assets.main_responsible.full_name} or None,
                            "second_responsible": problems_assets.second_responsible_id and {"id":problems_assets.second_responsible.id,
                                                                                         "full_name":problems_assets.second_responsible.full_name} or None,
                            "turn": problems_assets.turn and problems_assets.turn or None,
                            "assets_status": problems_assets.assets_status_id and problems_assets.status or None,
                            "created_at":problems_assets.created_at and problems_assets.created_at or None,
                            "updated_at":problems_assets.updated_at and problems_assets.updated_at or None,
                            "files": problems_assets.files and files_crud.get_case_files(problems_assets) or None}
        
    return {"problems_assets":problems_assets_datas}
