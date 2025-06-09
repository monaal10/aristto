THEME_IDENTIFICATION_PROMPT = """
You are an expert research assistant. Given the user's query, and the conversation history generate
        precise search queries that would help gather comprehensive information on the topic. 
        The number of search queries to generate will be provided by the user, generate exactly that many.
        There can be previous queries that were used already. If there are come up with new ones that haven't been used 
        and will fetch me different but still relevant results. Also, Give me the name of the topic that I can use 
        as the title for the name of this conversation.
        Return only a Python list of strings, for example: ['query1', 'query2', 'query3'].
        User Query :{query}
        Queries Used : {previous_search_queries}
        Conversation History : {conversation_history}
        Queries to generate : {queries_to_generate}
"""

PAPER_FINDING_PROMPT = """
What would be the most relevant papers to explore? 
Consider both seminal works and recent developments.
For the theme: {theme}
And the original query: {query}
"""

PAPER_VALIDATION_PROMPT = """
Check if the given  list of research papers(it has a title and the abstract) could be relevant to answer the user's question. 
Give your response in just one word. "True" if the paper is relevant to the theme and "False" if it isn't.
Make sure that the length of the output list is exactly equal to the length of the input list.
Return a list of "True" and "False" in the order of the input papers given. For example if first paper is relevant and second isn't,
return ["True", "False"].
Consider: relevance to query, methodology, and scientific rigor.
papers : {papers}
"""


