candidate_dict = {
    "comparative" : ['better', 'worse', 'older', 'younger', 'smarter', 'stronger', 'weaker', 'happier', 'taller', 'cooler', 'happier'],
    "country"     : ["the US", "China", ""],
    "city"        : ["Beijing", "Hong Kong", "Seattle", "London"],
    "person"      : ["Marco", "Julia", "Sherry", "Jeff", "Carlos"],
    "pronun"      : ["I", "you"]
}

raw_examples = [
    {
        "instance": [
            {"target": "Q1", "text": "Who is taller, Mary or Heather?"},
            {"target": "Q2", "text": "Who is taller, Heather or Mary?"}
        ], 
        "pred": "1",
        "conf": 0.5,
        "expect": "0",
        "status": "fail",
        "tags": ["person1=Mary", "person2=Heather", "comparative=taller"]
    }, {
        "instance": [
            {"target": "Q1", "text": "Who is cooler, Mary or Heather?"},
            {"target": "Q2", "text": "Who is cooler, Heather or Mary?"}
        ], 
        "pred": "1",
        "conf": 0.5,
        "expect": "0",
        "status": "fail",
        "tags": ["person1=Mary", "person2=Heather", "comparative=cooler"]
    }, {
        "instance": [
            {"target": "Q1", "text": "Who is cooler, Mary or Marco?"},
            {"target": "Q2", "text": "Who is cooler, Marco or Mary?"}
        ], 
        "pred": "0",
        "expect": "0",
        "status": "success",
        "tags": ["person1=Mary", "person2=Marco", "comparative=cooler"]
    }, {
        "instance": [
            {"target": "Q1", "text": "Who is taller, Mary or Marco?"},
            {"target": "Q2", "text": "Who is taller, Marco or Mary?"}
        ], 
        "pred": "0",
        "conf": 0.5,

        "expect": "0",
        "status": "success",
        "tags": ["person1=Mary", "person2=Marco", "comparative=taller"]
    }, {
        "instance": [
            {
                "target": "Q1", 
                "text": "Who is taller, Mary or Heather?",
                "oldText": "Who is cooler, Mary or Heather?"
            },{
                "target": "Q2", 
                "text": "Who is taller, Heather or Mary?",
                "oldText": "Who is cooler, Heather or Mary?"
            }
        ], 
        "pred": "1",
        "conf": 0.5,
        "expect": "0",
        "status": "fail",
        "tags": ["person1=Mary", "person2=Heather", "comparative=taller"]
    }, {
        "instance": [
            {
                "target": "Q1", 
                "text": "Who is cooler, Heather or Mary?",
                "oldText": "Who is cooler, Mary or Heather?"
            },{
                "target": "Q2", 
                "text": "Who is cooler, Heather or Mary?",
                "oldText": "Who is cooler, Heather or Mary?"
            }
        ], 
        "pred": "1",
        "conf": 0.5,
        "expect": "0",
        "status": "fail",
        "tags": ["person1=Mary", "person2=Heather", "comparative=cooler"]
    }
]