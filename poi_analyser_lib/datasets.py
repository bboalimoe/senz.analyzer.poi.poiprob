import numpy as np
import random
import scipy.stats as ss

def standardNormalRand(range_x, range_y):
    '''
    Standard Normal Rand
    Generate a standard normal rand number,
    the X axis ranges from -1*range_x to range_x,
    the Y axis ranges from -1*range_y to range_y
    '''
    while True:
        X = random.uniform((-1)*range_x, range_x)
        Y = random.uniform(0.0, range_y)
        if Y < ss.norm.pdf(X):
            return abs(X)



class Dataset(object):

    poi_distribution = {
        "chineseRestaurant": [
            {
                "mean": 12*60*60*1000,
                "coviariance": 1,
                "weight": 0.5
            },
            {
                "mean": 18*60*60*1000,
                "coviariance": 1,
                "weight": 0.5
            }
        ]
    }


    def __init__(self, obs, location_type):
        self.obs = obs
        self.locationType = location_type

    def getDataset(self):
        dataset = []
        for ob in self.obs:
            dataset.append(self.locationType.index(ob["poiType"]))
        return dataset


if __name__ == "__main__":
    obs = [
        {"poiType": "restaurant"},
        {"poiType": "restaurant"},
        {"poiType": "restaurant"},
        {"poiType": "street"},
    ]

    location_type = ["restaurant", "street"]

    d = Dataset(obs, location_type)

    print d.getDataset()

