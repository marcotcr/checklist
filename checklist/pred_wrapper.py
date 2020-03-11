import numpy as np

class PredictorWrapper:
    @staticmethod
    def wrap_softmax(softmax_fn):
        def pred_and_conf(inputs):
            confs = softmax_fn(inputs)
            preds = np.argmax(confs, axis=1)
            return preds, confs
        pred_and_conf.conf = 'softmax'
        return pred_and_conf

    @staticmethod
    def wrap_predict(predict_fn):
        def pred_and_conf(inputs):
            preds = predict_fn(inputs)
            confs = np.ones(len(preds))
            return preds, confs
        return pred_and_conf
