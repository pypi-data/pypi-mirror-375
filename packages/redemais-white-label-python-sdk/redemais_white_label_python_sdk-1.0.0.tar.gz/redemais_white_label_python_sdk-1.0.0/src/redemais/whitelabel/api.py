import os, base64, logging
from fmconsult.http.api import ApiBase

class RedeMaisWhiteLabelApi(ApiBase):

    def __init__(self):
        try:
            self.api_token          = os.environ['redemais.whitelabel.api.token']
            self.api_environment    = os.environ['redemais.whitelabel.api.environment']
            self.id_cliente         = os.environ('redemais.whitelabel.api.id_cliente')
            self.id_contrato_plano  = os.environ('redemais.whitelabel.api.id_contrato_plano')

            self.headers = {
                'x-api-key': self.api_token
            }

            url_endpoint = (lambda env: 'prd-v1' if env == 'live' else 'hml-v1' if env == 'sandbox' else None)(self.environment)

            self.base_url = f'https://ddt8urmaeb.execute-api.us-east-1.amazonaws.com/{url_endpoint}/rms1'
        except:
            raise