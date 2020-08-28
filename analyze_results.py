import pandas as pd
import numpy as np
import extract_info
import validate_preds
import seaborn as sns
import matplotlib.pyplot as plt

'''
Analyze results of predictions.
'''

df = pd.read_csv("report_text_2.csv")

def gen_merged_df(df):
    df = extract_info.get_snippets(df, 'SITUATION')
    df = extract_info.get_snippets(df, 'FORECAST')
    df = extract_info.prelim_cleaning(df)
    return validate_preds.make_merged_df(df)
     


def gen_results_df(df, loc_matching=False):
    
    #df['most_gran_data'] = df.apply(lambda x: validate_preds.granular_corroborate(x.FORECAST, x.SIT_1, x.SIT_2, match_type='exact'), axis=1)
    #print('col is', df['most_gran_data'])
    #df['most_gran_results'] = df['most_gran_data'].apply(lambda most_gran_data: most_gran_data[0])
    #df['most_gran_results_sig_preds'] = df['most_gran_data'].apply(lambda most_gran_data: most_gran_data[1])
    df['most_gran_results'] = df.apply(lambda x: validate_preds.granular_corroborate(x.FORECAST, x.SIT_1, x.SIT_2, match_type='exact')[0], axis=1)
    #print('col is: ', df['most_gran_results'])
    df['most_gran_results_sig_preds'] = df.apply(lambda x: validate_preds.granular_corroborate(x.FORECAST, x.SIT_1, x.SIT_2, match_type='exact')[1], axis=1)
    df['most_gran_results_pct_true'] = df.apply(lambda x: validate_preds.percent_result_type(x.most_gran_results, True), axis=1)
    df['most_gran_results_pct_false'] = df.apply(lambda x: validate_preds.percent_result_type(x.most_gran_results, False), axis=1)
    df['most_gran_results_pct_no_match'] = df.apply(lambda x: validate_preds.percent_result_type(x.most_gran_results, "False - No match"), axis=1)

    #df['any_by_place_data'] = df.apply(lambda x: validate_preds.results_by_place(x.FORECAST, x.SIT_1, x.SIT_2), axis=1)
    df['any_by_place'] = df.apply(lambda x: validate_preds.results_by_place(x.FORECAST, x.SIT_1, x.SIT_2)[0], axis=1)
    df['any_by_place_sig_preds'] = df.apply(lambda x: validate_preds.results_by_place(x.FORECAST, x.SIT_1, x.SIT_2)[1], axis=1)
    df['any_by_place_pct_true'] = df.apply(lambda x: validate_preds.percent_result_type(x.any_by_place, True), axis=1)
    df['any_by_place_pct_false'] = df.apply(lambda x: validate_preds.percent_result_type(x.any_by_place, False), axis=1)
    df['any_by_place_pct_no_match'] = df.apply(lambda x: validate_preds.percent_result_type(x.any_by_place, "False - No match"), axis=1)

    #df['any_by_place'] = df['any_by_place_data'].apply(lambda any_by_place_data: any_by_place_data[0])
    #df['any_by_place_sig_preds'] = df['any_by_place_data'].apply(lambda any_by_place_data: any_by_place_data[1])

    
    df['sentence_by_gen_stage_data'] = df.apply(lambda x: validate_preds.results_by_sentence(x.FORECAST, x.SIT_1, x.SIT_2), axis=1)
    df['sentence_by_gen_stage'] = df.apply(lambda x: validate_preds.results_by_sentence(x.FORECAST, x.SIT_1, x.SIT_2)[0], axis=1)
    df['sentence_by_gen_stage_sig_preds'] = df.apply(lambda x: validate_preds.results_by_sentence(x.FORECAST, x.SIT_1, x.SIT_2)[1], axis=1)
    df['sentence_by_gen_stage_pct_true'] = df.apply(lambda x: validate_preds.percent_result_type(x.sentence_by_gen_stage, True), axis=1)
    df['sentence_by_gen_stage_pct_false'] = df.apply(lambda x: validate_preds.percent_result_type(x.sentence_by_gen_stage, False), axis=1)
    df['sentence_by_gen_stage_pct_no_match'] = df.apply(lambda x: validate_preds.percent_result_type(x.sentence_by_gen_stage, "False - No match"), axis=1)

    #df['sentence_by_gen_stage'] = df['sentence_by_gen_stage_data'].apply(lambda sentence_by_gen_stage_data: sentence_by_gen_stage_data[0])
    #df['sentence_by_gen_stage_sig_preds'] = df['sentence_by_gen_stage_data'].apply(lambda sentence_by_gen_stage_data: sentence_by_gen_stage_data[1])
    #df['sentence_by_gen_stage'] = df.apply(lambda x: validate_preds.results_by_sentence(x.FORECAST, x.SIT_1, x.SIT_2)[1], axis=1)
    #df['sent_by_gen_stage_pct'] = df.apply(lambda x: validate_preds.percent_true(x.sentence_by_gen_stage), axis=1)
    #df.drop(columns=['most_gran_data', 'any_by_place_data', 'any_by_gen_stage_data'], inplace=True)
    return df

