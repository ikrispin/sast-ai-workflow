import math
from decimal import Decimal

from Utils.config_utils import load_config


def count_predicted_values(data):
    positives = set()
    negatives = set()
    for (issue_id, llm_text, metric_ar) in data:
        if "not a false positive" in str(llm_text).lower():
            positives.add(issue_id)
        else:
            negatives.add(issue_id)
    return positives, negatives

def count_actual_values(data, ground_truth):
    positives = set()
    negatives = set()
    
    for (issue_id, _, _) in data:
        if not issue_id in ground_truth:
            print(f"WARNING: Issue ID {issue_id} does not exist in the human verified excel sheet")
        elif ground_truth[issue_id] == 'y':
            negatives.add(issue_id)
        else:
            positives.add(issue_id)
    return positives, negatives

def calculate_confusion_matrix_metrics(actual_true_positives, actual_false_positives, predicted_true_positives, predicted_false_positives):
    tp = len(actual_true_positives & predicted_true_positives)      # Both human and AI labeled as real issue
    tn = len(actual_false_positives & predicted_false_positives)    # Both human and AI labeled as not real issue
    fp = len(predicted_true_positives - actual_true_positives)      # AI falsely labeled as real issue
    fn = len(actual_true_positives - predicted_true_positives)      # AI falsely labeled as not real issue
   
    return tp, tn, fp, fn

def get_metrics(tp, tn, fp, fn):
    EPSILON = 1e-11 
    accuracy = (tp + tn) / (tp + tn + fp + fn + EPSILON)
    recall = tp / (tp + fn + EPSILON)
    precision = tp / (tp + fp + EPSILON)
    f1_score = 2 * precision * recall / (precision + recall + EPSILON)
    return accuracy, recall, precision, f1_score

def get_numeric_value(value):
    return 0 if math.isnan(value) or math.isinf(value) else value

def get_percentage_value(n):
    n = get_numeric_value(n)
    n = n if isinstance(n, Decimal) else Decimal(str(n))
    return round(n, 2) * 100

def get_predicted_summary(data):
    summary = []
    config = load_config()

    for _, (issue, summary_info) in enumerate(data):
        ar = 0
        if summary_info and 'answer_relevancy' in summary_info.metrics:
            ar = get_percentage_value(summary_info.metrics['answer_relevancy'])
        llm_response = summary_info.critique_response if config["USE_CRITIQUE_AS_FINAL_RESULTS"] else summary_info.llm_response
        summary.append((issue.id, llm_response, ar))
    return summary
