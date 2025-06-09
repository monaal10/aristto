import os

import pandas as pd
from rapidfuzz import process

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
csv_path = os.path.join(parent_dir, "modules", "jqr.csv")

def apply_publication_filter(paper, user_publication_names, sjr_requested):
    try:
        if paper.publication:
            paper_publication_names = [paper.publication]
            if user_publication_names and len(user_publication_names) > 0:
                if match_publications(user_publication_names, paper_publication_names):
                   return True
            elif sjr_requested and len(sjr_requested) > 0:
                sjr = get_sjr_rank_fuzzy_search(paper_publication_names)
                if sjr in sjr_requested:
                    return True
            else:
                return True
        return False
    except Exception as e:
        raise f"Could not get apply publication filter {e}"


def match_publications(user_requested_publications, paper_publications, threshold=80):
    """
    Performs fuzzy matching between two lists of publications to find matches.

    Args:
        user_requested_publications (list): List of publication names requested by the user
        paper_publications (list): List of publication names from papers
        threshold (int): Minimum similarity score to consider a match (0-100)

    Returns:
        dict: Dictionary containing matched publications with their scores
    """
    try:
        matches = {}
        user_requested_publications = [pub.lower().strip() for pub in user_requested_publications]
        paper_publications = [pub.lower().strip() for pub in paper_publications]
        # For each requested publication
        for requested_pub in user_requested_publications:
            # Find the best match among paper publications
            best_match, score, _ = process.extractOne(requested_pub, paper_publications)

            # If the match score is above threshold, return True
            if score >= threshold:
              return True
        return False

    except Exception as e:
        raise Exception(f"Error in matching publications: {str(e)}")


def get_sjr_rank_fuzzy_search(journal_names, threshold=80):
    try:

        df = pd.read_csv(csv_path)
        for journal in journal_names:
            # Find the closest match in the 'title' column
            best_match, score, temp = process.extractOne(journal, df['title'])

            # If the match score is above the threshold, we consider it a valid match
            if score >= threshold:
                # Retrieve the corresponding SJR value
                sjr_value = df[df['title'] == best_match]['sjr'].values[0]
                return sjr_value
        return ''
    except Exception as e:
        raise f"Could not get sjr rank fuzzy search {e}"
