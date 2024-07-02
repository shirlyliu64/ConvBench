import argparse
import pprint
import openai
import numpy as np
import json
import os
import time
import collections
import prompts
import copy
import tqdm
import pandas as pd
from PIL import Image
import base64
from openai import OpenAI
import time
import re
from uuid import uuid4
import pdb
import os.path as osp
import random
import yaml

os.environ["OPENAI_API_KEY"] = "xxxxxxxxxxxxxxxxxx"
os.environ["OPENAI_BASE_URL"] = "https://api.openai-sb.com/v1"

# Pairwise with reference (ref, cand A, cand B)
_PROMPT_SYSTEM_PAIRWISE_V1_MT_first_turn, _PROMPT_USER_PAIRWISE_V1_MT_first_turn, _PROMPT_ASSISTANT_PAIRWISE_V1_MT_first_turn  = (
    prompts._PROMPT_SYSTEM_PAIRWISE_V1_MT_first_turn,
    prompts._PROMPT_USER_PAIRWISE_V1_MT_first_turn,
    prompts._PROMPT_ASSISTANT_PAIRWISE_V1_MT_first_turn
)

_PROMPT_SYSTEM_PAIRWISE_V1_MT_second_turn, _PROMPT_USER_PAIRWISE_V1_MT_second_turn, _PROMPT_ASSISTANT_PAIRWISE_V1_MT_second_turn  = (
    prompts._PROMPT_SYSTEM_PAIRWISE_V1_MT_second_turn,
    prompts._PROMPT_USER_PAIRWISE_V1_MT_second_turn,
    prompts._PROMPT_ASSISTANT_PAIRWISE_V1_MT_second_turn
)

_PROMPT_SYSTEM_PAIRWISE_V1_MT_third_turn, _PROMPT_USER_PAIRWISE_V1_MT_third_turn, _PROMPT_ASSISTANT_PAIRWISE_V1_MT_third_turn  = (
    prompts._PROMPT_SYSTEM_PAIRWISE_V1_MT_third_turn,
    prompts._PROMPT_USER_PAIRWISE_V1_MT_third_turn,
    prompts._PROMPT_ASSISTANT_PAIRWISE_V1_MT_third_turn
)

_PROMPT_SYSTEM_PAIRWISE_V1_MT_overall_conversation, _PROMPT_USER_PAIRWISE_V1_MT_overall_conversation, _PROMPT_ASSISTANT_PAIRWISE_V1_MT_overall_conversation  = (
    prompts._PROMPT_SYSTEM_PAIRWISE_V1_MT_overall_conversation,
    prompts._PROMPT_USER_PAIRWISE_V1_MT_overall_conversation,
    prompts._PROMPT_ASSISTANT_PAIRWISE_V1_MT_overall_conversation
)

