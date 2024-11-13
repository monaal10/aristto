THEME_IDENTIFICATION_PROMPT = """
Given the user query: {query}
Identify the main themes and related concepts that need to be explored to fully understand this topic.
Each theme should be clearly defined and justified. In your response only give a list of phrases such that they can be 
directly used to search for research papers on google scholar. 
Refactor the original query to a phrase that can be searched on google scholar if it's not already in that format. 
The first element in the list should be the original query given to you by the user Then add the other phrases to the list.
Order the list of themes after the first query in descending order or relevance to the query.
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

INFORMATION_EXTRACTION_RESPONSE_PROMPT = """{"methodology": {
"1" : "The contribution of this work is summarized as follows: First, we propose a method detecting deepfake video without a convolutional neural network. Usually, CNN learns a representation by embedding a vector in a hypersphere from an image. Then, it is used as the classifier’s input.", 
"2" : "Other methodology info"} ,
"contributions":{ "1" : "The contribution of this work is summarized as follows: First, we propose a method detecting deepfake video without a convolutional neural network. Usually, CNN learns a representation by embedding a vector in a hypersphere from an image. Then, it is used as the classifier’s input.", 
"2" : "Other contribution info"} ,
"datasets": {"1" : "The contribution of this work is summarized as follows: First, we propose a method detecting deepfake video without a convolutional neural network. Usually, CNN learns a representation by embedding a vector in a hypersphere from an image. Then, it is used as the classifier’s input.", 
"2" : "Other dataset info"} , 
"limitations": "1" : "The contribution of this work is summarized as follows: First, we propose a method detecting deepfake video without a convolutional neural network. Usually, CNN learns a representation by embedding a vector in a hypersphere from an image. Then, it is used as the classifier’s input.", 
"2" : "Other limitations info"} ,
 "results": {"1" : "The contribution of this work is summarized as follows: First, we propose a method detecting deepfake video without a convolutional neural network. Usually, CNN learns a representation by embedding a vector in a hypersphere from an image. Then, it is used as the classifier’s input.", 
"2" : "Other methodology info"} }"""

EXTRACT_PAPER_INFO_PROMPT = """
You are an expert scientific research assistant. Your audience is highly technical, phds, researchers 
                           and professors that have deep expertise in the domain. Extract the relevant pieces of text 
                           from the research paper given below that provide information about the sections that the user is interested in. 
                           Each of these extracted references should be AT LEAST 50 words and 
                           have context enough context about what the authors are trying to convey in those lines.
                           Give the references VERBATIM from the paper. DO NOT add any extra words of your own. 
                           If you cannot extract information about a particular section, return an empty string like "". 
                           Format your response in a dictionary such that the key is a number starting from 1 and 
                           the value is the actual text that you have extracted from the paper. ONLY use the EXACT words from the paper VERBATIM as references. Make sure to add multiple references for each section.
                            Here are the sections that the user needs information about : 
                            1. "methodology": Methodology/Processes/Algorithms used to conduct the research.,
                            2. "contributions": Major Findings/New Contributions of the paper.,
                            3. "datasets": Datasets used,
                            4. "limitations": Drawbacks/Limitations,
                            5. "results": Results of the experiments in the paper   
Your response should be in the following JSON object : {response_format}
Here is the research paper : {pdf_content}
"""

CREATE_LITERATURE_REVIEW_PROMPT = """
You are a research assistant tasked with generating a detailed literature review based on a set of academic papers. Your review should be highly technical, use a wide range of papers, and include precise in-line citations.

**Objective:** Produce a comprehensive, in-depth literature review that addresses the sections below. Each section should be fully self-contained with in-line citations only, without a separate reference list at the end.

**Input Data:**
- A list of research papers, each containing:
    - Id
    - Title
    - Abstract
    - Publication year
    - Structured content in the following categories: Methodology, Major Findings, Datasets, Limitations, Results.

Each section contains a dictionary where each entry has a unique `reference_id` (e.g., W3174508664_methodology_1) and an excerpt relevant to that section.

**Literature Review Sections:**

