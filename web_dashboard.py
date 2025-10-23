"""
Play-to-Earn Web Dashboard (Fixed)
Flask web interface to visualize blockchain tokens and game progress
"""

from flask import Flask, render_template_string, jsonify
from web3 import Web3
import json

app = Flask(__name__)

# Blockchain Configuration
RPC_URL = "https://rpc-mumbai.maticvigil.com"  # Polygon Mumbai RPC
CONTRACT_ADDRESS = "0xf8e81D47203A594245E36C48e151709F0C19fBe8"
PLAYER_WALLET = "0x461c676225b325142b30fBd6e2BcB99E22177577"

CONTRACT_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Game data
game_data = {
    "player_name": "Player",
    "level": 1,
    "tokens": 0,
    "tasks": [
        {"id": 1, "title": "Complete Daily Login", "reward": 10, "completed": False, "difficulty": "Easy"},
        {"id": 2, "title": "Complete 5 Tasks", "reward": 25, "completed": False, "difficulty": "Medium"},
        {"id": 3, "title": "Reach Level 5", "reward": 50, "completed": False, "difficulty": "Hard"}
    ]
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Play-to-Earn Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }
        
        .token-value {
            color: #f59e0b;
        }
        
        .level-value {
            color: #ec4899;
        }
        
        .tasks-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        
        .tasks-section h2 {
            color: #333;
            margin-bottom: 25px;
            font-size: 1.8em;
        }
        
        .tasks-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .task-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 12px;
            padding: 20px;
            border-left: 5px solid #667eea;
            transition: all 0.3s;
        }
        
        .task-card.completed {
            background: linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%);
            border-left-color: #10b981;
        }
        
        .task-card:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .task-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 12px;
        }
        
        .task-title {
            font-weight: bold;
            color: #333;
            font-size: 1.1em;
        }
        
        .task-difficulty {
            font-size: 0.8em;
            padding: 4px 12px;
            border-radius: 20px;
            background: white;
            color: #667eea;
            font-weight: 600;
        }
        
        .task-difficulty.easy {
            background: #dcfce7;
            color: #16a34a;
        }
        
        .task-difficulty.medium {
            background: #fef3c7;
            color: #b45309;
        }
        
        .task-difficulty.hard {
            background: #fee2e2;
            color: #dc2626;
        }
        
        .task-reward {
            color: #f59e0b;
            font-weight: bold;
            font-size: 1.2em;
            margin-top: 10px;
        }
        
        .task-status {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid rgba(0,0,0,0.1);
            color: #666;
            font-size: 0.9em;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
        }
        
        .status-badge.completed {
            background: #10b981;
            color: white;
        }
        
        .status-badge.pending {
            background: #f59e0b;
            color: white;
        }
        
        .wallet-info {
            background: rgba(255,255,255,0.1);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 0.9em;
            word-break: break-all;
        }
        
        .wallet-label {
            opacity: 0.8;
            margin-bottom: 5px;
        }
        
        .status-box {
            background: rgba(255,255,255,0.1);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 0.9em;
        }
        
        .status-box.error {
            background: rgba(220,38,38,0.3);
            border: 1px solid rgba(220,38,38,0.5);
        }
        
        .status-box.success {
            background: rgba(16,185,129,0.3);
            border: 1px solid rgba(16,185,129,0.5);
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: background 0.3s;
            margin-bottom: 20px;
        }
        
        .refresh-btn:hover {
            background: #764ba2;
        }
        
        @media (max-width: 768px) {
            h1 {
                font-size: 1.8em;
            }
            
            .stat-value {
                font-size: 2em;
            }
            
            .tasks-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎮 Play-to-Earn Dashboard</h1>
            <p>Track your blockchain tokens in real-time</p>
        </header>
        
        <div class="wallet-info">
            <div class="wallet-label">📍 Your Wallet:</div>
            <div id="wallet-address">Loading...</div>
        </div>
        
        <div id="status-box" class="status-box" style="display: none;"></div>
        
        <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Balance</button>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Blockchain Tokens</div>
                <div class="stat-value token-value" id="token-balance">0</div>
                <div style="margin-top: 10px; color: #999; font-size: 0.9em;">On Ganache</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Current Level</div>
                <div class="stat-value level-value" id="player-level">1</div>
                <div style="margin-top: 10px; color: #999; font-size: 0.9em;">⭐ Experience</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Tasks Completed</div>
                <div class="stat-value" id="completed-tasks">0</div>
                <div style="margin-top: 10px; color: #999; font-size: 0.9em;">Out of 3</div>
            </div>
        </div>
        
        <div class="tasks-section">
            <h2>📋 Available Tasks</h2>
            <div class="tasks-grid" id="tasks-container">
                Loading tasks...
            </div>
        </div>
    </div>
    
    <script>
        const WALLET = "{{ wallet }}";
        const CONTRACT = "{{ contract }}";
        
        function showStatus(message, isError = false) {
            const statusBox = document.getElementById('status-box');
            statusBox.textContent = message;
            statusBox.className = isError ? 'status-box error' : 'status-box success';
            statusBox.style.display = 'block';
            setTimeout(() => {
                statusBox.style.display = 'none';
            }, 5000);
        }
        
        function displayWallet() {
            document.getElementById('wallet-address').textContent = WALLET;
        }
        
        function renderTasks(tasks) {
            const container = document.getElementById('tasks-container');
            container.innerHTML = tasks.map(task => `
                <div class="task-card ${task.completed ? 'completed' : ''}">
                    <div class="task-header">
                        <div class="task-title">${task.title}</div>
                        <div class="task-difficulty ${task.difficulty.toLowerCase()}">
                            ${task.difficulty}
                        </div>
                    </div>
                    <div class="task-reward">+${task.reward} P2E Tokens</div>
                    <div class="task-status">
                        <span class="status-badge ${task.completed ? 'completed' : 'pending'}">
                            ${task.completed ? '✅ Completed' : '⏳ Pending'}
                        </span>
                    </div>
                </div>
            `).join('');
        }
        
        async function refreshData() {
            try {
                const response = await fetch('/api/balance');
                const data = await response.json();
                
                if (data.error) {
                    showStatus('⚠️ ' + data.error, true);
                    document.getElementById('token-balance').textContent = 'Error';
                } else {
                    document.getElementById('token-balance').textContent = data.balance;
                    document.getElementById('player-level').textContent = data.level;
                    document.getElementById('completed-tasks').textContent = data.completed_tasks;
                    renderTasks(data.tasks);
                    showStatus('✅ Data refreshed successfully!', false);
                }
            } catch (error) {
                console.error('Error fetching data:', error);
                showStatus('❌ Connection failed. Is the server running on port 5000?', true);
            }
        }
        
        // Initial load
        displayWallet();
        refreshData();
        
        // Auto-refresh every 10 seconds
        setInterval(refreshData, 10000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(
        HTML_TEMPLATE,
        wallet=PLAYER_WALLET,
        contract=CONTRACT_ADDRESS
    )

@app.route('/api/balance')
def get_balance():
    try:
        # Check if connected to Ganache
        if not w3.is_connected():
            return jsonify({
                "error": "Not connected to blockchain. Is Ganache running on port 8545?"
            }), 500
        
        try:
            # Try to get contract balance
            contract = w3.eth.contract(
                address=Web3.to_checksum_address(CONTRACT_ADDRESS),
                abi=CONTRACT_ABI
            )
            balance = contract.functions.balanceOf(Web3.to_checksum_address(PLAYER_WALLET)).call()
        except Exception as contract_error:
            # If contract call fails, show wallet balance instead
            balance = w3.eth.get_balance(Web3.to_checksum_address(PLAYER_WALLET))
            print(f"Contract call failed: {str(contract_error)}")
            print(f"Showing ETH wallet balance instead: {balance} Wei")
        
        return jsonify({
            "balance": balance,
            "level": game_data["level"],
            "completed_tasks": sum(1 for t in game_data["tasks"] if t["completed"]),
            "tasks": game_data["tasks"]
        })
    except Exception as e:
        print(f"Error in get_balance: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/update-task/<int:task_id>')
def update_task(task_id):
    for task in game_data["tasks"]:
        if task["id"] == task_id:
            task["completed"] = True
            break
    return jsonify({"status": "updated"})

if __name__ == '__main__':
    print("Starting Play-to-Earn Web Dashboard...")
    print(f"RPC URL: {RPC_URL}")
    print(f"Contract: {CONTRACT_ADDRESS}")
    print(f"Player Wallet: {PLAYER_WALLET}")
    print("Open your browser and go to: http://localhost:5000")
    print("Make sure Ganache is running on port 8545!")
    app.run(debug=True, port=5000)