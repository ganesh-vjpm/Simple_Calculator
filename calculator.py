from flask import Flask, render_template_string, request, jsonify
import re

app = Flask(__name__)

# HTML template for the calculator
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Arial', sans-serif;
        }
        
        .calculator-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 20px;
            width: 320px;
        }
        
        .display {
            background: #222;
            color: #fff;
            font-size: 32px;
            padding: 20px;
            border-radius: 10px;
            text-align: right;
            margin-bottom: 20px;
            word-wrap: break-word;
            word-break: break-all;
            min-height: 60px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
        }
        
        .buttons {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
        }
        
        button {
            padding: 20px;
            font-size: 18px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: bold;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .number {
            background: #f0f0f0;
            color: #333;
        }
        
        .number:hover {
            background: #e0e0e0;
        }
        
        .operator {
            background: #667eea;
            color: white;
        }
        
        .operator:hover {
            background: #5568d3;
        }
        
        .equals {
            background: #48bb78;
            color: white;
            grid-column: span 2;
        }
        
        .equals:hover {
            background: #38a169;
        }
        
        .clear {
            background: #f56565;
            color: white;
            grid-column: span 2;
        }
        
        .clear:hover {
            background: #e53e3e;
        }
        
        h1 {
            text-align: center;
            color: white;
            margin-bottom: 20px;
            font-size: 28px;
        }
    </style>
</head>
<body>
    <div>
        <h1>Calculator</h1>
        <div class="calculator-container">
            <div class="display" id="display">0</div>
            <div class="buttons">
                <button class="clear" onclick="clearDisplay()">C</button>
                <button class="operator" onclick="appendOperator('/')">÷</button>
                <button class="operator" onclick="appendOperator('*')">×</button>
                
                <button class="number" onclick="appendNumber('7')">7</button>
                <button class="number" onclick="appendNumber('8')">8</button>
                <button class="number" onclick="appendNumber('9')">9</button>
                <button class="operator" onclick="appendOperator('-')">−</button>
                
                <button class="number" onclick="appendNumber('4')">4</button>
                <button class="number" onclick="appendNumber('5')">5</button>
                <button class="number" onclick="appendNumber('6')">6</button>
                <button class="operator" onclick="appendOperator('+')">+</button>
                
                <button class="number" onclick="appendNumber('1')">1</button>
                <button class="number" onclick="appendNumber('2')">2</button>
                <button class="number" onclick="appendNumber('3')">3</button>
                <button class="operator" onclick="toggleSign()">±</button>
                
                <button class="number" onclick="appendNumber('0')" style="grid-column: span 2;">0</button>
                <button class="number" onclick="appendNumber('.')">.</button>
                <button class="equals" onclick="calculate()">=</button>
            </div>
        </div>
    </div>
    
    <script>
        let display = document.getElementById('display');
        let currentInput = '0';
        let operator = null;
        let previousValue = null;
        let shouldResetDisplay = false;
        
        function updateDisplay() {
            display.textContent = currentInput;
        }
        
        function appendNumber(num) {
            if (shouldResetDisplay) {
                currentInput = num;
                shouldResetDisplay = false;
            } else {
                if (currentInput === '0' && num !== '.') {
                    currentInput = num;
                } else if (num === '.' && currentInput.includes('.')) {
                    return;
                } else {
                    currentInput += num;
                }
            }
            updateDisplay();
        }
        
        function appendOperator(op) {
            if (previousValue === null) {
                previousValue = currentInput;
            } else if (!shouldResetDisplay) {
                calculate();
                previousValue = display.textContent;
            }
            operator = op;
            shouldResetDisplay = true;
        }
        
        function clearDisplay() {
            currentInput = '0';
            operator = null;
            previousValue = null;
            shouldResetDisplay = false;
            updateDisplay();
        }
        
        function toggleSign() {
            if (currentInput !== '0') {
                currentInput = currentInput.startsWith('-') ? currentInput.slice(1) : '-' + currentInput;
                updateDisplay();
            }
        }
        
        function calculate() {
            if (operator === null || previousValue === null) {
                return;
            }
            
            const expression = previousValue + operator + currentInput;
            
            fetch('/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({expression: expression})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentInput = String(data.result);
                    operator = null;
                    previousValue = null;
                    shouldResetDisplay = true;
                    updateDisplay();
                } else {
                    currentInput = 'Error';
                    operator = null;
                    previousValue = null;
                    shouldResetDisplay = true;
                    updateDisplay();
                }
            });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/calculate', methods=['POST'])
def calculate_expression():
    try:
        data = request.json
        expression = data.get('expression', '')
        
        # Validate expression to prevent code injection
        if not re.match(r'^[\d.+\-*/()\s]+$', expression):
            return jsonify({'success': False, 'error': 'Invalid expression'})
        
        # Replace × and ÷ with * and /
        expression = expression.replace('×', '*').replace('÷', '/')
        
        # Evaluate the expression safely
        result = eval(expression)
        
        # Round to avoid floating point errors
        if isinstance(result, float):
            result = round(result, 10)
        
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
