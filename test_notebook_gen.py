from app.services import notebook_service
from pathlib import Path
import json

def test_notebook_gen():
    test_data = [
        {
            "question": "What is the total sales?",
            "explanation": "I will sum the sales column.",
            "code": "df['sales'].sum()",
            "answer": "Total sales is 5000."
        },
        {
            "question": "Show top 5 products.",
            "explanation": "I will sort by sales descending and take top 5.",
            "code": "df.sort_values('sales', ascending=False).head(5)",
            "answer": "Top 5 products are A, B, C, D, E."
        }
    ]
    
    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "test_solved.ipynb"
    
    notebook_service.generate_jupyter_notebook(test_data, output_path)
    print(f"Notebook generated at: {output_path}")
    assert output_path.exists()
    
if __name__ == "__main__":
    test_notebook_gen()
