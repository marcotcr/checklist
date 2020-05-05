# CheckList
This repository contains code for testing NLP Models as described in the following paper:
>[Beyond Accuracy: Behavioral Testing of NLP models with CheckList](http://homes.cs.washington.edu/~marcotcr/checklist_acl20.pdf)  
> Marco Tulio Ribeiro, Tongshuang Wu, Carlos Guestrin, Sameer Singh
> Association for Computational Linguistics (ACL), 2020

## Table of Contents
TODO

## Installation
From pypi:  
```bash
pip install checklist
```
From source:
```bash
git clone git@github.com:marcotcr/checklist.git
cd checklist
pip install -e .
```
## Tutorials

1. [Generating data](notebooks/tutorials/1.%20Generating%20data.ipynb)
2. [Perturbing data](notebooks/tutorials/2.$20Perturbing%20data.ipynb)
3. [Test types, expectation functions, running tests](notebooks/tutorials/3.%20Test%20types,%20expectation%20functions,%20running%20tests.ipynb)
4. [The CheckList process](notebooks/tutorials/4.%20The%20CheckList%20process.ipynb)

### Replicating paper tests, or running them with new models
For all of these, you need to unpack the release data (in the main repo folder after cloning):
```bash
tar xvzf release_data.tar.gz
```
#### Sentiment Analysis
Loading the suite:
```python
suite_path = 'release_data/sentiment/sentiment_suite.pkl'
suite = TestSuite.from_file(suite_path)
```
Running tests with precomputed `bert` predictions (replace `bert` on `pred_path` with `amazon`, `google`, `microsoft`, or `roberta` for others):
```python
pred_path = 'release_data/sentiment/predictions/bert'
suite.run_from_file(pred_path, overwrite=True)
suite.summary() # or suite.visual_summary_table()
```
To test your own model, get predictions for the texts in `release_data/sentiment/tests_n500` and save them in a file where each line has 4 numbers: the prediction (0 for negative, 1 for neutral, 2 for positive) and the prediction probabilities for (negative, neutral, positive).  
Then, update `pred_path` with this file and run the lines above.


#### QQP
The same as above, except:
- set `suite_path=release_data/qqp/qqp_suite.pkl`
- set `pred_path=release_data/qqp/predictions/bert` (or roberta)
- To test your own model, get predictions for pairs in `release_data/qqp/tests_n500` (format: tsv) and output them in a file where each line has a single number: the probability that the pair is a duplicate.

#### SQuAD
The same as above, except:
- set `suite_path=release_data/squad/squad_suite.pkl`
- set `pred_path=release_data/squad/predictions/bert` (or roberta)
- To test your own model, get predictions for pairs in `release_data/squad/squad.jsonl` (format: jsonl) or `release_data/squad/squad.json` (format: json, like SQuAD dev) and output them in a file where each line has a single string: the prediction span.

##  Code snippets
### Templates
### RoBERTa suggestions

### Perturbing data for INVs and DIRs

### Custom expectation functions

### Creating and running tests
.summary
.visual_summary
### Test Suites
running, saving, sharing, etc


### Code of Conduct
[Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct)
