---
layout: post
title: Searching on the space of text representations
description: Searching on the space of text representations
---

[EvoMSA](https://ieeexplore.ieee.org/document/8956106) combines text representations using a stacking generalization approach. There are five different text representations: a BoW using the training set, a model trained with a human-annotated dataset, a thumbs up-down lexicon, a self-supervised approach on emojis, and FastText representation.  

The aim is to increase the number of text representations and analyze the impact these representations have on the performance of the text classifier on different tasks. 

It is worth mentioning that the procedure used to increment the text representations follows the development of the human-annotated model. The model is trained on a dataset that corresponds to a polarity task where the aim is to predict the polarity (positive, neutral o negative) of a given text. A source of information to find similar datasets is the SemEval forum. 

Once various datasets have been collected, it is time to measure the models' impact on text categorization tasks which can be done by using search algorithms and recording the performance on the tasks.