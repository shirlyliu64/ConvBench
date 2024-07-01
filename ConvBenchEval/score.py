import argparse
import yaml
import os
import re
import string
import numpy as np
import random


def extract_rate(evaluation):
    analysis_result = re.search('Rating:(.*)', evaluation)
    if analysis_result== None:
        analysis_string = '0'
    else:
        analysis_string = analysis_result.group(1).strip()
        analysis_string = analysis_string.strip(string.punctuation)
    if analysis_string not in ['A','B']:
        analysis_string = 'C' 
        
    return analysis_string

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vqa_model', type=str, default='blip2_t5_xxl', help='model as Answerer.')
    parser.add_argument('--file_name', type=str, default='blip2_t5_xxl', help='model as Answerer.')
    args = parser.parse_args()
    return args

args = parse_args()
vqa_model = args.vqa_model
file_name = args.file_name
first_turn_rating = 0
second_turn_rating = 0
third_turn_rating = 0
overall_prediction = 0
save_path = "../result/" + vqa_model +"/" + file_name
pairwise = np.load("./pairwise.npy")    
TEST_SUM = 577
i = 0
for id in range(1,579): 
    position = pairwise[id-1]
    result_path = os.path.join(save_path, '{}.yaml'.format(str(id)))

    if os.path.exists(result_path) == False:
        first = 0
        second = 0
        third = 0
        overall = 0  
    else:
        i+=1
        with open(result_path, "r") as file:
            data_i = yaml.safe_load(file)
        first = data_i['first_turn_rating']
        second = data_i['second_turn_rating']
        third = data_i['third_turn_rating']
        overall = data_i['overall_prediction']


        if first not in ['A','B']:
            first = extract_rate(data_i['first_turn_evaluation'])
        if second not in ['A','B']:
            second = extract_rate(data_i['second_turn_evaluation'])
        if third not in ['A','B']:
            third = extract_rate(data_i['third_turn_evaluation'])
        if overall not in ['A','B']:
            overall = extract_rate(data_i['overall_evalaution'])

        pairwise_dict = dict()
        if position == 0:
            #pairwise_dict["A"] = "model_answer"
            #pairwise_dict["B"] = "human_answer"
            if first == "A":
                first_turn_rating +=1
            if second == "A":
                second_turn_rating +=1
            if third == "A":
                third_turn_rating +=1
            if overall == "A":
                overall_prediction +=1


        if position == 1:
            #pairwise_dict["A"] = "human_answer"
            #pairwise_dict["B"] = "model_answer"   
            if first == "B":
                first_turn_rating +=1
            if second == "B":
                second_turn_rating +=1
            if third == "B":
                third_turn_rating +=1
            if overall == "B":
                overall_prediction +=1

first_turn_rating = first_turn_rating/TEST_SUM
second_turn_rating = second_turn_rating/TEST_SUM
third_turn_rating = third_turn_rating/TEST_SUM
overall_prediction = overall_prediction/TEST_SUM

print("first_turn_rating", first_turn_rating)
print("second_turn_rating", second_turn_rating)
print("third_turn_rating", third_turn_rating)
print("overall_prediction", overall_prediction)