def analyze_results(df, loc_matching=False):
    df['total_true_any'] = df.apply(lambda x: count_true(x.any_by_place), axis=1)
    df['total_no_match_any'] = df.apply(lambda x: count_false_no_match(x.any_by_place), axis=1)
    df['total_false_any'] = df.apply(lambda x: count_false(x.any_by_place), axis=1)

    df['total_true_gen'] = df.apply(lambda x: count_true(x.sentence_by_gen_stage), axis=1)
    df['total_no_match_gen'] = df.apply(lambda x: count_false_no_match(x.sentence_by_gen_stage), axis=1)
    df['total_false_gen'] = df.apply(lambda x: count_false(x.sentence_by_gen_stage), axis=1)

    df['total_true_exact'] = df.apply(lambda x: count_true(x.most_gran_results), axis=1)
    df['total_no_match_exact'] = df.apply(lambda x: count_false_no_match(x.most_gran_results), axis=1)
    df['total_false_exact'] = df.apply(lambda x: count_false(x.most_gran_results), axis=1)

    return df

def confusion_matrix(df, results_col, sig_preds_col):
    '''
    Analyzes false and true positives and negatives.
    '''
    pred_correct = np.concatenate(df[results_col].reset_index(drop=True))
    pred_sig_pred = np.concatenate(df[sig_preds_col].reset_index(drop=True)) 
    print('len 1: ', len(pred_correct))
    print('len 2: ', len(pred_sig_pred))
    conf_matrix = pd.crosstab(pred_sig_pred, pred_correct, rownames=['sig. event predicted'], 
                                colnames=['pred result'])
    sns.heatmap(conf_matrix, annot=True, fmt='d')

def raw_counts_graph(df):
    fig, axes = plt.subplots(nrows=3, ncols=1, sharex=True, figsize=(10, 10))
    df.groupby('YEAR').total_true_any.sum().plot(ax=axes[0])
    df.groupby('YEAR').total_false_any.sum().plot(ax=axes[0])
    df.groupby('YEAR').total_no_match_any.sum().plot(ax=axes[0])

    df.groupby('YEAR').total_true_gen.sum().plot(ax=axes[1])
    df.groupby('YEAR').total_false_gen.sum().plot(ax=axes[1])
    df.groupby('YEAR').total_no_match_gen.sum().plot(ax=axes[1])

    df.groupby('YEAR').total_true_exact.sum().plot(ax=axes[2])
    df.groupby('YEAR').total_false_exact.sum().plot(ax=axes[2])
    df.groupby('YEAR').total_no_match_exact.sum().plot(ax=axes[2])
    plt.setp(axes, ylim=(0, 1450))
    axes[0].set(ylabel='any locusts by location')
    axes[1].set(ylabel='general stage by sentence')
    axes[2].set(ylabel='exact match - granular')
    plt.suptitle('Total Prediction Counts by Type')

def percent_type_graph(df):
    fig, axes = plt.subplots(nrows=3, ncols=1, sharex=True, figsize=(10, 10))
    df.groupby('YEAR').any_by_place_pct_true.mean().plot(ax=axes[0])
    df.groupby('YEAR').any_by_place_pct_false.mean().plot(ax=axes[0])
    df.groupby('YEAR').any_by_place_pct_no_match.mean().plot(ax=axes[0])

    df.groupby('YEAR').sentence_by_gen_stage_pct_true.mean().plot(ax=axes[1])
    df.groupby('YEAR').sentence_by_gen_stage_pct_false.mean().plot(ax=axes[1])
    df.groupby('YEAR').sentence_by_gen_stage_pct_no_match.mean().plot(ax=axes[1])

    df.groupby('YEAR').most_gran_results_pct_true.mean().plot(ax=axes[2])
    df.groupby('YEAR').most_gran_results_pct_false.mean().plot(ax=axes[2])
    df.groupby('YEAR').most_gran_results_pct_no_match.mean().plot(ax=axes[2])
    plt.setp(axes, ylim=(0, 1.0))
    axes[0].set(ylabel='any locusts by location')
    axes[1].set(ylabel='general stage by sentence')
    axes[2].set(ylabel='exact match - granular')
    plt.suptitle('Percent of Total Predictions by Type')

def any_true(results_list):
    return any(result == True for result in results_list)


def count_true(results_list):
    '''
    Gives a raw count of true predictions.
    '''
    return sum([result for result in results_list if result == True])

def count_false_no_match(results_list):
    return len([result for result in results_list if result == "False - No match"])

def count_false(results_list):
    '''
    count all false, including no match
    '''
    return len([result for result in results_list if result != True])