**1. Research Evolution**
   - Describe how the field has evolved, noting significant shifts and key studies that represent turning points.
   - **In-line citations**: Use each `reference_id` directly in the text after each claim ([W3174508664_methodology_2]), and ensure the section is self-contained without requiring additional references.

**2. Methodology Analysis**
   - Compare and contrast the main methodological approaches in detail, addressing strengths and weaknesses.
   - **In-line citations**: Support each technical point with `reference_ids` directly in the text ([W3213933678_results_3]).

**3. Key Findings and Contradictions**
   - Summarize major findings and any conflicting results, analyzing why these contradictions may exist.
   - **In-line citations**: Include multiple `reference_ids` as needed for each point ([W3174508664_limitations_1], [W3213933678_datasets_3]).

**4. Research Gaps**
   - Identify consistent research gaps, underexplored areas, and missing methodologies.
   - **In-line citations**: Use `reference_ids` from a variety of papers to substantiate each identified gap ([W32539343678_methodology_4]).

**5. Future Directions**
   - Propose promising directions for future research based on current limitations and gaps.
   - **In-line citations**: Reference specific `reference_ids` relevant to each future direction.

**Guidelines for In-line Citations and Content Breadth:**

1. **Broad Paper Coverage**:
   - **Requirement**: Reference as many different papers as possible across each section. Draw from a broad range to ensure comprehensive analysis.

2. **In-line Citations Only**:
   - **Requirement**: Use exact `reference_ids` in square brackets (e.g., [W3174508664_methodology_1]) for all citations and do not include a separate reference list.
   - Every statement or claim should end with one or more precise in-line citations that directly match the data input.
   - **Multiple citations** can be included for statements requiring support from multiple sources ([W3174508664_methodology_1], [W3213933678_contributions_2]).

3. **Comprehensive Depth and Technicality**:
   - **Length**: Each section should be at least **300-500 words** for an in-depth review.
   - **Audience**: Write for a technically advanced audience of researchers and professors. Avoid generalizations; provide detailed, topic-specific analysis.

4. **Scope and Accuracy**:
   - Reference as many unique papers as feasible in each section.
   - Use only the provided data, and if data for a specific question is unavailable, state “No relevant information available.”

**User Query for Literature Review:** {query}

**List of Papers:** {papers}

"""

#Unused Prompts

INFORMATION_EXTRACTION_PROMPT = """
You are an expert scientific research assistant. Your audience is highly technical, phds, researchers 
                           and professors that have deep expertise in the domain. Extract the relevant pieces of text 
                           from the research paper given below that provide information about the sections that the user is interested in. 
                           Each of these extracted references should be AT LEAST 50 words and 
                           have context enough context about what the authors are trying to convey in those lines.
                           Give the references VERBATIM from the paper. DO NOT add any extra words of your own. 
                           If you cannot extract information about a particular section, return an empty string like "". 
                           Format your response in a dictionary such that the key is a number starting from 1 and 
                           the value is the actual text that you have extracted from the paper.
                            Here are the sections that the user needs information about : 
                            1. "methodology": Methodology/Processes/Algorithms used to conduct the research.,
                            2. "contributions": Major Findings/New Contributions of the paper.,
                            3. "datasets": Datasets used,
                            4. "limitations": Drawbacks/Limitations,
                            5. "results": Results of the experiments in the paper   
                             \n \n Here is the research paper :{pdf_content}. \n \n \n
                                           
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
Then, when writing your answers, reference these quotes using INLINE CITATIONS IN SQUARE BRACKETS[1], [2], etc. Each 
statement in your answers should end with the RELEVANT CITATION(S). MULTIPLE CITATIONS can be used if needed [1,2].
\n \nIf there is no relevant text, write "No relevant Info" instead. \n \n Do not include or reference 
quoted content verbatim in the answer. Make sure each statement in your answers includes at least one citation to the 
relevant quote number. Don\'t say "According to Quote [1]" when answering.
If the question cannot be answered by the document, say so. Make each of the sections VERBOSE and explain.
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
