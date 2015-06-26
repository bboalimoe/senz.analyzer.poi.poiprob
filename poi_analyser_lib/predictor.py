import numpy as np
from utils import checkCovarianceType
from sklearn.mixture import GMM
from exception import *

class Predictor(object):
    def __init__(self, models):
        covars  = []
        means   = []
        weights = []
        sum     = 0           # the sum of each gmm"s sample spot.
        self.n_mixs      = []
        self.n_mix       = 0  # the count of Gaussian model of new gmm.
        self.covar_types = [] # the covariance type of each gmm.
        self.models      = models

        # Generate new GMM"s nMix and covarianceType
        for model in self.models:
            try:
                sum += model["count"]
                self.n_mixs.append(model["nMix"])
                self.n_mix += model["nMix"]
                self.covar_types.append(model["covarianceType"])
            except KeyError, error_key:
                raise ModelParamKeyError(error_key)


        # Generate every Gaussian model params.
        for model in self.models:
            try:
                params = model["params"]["params"]
                for covar in params["covars"]:
                    covars.append(covar)
                for mean in params["means"]:
                    means.append(mean)
                for weight in params["weights"]:
                    weight *= (float(model["count"])/float(sum))
                    weights.append(weight)
            except KeyError, error_key:
                raise ModelParamKeyError(error_key)

        # Build the new GMM.
        try:
            self.gmm = GMM(
                n_components=self.n_mix,
                covariance_type=checkCovarianceType(self.covar_types)
            )
        except CovarianceTypeError:
            raise
        except:
            raise ModelInitError(self.n_mix, self.covar_types, None)

        self.gmm.covars_  = np.array(covars)
        self.gmm.means_   = np.array(means)
        self.gmm.weights_ = np.array(weights)


    def scores(self, t):
        # To numpy array.
        _t = np.array(t)
        # if t"s dimensional is 1, then convert to 2.
        if _t.ndim == 1:
            _t = _t.reshape([len(_t), 1])
        # every spot"s score in new GMM.
        try:
            probs = self.gmm.score_samples(_t)[1].tolist()
        except:
            params = {
                "initParams": self.gmm,
                "covars": self.gmm.covars_,
                "means": self.gmm.means_,
                "weights": self.gmm.weights_
            }
            raise PredictingError(_t, params)

        result = []
        for prob in probs:
            scores = []
            index = 0
            for n_mix in self.n_mixs:
                score = 0
                for i in range(n_mix):
                    score += prob[index]
                    index += 1
                scores.append(score)
            result.append(scores)
        return result



if __name__ == "__main__":
    _model = [{"nMix": 4, "covarianceType": "full", "count": 1000,
              "params": {"nMix": 4, "covarianceType": "full", "params": {
                  "covars": [[[1.2221303985456107]], [[0.3086663025400781]], [[1.28502444797073]], [[0.26113702790883486]]],
                  "weights": [0.23603795980927875, 0.2527552282253478, 0.2800574289988682, 0.2311493829665058],
                  "means": [[4.536022877901543], [1.4914085123695209], [3.6895831128524326], [6.571810554595958]]}}},
              {"nMix": 4, "covarianceType": "full", "count": 500,
              "params": {"nMix": 4, "covarianceType": "full", "params": {
                  "covars": [[[1.2221303985456107]], [[0.3086663025400781]], [[1.28502444797073]], [[0.26113702790883486]]],
                  "weights": [0.23603795980927875, 0.2527552282253478, 0.2800574289988682, 0.2311493829665058],
                  "means": [[4.536022877901543], [1.4914085123695209], [3.6895831128524326], [6.571810554595958]]}}}]

    t = [3.9, 1.0, 2.2]

    p = Predictor(_model)
    print p.scores(t)
