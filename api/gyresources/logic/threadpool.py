from queue import Queue
from threading import Thread
import logging, sys

import models.Analysis
from repository.DiseaseRepository import DiseaseRepository
from repository.AnalysisResultRepository import AnalysisResultRepository
from api.restplus import FLASK_APP

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)


class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()
    
    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                logging.info("Inicia processo da thread...")
                self._return = func(*args, **kargs)
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
                analysis = args[0]
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

                logging.info("searching for disease...")
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
                
                logging.info("creating new analysis...")
                result = analysisResultRepo.create(analysisResult)
                logging.info("analysisresult={}".format(result))
            except Exception as e:
                logging.error("Error to get analysis result")
                raise e
            finally:
                self.tasks.task_done()
                sys.exit()


class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads): Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()
            