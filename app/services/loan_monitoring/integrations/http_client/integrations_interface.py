from app.config.config import IABS_LOGIN, IABS_SHINA_PASSWORD, IABS_API, \
                              PLAYMOBILE_API, PLAYMOBILE_TOKEN, \
                              SOLIQ_API, SOLIQ_AUTH_LOGIN, SOLIQ_AUTH_PASSWORD, \
                              SSP_API, SSP_AUTH_LOGIN, SSP_AUTH_PASSWORD, \
                              ADLIYA_API, ADLIYA_LOGIN, ADLIYA_PASSWORD, \
                              GAROV_API, GAROV_AUTH_LOGIN, GAROV_AUTH_PASSWORD
import json


class HttpIntegrationsInterface():
    iabs_auth = IABS_API + '/getToken'
    iabs_get_client_credit = IABS_API + '/1.0.0/get-client-credit-by-loan-id/'
    iabs_get_customer = IABS_API + '/1.0.0/get-customer'
    iabs_get_accounts = IABS_API + '/1.0.0/get-active-accounts/'
    iabs_get_account_turnover_for_loan = IABS_API + '/1.0.0/get-account-turnover-for-loan'
    iabs_get_corporate_customer = IABS_API + '/1.0.0/corporate/customers'
    iabs_get_loan_repayment_schedule = IABS_API + '/1.0.0/loan-repayment-schedule'
    iabs_get_currency_rate_jur = IABS_API + '/1.0.0/get-currency-rate-jur'
    
    playmobile_send = PLAYMOBILE_API + '/api/v1/play-mobile'
    
    soliq_auth = SOLIQ_API + '/api/v1/auth/authenticate'
    soliq_first_form = SOLIQ_API + '/api/v1/tax/buxbalans/v1'
    soliq_second_form = SOLIQ_API + '/api/v1/tax/finreport/v1'
    soliq_get_eauksion_orders = SOLIQ_API + '/api/v1/service/eauksion/v1/get-orders'
    soliq_get_eauksion_order_info = SOLIQ_API + '/api/v1/service/eauksion/v1/order-info'
    
    mib_actions_pinfl = SOLIQ_API + '/api/v1/mib/service/actions/v1/pinfl'
    mib_actions_stir = SOLIQ_API + '/api/v1/mib/service/actions/v1/stir'
    mib_debtors_pinfl = SOLIQ_API + '/api/v1/mib/service/debtors/v1/pinfl'
    mib_debtors_stir = SOLIQ_API + '/api/v1/mib/service/debtors/v1/stir'
    
    ssp_auth = SSP_API + '/api/v1/auth/authenticate'
    ssp_theme_list = SSP_API + '/api/v1/theme-list'
    ssp_organization_list= SSP_API + '/api/v1/organization-list'
    ssp_claim_list = SSP_API + '/api/v1/claim-list'
    ssp_currency_list = SSP_API + '/api/v1/currency-list'
    ssp_claim_application = SSP_API + '/api/v1/claim-application'
    ssp_language_list = SSP_API + '/api/v1/language-list'
    ssp_integration = SSP_API + '/api/v1/integration/'
    
    adliya_auth = ADLIYA_API + '/api/v1/adliya/auth/authenticate'
    adliya_lifting_ban_imposed_by_bank = ADLIYA_API + '/api/v1/adliya/remove-notarial-ban'
    adliya_lifting_ban_imposed_by_notary = ADLIYA_API + '/api/v1/adliya/remove-notarial-ban-notary'
    adliya_post_info = ADLIYA_API + '/api/v1/adliya/info/post-info'
    adliya_doc_type = ADLIYA_API + '/api/v1/adliya/info/doc-type'
    adliya_subject_type = ADLIYA_API + '/api/v1/adliya/info/subject-type'
    adliya_org_type = ADLIYA_API + '/api/v1/adliya/info/org-type'
    adliya_personal_document_type = ADLIYA_API + '/api/v1/adliya/info/personal-document-type'
    
    
    garov_auth = GAROV_API + '/api/v1/garov/auth/authenticate'
    garov_notary_ban = GAROV_API + '/api/v1/garov/notary/ban'
    garov_notary_ban_cancel = GAROV_API + '/api/v1/garov/notary/bancancel'
    garov_notary_ban_list = GAROV_API + '/api/v1/garov/notary/search'
    garov_get_notary_subject_type = GAROV_API + '/api/v1/garov/ref/notary/subject_type'
    garov_get_notary_property_type = GAROV_API + '/api/v1/garov/ref/notary/property_type'
    garov_get_notary_document_type = GAROV_API + '/api/v1/garov/ref/notary/doc_type'

    def get_playmobile_token(self):
       return PLAYMOBILE_TOKEN

    def get_token_data(self):
      return json.dumps({
        "username": IABS_LOGIN,
        "password": IABS_SHINA_PASSWORD
      })
    
    def get_account_turnover_params(self, account: str, codeFilial: str, dateBegin: str, dateClose: str):
        return {
            'account': account,
            'codeFilial': codeFilial,
            'pageNumber': 1,
            'pageSize': 1000,
            'type': 3,
            'dateBegin': dateBegin,
            'dateClose': dateClose
        }
    

    def get_soliq_token_data(self):
        return json.dumps({
            "username" : SOLIQ_AUTH_LOGIN,
            "password" : SOLIQ_AUTH_PASSWORD
        })

    def get_ssp_token_data(self):
        return json.dumps({
            "username" : SSP_AUTH_LOGIN,
            "password" : SSP_AUTH_PASSWORD
        })

    def get_adliya_token_data(self):
        return json.dumps({
            "username" : ADLIYA_LOGIN,
            "password" : ADLIYA_PASSWORD
        })

    def get_garov_token_data(self):
        return json.dumps({
            "username" : GAROV_AUTH_LOGIN,
            "password" : GAROV_AUTH_PASSWORD
        })