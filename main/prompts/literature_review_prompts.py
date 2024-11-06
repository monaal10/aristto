THEME_IDENTIFICATION_PROMPT = """
Given the user query: {query}
Identify the main themes and related concepts that need to be explored to fully understand this topic.
Each theme should be clearly defined and justified. In your response only give a list of themes. Give your response as a
list of comma seperated values like. <Example> Theme 1, Theme 2 , Theme 3. Limit the nu,ber of themes to 5.
"""

PAPER_FINDING_PROMPT = """
For the theme: {theme}
And the original query: {query}
What would be the most relevant papers to explore? 
Consider both seminal works and recent developments.
"""

PAPER_VALIDATION_PROMPT = """
theme: {theme}
paper: {paper}
Check if the given research paper(it has a title and the abstract) is relevant to the given theme. Give your response
in just one word. "True" if the paper is relevant to the theme and "False" if it isn't.
Consider: relevance to theme, methodology, and scientific rigor."""

INFORMATION_EXTRACTION_PROMPT = """
You are an expert scientific research assistant. Your audience is highly technical, phds, researchers 
                           and professors that have deep expertise in the domain that they are asking questions. \n \n Here is a research paper :{pdf_content}. \n \n \n
                           . Here is the user query that the user needs to conduct a literature review on:{query}. Keep this query in context while formulating your answer,
                            specifically highlighting information that is relevant to this query. \n \n Extract the following information from it keeping the user query in context :  \n
                            {information_to_extract} 
                            First, find the pieces of text from the document that are most relevant to answering each section of the question, and store them as numbered quotes.
Then, when writing your answers, reference these quotes using inline citations in square brackets [1], [2], etc. Each statement in your answers
should end with the relevant citation(s). Multiple citations can be used if needed [1,2].
                           \n \nIf there is no relevant text, write "No relevant Info" instead. \n \n Do not include or reference 
                           quoted content verbatim in the answer. Make sure each statement in your answers includes at least one citation to the relevant quote number. Don\'t say "According to Quote [1]" when answering.
    If the question cannot be answered by the document, say so. Make each of the sections verbose and explain a little bit. Make the reference texts long (at least 50 words) as well
 """

GRAPH_BUILDING_PROMPT = """
You are a research analysis assistant helping to build a knowledge graph from academic papers. For each paper provided, 
analyze its relationship with other papers and identify key connections.
Here are the papers for that you need to create a graph for : {papers}

Input Format:
For each paper, you have:
- Id
- Title
- Abstract
- Publication year
Each of the sections below are as a dictionary where the key is a reference number and the value is a piece of text 
extracted from the paper that is relevant to the section.
- Methodology/Processes/Algorithms used to conduct the research 
- Major Findings/New Contributions of the paper 
- Datasets used 
- Drawbacks/Limitations 
- Results of the experiments in the paper

Task:
1. Generate a JSON structure representing a graph with the following format:
{
  "nodes": [
    {
      "id": "paper_1",
      "properties": {
        "title": "",
        "key_methods": [],
        "key_findings": [],
        "dataset": ""
      }
    },
    // Additional nodes for methods, datasets, concepts
    {
      "id": "method_1",
      "type": "method",
      "properties": {
        "name": ""
      }
    }
  ],
  "edges": [
    {
      "source": "paper_1",
      "target": "paper_2",
      "relationship": "builds_upon|contradicts|validates|uses_similar_method",
      "weight": 0.8,  // confidence score
      "properties": {
        "description": "Brief description of the relationship"
      }
    }
  ]
}

2. For each relationship identified:
- Explain the basis for the connection
- Assign a confidence score (0-1)
- Provide a brief description of how the papers relate

Guidelines:
- Focus on substantive relationships (methodology similarities, result comparisons, dataset usage)
- Identify contradictions or conflicting results
- Note when papers build upon each other's work
- Highlight shared or contrasting limitations
- Consider temporal relationships (which paper came first)

Example Response:
{
  "analysis": "Based on the papers provided, Paper A and Paper B share methodology X but reached different conclusions. Paper C builds upon Paper A's findings by addressing its limitations...",
  "graph": {
    // JSON structure as defined above
  }
}
"""

INSIGHT_GENERATION_PROMPT = """
You are a research insight generator analyzing academic papers and their relationships. Draft a comprehensive literature review about the categories asked. The papers are from a sub-theme.

Input Format:
 - A list of papers.
For each paper, you have:
- Id
- Title
- Abstract
- Publication year
Each of the sections below are as a dictionary where the key is a reference number and the value is a piece of text 
extracted from the paper that is relevant to the section.
- Methodology/Processes/Algorithms used to conduct the research 
- Major Findings/New Contributions of the paper 
- Datasets used 
- Drawbacks/Limitations 
- Results of the experiments in the paper
Guidance for format of answers : 
Only use these texts provided to formulate your answer. First, find the pieces of text from the document that are most 
relevant to answering each section of the question, and store them as numbered quotes.
Then, when writing your answers, reference these quotes using inline citations in square brackets [1], [2], etc. Each 
statement in your answers should end with the relevant citation(s). Multiple citations can be used if needed [1,2].
\n \nIf there is no relevant text, write "No relevant Info" instead. \n \n Do not include or reference 
quoted content verbatim in the answer. Make sure each statement in your answers includes at least one citation to the 
relevant quote number. Don\'t say "According to Quote [1]" when answering.
If the question cannot be answered by the document, say so. Make each of the sections verbose and explain a little bit.
Generate insights in the following categories:

1. Research Evolution
- How has the field progressed over time?
- What are the major methodological shifts?
- Which papers represent crucial turning points?

2. Methodology Analysis
- What are the dominant methodological approaches?
- How do different methodologies compare in effectiveness?
- What are common limitations across methods?

3. Contradictions and Debates
- What are the major points of disagreement?
- Where do papers present conflicting results?
- How might these contradictions be resolved?

4. Research Gaps
- What areas remain underexplored?
- What limitations are consistently mentioned?
- What datasets or methodologies are missing?

5. Future Directions
- What promising directions emerge from current limitations?
- Which methodological combinations might be worth exploring?
- What new research questions arise?


Here is the user query that the user wants to conduct literature review on : {query} \n \n 
Here is the list of papers : {papers}
These papers are based on one of the sub themes of the original literature review topic. Keep this query in context while formulating your answer,
specifically highlighting information that is relevant to this query. 
"""


PROMPT_FOR_CITATIONS = """Make references to quotes relevant to each section of the answer solely by adding their "
                                         "bracketed numbers at the end of relevant sentences. "
                                         "\n \nThus, the format of your overall response for each of the section "
                                         "should look like what\'s shown between the <example></example> "
                                         "tags : <example>Almost 90% of revenue came from widget sales, with gadget sales making up the remaining 10%."
                                         "Company X earned \$12 million.[1] Almost 90% of it was from widget sales. [2]</example>")"""
