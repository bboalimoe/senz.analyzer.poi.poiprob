import numpy as np
from sklearn.mixture import GMM
from exception import *

class Trainer(object):
    def __init__(self, model):
        try:
            self.n_c = model["nMix"]
            self.c_t = model["covarianceType"]
            self.n_i = model["nIter"]
            self.count = model["count"]
            init_params = model["params"]
        except KeyError, error_key:
            raise ModelParamKeyError(error_key)

        try:
            self.gmm = GMM(n_components=self.n_c, covariance_type=self.c_t,
                           random_state=None, thresh=None, tol=1e-3, min_covar=1e-3,
                           n_iter=self.n_i, n_init=1, params="wmc", init_params="wmc")
        except:
            raise ModelInitError(self.n_c, self.c_t, self.n_i)

        if init_params.has_key("params"):
            gmm_param = init_params["params"]
            try:
                self.gmm.covars_ = np.array(gmm_param["covars"])
                self.gmm.means_ = np.array(gmm_param["means"])
                self.gmm.weights_ = np.array(gmm_param["weights"])
            except KeyError, error_key:
                raise ModelParamKeyError(error_key)

    def fit(self, x):
        self.x = x
        _x = np.array(x)
        if _x.ndim == 1:
            _x = _x.reshape([len(x), 1])
        try:
            self.gmm.fit(X=_x, y=None)
        except:
            params = {
                "initParams": self.gmm,
                "covars": self.gmm.covars_,
                "means": self.gmm.means_,
                "weights": self.gmm.weights_
            }
            raise FittingError(_x, params)

    def modelParams(self):
        new_params = {
            "nMix": self.n_c,
            "covarianceType": self.c_t,
            "count": self.count + len(self.x),
            "params": {
                "nMix": self.n_c,
                "covarianceType": self.c_t,
                "params": {
                    "covars": self.gmm.covars_.tolist(),
                    "means": self.gmm.means_.tolist(),
                    "weights": self.gmm.weights_.tolist()
                }
            }
        }
        return new_params


if __name__ == "__main__":
    _model = {"nMix": 4, "covarianceType": "full", "nIter": 50, "count": 100,
              "params": {"nMix": 4, "covarianceType": "full", "params": {
                  "covars": [[[1.2221303985456107]], [[0.3086663025400781]], [[1.28502444797073]],
                             [[0.26113702790883486]]],
                  "weights": [0.23603795980927875, 0.2527552282253478, 0.2800574289988682, 0.2311493829665058],
                  "means": [[4.536022877901543], [1.4914085123695209], [3.6895831128524326], [6.571810554595958]]}}}

    # _model = {"nMix": 4, "covarianceType": "full", "nIter": 50,
    #           "params": {"nMix": 4, "covarianceType": "full"}
    # }
    _obs = [1, 1, 1, 1, 5, 5, 5, 5, 19, 19, 19, 19, 33, 33, 33, 33]

    t = Trainer(_model)
    t.fit(_obs)

    print t.modelParams()