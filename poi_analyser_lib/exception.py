from utils import getTracebackInfo

__all__ = ["FittingError", "ModelParamKeyError", "ModelInitError", "PredictingError", "CovarianceTypeError"]

class PoiMiddlewareError(Exception):
    def __init__(self):
        self.traceback = getTracebackInfo()

class FittingError(PoiMiddlewareError):
    def __init__(self, _x, _model):
        PoiMiddlewareError.__init__(self)
        self.X = _x
        self.model = _model

    def __str__(self):
        return "<%s> caused FITTING failed, input X: %s, input Model: %s\n Traceback: %s" % \
               (self.__class__.__name__, self.X, self.model, self.traceback)

class PredictingError(PoiMiddlewareError):
    def __init__(self, _t, _model):
        PoiMiddlewareError.__init__(self)
        self.T = _t
        self.model = _model

    def __str__(self):
        return "<%s> caused Predicting failed, input T: %s, input Model: %s\n Traceback: %s" % \
               (self.__class__.__name__, self.T, self.model, self.traceback)

class ModelParamKeyError(PoiMiddlewareError):
    def __init__(self, key):
        PoiMiddlewareError.__init__(self)
        self.key = key

    def __str__(self):
        return "<%s> caused KEY error, there is no key named %s\n Traceback: %s" % \
               (self.__class__.__name__, self.key, self.traceback)

class CovarianceTypeError(PoiMiddlewareError):
    def __init__(self, covariance_type):
        PoiMiddlewareError.__init__(self)
        self.covarianceType = covariance_type

    def __str__(self):
        if self.covarianceType is None:
            return "<%s> caused COVARIANCE TYPE error, there is no specific covariance type\n Traceback: %s" % \
                   (self.__class__.__name__, self.traceback)
        elif self.covarianceType == "inconformity":
            return "<%s> caused COVARIANCE TYPE error, inconformity of covariance types in the list occurred\n Traceback: %s" % \
                   (self.__class__.__name__, self.traceback)
        else:
            return "<%s> caused COVARIANCE TYPE error, there is no covariance type named %s\n Traceback: %s" % \
                   (self.__class__.__name__, self.covarianceType, self.traceback)

class ModelInitError(PoiMiddlewareError):
    def __init__(self, n_component, covariance_type, n_iter):
        PoiMiddlewareError.__init__(self)
        self.nComponent = n_component
        self.covarianceType = covariance_type
        self.nIter = n_iter

    def __str__(self):
        return "<%s> caused some errors occurred when gmm init, nComponent: %s, CovarianceType: %s, nIter: %s\n Traceback: %s" % \
               (self.__class__.__name__, self.nComponent, self.covarianceType, self.nIter, self.traceback)
