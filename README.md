# Humour Detector

Humour detector is a bot trained on [this dataset](https://www.kaggle.com/datasets/deepcontractor/200k-short-texts-for-humor-detection). It achieved ~94% testing accuracy and took about 14 minutes to train.

Upon using cross-validation to attempt to benchmark the neural network against a few other classifiers, it appears a linear support vector model would be slightly more accurate and require much less time to train, although I haven't implemented this yet.
