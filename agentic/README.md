# MCP Server for Zerodha Trading

This is a Model Context Protocol (MCP) server implementation that interfaces with Zerodha's KiteConnect API to provide context and execute trades based on AI model decisions.

## Features

- WebSocket-based Model Context Protocol implementation
- Real-time market data context provision
- Position and portfolio context management
- Trading action execution based on model decisions
- Secure authentication and session management
- Dockerized deployment ready
- AWS ECS deployment support

## Prerequisites

- Python 3.8+
- Zerodha KiteConnect API credentials
- pip (Python package manager)
- Docker
- AWS CLI configured with appropriate permissions
- AWS ECR repository
- AWS ECS cluster

## Local Development

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Zerodha API credentials:
   ```
   KITE_API_KEY=your_api_key
   KITE_API_SECRET=your_api_secret
   ```
4. Run the server:
   ```bash
   python main.py
   ```

## Docker Development

1. Build and run using Docker Compose:
   ```bash
   docker-compose up --build
   ```
2. The server will be available at `http://localhost:8000`

## AWS ECS Deployment

1. Update the following files with your AWS account details:

   - `task-definition.json`: Replace `<AWS_ACCOUNT_ID>` and `<REGION>`
   - `deploy.sh`: Replace `<AWS_ACCOUNT_ID>` and `<REGION>`

2. Make the deployment script executable:

   ```bash
   chmod +x deploy.sh
   ```

3. Run the deployment script:

   ```bash
   ./deploy.sh
   ```

4. The deployment process will:
   - Build and tag the Docker image
   - Push the image to ECR
   - Register the task definition
   - Update the ECS service

## Model Context Protocol

The server implements the following MCP commands:

### Context Request

```json
{
  "command": "context_request",
  "context_type": "market_data",
  "instruments": ["NSE:RELIANCE", "NSE:INFY"]
}
```

### Context Update

```json
{
  "command": "context_update",
  "context_type": "market_subscription",
  "data": ["NSE:RELIANCE", "NSE:INFY"]
}
```

### Model Response

```json
{
  "command": "model_response",
  "response_type": "trading_signal",
  "data": {
    "instrument": "NSE:RELIANCE",
    "signal": "BUY",
    "confidence": 0.85
  }
}
```

### Trading Action

```json
{
  "command": "trading_action",
  "action_type": "place_order",
  "params": {
    "variety": "regular",
    "exchange": "NSE",
    "tradingsymbol": "RELIANCE",
    "transaction_type": "BUY",
    "quantity": 1,
    "price": 0,
    "product": "MIS",
    "order_type": "MARKET"
  }
}
```

## Security Notes

- Never commit your `.env` file
- Use HTTPS in production
- Implement proper authentication for WebSocket connections
- Regularly rotate your API keys
- Validate all model responses before executing trades
- Use AWS Secrets Manager for sensitive credentials in production
- Implement proper IAM roles and policies

## License

MIT License
