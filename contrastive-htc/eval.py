#!/usr/bin/env python
# coding:utf-8

import numpy as np


def _precision_recall_f1(right, predict, total):
    """
    :param right: int, the count of right prediction
    :param predict: int, the count of prediction
    :param total: int, the count of labels
    :return: p(precision, Float), r(recall, Float), f(f1_score, Float)
    """
    p, r, f = 0.0, 0.0, 0.0
    if predict > 0:
        p = float(right) / predict
    if total > 0:
        r = float(right) / total
    if p + r > 0:
        f = p * r * 2 / (p + r)
    return p, r, f


def evaluate(epoch_predicts, epoch_labels, id2label, threshold=0.5, top_k=None):
    """
    :param epoch_labels: List[List[int]], ground truth, label id
    :param epoch_predicts: List[List[Float]], predicted probability list
    :param vocab: data_modules.Vocab object
    :param threshold: Float, filter probability for tagging
    :param top_k: int, truncate the prediction
    :return:  confusion_matrix -> List[List[int]],
    Dict{'precision' -> Float, 'recall' -> Float, 'micro_f1' -> Float, 'macro_f1' -> Float}
    """
    assert len(epoch_predicts) == len(epoch_labels), 'mismatch between prediction and ground truth for evaluation'
    # label2id = vocab.v2i['label']
    # id2label = vocab.i2v['label']
    # epoch_gold_label = list()
    # # get id label name of ground truth
    # for sample_labels in epoch_labels:
    #     sample_gold = []
    #     for label in sample_labels:
    #         assert label in id2label.keys(), print(label)
    #         sample_gold.append(id2label[label])
    #     epoch_gold_label.append(sample_gold)

    epoch_gold = epoch_labels

    # initialize confusion matrix
    confusion_count_list = [[0 for _ in range(len(id2label))] for _ in range(len(id2label))]
    right_count_list = [0 for _ in range(len(id2label))]
    gold_count_list = [0 for _ in range(len(id2label))]
    predicted_count_list = [0 for _ in range(len(id2label))]

    for sample_predict, sample_gold in zip(epoch_predicts, epoch_gold):
        np_sample_predict = np.array(sample_predict, dtype=np.float32)
        sample_predict_descent_idx = np.argsort(-np_sample_predict)
        sample_predict_id_list = []
        if top_k is None:
            top_k = len(sample_predict)
        for j in range(top_k):
            if np_sample_predict[sample_predict_descent_idx[j]] > threshold:
                sample_predict_id_list.append(sample_predict_descent_idx[j])

        for i in range(len(confusion_count_list)):
            for predict_id in sample_predict_id_list:
                confusion_count_list[i][predict_id] += 1

        # count for the gold and right items
        for gold in sample_gold:
            gold_count_list[gold] += 1
            for label in sample_predict_id_list:
                if gold == label:
                    right_count_list[gold] += 1

        # count for the predicted items
        for label in sample_predict_id_list:
            predicted_count_list[label] += 1

        #print labels
        print('**sample gold**')
        gold_labels = []
        for gold in sample_gold:
            gold_labels.append(id2label[gold])
        print(gold_labels)
        
        print('**sample predict id list**')
        sample_labels = []
        for sample in sample_predict_id_list:
            sample_labels.append(id2label[sample])
        print(sample_labels)

        
    precision_dict = dict()
    recall_dict = dict()
    fscore_dict = dict()
    right_total, predict_total, gold_total = 0, 0, 0

    for i, label in id2label.items():
        label = label + '_' + str(i)
        precision_dict[label], recall_dict[label], fscore_dict[label] = _precision_recall_f1(right_count_list[i],
                                                                                             predicted_count_list[i],
                                                                                             gold_count_list[i])
        right_total += right_count_list[i]
        gold_total += gold_count_list[i]
        predict_total += predicted_count_list[i]

    # Macro-F1
    precision_macro = sum([v for _, v in precision_dict.items()]) / len(list(precision_dict.keys()))
    recall_macro = sum([v for _, v in recall_dict.items()]) / len(list(precision_dict.keys()))
    macro_f1 = sum([v for _, v in fscore_dict.items()]) / len(list(fscore_dict.keys()))
    # Micro-F1
    precision_micro = float(right_total) / predict_total if predict_total > 0 else 0.0
    recall_micro = float(right_total) / gold_total
    micro_f1 = 2 * precision_micro * recall_micro / (precision_micro + recall_micro) if (precision_micro + recall_micro) > 0 else 0.0

    return {'precision': precision_micro,
            'recall': recall_micro,
            'micro_f1': micro_f1,
            'macro_f1': macro_f1,
            'full': [precision_dict, recall_dict, fscore_dict, right_count_list, predicted_count_list, gold_count_list]}
