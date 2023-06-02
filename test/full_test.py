from AutoSurvey.llm_inference.openai_inference import OpenAIInference
from AutoSurvey.searchers.semantic_scholar import SemanticScholarSearcher
from AutoSurvey.filters.field_in_list_filter import FieldInListFilter
from AutoSurvey.filters.field_numeric_filter import FieldNumericFilter
from AutoSurvey.pdf_generation.pdf_generator import PDFGenerator
from tqdm import tqdm
import json

paper_template="""- Paper {I}
Title:{TITLE}
Summary: {SUMMARY}
"""

template_messages=[
    {"role": "system", "content": "You Are an expert in scientific literature review, your job is, given a series of papers and theirs summaries, write a paragraph with a given title citing relevant information in the traditional format (e.g [1,2,3] [1]) from the provided papers"},
]

searcher=SemanticScholarSearcher()

agent=OpenAIInference(api_key="", engine="gpt-3.5-turbo")


def query_to_documents(query):
  # search for papers with "deep learning" in the title
  params={
      "query": query,
      "limit": 100, # max 100
      "fields": "title,authors,citationCount,year,tldr,url,abstract"
  }

  # compose as many filters as you like, they are applied in sequence
  filters=[
      FieldNumericFilter("citationCount", lower_bound=2), # at least 10 citations
      FieldNumericFilter("authors", lower_bound=2), # at least 2  authors
      FieldNumericFilter("year", lower_bound=2020, upper_bound=2023), # between 2020 and 2023
  ]

  results=searcher.search(params, filters=filters)

  return results

def documents_to_section(results, query):

  user_prompt=""
  current_paper_number=0
  for i,result in enumerate(results):

    if result["abstract"]:
      paper_summary=result["abstract"]

    elif result["tldr"]:
      paper_summary=result["tldr"]["text"]
    else:
      continue

    current_paper_number+=1

    if current_paper_number>=6:
      break

    
    paper_text=paper_template.format(I=i+1,SUMMARY=paper_summary, TITLE=result["title"])
    user_prompt+=paper_text + "\n"

  user_prompt+= "Paragraph Subject: " + query

  current_msgs=template_messages.copy()

  current_msgs.append({
      "role": "user",
      "content": user_prompt
  })

  return agent.complete(current_msgs)


theme="deep learning"
sections=[
    "applications",
    "latest developments",
    "neural networks",
    "large language models"
]

sections_data={}

for section in tqdm(sections):
  query=theme + " - "+ section
  documents=query_to_documents(query)
  section_text=documents_to_section(documents, query)
  sections_data[section]=section_text


PDFGenerator.generate_pdf(theme,sections, sections_data, output_file="file.pdf")