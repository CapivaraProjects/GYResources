import os
import cv2
import uuid
import logging
import operator
import time
import tensorflow as tf
from grpc.beta import implementations
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2
from tools import Logger
from api.restplus import CELERY, FLASK_APP
import models.Disease
import models.Analysis
import models.AnalysisResult
from repository.AnalysisResultRepository import AnalysisResultRepository


logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s | %(asctime)s | %(threadName)-10s | %(message)s',)

tf.enable_eager_execution()


def read_tensor_from_image_file(file_name,
                                input_height=299,
                                input_width=299,
                                input_mean=0,
                                input_std=255):
    try:
        input_name = "file_reader"
        file_reader = tf.read_file(file_name, input_name)
        if file_name.endswith(".png"):
            image_reader = tf.image.decode_png(
                file_reader, channels=3, name="png_reader")
        elif file_name.endswith(".gif"):
            image_reader = tf.squeeze(
                tf.image.decode_gif(file_reader, name="gif_reader"))
        elif file_name.endswith(".bmp"):
            image_reader = tf.image.decode_bmp(file_reader, name="bmp_reader")
        else:
            image_reader = tf.image.decode_jpeg(
                file_reader, channels=3, name="jpeg_reader")
        float_caster = tf.cast(image_reader, tf.float32)
        dims_expander = tf.expand_dims(float_caster, 0)
        resized = tf.image.resize_bilinear(
            dims_expander, [input_height, input_width])
        normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    except Exception as exception:
        Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                             'Error',
                             'Error to convert image',
                             'read_tensor_from_image_file()',
                             '{}'.format(exception),
                             FLASK_APP.config["TYPE"])
    return normalized


def get_response(result):
    # final_result = {}
    # model_info = {}
    prediction_result = {}
    prediction = result.outputs['prediction'].float_val
    classes = result.outputs['classes'].string_val
    output_length = len(classes) if (len(classes) == len(prediction)) else -1

    if (output_length != -1):
        for i in range(output_length):
            prediction_result[classes[i].decode()] = float(prediction[i])

    sorted_result = sorted(
        prediction_result.items(),
        key=operator.itemgetter(1),
        reverse=True)
    return sorted_result[0:3]


def build_request(image):
    request = predict_pb2.PredictRequest()
    request.model_spec.name = 'inception'
    request.model_spec.signature_name = tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY

    try:
        request.inputs['image'].CopyFrom(
            tf.contrib.util.make_tensor_proto(image))
    except Exception as exception:
        Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                             'Error',
                             'Error to convert copy from input',
                             'make_prediction()',
                             '{}'.format(exception),
                             FLASK_APP.config["TYPE"])
    return request


