"""
Play-to-Earn Game with Blockchain Integration (Ethereum/Polygon)
This game integrates Web3 to interact with a smart contract and mint real tokens
"""

import json
from datetime import datetime
from typing import List, Dict
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

# ============= BLOCKCHAIN CONFIGURATION =============
class BlockchainConfig:
    # For Local Ganache
    RPC_URL = "http://127.0.0.1:8545"
    CHAIN_ID = 1337
    
    # Smart Contract ABI (simplified ERC-20 token contract)
    CONTRACT_ABI = [
        {
            "inputs": [{"internalType": "address", "name": "player", "type": "address"}, 
                       {"internalType": "uint256", "name": "amount", "type": "uint256"}],
            "name": "awardTokens",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "address", "name": "to", "type": "address"},
                       {"internalType": "uint256", "name": "amount", "type": "uint256"}],
            "name": "transfer",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]


class PlayToEarnGame:
    def __init__(self, contract_address: str, player_wallet: str, private_key: str):
        """Initialize game with blockchain connection"""
        self.player_name = ""
        self.player_wallet = Web3.to_checksum_address(player_wallet)
        self.private_key = private_key
        self.tokens = 0
        self.level = 1
        self.blockchain_tokens = 0  # Actual tokens on blockchain
        
        self.tasks = [
            {"id": 1, "title": "Complete Daily Login", "reward": 10, "completed": False, "difficulty": "Easy", "tx_hash": None},
            {"id": 2, "title": "Complete 5 Tasks", "reward": 25, "completed": False, "difficulty": "Medium", "tx_hash": None},
            {"id": 3, "title": "Reach Level 5", "reward": 50, "completed": False, "difficulty": "Hard", "tx_hash": None}
        ]
        self.next_task_id = 4
        
        # Initialize Web3 connection
        self.w3 = Web3(Web3.HTTPProvider(BlockchainConfig.RPC_URL))
        
        if not self.w3.is_connected():
            raise Exception("❌ Failed to connect to blockchain! Check your internet connection.")
        
        print("✅ Connected to Polygon Mumbai Testnet")
        
        # Initialize smart contract
        try:
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=BlockchainConfig.CONTRACT_ABI
            )
            print(f"✅ Connected to smart contract: {contract_address}\n")
        except Exception as e:
            raise Exception(f"❌ Contract initialization failed: {e}")
    
    def start_game(self, name: str):
        """Initialize the game with player name"""
        if not name.strip():
            print("❌ Invalid player name!")
            return False
        self.player_name = name
        print(f"\n🎮 Welcome to Blockchain Play-to-Earn, {self.player_name}!")
        print(f"📍 Your Wallet: {self.player_wallet}")
        print("Complete tasks to earn ERC-20 tokens on the blockchain!\n")
        return True
    
    def sync_blockchain_balance(self):
        """Check balance on blockchain"""
        try:
            balance = self.contract.functions.balanceOf(self.player_wallet).call()
            self.blockchain_tokens = balance
            print(f"✅ Synced balance from blockchain: {balance} tokens")
        except Exception as e:
            print(f"⚠️  Could not sync balance: {e}")
    
    def display_stats(self):
        """Display current player statistics"""
        print("\n" + "="*60)
        print(f"👤 Player: {self.player_name}")
        print(f"🔐 Wallet: {self.player_wallet}")
        print(f"💰 Local Tokens: {self.tokens} | 🔗 Blockchain Tokens: {self.blockchain_tokens}")
        print(f"⭐ Level: {self.level}")
        completed = len([t for t in self.tasks if t["completed"]])
        print(f"✅ Tasks Completed: {completed}/{len(self.tasks)}")
        print("="*60 + "\n")
    
    def display_tasks(self):
        """Show all available tasks"""
        print("📋 AVAILABLE TASKS:\n")
        for task in self.tasks:
            status = "✅" if task["completed"] else "⭕"
            tx_info = f" [TxHash: {task['tx_hash'][:10]}...]" if task['tx_hash'] else ""
            print(f"{status} [{task['id']}] {task['title']}{tx_info}")
            print(f"   Difficulty: {task['difficulty']} | Reward: +{task['reward']} tokens")
            print()
    
    def complete_task(self, task_id: int):
        """Complete a task and mint tokens on blockchain"""
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        
        if not task:
            print("❌ Task not found!")
            return False
        
        if task["completed"]:
            print("⚠️  This task is already completed!")
            return False
        
        # Mark task as completed locally
        task["completed"] = True
        self.tokens += task["reward"]
        
        print(f"\n⏳ Completing task: {task['title']}...")
        print(f"💰 Reward: +{task['reward']} tokens")
        
        # Send transaction to blockchain
        try:
            tx_hash = self.mint_tokens_on_blockchain(task['reward'])
            task["tx_hash"] = tx_hash
            self.blockchain_tokens += task['reward']
            
            print(f"🎉 Task completed and tokens minted on blockchain!")
            print(f"📤 Transaction Hash: {tx_hash}")
            
            # Check for level up
            completed_count = len([t for t in self.tasks if t["completed"]])
            if completed_count % 2 == 0:
                self.level += 1
                print(f"🚀 LEVEL UP! You are now Level {self.level}!")
            
            return True
            
        except Exception as e:
            print(f"❌ Blockchain transaction failed: {e}")
            task["completed"] = False
            self.tokens -= task['reward']
            return False
    
    def mint_tokens_on_blockchain(self, amount: int) -> str:
        """Mint tokens by calling smart contract"""
        try:
            # Get current gas price and nonce
            gas_price = self.w3.eth.gas_price
            nonce = self.w3.eth.get_transaction_count(self.player_wallet)
            
            # Build transaction
            tx = self.contract.functions.awardTokens(
                self.player_wallet,
                amount
            ).build_transaction({
                'from': self.player_wallet,
                'gas': 300000,
                'gasPrice': gas_price,
                'nonce': nonce,
            })
            
            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            
            # Send transaction - use correct attribute name
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Wait for receipt
            print("⏳ Waiting for transaction confirmation...")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt['status'] == 1:
                return self.w3.to_hex(tx_hash)
            else:
                raise Exception("Transaction failed on blockchain")
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception(f"Minting failed: {str(e)}")
    
    def add_custom_task(self, title: str, reward: int):
        """Add a custom task"""
        if not title.strip():
            print("❌ Task title cannot be empty!")
            return False
        
        if reward <= 0:
            print("❌ Reward must be positive!")
            return False
        
        new_task = {
            "id": self.next_task_id,
            "title": title,
            "reward": reward,
            "completed": False,
            "difficulty": "Custom",
            "tx_hash": None
        }
        self.tasks.append(new_task)
        self.next_task_id += 1
        print(f"✨ New task added: {title} (+{reward} tokens)")
        return True
    
    def delete_task(self, task_id: int):
        """Delete a task (only if not completed)"""
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        
        if not task:
            print("❌ Task not found!")
            return False
        
        if task["completed"]:
            print("⚠️  Cannot delete completed tasks!")
            return False
        
        self.tasks.remove(task)
        print(f"🗑️  Task deleted: {task['title']}")
        return True
    
    def get_game_summary(self):
        """Get overall game summary"""
        total_potential_tokens = sum(t["reward"] for t in self.tasks)
        completed = len([t for t in self.tasks if t["completed"]])
        
        print("\n" + "="*60)
        print("🏆 GAME SUMMARY")
        print("="*60)
        print(f"Total Tasks: {len(self.tasks)}")
        print(f"Completed: {completed}")
        print(f"Local Tokens: {self.tokens}/{total_potential_tokens}")
        print(f"Blockchain Tokens: {self.blockchain_tokens}")
        print(f"Completion Rate: {(completed/len(self.tasks)*100):.1f}%")
        print("="*60 + "\n")
    
    def save_progress(self, filename: str = "game_progress.json"):
        """Save game progress to file"""
        data = {
            "player_name": self.player_name,
            "player_wallet": self.player_wallet,
            "tokens": self.tokens,
            "blockchain_tokens": self.blockchain_tokens,
            "level": self.level,
            "tasks": self.tasks,
            "saved_at": datetime.now().isoformat()
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Progress saved to {filename}")


def main():
    """Main game loop with blockchain integration"""
    
    print("\n" + "="*60)
    print("🎮 BLOCKCHAIN PLAY-TO-EARN GAME 🎮")
    print("="*60)
    print("Complete tasks to earn ERC-20 tokens on Polygon network!\n")
    
    # Get blockchain credentials
    print("🔐 BLOCKCHAIN SETUP")
    print("-" * 60)
    
    contract_address = input("Enter Smart Contract Address (deployed): ").strip()
    player_wallet = input("Enter your Ethereum wallet address: ").strip()
    private_key = input("Enter your wallet private key (⚠️ Keep it secret!): ").strip()
    
    if not all([contract_address, player_wallet, private_key]):
        print("❌ Missing blockchain credentials!")
        return
    
    # Initialize game
    try:
        game = PlayToEarnGame(contract_address, player_wallet, private_key)
    except Exception as e:
        print(f"❌ Game initialization failed: {e}")
        return
    
    # Get player name
    print("\n")
    while True:
        name = input("Enter your player name: ").strip()
        if game.start_game(name):
            break
    
    # Main game loop
    while True:
        game.display_stats()
        game.display_tasks()
        
        print("\n📌 COMMANDS:")
        print("  'complete <id>' - Complete a task and mint tokens")
        print("  'sync' - Sync balance from blockchain")
        print("  'add' - Add a custom task")
        print("  'delete <id>' - Delete a task")
        print("  'summary' - View game summary")
        print("  'save' - Save progress")
        print("  'quit' - Exit game\n")
        
        command = input("Enter command: ").strip().lower().split()
        
        if not command:
            print("❌ Please enter a command!")
            continue
        
        action = command[0]
        
        if action == "complete":
            if len(command) > 1:
                try:
                    task_id = int(command[1])
                    game.complete_task(task_id)
                except ValueError:
                    print("❌ Invalid task ID!")
            else:
                print("❌ Please provide a task ID!")
        
        elif action == "sync":
            game.sync_blockchain_balance()
        
        elif action == "add":
            title = input("Enter task title: ").strip()
            try:
                reward = int(input("Enter reward (tokens): "))
                game.add_custom_task(title, reward)
            except ValueError:
                print("❌ Invalid reward amount!")
        
        elif action == "delete":
            if len(command) > 1:
                try:
                    task_id = int(command[1])
                    game.delete_task(task_id)
                except ValueError:
                    print("❌ Invalid task ID!")
            else:
                print("❌ Please provide a task ID!")
        
        elif action == "summary":
            game.get_game_summary()
        
        elif action == "save":
            game.save_progress()
        
        elif action == "quit":
            print("\n👋 Thanks for playing! Your tokens are on the blockchain. Goodbye!")
            break
        
        else:
            print("❌ Unknown command!")


if __name__ == "__main__":
    main()