GENERATE_DEEP_RESEARCH_REPORT_PROMPT = """
Comprehensive Literature Review Generator
You are a research assistant tasked with generating a comprehensive literature review based on academic papers. Your review must draw extensively from ALL available sources in the provided dataset, ensuring maximum breadth and depth of coverage while maintaining meaningful citations.
Primary Objective
Produce an expansive, in-depth literature review that incorporates insights from the COMPLETE RANGE of provided papers. Each section must synthesize information from as many relevant sources as possible, leaving no paper unexamined or unused unless completely irrelevant.
Input Data

A list of research papers, each containing:

Id
Context - relevant context from that paper



Guidelines for Maximizing Source Utilization
1. Comprehensive Paper Coverage (HIGHEST PRIORITY)

STRICT REQUIREMENT: Utilize AT LEAST 95% of the provided papers in your review
Methodically examine each paper in the dataset before drafting any content
Create a detailed mapping of how each paper contributes to different aspects of the topic
Develop a structured citation plan ensuring representation of ALL papers
For papers that seem less central, identify creative ways to incorporate their peripheral findings or methodological approaches

2. Paper Utilization Tracking System

Before writing, create a mental checklist of all paper IDs
As you write, track which papers have been cited and which remain unused
Periodically review your citation distribution to ensure balanced coverage
Deliberately incorporate underutilized papers into appropriate sections
Before finalizing, conduct a thorough audit to verify that at least 95% of papers are meaningfully cited

3. Multi-dimensional Analysis Structure

Design a comprehensive framework that accommodates perspectives from ALL papers
Create primary sections covering major dimensions and secondary sections for specialized topics
For each section and subsection, incorporate insights from multiple papers
Include dedicated sections for outlier perspectives, emerging approaches, and contrasting methodologies
Balance theoretical foundations, empirical findings, methodological innovations, and practical applications

4. Strategic Citation Distribution

STRICT REQUIREMENT: Distribute citations EVENLY throughout the entire document
CRITICAL PROHIBITION: NEVER include "citation dumps" where multiple papers are cited together without specific contributions (e.g., "Several studies support this [id1, id2, id3, id4, id5, ...]")
Limit each citation group to a MAXIMUM of 3-4 papers, and only when they make similar specific points
Each paragraph should reference 2-3 different papers with clear explanations of their contributions
Avoid over-reliance on any single paper or small group of papers
When multiple papers make similar points, select the most representative 2-3 papers rather than citing all of them

5. Citation Quality Control (HIGHEST PRIORITY)

ABSOLUTE PROHIBITION: DO NOT include concluding paragraphs or sentences that dump large numbers of citations
ABSOLUTE PROHIBITION: DO NOT include statements like "This comprehensive synthesis integrates findings from a broad spectrum of studies [id1, id2, id3, ... id40]"
ABSOLUTE PROHIBITION: DO NOT list more than 4 citations in a row anywhere in the document
Every citation must be tied to a specific finding, method, theory, or perspective
Citations must be integrated into the text with clear explanations of what each cited paper contributes
Review your final document and remove any section that contains excessive citation lists

6. Advanced Citation Integration Techniques

Use comparative citations: "While [id1] found X, [id2] demonstrated Y"
Employ synthesizing citations: "Integrating findings from [id1] and [id2] suggests..."
Utilize confirmatory citations: "This pattern has been observed in two major studies [id1][id2]"
Implement contextual citations: "When viewed through the framework established by [id1], the approach in [id2] reveals..."
Apply evolutionary citations: "This concept evolved from [id1]'s foundational work through refinements in [id2]"

7. Underutilized Paper Integration Strategies

Identify papers with lower citation potential and deliberately prioritize their inclusion
Create specialized subsections to highlight unique contributions from less frequently cited papers
Frame niche findings as valuable complementary perspectives to mainstream views
Incorporate methodological details, limitations, or future directions from less central papers
Use contrast and comparison to integrate papers with outlier findings or approaches

8. Web-Friendly Formatting Requirements

Respond with a comprehensive literature review formatted in clean, web-compatible Markdown
Use appropriate headings (##, ###), bullet points, and numbered lists for clear visual hierarchy
Ensure all Markdown syntax is properly closed and nested
Format citations consistently as [id#] throughout the document
Use short paragraphs (3-6 sentences) for better readability on web interfaces
Include appropriate spacing between sections for visual clarity
Avoid overly complex formatting that might break in web rendering

9. Final Quality Assurance Checklist

VERIFY: Each paper in the dataset has been meaningfully incorporated
COUNT: Calculate the percentage of unique papers cited (must be ≥95%)
AUDIT: Ensure no section relies excessively on a small subset of papers
BALANCE: Confirm citations are distributed evenly throughout the review
CLEAN: Remove any instances of citation dumping or excessive citation lists
PURPOSE: Verify each citation serves a meaningful analytical purpose
ACCURACY: Confirm all citation IDs match papers provided in the input
FORMAT: Ensure the document will render correctly in a web interface
PROHIBITION: DO NOT add a references section at the end

Strict Prohibitions

DO NOT add commentary before or after the requested literature review
DO NOT fabricate citation IDs not present in the input dataset
DO NOT add a references or bibliography section
DO NOT include any paragraph or sentence that lists more than 4 citation IDs together
DO NOT conclude sections or the document with citation dumps
DO NOT rely on a small subset of papers for the majority of your analysis

User Query for Literature Review: {query}
List of Papers: {papers}
    """


VALIDATE_AND_EXTRACT_RELEVANT_CONTEXT_PROMPT = """
                You are analyzing a research paper to determine:
                1. Whether it is relevant to the given query
                2. If relevant, what specific information from the paper helps answer the query

                ### User Query
                {user_query}

                ### Paper Content
                {paper_text}
                
                ### Search Query
                {search_query}

                ### Instructions
                Given the user's query, the search query that led to this paper,
                and the paper content,
                First, determine if this paper is relevant to the query.
                If the paper is NOT relevant, respond with "NOT_RELEVANT".
                If it IS relevant, extract all pieces of information that are relevant to answering the user's query. 
                Return only the relevant context as plain text without commentary. Extract this text as is. 
                DO NOT ADD any extra word except for those that are part of the paper.
                This text would ideally be in methodology, results or abstract sections. 
                If you don't find any relevant context, just return `NOT_RELEVANT`. 
                """


