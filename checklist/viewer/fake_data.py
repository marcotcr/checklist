tag_dict = {'pos_adj': 'good', 'air_noun': 'flight', 'intens': 'very'}
raw_templates = [
    ['It', 'is', ['good', 'a:pos_adj'], ['flight', 'air_noun'], '.'],
    ['It', ['', 'a:mask'], ['very', 'a:intens'], ['good', 'pos_adj'], ['', 'mask'],'.']
]

suggests = [
    ['was', 'day'],
    ['been', 'day'],
    ['been', 'week'],
    ['was', 'time'],
    ['been', 'year'],
    ['was', 'experience'],
    ['been', 'weekend'],
    ['was', 'moment'],
    ['s', 'day'],
    ['was', 'game']
]

raw_testcases = [
    {
        "examples": [{
            "new": {
                "tokens": [
                    ["Who", "is", "taller", ",", "Mary", "or", "Heather", "?"],
                    ["Who", "is", "taller", ",", "Heather", "or", "Mary", "?"]
                ],
                "pred": "1",
                "conf": 0.7
            },
            "old": None,
            "label": "1",
            "succeed": 0,
        }],
        "tags": ["person1=Mary", "person2=Heather", "comparative=taller"],
        "succeed": 0,
    }, {
        "examples": [{
            "new": {
                "tokens": [
                    ["Who", "is", "taller", ",", "Mary", "or", "Heather", "?"],
                    ["Who", "is", "taller", ",", "Heather", "or", "Mary", "?"]
                ],
                "pred": "1",
                "conf": 0.7
            },
            "old": None,
            "label": "1",
            "succeed": 1,
        }, {
            "new": {
                "tokens": [
                    ["Who", "is", "cooler", ",", "Mary", "or", "Heather", "?"],
                    ["Who", "is", "cooler", ",", "Heather", "or", "Mary", "?"]
                ],
                "pred": "1",
                "conf": 0.7
            },
            "old": None,
            "label": "1",
            "succeed": 1,
        }],
        "tags": ["person1=Mary", "person2=Heather", "comparative=taller", "comparative=cooler"],
        "succeed": 1,
    }, {
        "examples": [{
            "new": {
                "tokens": [
                    ["Who", "is", "taller", ",", "Mary", "or", "Heather", "?"],
                    ["Who", "is", "taller", ",", "Heather", "or", "Mary", "?"]
                ],
                "pred": "0",
                "conf": 0.9
            },
            "old": {
                "tokens": [
                    ["Who", "is", "taller", ",", "Mary", "or", "Heather", "?"],
                    ["Who", "is", "taller", ",", "Mary", "or", "Heather", "?"]
                ],
                "pred": "1",
                "conf": 0.7
            },
            "succeed": 0,
            "label": None,
        }, {
            "new": {
                "tokens": [
                    ["Who", "is", "cooler", ",", "Mary", "or", "Heather", "?"],
                    ["Who", "is", "cooler", ",", "Heather", "or", "Mary", "?"]
                ],
                "pred": "1",
                "conf": 0.7
            },
            "old": {
                "tokens": [
                    ["Who", "is", "cooler", ",", "Mary", "or", "Heather", "?"],
                    ["Who", "is", "cooler", ",", "Mary", "or", "Heather", "?"]
                ],
                "pred": "0",
                "conf": 0.8
            },
            "label": None,
            "succeed": 0,
        }],
        "succeed": 0,
        "tags": ["person1=Mary", "person2=Heather", "comparative=cooler", "comparative=taller"]
    }
]

raw_testresult = {
    "name": "Change the PERSON order",
    "type": "inv",
    "expect_meta": {"expected": "equal"},
    "tags": [
        "person1=Mary",
        "person2=Heather",
        "person2=Marco",
        "comparative=cooler",
        "comparative=taller"
    ],
    "stats": {"nfailed": 10, "npassed": 20, "nfiltered": 20}
 }
