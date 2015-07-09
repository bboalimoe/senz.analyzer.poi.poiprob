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


def generate_train_dataset(init_means, seq_count, covariance):
    '''
    generage train dataset for gmm, size is seq_count

    Parameters
    ----------
    init_means: list
      every elem represent one mean
    seq_count: int
    covariance: double

    Returns
    -------
    result: list
      len(result) == seq_count
    '''
    result = []

    for mean in init_means:
        result += ss.norm.rvs(loc=mean, scale=covariance, size=seq_count).astype(int).tolist()
    random.shuffle(result)

    return result[:seq_count]

def plot_date(init_means, seq_count, covariance):
    '''plot date generate by func `generate_train_dateset`

    Parameters
    ----------
    init_means: list
      every elem represent one mean
    seq_count: int
    covariance: double
    '''
    import arrow
    from matplotlib.dates import DateFormatter, MinuteLocator
    import matplotlib.pyplot as plt
    import numpy as np

    loc = MinuteLocator(interval=30)
    formatter = DateFormatter('%H:%M:%S')

    result = generate_train_dataset(init_means, seq_count, covariance)
    dates = [arrow.get(e/1000).datetime for e in result]
    s = np.array([1]*len(dates))

    fix, ax = plt.subplots()
    plt.plot_date(dates, s)
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(formatter)

    plt.show()


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

    print('-'*20)
    print(generate_train_dataset([-10,10], 5, 1))
