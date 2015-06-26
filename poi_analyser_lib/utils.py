import sys, traceback

def checkCovarianceType(covariance_type):
    import exception
    if len(covariance_type) < 1:
        raise exception.CovarianceTypeError(None)
    pre_c = covariance_type[0]
    for c_t in covariance_type:
        if c_t not in ["full", "diag", "tied", "spherical"]:
            raise exception.CovarianceTypeError(c_t)
        if pre_c != c_t:
            raise exception.CovarianceTypeError("inconformity")
        pre_c = c_t
    return covariance_type[0]

def getTracebackInfo():
    _, _, exc_traceback = sys.exc_info()
    traceback_details = []
    for filename, linenum, funcname, source in traceback.extract_tb(exc_traceback):
        t_d = "%-23s:%s '%s' in %s()" % (filename, linenum, source, funcname)
        traceback_details.append(t_d)

    return traceback_details