# Answer extraction
_PROMPT_SYSTEM_ANSWER_EXTRACTION_V1, _ICL_SYSTEM_ANSWER_EXTRACTION_V1 = (
    prompts._PROMPT_SYSTEM_ANSWER_EXTRACTION_V1,
    prompts._ICL_SYSTEM_ANSWER_EXTRACTION_V1
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vqa_model', type=str, default='blip2_t5_xxl', help='model as Answerer.')
    args = parser.parse_args()
    return args

def encode_image_file_to_base64(image_path):
    if image_path.endswith('.png'):
        tmp_name = f'{timestr(second=True)}.jpg'
        img = Image.open(image_path)
        img.save(tmp_name)
        result = encode_image_file_to_base64(tmp_name)
        os.remove(tmp_name)
        return result
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
        
    encoded_image = base64.b64encode(image_data)
    return encoded_image.decode('utf-8')


def encode_image_to_base64(img, target_size=-1):
    # if target_size == -1, will not do resizing
    # else, will set the max_size ot (target_size, target_size)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    tmp = osp.join('/tmp', str(uuid4()) + '.jpg')
    if target_size > 0:
        img.thumbnail((target_size, target_size))
    img.save(tmp)
    ret = encode_image_file_to_base64(tmp)
    os.remove(tmp)
    return ret


def generate_request(turn_str,
                     image_path, 
                     image_description, 
                     cur_first_turn_instruction, 
                     cur_first_turn_response_A, 
                     cur_first_turn_response_B, 
                     cur_second_turn_instruction, 
                     cur_second_turn_response_A, 
                     cur_second_turn_response_B, 
                     cur_third_turn_instruction,
                     cur_third_turn_response_A, 
                     cur_third_turn_response_B,
                     cur_third_turn_demands=None,
                     perception_prediction=None,
                     reasoning_prediction=None,
                     composition_prediction=None):
    #base64_image = encode_image_to_base64(Image.open(image_path),768)
    global _PROMPT_SYSTEM_PAIRWISE_V1_MT_first_turn, _PROMPT_USER_PAIRWISE_V1_MT_first_turn, _PROMPT_ASSISTANT_PAIRWISE_V1_MT_first_turn
    global _PROMPT_SYSTEM_PAIRWISE_V1_MT_second_turn, _PROMPT_USER_PAIRWISE_V1_MT_second_turn, _PROMPT_ASSISTANT_PAIRWISE_V1_MT_second_turn
    global _PROMPT_SYSTEM_PAIRWISE_V1_MT_third_turn, _PROMPT_USER_PAIRWISE_V1_MT_third_turn, _PROMPT_ASSISTANT_PAIRWISE_V1_MT_third_turn
    global _PROMPT_SYSTEM_PAIRWISE_V1_MT_overall_conversation, _PROMPT_USER_PAIRWISE_V1_MT_overall_conversation, _PROMPT_ASSISTANT_PAIRWISE_V1_MT_overall_conversation


    turn_string = turn_str.split("_")[1] + " " + turn_str.split("_")[2]

    if turn_str=='_overall_conversation':
        system_p, user_p, assistant_p = _PROMPT_SYSTEM_PAIRWISE_V1_MT_overall_conversation, _PROMPT_USER_PAIRWISE_V1_MT_overall_conversation, _PROMPT_ASSISTANT_PAIRWISE_V1_MT_overall_conversation
        user_content = ('OK. Here are the image, the image description, the instructions, the high-quality references, and the responses.\nImage context: {}\n\n<|The Start of Assistant A’s Conversation with User|>\n### The first turn question from user:\n{}\n\n### The first turn response from Assistant A:\n{}\n\n### The second turn question from user:\n{}\n\n### The second turn response from Assistant A:\n{}\n\n### The third question from user:\n{}\n\n### The third turn response from Assistant A:\n{}\n\n<|The End of Assistant A’s Conversation with User|>\n\n<|The Start of Assistant B’s Conversation with User|>\n### The first turn question from user:\n{}\n\n### The first turn response from Assistant B:\n{}\n\n### The second turn question from user:\n{}\n\n### The second turn response from Assistant B:\n{}\n\n###The third turn question from user:\n{}\n\n### The third turn response from Assistant B:\n{}\n\n<|The End of Assistant B’s Conversation with User|>\n\nThe first turn evaluation: {}.\n The second turn evaluation: {}.\n The third turn evaluation: {}.\n\nThink step-by-step, compare the {} responses from the two assistants, and finish your response with "Overall, Response X is better." where X is either A or B.'.format(image_description, cur_first_turn_instruction, cur_first_turn_response_A, cur_second_turn_instruction, cur_second_turn_response_A, cur_third_turn_instruction, cur_third_turn_response_A, cur_first_turn_instruction, cur_first_turn_response_B, cur_second_turn_instruction, cur_second_turn_response_B, cur_third_turn_instruction, cur_third_turn_response_B, perception_prediction, reasoning_prediction, composition_prediction,  turn_string)) 
    elif turn_str == '_third_turn':
        system_p, user_p, assistant_p = _PROMPT_SYSTEM_PAIRWISE_V1_MT_third_turn, _PROMPT_USER_PAIRWISE_V1_MT_third_turn, _PROMPT_ASSISTANT_PAIRWISE_V1_MT_third_turn
        user_content = ('OK. Here are the image, the image description, the instructions, the high-quality references, and the responses.\nImage context: {}\n\n<|The Start of Assistant A’s Conversation with User|>\n### The first turn question from user:\n{}\n\n### The first turn response from Assistant A:\n{}\n\n### The second turn question from user:\n{}\n\n### The second turn response from Assistant A:\n{}\n\n### The third question from user:\n{}\n\n### The third turn response from Assistant A:\n{}\n\n<|The End of Assistant A’s Conversation with User|>\n\n<|The Start of Assistant B’s Conversation with User|>\n### The first turn question from user:\n{}\n\n### The first turn response from Assistant B:\n{}\n\n### The second turn question from user:\n{}\n\n### The second turn response from Assistant B:\n{}\n\n###The third turn question from user:\n{}\n\n### The third turn response from Assistant B:\n{}\n\n<|The End of Assistant B’s Conversation with User|>\n\nThere are some concerns which you should focus when make your judgements for the response:{}.\n\nThink step-by-step, compare the {} responses from the two assistants, and finish your response with "Overall, Response X is better." where X is either A or B.'.format(image_description, cur_first_turn_instruction, cur_first_turn_response_A, cur_second_turn_instruction, cur_second_turn_response_A, cur_third_turn_instruction, cur_third_turn_response_A, cur_first_turn_instruction, cur_first_turn_response_B, cur_second_turn_instruction, cur_second_turn_response_B, cur_third_turn_instruction, cur_third_turn_response_B, cur_third_turn_demands, turn_string)) 
    elif turn_str == '_first_turn':
        system_p, user_p, assistant_p = _PROMPT_SYSTEM_PAIRWISE_V1_MT_first_turn, _PROMPT_USER_PAIRWISE_V1_MT_first_turn, _PROMPT_ASSISTANT_PAIRWISE_V1_MT_first_turn
        user_content = ('OK. Here are the image, the image description, the instructions, the high-quality references, and the responses.\nImage context: {}\n\n<|The Start of Assistant A’s Conversation with User|>\n### The first turn question from user:\n{}\n\n### The first turn response from Assistant A:\n{}\n\n### The second turn question from user:\n{}\n\n### The second turn response from Assistant A:\n{}\n\n### The third question from user:\n{}\n\n### The third turn response from Assistant A:\n{}\n\n<|The End of Assistant A’s Conversation with User|>\n\n<|The Start of Assistant B’s Conversation with User|>\n### The first turn question from user:\n{}\n\n### The first turn response from Assistant B:\n{}\n\n### The second turn question from user:\n{}\n\n### The second turn response from Assistant B:\n{}\n\n###The third turn question from user:\n{}\n\n### The third turn response from Assistant B:\n{}\n\n<|The End of Assistant B’s Conversation with User|>\n\nThink step-by-step, compare the {} responses from the two assistants, and finish your response with "Overall, Response X is better." where X is either A or B.'.format(image_description, cur_first_turn_instruction, cur_first_turn_response_A, cur_second_turn_instruction, cur_second_turn_response_A, cur_third_turn_instruction, cur_third_turn_response_A, cur_first_turn_instruction, cur_first_turn_response_B, cur_second_turn_instruction, cur_second_turn_response_B, cur_third_turn_instruction, cur_third_turn_response_B, turn_string)) 
    elif turn_str == '_second_turn':
        system_p, user_p, assistant_p = _PROMPT_SYSTEM_PAIRWISE_V1_MT_second_turn, _PROMPT_USER_PAIRWISE_V1_MT_second_turn, _PROMPT_ASSISTANT_PAIRWISE_V1_MT_second_turn
        user_content = ('OK. Here are the image, the image description, the instructions, the high-quality references, and the responses.\nImage context: {}\n\n<|The Start of Assistant A’s Conversation with User|>\n### The first turn question from user:\n{}\n\n### The first turn response from Assistant A:\n{}\n\n### The second turn question from user:\n{}\n\n### The second turn response from Assistant A:\n{}\n\n### The third question from user:\n{}\n\n### The third turn response from Assistant A:\n{}\n\n<|The End of Assistant A’s Conversation with User|>\n\n<|The Start of Assistant B’s Conversation with User|>\n### The first turn question from user:\n{}\n\n### The first turn response from Assistant B:\n{}\n\n### The second turn question from user:\n{}\n\n### The second turn response from Assistant B:\n{}\n\n###The third turn question from user:\n{}\n\n### The third turn response from Assistant B:\n{}\n\n<|The End of Assistant B’s Conversation with User|>\n\nThink step-by-step, compare the {} responses from the two assistants, and finish your response with "Overall, Response X is better." where X is either A or B.'.format(image_description, cur_first_turn_instruction, cur_first_turn_response_A, cur_second_turn_instruction, cur_second_turn_response_A, cur_third_turn_instruction, cur_third_turn_response_A, cur_first_turn_instruction, cur_first_turn_response_B, cur_second_turn_instruction, cur_second_turn_response_B, cur_third_turn_instruction, cur_third_turn_response_B, turn_string)) 
    messages = [{'role': 'system', 'content': system_p},
                {'role': 'user', 'content': user_p},
                {'role': 'assistant', 'content': assistant_p},
                {'role': 'user', 'content': user_content}]


    return messages


def call_gpt(chatgpt_messages, model_name, temp_gpt=0.0):
    client = OpenAI()
    success = False
    while not success:
        try:
            response = client.chat.completions.create(model = model_name,messages = chatgpt_messages,max_tokens=512)
            reply = response.choices[0].message.content
            total_tokens = response.usage.total_tokens
            success = True
            return reply, total_tokens
        except Exception as e:
            e_str = str(e)
            exception_type = e_str[0:15]
            if exception_type == "Error code: 400":
                try:
                    response = client.chat.completions.create(model = "gpt-4",messages = chatgpt_messages,max_tokens=512)
                    reply = response.choices[0].message.content
                    total_tokens = response.usage.total_tokens
                    success = True
                    return reply, total_tokens
                except Exception as e1:
                    e1_str = str(e1)
                    if "context_length_exceeded" in e1_str:
                        chatgpt_messages_temp = []
                        chatgpt_messages_temp.append(chatgpt_messages[3])
                        response = client.chat.completions.create(model = "gpt-4",messages = chatgpt_messages_temp,max_tokens=512)
                        reply = response.choices[0].message.content
                        total_tokens = response.usage.total_tokens
                        success = True
                        return reply, total_tokens                    


            else:
                print('[Worker] an exception occured: %s (%s). retrying in 3 minutes.' % (type(e), str(e)))
                time.sleep(30)

                
def generate_parsing_answer_request(query):
    global _PROMPT_SYSTEM_ANSWER_EXTRACTION_V1, _ICL_SYSTEM_ANSWER_EXTRACTION_V1

    messages = [{"role": "system", "content": _PROMPT_SYSTEM_ANSWER_EXTRACTION_V1}]

    for ex, res in _ICL_SYSTEM_ANSWER_EXTRACTION_V1:
        messages.append({
            'role': 'user',
            'content': ex + '\nPlease extract the final answer from the above text.'}
        )

        messages.append({
            'role': 'assistant',
            'content': res})

    messages.append({
        'role': 'user',
        'content': query + '\nPlease extract the final answer from the above text.'})

    return messages


def extract_prediction_from_response(resp):
    selected = {'{}'.format(ch): int('response {} is better'.format(ch.lower()) in resp.lower()) for ch in 'AB'}
    #selected = {'{}'.format(ch): int('response {} is better'.format(ch) in resp) for ch in ['A','B']}
    if np.sum(list(selected.values())) == 1:
        for k, v in selected.items():
            if v: return k
    
    else:
        messages = generate_parsing_answer_request(resp)
        result, _ = call_gpt(messages, model_name = 'gpt-3.5-turbo')
        selected = {'{}'.format(ch): int('Final Answer: Response {}'.format(ch) in result) for ch in 'AB'}
        #selected = {'{}'.format(ch): int('Final Answer: Response {}'.format(ch) in result) for ch in ['A','B']}
        if np.sum(list(selected.values())) == 1:
            for k, v in selected.items():
                if v:
                    return k
        return None



def judge(image_path, 
          image_description, 
          cur_first_turn_instruction, 
          cur_second_turn_instruction, 
          cur_third_turn_instruction, 
          cur_first_turn_answer, 
          cur_second_turn_answer, 
          cur_third_turn_answer, 
          cur_first_turn_human_answer, 
          cur_second_turn_human_answer, 
          cur_third_turn_human_answer, 
          cur_third_turn_demands,
          position):

    pairwise_dict = dict()
    if position == 0:
        pairwise_dict["A"] = "model_answer"
        pairwise_dict["B"] = "human_answer"
        print("pairwise_dict", pairwise_dict)
        perception_evalaution = "response B is better"
        perception_prediction = "B"        

        messages = generate_request('_second_turn', image_path, image_description, cur_first_turn_instruction, cur_first_turn_answer, cur_first_turn_human_answer, cur_second_turn_instruction, cur_second_turn_answer, cur_second_turn_human_answer, cur_third_turn_instruction, cur_third_turn_answer, cur_third_turn_human_answer)
        reasoning_evalaution, token = call_gpt(messages, model_name = 'gpt-3.5-turbo')
        reasoning_prediction = extract_prediction_from_response(reasoning_evalaution)

        messages = generate_request('_third_turn', image_path, image_description, cur_first_turn_instruction, cur_first_turn_answer, cur_first_turn_human_answer, cur_second_turn_instruction, cur_second_turn_answer, cur_second_turn_human_answer, cur_third_turn_instruction, cur_third_turn_answer, cur_third_turn_human_answer, cur_third_turn_demands=cur_third_turn_demands)
        composition_evalaution, token = call_gpt(messages, model_name = 'gpt-3.5-turbo')
        composition_prediction = extract_prediction_from_response(composition_evalaution)

        messages = generate_request('_overall_conversation', image_path, image_description, cur_first_turn_instruction, cur_first_turn_answer, cur_first_turn_human_answer, cur_second_turn_instruction, cur_second_turn_answer, cur_second_turn_human_answer, cur_third_turn_instruction, cur_third_turn_answer, cur_third_turn_human_answer, perception_prediction=perception_evalaution, reasoning_prediction=reasoning_evalaution, composition_prediction=composition_evalaution)
        overall_evalaution, token = call_gpt(messages, model_name = 'gpt-3.5-turbo')
        overall_prediction = extract_prediction_from_response(overall_evalaution)    

    if position == 1:
        pairwise_dict["A"] = "human_answer"
        pairwise_dict["B"] = "model_answer"   
        print("pairwise_dict", pairwise_dict)
        perception_evalaution = "response A is better"
        perception_prediction = "A"    

        messages = generate_request('_second_turn', image_path, image_description, cur_first_turn_instruction, cur_first_turn_human_answer, cur_first_turn_answer, cur_second_turn_instruction, cur_second_turn_human_answer, cur_second_turn_answer, cur_third_turn_instruction, cur_third_turn_human_answer, cur_third_turn_answer)
        reasoning_evalaution, token = call_gpt(messages, model_name = 'gpt-3.5-turbo')
        reasoning_prediction = extract_prediction_from_response(reasoning_evalaution)

        messages = generate_request('_third_turn', image_path, image_description, cur_first_turn_instruction, cur_first_turn_human_answer, cur_first_turn_answer, cur_second_turn_instruction, cur_second_turn_human_answer, cur_second_turn_answer, cur_third_turn_instruction, cur_third_turn_human_answer, cur_third_turn_answer, cur_third_turn_demands=cur_third_turn_demands)
        composition_evalaution, token = call_gpt(messages, model_name = 'gpt-3.5-turbo')
        composition_prediction = extract_prediction_from_response(composition_evalaution)

        messages = generate_request('_overall_conversation', image_path, image_description, cur_first_turn_instruction, cur_first_turn_human_answer, cur_first_turn_answer, cur_second_turn_instruction, cur_second_turn_human_answer, cur_second_turn_answer, cur_third_turn_instruction, cur_third_turn_human_answer, cur_third_turn_answer, perception_prediction=perception_evalaution, reasoning_prediction=reasoning_evalaution, composition_prediction=composition_evalaution)
        overall_evalaution, token = call_gpt(messages, model_name = 'gpt-3.5-turbo')
        overall_prediction = extract_prediction_from_response(overall_evalaution)    

    return perception_evalaution, perception_prediction, reasoning_evalaution, reasoning_prediction, composition_evalaution, composition_prediction, overall_evalaution, overall_prediction, pairwise_dict 



args = parse_args()
vqa_model = args.vqa_model
path = "../ConvBench.xlsx"
dataset_root = "../visit_bench_images"
df = pd.read_excel(path)
save_path = "./result/" + vqa_model +"/1"
id = 0
if not os.path.exists(save_path):
    os.makedirs(save_path)
pairwise = np.load("./pairwise.npy")       
for i in range(len(df)):
    position = pairwise[id]
    id+=1

    result_path = os.path.join(save_path, '{}.yaml'.format(str(id)))
    cur_dir = "../VLMEvalKit/work_dirs/" + vqa_model + "/1/" + str(id) + ".yaml"
    if os.path.exists(cur_dir) == False:
        continue  

    print("result_path", result_path)
    if os.path.isfile(result_path):
        continue    
    cur_image_id = df['image_id'][i]
    cur_instruction_conditioned_caption = df['instruction-conditioned-caption'][i]
    image_path = os.path.join(dataset_root, 'images', cur_image_id)

    cur_first_turn_instruction = df['The_first_turn_instruction'][i]
    cur_second_turn_instruction =  df['The_second_turn_instruction'][i]
    cur_third_turn_instruction = df['The_third_turn_instruction'][i]

    cur_first_turn_category = df['First_turn_instruction_category'][i]
    cur_second_turn_category =  df['Second_turn_instruction_category'][i]
    cur_third_turn_category = df['Third_turn_instruction_category'][i]

    cur_first_turn_human_answer = df['first_turn_answer'][i]
    cur_second_turn_human_answer =  df['second_turn_answer'][i]
    cur_third_turn_human_answer = df['third_turn_answer'][i]
    cur_third_turn_demands = df['third_turn_demands'][i]

    
    with open(cur_dir, "r") as file:
        data_i = yaml.safe_load(file)
    #cur_first_turn_answer = data_i['first_turn_answer']
    cur_second_turn_answer =  data_i['second_turn_answer']
    cur_third_turn_answer = data_i['third_turn_answer']

    perception_evaluation, perception_prediction, reasoning_evaluation, reasoning_prediction, composition_evaluation, composition_prediction, overall_evalaution, overall_prediction, pairwise_dict  =  judge(image_path, cur_instruction_conditioned_caption, cur_first_turn_instruction, cur_second_turn_instruction, cur_third_turn_instruction, cur_first_turn_human_answer, cur_second_turn_answer, cur_third_turn_answer, cur_first_turn_human_answer, cur_second_turn_human_answer, cur_third_turn_human_answer, cur_third_turn_demands, position)
    results = {}
    results['image_path'] = image_path
    results['instruction_conditioned_caption'] = cur_instruction_conditioned_caption
    
    results['first_turn_instruction'] = cur_first_turn_instruction
    results['first_turn_human_answer'] = cur_first_turn_human_answer
    results['first_turn_category'] = cur_first_turn_category
    results['first_turn_evaluation'] = perception_evaluation
    results['first_turn_rating'] = perception_prediction


    results['second_turn_instruction'] = cur_second_turn_instruction
    results['second_turn_answer'] = cur_second_turn_answer
    results['second_turn_human_answer'] = cur_second_turn_human_answer
    results['second_turn_category'] = cur_second_turn_category    
    results['second_turn_evaluation'] = reasoning_evaluation
    results['second_turn_rating'] = reasoning_prediction       
    

    results['third_turn_instruction'] = cur_third_turn_instruction
    results['third_turn_answer'] = cur_third_turn_answer
    results['third_turn_human_answer'] = cur_third_turn_human_answer
    results['third_turn_category'] = cur_third_turn_category    
    results['third_turn_evaluation'] = composition_evaluation 
    results['third_turn_rating'] = composition_prediction   
    results['third_turn_demands'] = cur_third_turn_demands   

    results['overall_evalaution'] = overall_evalaution 
    results['overall_prediction'] = overall_prediction 
    results['pairwise_dict'] = pairwise_dict

    with open(result_path, 'w') as f:
        yaml.dump(results, f)
        

    
second_turn_rating = 0
third_turn_rating = 0
overall_prediction = 0
TEST_SUM = 577    
i = 0
for id in range(1,579): 
    position = pairwise[id-1]
    result_path = os.path.join(save_path, '{}.yaml'.format(str(id)))

    if os.path.exists(result_path) == False:
        second = 0
        third = 0
        overall = 0  
    else:
        i+=1
        with open(result_path, "r") as file:
            data_i = yaml.safe_load(file)
        second = data_i['second_turn_rating']
        third = data_i['third_turn_rating']
        overall = data_i['overall_prediction']


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
            if second == "A":
                second_turn_rating +=1
            if third == "A":
                third_turn_rating +=1
            if overall == "A":
                overall_prediction +=1


        if position == 1:
            #pairwise_dict["A"] = "human_answer"
            #pairwise_dict["B"] = "model_answer"   
            if second == "B":
                second_turn_rating +=1
            if third == "B":
                third_turn_rating +=1
            if overall == "B":
                overall_prediction +=1


second_turn_rating = second_turn_rating/TEST_SUM
third_turn_rating = third_turn_rating/TEST_SUM
overall_prediction = overall_prediction/TEST_SUM

print("second_turn_rating", second_turn_rating)
print("third_turn_rating", third_turn_rating)
print("overall_prediction", overall_prediction)