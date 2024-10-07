def reciprocal_rank_fusion(keyword_rankings, semantic_rankings):
    """
    Combines rankings from keyword and semantic search using reciprocal rank fusion logic.

    Arguments:
    keyword_rankings -- dict with document IDs as keys and their ranks in keyword search as values
    semantic_rankings -- dict with document IDs as keys and their ranks in semantic search as values
    
    Returns:
    Combined reciprocal rank fusion score for each document.
    """
     
    fusion_scores = {}
    
    
    all_docs = set(keyword_rankings.keys()).union(set(semantic_rankings.keys()))
    
    for doc in all_docs:
         
        rank_kw = keyword_rankings.get(doc, float('inf'))
        rank_sem = semantic_rankings.get(doc, float('inf'))
     
        fusion_scores[doc] = 1 / (1 + abs(rank_kw - rank_sem))
    
    return fusion_scores
