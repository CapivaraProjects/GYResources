from threading import Thread
import logging

import models.Analysis
from repository.DiseaseRepository import DiseaseRepository
from repository.AnalysisResultRepository import AnalysisResultRepository
from api.restplus import FLASK_APP

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] (%(threadName)-10s) %(message)s',)


class ThreadWithReturnValue(Thread):

    def __init__(
            self,
            group=None,
            target=None,
            name=None,
            args=(),
            kwargs=None,
            *,
            daemon=None):
        Thread.__init__(self, group, target, name, args, kwargs, daemon=daemon)
        self._return = None

    def run(self):
        if self._target is not None:

            logging.info("Inicia processo da thread...")
            self._return = self._target(*self._args, **self._kwargs)
            logging.info("Fim do make_prediction")
            # obtem o resultado da analise
            response = self._return
            # gambiarra por falta de padronização no banco
            disease_name=""
            logging.info("response={}".format(response))
            if response[0][0].capitalize() == "Noise":
                logging.info("Noise detected, ignoring prediction!")
                return
            elif response[0][0].capitalize() == "None":
                logging.info("Error to predict!")
                return
            else:
                if response[0][0] == "healthy":
                    disease_name=response[0][0]
                else:
                    disease_name=response[0][0].capitalize()


            # atributos para o AnalysisResult
            analysis = self._args[0]
            disease = models.Disease.Disease(
                                    plant=models.Plant.Plant(
                                        id=analysis['classifier']['plant']['id']),
                                    scientificName=disease_name)
            score = response[0][1]

            # obtem a doença a partir do nome
            diseaseRepo = DiseaseRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])
            result = diseaseRepo.search(disease=disease, pageSize=1, offset=0)
            logging.info("doencas={}".format(result))
            disease = result['content'][0]
            logging.info("doenca={}".format(disease))

            # cria o objeto AnalysisResult
            analysisResult = models.AnalysisResult.AnalysisResult(
                                id=None,
                                analysis=models.Analysis.Analysis(id=analysis['id']),
                                disease=models.Disease.Disease(id=disease.id),
                                score=score)

            # persistir o objeto
            analysisResultRepo = AnalysisResultRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])

            result = analysisResultRepo.create(analysisResult)
            logging.info("analysisresult={}".format(result))
