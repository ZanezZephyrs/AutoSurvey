import argparse
import openai
import json
from settings import settings
from textwrap import dedent


def evaluate(dataset: str, log_file: str):
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
    
    with open(log_file, "w") as f:
        all_scores = []
        for survey_name in data:
            for survey_section, content in data[survey_name].items():
                prompt = (
                    f"{base_prompt}\nSurvey Name: {survey_name.strip()}\nSurvey Section: {survey_section.strip()}\nContent: {content.strip()}\nEvaluation Form (scores ONLY)\nScore:"
                ) 
                score = get_llm_score(prompt)
                all_scores.append(score)
                json.dump({"survey_name": survey_name, "survey_section": survey_section, "content": content, "score": score}, f)
    
    return sum(all_scores)/len(all_scores)


def get_llm_score(prompt):
    system_prompt = dedent("""
    You will be given a text written for a survey section.
    Your task is to rate the content on one metric.
    Please make sure you read and understand the instructions carefully.
    Please keep the document open while reviewing, and refer to it as needed.""")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": prompt},
        ],
        max_tokens=settings.max_tokens,
        temperature=settings.temperature,
        top_p=settings.top_p,
        n=settings.n,
    )
    all_predictions = [int(item["message"]["content"]) for item in response.choices]
    # Scores are the sum of probabilities for each class multiplied by the class value
    scores = sum(all_predictions.count(i)/len(all_predictions) * i for i in range(1, 6))
    return scores
   

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--dataset", type=str, required=True, help="Path to the json dataset")
    argparser.add_argument("--logs", type=str, default="evaluation_results.json", help="Path to save the evaluation results")

    args = argparser.parse_args()

    openai.api_key = settings.openai_key

    base_prompt = dedent("""Evaluation Steps:
    1 - Carefully read the content to identify the main topic and key points.
    2 - Evaluate whether the content adequately addresses the main topic stated in the title and provides a comprehensive technical description of it.
    3 - Assign a score to the text on a scale of 1 to 5, where 1 represents the lowest score and 5 represents the highest score, according to the Evaluation Criteria.""")

    average_score = evaluate(args.dataset, args.logs)