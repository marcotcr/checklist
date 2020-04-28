import numpy as np

class PredictorWrapper:
    @staticmethod
    def wrap_softmax(softmax_fn):
        """Wraps softmax such that it outputs predictions and confidences

        Parameters
        ----------
        softmax_fn : fn
            Takes lists of inputs, outputs softmax probabilities (2d np.array)

        Returns
        -------
        function
            wrapped prediction function, returns (preds, confs) instead of softmax

        """
        def pred_and_conf(inputs):
            confs = softmax_fn(inputs)
            preds = np.argmax(confs, axis=1)
            return preds, confs
        pred_and_conf.conf = 'softmax'
        return pred_and_conf

    @staticmethod
    def wrap_predict(predict_fn):
        """Wraps prediction functions to output predictions and a confidence score of 1

        Parameters
        ----------
        predict_fn : function
            Outputs a list of predictions given inputs (strings, integers, whatever)

        Returns
        -------
        function
            wrapped prediction function, returns (preds, confs) such that confs is list of float(1)

        """
        def pred_and_conf(inputs):
            preds = predict_fn(inputs)
            confs = np.ones(len(preds))
            return preds, confs
        return pred_and_conf
