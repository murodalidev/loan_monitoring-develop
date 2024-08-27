from fastapi import FastAPI


from .services.websocket.create_websocket import ConnectionManager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .db.connect_db import SessionManager
from .api_routes.ping_api import ping
from .api_routes.create_tables import init
from .api_routes.loan_monitoring.kad_case import kad_case_api
from .api_routes.loan_monitoring.general_tasks import general_tasks
from .api_routes.loan_monitoring.general_tasks import general_tasks_category
from .api_routes.loan_monitoring.loan_portfolio import loan_portfolio_api, loan_portfolio_list_api, loan_portfolio_schedule_api
from .api_routes.loan_monitoring.loan_case import loan_case_api, monitoring_api
from .api_routes.loan_monitoring.loan_case import deadline_extension_api, holidays_api
from .api_routes.loan_monitoring.loan_portfolio import loan_product_api, local_code_api, lending_type_api
from .api_routes.loan_monitoring.loan_portfolio.account_turnover import account_turnover_api
from .api_routes.loan_monitoring.monitoring_case import monitoring_case_api, target_monitoring_api, result_reason_api, scheduled_monitoring_api, financial_analysis_api, unscheduled_monitoring_api, hybrid_letter_api
from .api_routes.loan_monitoring.problems_monitoring import problems_assets_get_api, out_of_balance_api, problems_assets_sell_api, problems_case_api, problems_monitoring_api
from .api_routes.loan_monitoring.problems_monitoring import judicial_api
from .api_routes.integrations import iabs_integrations_api, playmobile_integrations_api, soliq_integrations_api, ssp_integrations_api, adliya_integrations_api, mib_integrations_api, garov_integrations_api, logs as integration_logs
from .api_routes.loan_monitoring.directories import directories_api
from .api_routes.loan_monitoring.business_case import business_case_api
from .api_routes.user import user, user_tg_bot_api
from .api_routes.loan_monitoring.report_order import report_order_api
from .api_routes.user import attach_branches, attached_regions
from .api_routes.adliya import adliya_api
from .api_routes.loan_monitoring.notifications import notification_api
from .api_routes.authenticate import user_auth
from .api_routes.structure.region import branch
from .api_routes.structure.department import department
from .api_routes.structure.position import position
from .api_routes.rbac import permissions
from .api_routes.rbac import roles
from .services.rbac.permission_crud import update_endpoints 
from .services.websocket.create_websocket import manager
from .config import cache
app = FastAPI()
origins = ["*"]




import logging
from uvicorn.config import LOGGING_CONFIG

# Настраиваем форматтеры
LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
LOGGING_CONFIG["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(client_addr)s - \"%(request_line)s\" %(status_code)s"
LOGGING_CONFIG["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"

logging.config.dictConfig(LOGGING_CONFIG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_auth.router, prefix='/app')
app.include_router(integration_logs.router, prefix='/app')
app.include_router(adliya_api.router, prefix='/app')
app.include_router(adliya_integrations_api.router, prefix='/app')
app.include_router(iabs_integrations_api.router, prefix='/app')
app.include_router(soliq_integrations_api.router, prefix='/app')
app.include_router(ssp_integrations_api.router, prefix='/app')
app.include_router(mib_integrations_api.router, prefix='/app')
app.include_router(garov_integrations_api.router, prefix='/app')
app.include_router(account_turnover_api.router, prefix='/app')
app.include_router(loan_portfolio_api.router, prefix='/app')
app.include_router(playmobile_integrations_api.router, prefix='/app')
app.include_router(holidays_api.router, prefix='/app')
app.include_router(branch.router, prefix='/app')
app.include_router(department.router, prefix='/app')
app.include_router(position.router, prefix='/app')
app.include_router(general_tasks.router, prefix='/app')
app.include_router(general_tasks_category.router, prefix='/app')
app.include_router(user.router, prefix='/app')
app.include_router(user_tg_bot_api.router, prefix='/app')
app.include_router(attach_branches.router, prefix='/app')
app.include_router(attached_regions.router, prefix='/app')
app.include_router(loan_product_api.router, prefix='/app')
app.include_router(lending_type_api.router, prefix='/app')
app.include_router(local_code_api.router, prefix='/app')
app.include_router(roles.router, prefix='/app')
app.include_router(permissions.router, prefix='/app')
app.include_router(notification_api.router, prefix='/app')
app.include_router(loan_portfolio_list_api.router, prefix='/app')
app.include_router(loan_portfolio_schedule_api.router, prefix='/app')
app.include_router(business_case_api.router, prefix='/app')
app.include_router(kad_case_api.router, prefix='/app')
app.include_router(loan_case_api.router, prefix='/app')
app.include_router(monitoring_api.router, prefix='/app')
app.include_router(hybrid_letter_api.router, prefix='/app')
app.include_router(deadline_extension_api.router, prefix='/app')
app.include_router(monitoring_case_api.router, prefix='/app')
app.include_router(report_order_api.router, prefix='/app')
app.include_router(target_monitoring_api.router, prefix='/app')
app.include_router(result_reason_api.router, prefix='/app')
app.include_router(scheduled_monitoring_api.router, prefix='/app')
app.include_router(unscheduled_monitoring_api.router, prefix='/app')
app.include_router(financial_analysis_api.router, prefix='/app')
app.include_router(problems_case_api.router, prefix='/app')
app.include_router(problems_monitoring_api.router, prefix='/app')
app.include_router(judicial_api.router, prefix='/app')
app.include_router(problems_assets_get_api.router, prefix='/app')
app.include_router(problems_assets_sell_api.router, prefix='/app')
app.include_router(out_of_balance_api.router, prefix='/app')
app.include_router(directories_api.router, prefix='/app')
app.include_router(init.router, prefix='/app')
app.include_router(ping.router, prefix='/app')






@app.get("/tags")
async def tags():
    with SessionManager() as db_session:
        tags= []
        routes = []
        temp=''
        for route in app.router.__dict__["routes"]:
            if hasattr(route, "tags"):
                for rout in route.__dict__["tags"]:
                    if temp == rout:
                        break
                    temp = rout
                    for rou in app.router.__dict__["routes"]:
                        if hasattr(rou, "tags"):
                            for ro in rou.__dict__["tags"]:
                                if rout == ro:
                                    routes.append(rou.__dict__["path"])
                    tags.append({"tag": rout, "path":routes})
                    routes = []
        return update_endpoints(tags, db_session)
    


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id:int):
    await manager.connectSoc(client_id,websocket)
    try:
        
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.direct_disconnect(client_id,websocket)
