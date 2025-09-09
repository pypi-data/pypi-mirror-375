import logging, jsonpickle
from http import HTTPMethod
from fmconsult.utils.url import UrlUtil
from redemais.whitelabel.api import RedeMaisWhiteLabelApi
from redemais.whitelabel.dtos.beneficiario import Beneficiario

class Beneficiarios(RedeMaisWhiteLabelApi):
    
    def adesao(self, data:Beneficiario, id_tipo_plano: int):
        try:
            logging.info(f'add new person...')
            payload = {
                "idClienteContrato": int(self.id_contrato_plano),
                "idBeneficiarioTipo": 1,
                "nome": data.nome,
                "codigoExterno": data.codigo_externo,
                "idCliente": int(self.id_cliente),
                "cpf": data.cpf,
                "dataNascimento": data.data_nascimento,
                "sexo": data.sexo,
                "celular": data.celular,
                "email": data.email,
                "cep": data.cep,
                "logradouro": data.endereco,
                "numero": data.numero_endereco,
                "complemento": data.complemento_endereco,
                "bairro": data.bairro,
                "cidade": data.cidade,
                "uf": data.uf,
                "tipoPlano": id_tipo_plano
            }

            if not data.cpf_titular is None:
                payload['cpfTitular'] = data.cpf_titular
                
            self.endpoint_url = UrlUtil().make_url(self.base_url, ['adesao'])
            res = self.call_request(HTTPMethod.POST, self.endpoint_url, None, payload=payload)
            return jsonpickle.decode(res)
        except:
            raise