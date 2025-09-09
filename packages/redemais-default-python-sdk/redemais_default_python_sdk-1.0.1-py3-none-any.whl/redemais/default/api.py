import os, base64, logging
from fmconsult.http.api import ApiBase

class RedeMaisDefaultApi(ApiBase):

    def __init__(self):
        try:
            self.api_user           = os.environ['redemais.default.api.user']
            self.api_token          = os.environ['redemais.default.api.token']
            self.api_environment    = os.environ['redemais.default.api.environment']
            self.id_cliente         = os.environ['redemais.default.api.id_cliente']
            self.id_contrato_plano  = os.environ['redemais.default.api.id_contrato_plano']

            self.headers = {
                'usuario': self.api_user,
                'token': self.api_token,
            }
            
            self.base_url = f'https://z8u0zwbfqujqnz6-rmsdbdev01.adb.sa-saopaulo-1.oraclecloudapps.com/ords/rmsown/rmsapi'
        except:
            raise