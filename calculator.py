from flask import Flask, render_template_string, request, jsonify
import re
import math

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
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            transition: background 0.3s;
        }
        
        body.dark-mode {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        }
        
        .container {
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
            justify-content: center;
            align-items: flex-start;
            padding: 20px;
        }
        
        .header {
            position: absolute;
            top: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
        }
        
        .toggle-btn {
            background: linear-gradient(145deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.2) 100%);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 12px 18px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 700;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            font-size: 14px;
            letter-spacing: 0.5px;
        }
        
        .toggle-btn:hover {
            background: linear-gradient(145deg, rgba(255, 255, 255, 0.6) 0%, rgba(255, 255, 255, 0.4) 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        }
        
        .toggle-btn:active {
            transform: translateY(0);
        }
        
        .calculator-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 25px;
            width: 430px;
            transition: background 0.3s;
        }
        
        .dark-mode .calculator-container {
            background: #222;
            color: white;
        }
        
        .display-container {
            background: linear-gradient(145deg, #1a1a1a 0%, #0a0a0a 100%);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 25px;
            min-height: 100px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.5), inset 0 -2px 5px rgba(0, 0, 0, 0.3);
            border: 1px solid #333;
        }
        
        .dark-mode .display-container {
            background: linear-gradient(145deg, #111 0%, #000 100%);
            border: 1px solid #333;
        }
        
        .display-info {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            color: #666;
            margin-bottom: 8px;
        }
        
        .memory-indicator {
            background: linear-gradient(145deg, #667eea 0%, #5568d3 100%);
            color: white;
            padding: 3px 8px;
            border-radius: 5px;
            font-size: 11px;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }
        
        .expression {
            color: #555;
            font-size: 16px;
            text-align: right;
            word-wrap: break-word;
            word-break: break-all;
            min-height: 20px;
            font-weight: 500;
        }
        
        .dark-mode .expression {
            color: #888;
        }
        
        .display {
            color: #fff;
            font-size: 38px;
            text-align: right;
            word-wrap: break-word;
            word-break: break-all;
            min-height: 50px;
            display: flex;
            align-items: flex-end;
            justify-content: flex-end;
            font-weight: 600;
            letter-spacing: 1px;
        }
        
        .buttons {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 12px;
        }
        
        button {
            padding: 18px 12px;
            font-size: 16px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.15s ease;
            font-weight: 600;
            position: relative;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2), inset 0 -2px 0 rgba(0, 0, 0, 0.2);
            user-select: none;
            letter-spacing: 0.5px;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25), inset 0 -2px 0 rgba(0, 0, 0, 0.2);
        }
        
        button:active {
            transform: translateY(1px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15), inset 0 -1px 0 rgba(0, 0, 0, 0.2);
        }
        
        button:hover::after {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 110%;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            white-space: nowrap;
            margin-bottom: 8px;
            z-index: 1000;
            pointer-events: none;
            font-weight: 500;
        }
        
        .number {
            background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%);
            color: #212529;
            border: 1px solid #dee2e6;
        }
        
        .number:hover {
            background: linear-gradient(145deg, #ffffff 0%, #f0f3f7 100%);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15), inset 0 -2px 0 rgba(0, 0, 0, 0.2);
        }
        
        .number:active {
            background: linear-gradient(145deg, #e9ecef 0%, #dee2e6 100%);
        }
        
        .dark-mode .number {
            background: linear-gradient(145deg, #444 0%, #333 100%);
            color: #fff;
            border: 1px solid #555;
        }
        
        .dark-mode .number:hover {
            background: linear-gradient(145deg, #555 0%, #444 100%);
        }
        
        .dark-mode .number:active {
            background: linear-gradient(145deg, #333 0%, #222 100%);
        }
        
        .operator {
            background: linear-gradient(145deg, #667eea 0%, #5568d3 100%);
            color: white;
            border: 1px solid #4a52bf;
        }
        
        .operator:hover {
            background: linear-gradient(145deg, #7e8fef 0%, #6979e0 100%);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4), inset 0 -2px 0 rgba(0, 0, 0, 0.2);
        }
        
        .operator:active {
            background: linear-gradient(145deg, #5568d3 0%, #4a52bf 100%);
        }
        
        .dark-mode .operator {
            background: linear-gradient(145deg, #7e8fef 0%, #6979e0 100%);
        }
        
        .dark-mode .operator:hover {
            background: linear-gradient(145deg, #9aa5f7 0%, #8f99f0 100%);
        }
        
        .equals {
            background: linear-gradient(145deg, #48bb78 0%, #38a169 100%);
            color: white;
            grid-column: span 5;
            border: 1px solid #2f855a;
            font-size: 18px;
        }
        
        .equals:hover {
            background: linear-gradient(145deg, #5ac98f 0%, #48bb78 100%);
            box-shadow: 0 6px 20px rgba(72, 187, 120, 0.4), inset 0 -2px 0 rgba(0, 0, 0, 0.2);
        }
        
        .equals:active {
            background: linear-gradient(145deg, #38a169 0%, #2f855a 100%);
        }
        
        .dark-mode .equals:hover {
            background: linear-gradient(145deg, #68d391 0%, #5ac98f 100%);
        }
        
        .clear {
            background: linear-gradient(145deg, #f56565 0%, #e53e3e 100%);
            color: white;
            grid-column: span 2;
            border: 1px solid #c53030;
        }
        
        .clear:hover {
            background: linear-gradient(145deg, #fa8072 0%, #f56565 100%);
            box-shadow: 0 6px 20px rgba(245, 101, 101, 0.4), inset 0 -2px 0 rgba(0, 0, 0, 0.2);
        }
        
        .clear:active {
            background: linear-gradient(145deg, #e53e3e 0%, #c53030 100%);
        }
        
        .dark-mode .clear {
            background: linear-gradient(145deg, #fa8072 0%, #f56565 100%);
        }
        
        .dark-mode .clear:hover {
            background: linear-gradient(145deg, #ffb3b3 0%, #fa8072 100%);
        }
        
        .memory-btn {
            background: linear-gradient(145deg, #ed8936 0%, #dd6b20 100%);
            color: white;
            font-size: 14px;
            border: 1px solid #c05621;
        }
        
        .memory-btn:hover {
            background: linear-gradient(145deg, #f6ad55 0%, #ed8936 100%);
            box-shadow: 0 6px 20px rgba(237, 137, 54, 0.4), inset 0 -2px 0 rgba(0, 0, 0, 0.2);
        }
        
        .memory-btn:active {
            background: linear-gradient(145deg, #dd6b20 0%, #c05621 100%);
        }
        
        .dark-mode .memory-btn {
            background: linear-gradient(145deg, #f6ad55 0%, #ed8936 100%);
        }
        
        .dark-mode .memory-btn:hover {
            background: linear-gradient(145deg, #fcc28e 0%, #f6ad55 100%);
        }
        
        h1 {
            text-align: center;
            color: white;
            margin-bottom: 25px;
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -0.5px;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }
        
        .history-panel {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 25px;
            width: 300px;
            max-height: 600px;
            overflow-y: auto;
        }
        
        .dark-mode .history-panel {
            background: #222;
            color: white;
        }
        
        .history-panel h3 {
            margin-top: 0;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 12px;
            font-size: 16px;
            font-weight: 700;
        }
        
        .history-item {
            padding: 12px;
            margin: 8px 0;
            background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 8px;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid #dee2e6;
            font-weight: 500;
        }
        
        .dark-mode .history-item {
            background: linear-gradient(145deg, #333 0%, #2a2a2a 100%);
            border: 1px solid #444;
        }
        
        .history-item:hover {
            background: linear-gradient(145deg, #ffffff 0%, #f0f3f7 100%);
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        }
        
        .dark-mode .history-item:hover {
            background: linear-gradient(145deg, #444 0%, #3a3a3a 100%);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        .memory-display {
            background: linear-gradient(145deg, #fff3cd 0%, #ffe8a1 100%);
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 12px;
            font-size: 13px;
            font-weight: 700;
            text-align: center;
            border: 1px solid #ffc800;
            color: #856404;
            box-shadow: 0 3px 10px rgba(255, 200, 0, 0.2);
        }
        
        .dark-mode .memory-display {
            background: linear-gradient(145deg, #444 0%, #333 100%);
            color: #ffc107;
            border: 1px solid #555;
        }
        
        .clear-history {
            width: 100%;
            padding: 12px;
            margin-top: 15px;
            background: linear-gradient(145deg, #f56565 0%, #e53e3e 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        .clear-history:hover {
            background: linear-gradient(145deg, #fa8072 0%, #f56565 100%);
            box-shadow: 0 6px 20px rgba(245, 101, 101, 0.3);
        }
        
        .clear-history:active {
            transform: translateY(2px);
        }
        
        .function-group {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #eee;
        }
        
        .dark-mode .function-group {
            border-top: 1px solid #444;
        }
        
        .function-group-title {
            font-size: 12px;
            color: #999;
            text-transform: uppercase;
            margin-bottom: 8px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="header">
        <button class="toggle-btn" onclick="toggleAngleMode()" id="angleMode">DEG</button>
        <button class="toggle-btn" onclick="toggleDarkMode()">🌙</button>
    </div>
    
    <div class="container">
        <div>
            <h1>Advanced Calculator</h1>
            <div class="calculator-container">
                <div class="display-container">
                    <div class="display-info">
                        <span id="memoryIndicator" class="memory-indicator" style="display:none;">M: <span id="memoryValue">0</span></span>
                        <span id="angleIndicator">Degrees</span>
                    </div>
                    <div class="expression" id="expression"></div>
                    <div class="display" id="display">0</div>
                </div>
                <div class="buttons">
                    <!-- Row 1: Trig Functions -->
                    <button class="operator" onclick="trigFunction('sin')" data-tooltip="Sine">sin</button>
                    <button class="operator" onclick="trigFunction('asin')" data-tooltip="Inverse Sine">asin</button>
                    <button class="operator" onclick="trigFunction('cos')" data-tooltip="Cosine">cos</button>
                    <button class="operator" onclick="trigFunction('acos')" data-tooltip="Inverse Cosine">acos</button>
                    <button class="operator" onclick="trigFunction('tan')" data-tooltip="Tangent">tan</button>
                    
                    <!-- Row 2: Advanced Math -->
                    <button class="operator" onclick="squareRoot()" data-tooltip="Square Root">√</button>
                    <button class="operator" onclick="cubeRoot()" data-tooltip="Cube Root">∛</button>
                    <button class="operator" onclick="power()" data-tooltip="Power (x²)">x²</button>
                    <button class="operator" onclick="customPower()" data-tooltip="Power (x^y)">x^y</button>
                    <button class="operator" onclick="factorial()" data-tooltip="Factorial">!</button>
                    
                    <!-- Row 3: Logarithms & Constants -->
                    <button class="operator" onclick="logarithm()" data-tooltip="Log (base 10)">log</button>
                    <button class="operator" onclick="naturalLog()" data-tooltip="Natural Log">ln</button>
                    <button class="operator" onclick="appendConstant('π')" data-tooltip="Pi">π</button>
                    <button class="operator" onclick="appendConstant('e')" data-tooltip="Euler's number">e</button>
                    <button class="operator" onclick="reciprocal()" data-tooltip="Reciprocal (1/x)">1/x</button>
                    
                    <!-- Row 4: Memory Functions -->
                    <button class="memory-btn" onclick="memoryClear()" data-tooltip="Memory Clear">MC</button>
                    <button class="memory-btn" onclick="memoryRecall()" data-tooltip="Memory Recall">MR</button>
                    <button class="memory-btn" onclick="memoryAdd()" data-tooltip="Memory Add">M+</button>
                    <button class="memory-btn" onclick="memorySubtract()" data-tooltip="Memory Subtract">M-</button>
                    <button class="operator" onclick="modulo()" data-tooltip="Modulo">mod</button>
                    
                    <!-- Row 5: Basic Operations -->
                    <button class="clear" onclick="clearDisplay()" data-tooltip="Clear (Esc)">C</button>
                    <button class="operator" onclick="appendNumber('(')" data-tooltip="Left Paren">(</button>
                    <button class="operator" onclick="appendNumber(')')" data-tooltip="Right Paren">)</button>
                    <button class="operator" onclick="deleteLast()" data-tooltip="Delete (Backspace)">DEL</button>
                    <button class="operator" onclick="exponential()" data-tooltip="e^x">eˣ</button>
                    
                    <!-- Row 6: Numbers 7-9 -->
                    <button class="number" onclick="appendNumber('7')" data-tooltip="7">7</button>
                    <button class="number" onclick="appendNumber('8')" data-tooltip="8">8</button>
                    <button class="number" onclick="appendNumber('9')" data-tooltip="9">9</button>
                    <button class="operator" onclick="appendOperator('/')" data-tooltip="Divide">÷</button>
                    <button class="operator" onclick="percentage()" data-tooltip="Percentage">%</button>
                    
                    <!-- Row 7: Numbers 4-6 -->
                    <button class="number" onclick="appendNumber('4')" data-tooltip="4">4</button>
                    <button class="number" onclick="appendNumber('5')" data-tooltip="5">5</button>
                    <button class="number" onclick="appendNumber('6')" data-tooltip="6">6</button>
                    <button class="operator" onclick="appendOperator('*')" data-tooltip="Multiply">×</button>
                    <button class="operator" onclick="toggleSign()" data-tooltip="Toggle Sign">±</button>
                    
                    <!-- Row 8: Numbers 1-3 -->
                    <button class="number" onclick="appendNumber('1')" data-tooltip="1">1</button>
                    <button class="number" onclick="appendNumber('2')" data-tooltip="2">2</button>
                    <button class="number" onclick="appendNumber('3')" data-tooltip="3">3</button>
                    <button class="operator" onclick="appendOperator('-')" data-tooltip="Subtract">−</button>
                    <button class="operator" onclick="absolute()" data-tooltip="Absolute Value">|x|</button>
                    
                    <!-- Row 9: Zero, Decimal, Plus -->
                    <button class="number" onclick="appendNumber('0')" style="grid-column: span 2;" data-tooltip="0">0</button>
                    <button class="number" onclick="appendNumber('.')" data-tooltip="Decimal">.</button>
                    <button class="operator" onclick="appendOperator('+')" data-tooltip="Add">+</button>
                    
                    <!-- Row 10: Equals -->
                    <button class="equals" onclick="calculate()" data-tooltip="Calculate (Enter)" style="grid-column: span 5;">=</button>
                </div>
            </div>
        </div>
        
        <!-- History Panel -->
        <div class="history-panel">
            <h3>History</h3>
            <div id="historyList" style="min-height: 200px;"></div>
            <button class="clear-history" onclick="clearHistory()">Clear History</button>
        </div>
    </div>
    
    <script>
        let display = document.getElementById('display');
        let expressionDisplay = document.getElementById('expression');
        let currentInput = '0';
        let operator = null;
        let previousValue = null;
        let shouldResetDisplay = false;
        let operatorSymbol = null;
        let memory = 0;
        let angleMode = 'degrees'; // 'degrees' or 'radians'
        let history = [];
        let darkMode = false;
        
        // Load history from localStorage
        window.addEventListener('load', function() {
            const savedHistory = localStorage.getItem('calcHistory');
            if (savedHistory) {
                history = JSON.parse(savedHistory);
                updateHistoryDisplay();
            }
            const savedMemory = localStorage.getItem('calcMemory');
            if (savedMemory) {
                memory = parseFloat(savedMemory);
                updateMemoryIndicator();
            }
        });
        
        function toggleDarkMode() {
            darkMode = !darkMode;
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', darkMode);
        }
        
        function toggleAngleMode() {
            angleMode = angleMode === 'degrees' ? 'radians' : 'degrees';
            document.getElementById('angleMode').textContent = angleMode === 'degrees' ? 'DEG' : 'RAD';
            document.getElementById('angleIndicator').textContent = angleMode === 'degrees' ? 'Degrees' : 'Radians';
        }
        
        function updateMemoryIndicator() {
            const indicator = document.getElementById('memoryIndicator');
            const value = document.getElementById('memoryValue');
            if (memory !== 0) {
                indicator.style.display = 'inline-block';
                value.textContent = memory.toFixed(4);
            } else {
                indicator.style.display = 'none';
            }
            localStorage.setItem('calcMemory', memory);
        }
        
        function addToHistory(expression, result) {
            const item = expression + ' = ' + result;
            history.unshift(item);
            if (history.length > 50) history.pop();
            localStorage.setItem('calcHistory', JSON.stringify(history));
            updateHistoryDisplay();
        }
        
        function updateHistoryDisplay() {
            const list = document.getElementById('historyList');
            if (history.length === 0) {
                list.innerHTML = '<div style="color: #999; text-align: center; padding: 20px;">No history yet</div>';
                return;
            }
            list.innerHTML = history.map((item, index) => 
                `<div class="history-item" onclick="useHistoryItem('${item}')">${item}</div>`
            ).join('');
        }
        
        function useHistoryItem(item) {
            const parts = item.split(' = ');
            if (parts.length === 2) {
                currentInput = parts[1];
                updateDisplay();
            }
        }
        
        function clearHistory() {
            if (confirm('Clear all history?')) {
                history = [];
                localStorage.removeItem('calcHistory');
                updateHistoryDisplay();
            }
        }
        
        function memoryClear() {
            memory = 0;
            updateMemoryIndicator();
        }
        
        function memoryRecall() {
            currentInput = String(memory);
            shouldResetDisplay = true;
            updateDisplay();
        }
        
        function memoryAdd() {
            let num = parseFloat(currentInput);
            if (!isNaN(num)) {
                memory += num;
                updateMemoryIndicator();
                shouldResetDisplay = true;
            }
        }
        
        function memorySubtract() {
            let num = parseFloat(currentInput);
            if (!isNaN(num)) {
                memory -= num;
                updateMemoryIndicator();
                shouldResetDisplay = true;
            }
        }
        
        // Keyboard support
        document.addEventListener('keydown', function(event) {
            const key = event.key;
            
            if (key >= '0' && key <= '9') {
                appendNumber(key);
                event.preventDefault();
            }
            else if (key === '.') {
                appendNumber('.');
                event.preventDefault();
            }
            else if (key === '+') {
                appendOperator('+');
                event.preventDefault();
            }
            else if (key === '-') {
                appendOperator('-');
                event.preventDefault();
            }
            else if (key === '*') {
                appendOperator('*');
                event.preventDefault();
            }
            else if (key === '/') {
                appendOperator('/');
                event.preventDefault();
            }
            else if (key === 'Enter') {
                calculate();
                event.preventDefault();
            }
            else if (key === 'Escape') {
                clearDisplay();
                event.preventDefault();
            }
            else if (key === 'Backspace') {
                deleteLast();
                event.preventDefault();
            }
            else if (key === '(') {
                appendNumber('(');
                event.preventDefault();
            }
            else if (key === ')') {
                appendNumber(')');
                event.preventDefault();
            }
        });
        
        function updateDisplay() {
            display.textContent = currentInput;
            updateExpressionDisplay();
        }
        
        function updateExpressionDisplay() {
            if (previousValue === null) {
                expressionDisplay.textContent = '';
            } else {
                let expr = previousValue;
                if (operatorSymbol) {
                    expr += ' ' + operatorSymbol + ' ';
                    if (!shouldResetDisplay) {
                        expr += currentInput;
                    }
                }
                expressionDisplay.textContent = expr;
            }
        }
        
        function appendNumber(num) {
            if (shouldResetDisplay) {
                currentInput = num;
                shouldResetDisplay = false;
            } else {
                if (currentInput === '0' && num !== '.' && num !== '(' && num !== ')') {
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
            let opSymbol = op === '/' ? '÷' : op === '*' ? '×' : op;
            
            if (previousValue === null) {
                previousValue = currentInput;
            } else if (!shouldResetDisplay) {
                calculate();
                previousValue = display.textContent;
            }
            operator = op;
            operatorSymbol = opSymbol;
            shouldResetDisplay = true;
            updateExpressionDisplay();
        }
        
        function deleteLast() {
            if (!shouldResetDisplay && currentInput !== '0') {
                currentInput = currentInput.slice(0, -1);
                if (currentInput === '') {
                    currentInput = '0';
                }
                updateDisplay();
            }
        }
        
        function percentage() {
            try {
                let num = parseFloat(currentInput);
                if (!isNaN(num)) {
                    currentInput = String(num / 100);
                    updateDisplay();
                }
            } catch (e) {
                currentInput = 'Error';
                updateDisplay();
            }
        }
        
        function modulo() {
            if (previousValue === null) {
                previousValue = currentInput;
            } else if (!shouldResetDisplay) {
                calculate();
                previousValue = display.textContent;
            }
            operator = '%';
            operatorSymbol = 'mod';
            shouldResetDisplay = true;
            updateExpressionDisplay();
        }
        
        function absolute() {
            try {
                let num = parseFloat(currentInput);
                if (!isNaN(num)) {
                    currentInput = String(Math.abs(num));
                    updateDisplay();
                }
            } catch (e) {
                currentInput = 'Error';
                updateDisplay();
            }
        }
        
        function cubeRoot() {
            try {
                let num = parseFloat(currentInput);
                if (!isNaN(num)) {
                    currentInput = String(Math.cbrt(num));
                    shouldResetDisplay = true;
                    updateDisplay();
                }
            } catch (e) {
                currentInput = 'Error';
                updateDisplay();
            }
        }
        
        function naturalLog() {
            try {
                let num = parseFloat(currentInput);
                if (!isNaN(num) && num > 0) {
                    currentInput = String(Math.log(num));
                    shouldResetDisplay = true;
                    updateDisplay();
                } else {
                    currentInput = 'Error';
                    updateDisplay();
                }
            } catch (e) {
                currentInput = 'Error';
                updateDisplay();
            }
        }
        
        function customPower() {
            if (previousValue === null) {
                previousValue = currentInput;
            } else if (!shouldResetDisplay) {
                calculate();
                previousValue = display.textContent;
            }
            operator = '**';
            operatorSymbol = '^';
            shouldResetDisplay = true;
            updateExpressionDisplay();
        }
        
        function trigFunction(func) {
            try {
                let num = parseFloat(currentInput);
                if (!isNaN(num)) {
                    fetch('/trig', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({function: func, value: num, mode: angleMode})
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            currentInput = String(data.result);
                            shouldResetDisplay = true;
                            updateDisplay();
                        } else {
                            currentInput = 'Error';
                            updateDisplay();
                        }
                    });
                }
            } catch (e) {
                currentInput = 'Error';
                updateDisplay();
            }
        }
        
        function squareRoot() {
            try {
                let num = parseFloat(currentInput);
                if (!isNaN(num) && num >= 0) {
                    currentInput = String(Math.sqrt(num));
                    shouldResetDisplay = true;
                    updateDisplay();
                } else {
                    currentInput = 'Error';
                    updateDisplay();
                }
            } catch (e) {
                currentInput = 'Error';
                updateDisplay();
            }
        }
        
        function power() {
            try {
                let num = parseFloat(currentInput);
                if (!isNaN(num)) {
                    currentInput = String(num * num);
                    shouldResetDisplay = true;
                    updateDisplay();
                }
            } catch (e) {
                currentInput = 'Error';
                updateDisplay();
            }
        }
        
        function reciprocal() {
            try {
                let num = parseFloat(currentInput);
                if (!isNaN(num) && num !== 0) {
                    currentInput = String(1 / num);
                    shouldResetDisplay = true;
                    updateDisplay();
                } else {
                    currentInput = 'Error';
                    updateDisplay();
                }
            } catch (e) {
                currentInput = 'Error';
                updateDisplay();
            }
        }
        
        function exponential() {
            try {
                let num = parseFloat(currentInput);
                if (!isNaN(num)) {
                    currentInput = String(Math.exp(num));
                    shouldResetDisplay = true;
                    updateDisplay();
                }
            } catch (e) {
                currentInput = 'Error';
                updateDisplay();
            }
        }
        
        function factorial() {
            try {
                let num = parseInt(currentInput);
                if (num >= 0 && num <= 170 && Number.isInteger(num)) {
                    let result = 1;
                    for (let i = 2; i <= num; i++) {
                        result *= i;
                    }
                    currentInput = String(result);
                    shouldResetDisplay = true;
                    updateDisplay();
                } else {
                    currentInput = 'Error';
                    updateDisplay();
                }
            } catch (e) {
                currentInput = 'Error';
                updateDisplay();
            }
        }
        
        function logarithm() {
            try {
                let num = parseFloat(currentInput);
                if (!isNaN(num) && num > 0) {
                    currentInput = String(Math.log10(num));
                    shouldResetDisplay = true;
                    updateDisplay();
                } else {
                    currentInput = 'Error';
                    updateDisplay();
                }
            } catch (e) {
                currentInput = 'Error';
                updateDisplay();
            }
        }
        
        function appendConstant(constant) {
            if (constant === 'π') {
                currentInput = String(Math.PI);
                shouldResetDisplay = true;
                updateDisplay();
            } else if (constant === 'e') {
                currentInput = String(Math.E);
                shouldResetDisplay = true;
                updateDisplay();
            }
        }
        
        function clearDisplay() {
            currentInput = '0';
            operator = null;
            operatorSymbol = null;
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
            
            let expression = previousValue + operator + currentInput;
            
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
                    addToHistory(expressionDisplay.textContent, data.result);
                    operator = null;
                    operatorSymbol = null;
                    previousValue = null;
                    shouldResetDisplay = true;
                    updateDisplay();
                } else {
                    currentInput = 'Error';
                    operator = null;
                    operatorSymbol = null;
                    previousValue = null;
                    shouldResetDisplay = true;
                    updateDisplay();
                }
            })
            .catch(error => {
                currentInput = 'Error';
                operator = null;
                operatorSymbol = null;
                previousValue = null;
                shouldResetDisplay = true;
                updateDisplay();
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
        if not re.match(r'^[\d.+\-*/%()^\s]+$', expression):
            return jsonify({'success': False, 'error': 'Invalid expression'})
        
        # Replace × and ÷ with * and /
        expression = expression.replace('×', '*').replace('÷', '/')
        # Replace ^ with **
        expression = expression.replace('^', '**')
        # Handle modulo
        expression = expression.replace('%', '%')
        
        # Evaluate the expression safely
        result = eval(expression)
        
        # Round to avoid floating point errors
        if isinstance(result, float):
            result = round(result, 10)
        
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/trig', methods=['POST'])
def trigonometric_function():
    try:
        data = request.json
        func = data.get('function', '')
        value = data.get('value', 0)
        mode = data.get('mode', 'degrees')
        
        result = None
        
        # Convert to radians if mode is degrees
        if mode == 'degrees':
            rad_value = math.radians(value)
        else:
            rad_value = value
        
        if func == 'sin':
            result = math.sin(rad_value)
        elif func == 'cos':
            result = math.cos(rad_value)
        elif func == 'tan':
            result = math.tan(rad_value)
        elif func == 'asin':
            if -1 <= value <= 1:
                result = math.degrees(math.asin(value)) if mode == 'degrees' else math.asin(value)
            else:
                return jsonify({'success': False, 'error': 'asin domain error'})
        elif func == 'acos':
            if -1 <= value <= 1:
                result = math.degrees(math.acos(value)) if mode == 'degrees' else math.acos(value)
            else:
                return jsonify({'success': False, 'error': 'acos domain error'})
        elif func == 'atan':
            result = math.degrees(math.atan(value)) if mode == 'degrees' else math.atan(value)
        else:
            return jsonify({'success': False, 'error': 'Unknown function'})
        
        # Round to avoid floating point errors
        result = round(result, 10)
        
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
