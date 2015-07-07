# senz.analyzer.poi.poiprob
A python project deploy in LeanEngine

FORMAT: 1A

HOST: 

# senz.analyzer.poi.poiprob

提供服务用以初始化模型，训练模型，以及用训练好的模型分类。

## Group Algorithm

Resources related to algorithm in the API.

## Init GMM [/create/]

根据输入的参数和数据库中的config初始化模型

### Create Init Models [POST]

+ X-request-Id(string): 每次请求在headers里必须带上，可以是任意string
+ covariance_type(string, optional, dafault 'full'): model covariance type
+ covariance_value(float, optional, default 1.0): model covariance value
+ n_components(int, optional, default 24): model n_components

+ Request (application/json)
    
    + Headers
            
            X-request-Id: (example)"5577f12ee4b01db3e6e6bd9f", can be any string

    + Body

            {
                "covariance_type": "full",
                "covariance_value": 1,
                "n_components": 24
            }

+ Response 201 (application/json)

        {
            "code": 0,
            "message": "success",
            "result": ""
        }


## Train GMM Randomly [/trainRandomly/]

随机训练(输入的algo_type和tag对应的)模型

### Request Train GMM Randomly [POST]

+ X-request-Id(string): 每次请求在headers里必须带上，可以是任意string
+ tag(string): model tag
+ seq_count(int): train seq length
+ covariance(float, optional, default 60000 (10 mins)): sequence covariance. And seq means are from `config` table
+ algo_type(string, optional, default 'gmm'): algrithom type

+ Request (application/json)

    + Headers
    
            X-request-Id: (example)"5577f12ee4b01db3e6e6bd9f", can be any string
    
    + Body
    
            {
                "tag": "init_model",
                "seq_count": 30,
                "covariance": 60000,
                "algo_type": "gmm"
            }
        
+ Response 201 (application/json)

        {
            "code": 0,
            "message": "success",
            "result": ""
        }
        

## Train GMM With Sequence [/trainWithSeq/]

使用输入的序列训练模型

### Train GMM with Seq [POST]

+ X-request-Id(string): 每次请求在headers里必须带上，可以是任意string
+ tag(string): model tag
+ poi_label(string): model label
+ seq(list): observation sequence, assert len(seq) >= n_component 
+ description(string): train message
+ algo_type(string, optional, default 'gmm'): algrithom type

+ Request (application/json)

    + Headers
    
            X-request-Id: (example)"5577f12ee4b01db3e6e6bd9f", can be any string

    + Body
    
            {
                "tag": "init_model",
                "poi_label": "poi#healthcare",
                "seq": [
                    1,
                    2,
                    3,
                    4,
                    5
                ],
                "description": "train demo"
            }
            
+ Response 201 (application/json)

        {
            "code": 0,
            "message": "success",
            "result": ""
        }

        
## Train GMM [/train/]

使用数据库中的数据训练模型

### Train GMM with seq in db [POST]

+ X-request-Id(string): 每次请求在headers里必须带上，可以是任意string
+ tag(string): model tag
+ poi_label(string): model label
+ description(string): train message
+ seq_type(int, optional, default 0): 0 代表用未被训练的数据训练，1 代表用所有数据训练
+ algo_type(string, optional, default 'gmm'): algrithom type

+ Request (application/json)

    + Headers
    
            X-request-Id: (example)"5577f12ee4b01db3e6e6bd9f", can be any string

    + Body

            {
                "tag": "init_model",
                "poi_label": "poi#healthcare",
                "description": "train demo"
            }
            
+ Response 201 (application/json)

        {
            "code": 0,
            "message": "success",
            "result": ""
        }
        

## Classify [/classify/]

用已训练好的模型对输入seq进行分类

### classify seq using models [POST]

+ X-request-Id(string): 每次请求在headers里必须带上，可以是任意string
+ tag(string): model tag
+ seq(list): observation sequence
+ algo_type(string, optional, default 'gmm'): algrithom type
+ Request (application/json)

    + Headers
    
            X-request-Id: (example)"5577f12ee4b01db3e6e6bd9f", can be any string

    + Body
    
            {
                "tag": "random_train",
                "seq": [ 3600000]
            }
            
+ Response 201 (application/json)

        {
            "code": 0,
            "message": "success",
            "result": ""
        }

