# Loan Optimizer

Loan Optimizer is a web-based financial application that optimizes loan allocation across facilities based on constraints and covenants. The app leverages Python, Dash, and Gurobi to preprocess data, assign loans, and visualize allocation metrics, all through an intuitive, user-friendly interface.

## Features

- Upload CSV files for loans, facilities, and optimization order.
- Preprocess loan data and assign loans to facilities using custom constraints and optimization logic.
- Visualize facility budget utilization with dynamic, dark-themed charts.
- Download processed data as CSV files.
- Authentication mechanism for secure access.
- Modern, responsive UI built with Dash and Bootstrap.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/loan-optimizer.git
   cd loan-optimizer
    ```

2. Create a virtual environment:
    ```bash
        python -m venv loan-optimizer-env
        source loan-optimizer-env/bin/activate  # On Windows: loan-optimizer-env\Scripts\activate
    ```

3. Install dependencies:
    ```bash
        pip install -r requirements.txt
    ```

4. Obtain Gurobi License: 
    - Follow [Gurobi License Instructions](https://support.gurobi.com/hc/en-us/articles/12684663118993-How-do-I-obtain-a-Gurobi-license) to get Gurobipy working on your system. 

## Usage 
1. Run the application 
```bash
    python app/app.py
```
2. Open the app in your browser
3. Upload your CSV files, according to instruction
4. View Metrics and visualizations:
    - Facility budget utilization by loan value.
    - Facility budget utilization by loan type.
5. Download the loan allocation data by clicking on the Download button.

## Technologies Used 
- Backend: Python, Gurobipy
- Frontend: Dash, Plotly

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Disclaimer:** This application is provided "as is," without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the application or the use or other dealings in the application.

