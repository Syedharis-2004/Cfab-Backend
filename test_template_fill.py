import nbformat as nbf
from app.services import notebook_template_service
from pathlib import Path

def test_template_filling():
    # 1. Create a mock template
    nb = nbf.v4.new_notebook()
    nb.cells.append(nbf.v4.new_markdown_cell("# Original Template Content"))
    template_path = Path("mock_template.ipynb")
    with open(template_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
        
    # 2. Mock questions data
    test_data = [
        {
            "question": "What is total sales?",
            "explanation": "Summing sales column.",
            "code": "df['sales'].sum()",
            "answer": "Total is 500."
        }
    ]
    
    # 3. Fill template
    output_path = Path("filled_mock.ipynb")
    notebook_template_service.fill_notebook_template(template_path, test_data, output_path)
    
    # 4. Verify
    with open(output_path, 'r', encoding='utf-8') as f:
        filled_nb = nbf.read(f, as_version=4)
    
    print(f"Cells in filled notebook: {len(filled_nb.cells)}")
    assert len(filled_nb.cells) > 1
    assert "Original Template Content" in filled_nb.cells[0].source
    print("Verification Successful!")

if __name__ == "__main__":
    test_template_filling()
    # Cleanup
    if Path("mock_template.ipynb").exists(): Path("mock_template.ipynb").unlink()
    if Path("filled_mock.ipynb").exists(): Path("filled_mock.ipynb").unlink()
