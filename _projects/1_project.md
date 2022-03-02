---
layout: post
title: Heuristic Search and Natural Language Processing
# description: description of the short project which is long enough
---

Natural language processing (NLP) tasks such as identifying the polarity of a text, natural language inference, and named entity recognition can be defined as supervised learning problems. As expected, different Machine Learning (ML) techniques have been incorporated into the NLP field. Among these, one can find the usage of ensembles to improve the performance of single classifiers. However, in NLP, there is an extra ingredient to consider, which is the pre-trained models. One is faced with selecting the ML algorithms, the procedure to combine them, and the pre-trained models.  Deciding the components that are the more suitable for solving a problem is a time-consuming and challenging task that depends on the user's expertise; this decision problem gets more severe when the number of algorithms, combination schemes, and models increases, making it unfeasible to explore all the combinations. Under these conditions, one relies on search algorithms to choose the combination of these components that produce the best model. On the other hand, it is essential to mention that search algorithms are also used within the elements, e.g., they are used to estimate the parameters of the pre-trained models, estimate the weights of an artificial neural network or search for the text transformations and tokenizers used on the text. 

This research line aims to understand and develop algorithms capable of selecting the combination of pre-trained models, ML techniques, and the procedure to combine them given an NLP task. As one would imagine, there are a plethora of research projects that fit in this research avenue; however, the interest is on the following specific project that has as a starting point the research described in [EvoMSA: A Multilingual Evolutionary Approach for Sentiment Analysis](https://ieeexplore.ieee.org/abstract/document/8956106).