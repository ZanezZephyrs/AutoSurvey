import argparse
import openai
import json
from settings import settings
from textwrap import dedent
from pathlib import Path
import os


def evaluate(dataset: str, gold_path, log_file: str):
    """
    Returns the average score for the dataset.
    Args:
        dataset: Path to the json dataset
        log_file: Path to save the evaluation results
    Returns:
        Average score for the dataset 
    """    
    with open(dataset, "r") as f:
        data = json.load(f)

    with open(gold_path, "r", encoding="utf8") as f:
        gold_data = json.load(f)
    
    with open(log_file, "w") as f:
        all_candidate_scores = []
        all_ground_truth_scores = []
        for survey_name in data:
            for survey_section, content in data[survey_name].items():
                exps = None
                if content.get("subsections"):
                    sub_scores = []
                    for sub_name, sub_content in content.get("subsections").items():
                        generated_content = sub_content["content"]
                        ground_truth = gold_data[survey_name][survey_section]["subsections"][sub_name]["content"]
                        if ground_truth == "":
                            raise ValueError("Ground truth is empty")
                        sub_score, _ = get_llm_score(survey_name, survey_section, generated_content, ground_truth)
                        sub_scores.append((sub_score[0], sub_score[1]))
                    score = [sum([s[0] for s in sub_scores])/len(sub_scores), sum([s[1] for s in sub_scores])/len(sub_scores)]
                else:
                    generated_content = content["content"]
                    ground_truth = gold_data[survey_name][survey_section]["content"]
                    if ground_truth == "":
                        raise ValueError("Ground truth is empty")
                    score, exps = get_llm_score(survey_name, survey_section, generated_content, ground_truth)
                all_candidate_scores.append(score[0])
                all_ground_truth_scores.append(score[1])
                json.dump({"survey_name": survey_name, "survey_section": survey_section, "content": generated_content, "candidate_score": score[0], "ground_truth_score": score[1], "explanations": exps}, f)
                f.write("\n")
    
    return [sum(all_candidate_scores)/len(all_candidate_scores), sum(all_ground_truth_scores)/len(all_ground_truth_scores)]


def get_llm_score(paper_title, section_title, candidate, ground_truth):
    prompt_template= "[Paper title]{paper_title}[Section title]\n{section}\n\n[The Start of Assistant 1's section]\n{answer_1}\n\n[The End of Assistant 1's section]\n\n[The Start of Assistant 2's section]\n{answer_2}\n\n[The End of Assistant 2's section]\n\n[System]\n{prompt}\n\n"
    system_prompt = dedent("""
    You are a helpful and precise assistant for checking the quality of an scientific section""")

    user_question = "We would like to request your feedback on the performance of two AI assistants in the elaboration of an section for a scientific review in the theme displayed above.\nPlease rate the helpfulness, relevance, accuracy, level of details of their responses. Each assistant receives an overall score on a scale of 1 to 10, where a higher score indicates better overall performance.\nPlease first output a single line containing only two values indicating the scores for Assistant 1 and 2, respectively. The two scores are separated by a space. In the subsequent line, please provide a comprehensive explanation of your evaluation, avoiding any potential bias and ensuring that the order in which the responses were presented does not affect your judgment. Please judge the assistants based on the content of the section and pay especial attention if they are relevant for the given section title."

    prompt_1 = prompt_template.format(paper_title=paper_title, section=section_title, answer_1=candidate, answer_2=ground_truth, prompt=user_question)
    
    prompt_2= prompt_template.format(paper_title=paper_title, section=section_title, answer_1=ground_truth, answer_2=candidate, prompt=user_question)

    scores=[]
    exps=[]
    for prompt in [prompt_1, prompt_2]:

        response = openai.ChatCompletion.create(
            model=settings.model,
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": prompt},
            ],
            temperature=settings.temperature,
            top_p=settings.top_p,
        )
        
        response = response.choices[0]["message"]["content"]
        score=response.split("\n")[0].strip()# "number number"
        score=score.split(" ") # ["number","number"]
        score=[float(s) for s in score] # [number,number]
        scores.append(score)
        exps.append(response)
        # Scores are the sum of probabilities for each class multiplied by the class value


    total_score_truth=(scores[0][1]+scores[1][0])/2
    total_score_candidate=(scores[0][0]+scores[1][1])/2


    print(scores[0][1], scores[1][0])
    print(scores[0][0], scores[1][1])

    
    return [total_score_candidate,total_score_truth], exps

# python evaluate_preference.py --dataset /home/thales/Documents/AutoSurvey/test/proc1/proc1.json --gold /home/thales/Documents/AutoSurvey/data/dataset/survey_3.json --logs pref_eval/proc1_eval.json

# python evaluate_preference.py --dataset /home/thales/Documents/AutoSurvey/test/proc2/proc2.json --gold /home/thales/Documents/AutoSurvey/data/dataset/survey_3.json --logs pref_eval/proc2_eval.json

# python evaluate_preference.py --dataset /home/thales/Documents/AutoSurvey/test/proc3/proc3.json --gold /home/thales/Documents/AutoSurvey/data/dataset/survey_3.json --logs pref_eval/proc3_eval.json

# python evaluate_preference.py --dataset /home/thales/Documents/AutoSurvey/test/proc4/proc4.json --gold /home/thales/Documents/AutoSurvey/data/dataset/survey_3.json --logs pref_eval/proc4_eval.json

# python evaluate_preference.py --dataset /home/thales/Documents/AutoSurvey/test/proc5/proc5.json --gold /home/thales/Documents/AutoSurvey/data/dataset/survey_3.json --logs pref_eval/proc5_eval.json

# python evaluate_preference.py --dataset /home/thales/Documents/AutoSurvey/test/proc6/proc6.json --gold /home/thales/Documents/AutoSurvey/data/dataset/survey_3.json --logs pref_eval/proc6_eval.json


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--dataset", type=str, required=True, help="Path to the json dataset")
    argparser.add_argument("--gold", type=str, required=True, help="Path to the json dataset")

    argparser.add_argument("--logs", type=str, default="evaluation_results.json", help="Path to save the evaluation results")

    args = argparser.parse_args()

    out_path=Path(args.logs)
    os.makedirs(out_path.parent, exist_ok=True)

    openai.api_key = settings.openai_key

    base_prompt = dedent("""Evaluation Steps:
    1 - Carefully read the content to identify the main topic and key points.
    2 - Evaluate whether the content adequately addresses the main topic stated in the title and provides a comprehensive technical description of it.
    3 - Assign a score to the text on a scale of 1 to 10, where 1 represents the lowest score and 10 represents the highest score, according to the Evaluation Criteria.""")

    average_score = evaluate(args.dataset, args.gold, args.logs)

    print(f"Average score candidate: {average_score[0]}")
    print(f"Average score ground truth: {average_score[1]}")