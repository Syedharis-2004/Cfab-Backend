import nbformat as nbf
from pathlib import Path
from typing import List, Dict
from app.utils.logger import logger

def fill_notebook_template(template_path: Path, questions_data: List[Dict], output_path: Path):
    """
    Reads an uploaded .ipynb template and injects AI-generated solutions.
    """
    logger.info(f"Filling notebook template: {template_path}")
    try:
        # Load the template
        with open(template_path, 'r', encoding='utf-8') as f:
            nb = nbf.read(f, as_version=4)
        
        # Add a separator if the template has content
        if nb.cells:
            nb.cells.append(nbf.v4.new_markdown_cell("---"))
            nb.cells.append(nbf.v4.new_markdown_cell("# AI Generated Solutions"))
        
        # Inject generated content
        for item in questions_data:
            # Question Markdown
            nb.cells.append(nbf.v4.new_markdown_cell(f"## Question: {item.get('question', 'N/A')}"))
            
            # Explanation Markdown
            nb.cells.append(nbf.v4.new_markdown_cell(f"### Analysis Approach\n{item.get('explanation', 'N/A')}"))
            
            # Code Cell
            code = item.get('code', '')
            if code:
                nb.cells.append(nbf.v4.new_code_cell(code))
            
            # Answer Markdown
            nb.cells.append(nbf.v4.new_markdown_cell(f"### Final Answer\n{item.get('answer', 'N/A')}"))
            
        # Save the completed notebook
        with open(output_path, 'w', encoding='utf-8') as f:
            nbf.write(nb, f)
            
        logger.info(f"Notebook successfully filled and saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error filling notebook template: {str(e)}")
        raise e