@CELERY.task(name='tf_serving_client.split_prediction')
def split_prediction(
        img,
        window_size,
        init,
        end,
        analysis,
        diseases):
    img = cv2.imread(os.path.join(
        FLASK_APP.config['IMAGESPATH'],
        img))

    channel = implementations.insecure_channel(
        FLASK_APP.config["TFSHOST"],
        int(FLASK_APP.config["TFSPORT"]))
    stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)

    saliency = cv2.saliency.StaticSaliencyFineGrained_create()
    (success, saliencyMap) = saliency.computeSaliency(img)

    threshMap = cv2.threshold(
        saliencyMap,
        0,
        255,
        cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    results = []
    for y in range(init, end, window_size):
        for x in range(0, img.shape[1], window_size):
            crop = img[y:y + window_size, x: x + window_size]

            if crop.shape[0] != window_size or crop.shape[1] != window_size:
                continue
            thresh_roi = threshMap[y:y + window_size, x: x + window_size]
            if (cv2.countNonZero(thresh_roi) * 100) / (
                    window_size ** 2) > 20:

                crop_filepath = os.path.join(
                    '/tmp',
                    str(uuid.uuid4()) + '.jpg')

                cv2.imwrite(crop_filepath, crop)
                frame = str([y, y + window_size, x, x + window_size])

                image = read_tensor_from_image_file(crop_filepath)
                request = build_request(image)
                response = [("None", 0)]
                try:
                    start_time = time.time()
                    result = stub.Predict(request, 120.0)
                    request_proccess_time = int(
                        round((time.time() - start_time) * 1000))
                    logging.info("request time: {0}ms".format(
                        request_proccess_time))
                    Logger.Logger.create(
                        FLASK_APP.config["ELASTICURL"],
                        'Info',
                        'request time: {0}ms'.format(request_proccess_time),
                        'make_prediction()',
                        '',
                        FLASK_APP.config["TYPE"])
                    response = get_response(result)
                    logging.info("response={}".format(response))
                    if response[0][0].capitalize() == "Noise":
                        logging.info("Noise detected, ignoring prediction!")
                        continue
                    elif response[0][0].capitalize() == "None":
                        logging.info("Error to predict!")
                        continue
                    else:
                        healthy = [d if d['commonName'] == 'healthy' else {} for d in diseases][0]
                        if not healthy:
                            continue
                        if int(response[0][0]) == healthy['id']:
                            # means that this frame is healthy
                            continue
                        else:
                            disease_id = int(response[0][0])

                        score = response[0][1]

                        # obtem a doença a partir do nome
                        for x in diseases:
                            if disease_id == x['id']:
                                disease = x

                        # cria o objeto AnalysisResult
                        results.append(models.AnalysisResult.AnalysisResult(
                            id=None,
                            analysis=models.Analysis.Analysis(
                                id=analysis['id'],
                                image=None,
                                classifier=None).__dict__,
                            disease=models.Disease.Disease(
                                id=disease['id'],
                                plant=None).__dict__,
                            score=score,
                            frame=frame).__dict__)

                except Exception as exception:
                    logging.error(
                        "make_prediction: %s" % (str(exception)))
                    Logger.Logger.create(
                        FLASK_APP.config["ELASTICURL"],
                        'Error',
                        'Error to predict',
                        'make_prediction()',
                        '{}'.format(exception),
                        FLASK_APP.config["TYPE"])
    return results


@CELERY.task(name='tf_serving_client.make_prediction')
def make_prediction(
        analysis,
        diseases):
    img = cv2.imread(os.path.join(
        FLASK_APP.config['IMAGESPATH'],
        analysis['image']['url']))

    window_size = FLASK_APP.config['WINDOW_SIZE']

    img_step = img.shape[0] // FLASK_APP.config['THREADS']
    init = [0] * FLASK_APP.config['THREADS']
    end = [0] * FLASK_APP.config['THREADS']
    for i in range(0, FLASK_APP.config['THREADS']):
        init[i] = img_step * i
        end[i] = init[i] * img_step

    tasks = [split_prediction.delay(
        analysis['image']['url'],
        window_size,
        init[i],
        end[i],
        analysis,
        diseases) for i in range(0, FLASK_APP.config['THREADS'])]
    try:
        analysisResultRepo = AnalysisResultRepository(
            FLASK_APP.config["DBUSER"],
            FLASK_APP.config["DBPASS"],
            FLASK_APP.config["DBHOST"],
            FLASK_APP.config["DBPORT"],
            FLASK_APP.config["DBNAME"])
        results = []
        for t in tasks:
            while not t.ready():
                logging.info('waiting end task')
            if t.ready():
                results.extend([models.AnalysisResult.AnalysisResult(
                    id=None,
                    analysis=models.Analysis.Analysis(id=r['analysis']['id']),
                    disease=models.Disease.Disease(id=r['disease']['id']),
                    score=r['score'],
                    frame=r['frame']) for r in t.get()])
        analysisResultRepo.create_using_list(results)
    except Exception as ex:
        logging.error('AnalysisResult insertion: %s' % str(ex))
