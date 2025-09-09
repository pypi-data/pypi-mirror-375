import logging, jsonpickle
from http import HTTPMethod
from fmconsult.utils.url import UrlUtil
from redemais.default.api import RedeMaisDefaultApi
from redemais.default.dtos.beneficiario import Beneficiario

class Beneficiarios(RedeMaisDefaultApi):
    
    def adesao(self, data:Beneficiario, id_tipo_plano: int):
        try:
            logging.info(f'add new person...')
            payload = {
                "ID_CONTRATO_PLANO": int(self.id_contrato_plano),
                "ID_BENEFICIARIO_TIPO": 1,
                "NOME": data.nome,
                "CODIGO_EXTERNO": data.codigo_externo,
                "ID_CLIENTE": int(self.id_cliente),
                "CPF": data.cpf,
                "DATA_NASCIMENTO": data.data_nascimento,
                "SEXO": data.sexo,
                "CELULAR": data.celular,
                "EMAIL": data.email,
                "CEP": data.cep,
                "LOGRADOURO": data.endereco,
                "NUMERO": data.numero_endereco,
                "COMPLEMENTO": data.complemento_endereco,
                "BAIRRO": data.bairro,
                "CIDADE": data.cidade,
                "UF": data.uf,
                "TIPO_PLANO": id_tipo_plano
            }

            if not data.cpf_titular is None:
                payload['CPF_TITULAR'] = data.cpf_titular
                
            self.endpoint_url = UrlUtil().make_url(self.base_url, ['adesao'])
            res = self.call_request(HTTPMethod.POST, self.endpoint_url, None, payload=payload)
            return jsonpickle.decode(res)
        except:
            raise