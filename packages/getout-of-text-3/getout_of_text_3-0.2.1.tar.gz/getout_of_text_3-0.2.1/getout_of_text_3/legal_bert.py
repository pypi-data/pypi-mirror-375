"""
Legal-BERT module for getout_of_text_3
Provides masked language modeling capabilities using Legal-BERT pipeline
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from transformers import pipeline
from typing import List, Dict, Optional, Any


# Global pipeline instance (lazy loaded)
_pipe = None


def _get_pipeline(model_name: str = "nlpaueb/legal-bert-base-uncased"):
    """Get or create the Legal-BERT pipeline"""
    global _pipe
    if _pipe is None:
        _pipe = pipeline("fill-mask", model=model_name)
    return _pipe


def pipe(statement: str, masked_token: Optional[str] = None, 
         token_mask: str = '[MASK]', top_k: int = 5, 
         visualize: bool = True) -> List[Dict[str, Any]]:
    """
    Legal-BERT pipeline for masked language modeling
    
    Args:
        statement (str): The legal text with masked token(s)
        masked_token (str, optional): The actual token for display purposes
        token_mask (str): The mask token to replace (default: '[MASK]')
        top_k (int): Number of top predictions to return
        visualize (bool): Whether to show visualization
        
    Returns:
        List[Dict]: List of predictions with token_str, score, and other metadata
        
    Raises:
        ValueError: If token_mask is not found in statement
        
    Example:
        >>> import getout_of_text_3 as got3
        >>> statement = "The court ruled that the contract was [MASK]."
        >>> results = got3.embedding.legal_bert.pipe(statement, masked_token='valid')
    """
    if token_mask not in statement:
        raise ValueError(f"The token_mask '{token_mask}' is not in the statement.")
    
    # Get the pipeline and make predictions
    legal_bert_pipeline = _get_pipeline()
    results = legal_bert_pipeline(statement, top_k=top_k)
    
    if visualize:
        _visualize_predictions(results, statement, masked_token, token_mask)
    
    return results


def _visualize_predictions(results: List[Dict], statement: str, 
                         masked_token: Optional[str] = None, 
                         token_mask: str = '[MASK]', 
                         figsize: tuple = (8, 4)) -> None:
    """Create a visualization of masked token predictions"""
    # Extract token strings and scores
    tokens = [result['token_str'] for result in results]
    scores = [result['score'] for result in results]
    
    # Create DataFrame and sort by score descending
    df = pd.DataFrame({'token': tokens, 'score': scores})
    df = df.sort_values('score', ascending=False)
    
    # Set modern style
    sns.set_palette("viridis")
    
    # Create a horizontal bar plot
    plt.figure(figsize=figsize)
    bars = plt.barh(df['token'], df['score'], 
                   color=sns.color_palette("viridis", len(df)), 
                   edgecolor='white', linewidth=0.8)
    
    plt.xlabel('Prediction Score', fontsize=11)
    plt.ylabel('Predicted Tokens', fontsize=11)
    plt.title('Legal-BERT Masked Token Predictions', fontsize=12, fontweight='bold', pad=15)
    
    # Add subtitle with the statement
    if masked_token:
        display_statement = statement.replace(token_mask, f' [{masked_token}] ')
    else:
        display_statement = statement
        
    plt.suptitle(f"Statement: {display_statement}", 
                fontsize=10, fontweight='bold', y=-0.05, color='blue')
    
    # Add score labels on the bars
    for i, (token, score) in enumerate(zip(df['token'], df['score'])):
        plt.text(score + 0.005, i, f'{score:.3f}', 
                va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.show()
    
    # Print results
    print("Top predictions for masked token (highest to lowest):")
    for i, (_, row) in enumerate(df.iterrows(), 1):
        print(f"{i}. '{row['token']}' - Score: {row['score']:.4f}")


def get_best_prediction(statement: str, token_mask: str = '[MASK]') -> Dict[str, Any]:
    """Get the top prediction for a masked token
    
    Args:
        statement (str): The legal text with masked token(s)
        token_mask (str): The mask token to replace (default: '[MASK]')
        
    Returns:
        Dict: The top prediction with token_str, score, and other metadata
    """
    results = pipe(statement, token_mask=token_mask, top_k=1, visualize=False)
    return results[0] if results else None


# Legacy compatibility - redirect to pipe function
def legal_bert(*args, **kwargs):
    """Legacy function - redirects to pipe()"""
    return pipe(*args, **kwargs)
