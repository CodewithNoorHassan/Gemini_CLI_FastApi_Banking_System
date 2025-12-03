from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any

app = FastAPI()

# In-memory storage for demonstration purposes
# In a real application, this would be a database
users_db: List[Dict[str, Any]] = []

class User(BaseModel):
    name: str
    pin_number: str
    bank_balance: float = Field(default=1000.0)

class Transfer(BaseModel):
    sender: str
    recipient_name: str
    amount: float

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI authentication and banking service!"}

@app.post("/authenticate")
async def authenticate_user(user: User):
    # Check if the user already exists (by name, case-insensitive)
    existing_user_index = next((i for i, u in enumerate(users_db) if u["name"].lower() == user.name.lower()), None)

    if existing_user_index is not None:
        existing_user = users_db[existing_user_index]
        # User exists, attempt to log in
        if existing_user["pin_number"] == user.pin_number:
            return {
                "message": f"Welcome back, {user.name}!",
                "bank_balance": f"${existing_user['bank_balance']:.2f}"
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials.")
    else:
        # User does not exist, create a new one
        user_data = user.dict()
        # Set a default balance for new users if not provided
        if 'bank_balance' not in user_data or user_data['bank_balance'] is None:
            user_data['bank_balance'] = 1000.0
        
        users_db.append(user_data)
        return {
            "message": f"User '{user.name}' registered and authenticated with an initial balance of ${user_data['bank_balance']:.2f}.",
            "bank_balance": f"${user_data['bank_balance']:.2f}"
        }

@app.get("/users")
async def get_users():
    return users_db

@app.post("/bank-transfer")
async def bank_transfer(transfer: Transfer):
    # Find sender and recipient
    sender_account = next((u for u in users_db if u["name"].lower() == transfer.sender.lower()), None)
    recipient_account = next((u for u in users_db if u["name"].lower() == transfer.recipient_name.lower()), None)

    # Check if both accounts exist
    if not sender_account:
        raise HTTPException(status_code=404, detail=f"Sender '{transfer.sender}' not found.")
    if not recipient_account:
        raise HTTPException(status_code=404, detail=f"Recipient '{transfer.recipient_name}' not found.")

    # Check for sufficient funds
    if sender_account["bank_balance"] < transfer.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds.")

    # Perform the transfer
    sender_account["bank_balance"] -= transfer.amount
    recipient_account["bank_balance"] += transfer.amount

    return {
        "message": "Transfer successful!",
        "sender_balance": f"${sender_account['bank_balance']:.2f}",
        "recipient_balance": f"${recipient_account['bank_balance']:.2f}"
    }
