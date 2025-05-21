from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from kiteconnect import KiteConnect
import os
from dotenv import load_dotenv
from typing import Dict, List
import json
import asyncio

# Load environment variables
load_dotenv()

app = FastAPI(title="MCP Server")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize KiteConnect
kite = KiteConnect(api_key=os.getenv("KITE_API_KEY"))

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}


class MCPProtocol:
    @staticmethod
    async def handle_message(websocket: WebSocket, message: str):
        try:
            data = json.loads(message)
            command = data.get("command")

            if command == "context_request":
                await MCPProtocol.handle_context_request(websocket, data)
            elif command == "context_update":
                await MCPProtocol.handle_context_update(websocket, data)
            elif command == "model_response":
                await MCPProtocol.handle_model_response(websocket, data)
            elif command == "trading_action":
                await MCPProtocol.handle_trading_action(websocket, data)
            else:
                await websocket.send_json({
                    "status": "error",
                    "message": "Unknown command"
                })
        except Exception as e:
            await websocket.send_json({
                "status": "error",
                "message": str(e)
            })

    @staticmethod
    async def handle_context_request(websocket: WebSocket, data: dict):
        try:
            context_type = data.get("context_type")
            if not context_type:
                raise HTTPException(
                    status_code=400, detail="Context type is required")

            # Get market data based on context type
            if context_type == "market_data":
                instruments = data.get("instruments", [])
                if not instruments:
                    raise HTTPException(
                        status_code=400, detail="Instruments list is required")

                # Get market data for instruments
                market_data = kite.quote(instruments)

                await websocket.send_json({
                    "status": "success",
                    "context_type": "market_data",
                    "data": market_data
                })
            elif context_type == "positions":
                positions = kite.positions()
                await websocket.send_json({
                    "status": "success",
                    "context_type": "positions",
                    "data": positions
                })
            else:
                raise HTTPException(
                    status_code=400, detail="Unsupported context type")

        except Exception as e:
            await websocket.send_json({
                "status": "error",
                "message": str(e)
            })

    @staticmethod
    async def handle_context_update(websocket: WebSocket, data: dict):
        try:
            context_type = data.get("context_type")
            update_data = data.get("data")

            if not context_type or not update_data:
                raise HTTPException(
                    status_code=400, detail="Context type and data are required")

            # Handle context updates
            if context_type == "market_subscription":
                kite.subscribe(update_data)
                await websocket.send_json({
                    "status": "success",
                    "message": f"Subscribed to {len(update_data)} instruments"
                })
            else:
                raise HTTPException(
                    status_code=400, detail="Unsupported context type")

        except Exception as e:
            await websocket.send_json({
                "status": "error",
                "message": str(e)
            })

    @staticmethod
    async def handle_model_response(websocket: WebSocket, data: dict):
        try:
            response_type = data.get("response_type")
            response_data = data.get("data")

            if not response_type or not response_data:
                raise HTTPException(
                    status_code=400, detail="Response type and data are required")

            # Handle model responses
            if response_type == "trading_signal":
                # Process trading signal from the model
                await websocket.send_json({
                    "status": "success",
                    "message": "Trading signal received"
                })
            else:
                raise HTTPException(
                    status_code=400, detail="Unsupported response type")

        except Exception as e:
            await websocket.send_json({
                "status": "error",
                "message": str(e)
            })

    @staticmethod
    async def handle_trading_action(websocket: WebSocket, data: dict):
        try:
            action_type = data.get("action_type")
            action_params = data.get("params")

            if not action_type or not action_params:
                raise HTTPException(
                    status_code=400, detail="Action type and parameters are required")

            if action_type == "place_order":
                order_id = kite.place_order(
                    variety=action_params.get("variety", "regular"),
                    exchange=action_params["exchange"],
                    tradingsymbol=action_params["tradingsymbol"],
                    transaction_type=action_params["transaction_type"],
                    quantity=action_params["quantity"],
                    price=action_params.get("price", 0),
                    product=action_params.get("product", "MIS"),
                    order_type=action_params.get("order_type", "MARKET")
                )

                await websocket.send_json({
                    "status": "success",
                    "message": "Order placed successfully",
                    "order_id": order_id
                })
            else:
                raise HTTPException(
                    status_code=400, detail="Unsupported action type")

        except Exception as e:
            await websocket.send_json({
                "status": "error",
                "message": str(e)
            })


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = id(websocket)
    active_connections[client_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            await MCPProtocol.handle_message(websocket, data)
    except WebSocketDisconnect:
        del active_connections[client_id]


@app.get("/")
async def root():
    return {"message": "MCP Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
