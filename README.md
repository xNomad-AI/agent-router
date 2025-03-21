# Action Planner API

A FastAPI-based service for handling action planning requests.

## API Usage

### Plan Endpoint

Send a POST request to `/plan`:

```bash
curl -X POST 'http://localhost:8080/plan' \
-H 'Content-Type: application/json' \
-d '{
  "chat_history": [
    {
      "role": "assistant", 
      "content": "Previous message",
      "attachments": null
    },
    {
      "role": "user",
      "content": "User message", 
      "attachments": []
    }
  ],
  "task_definition": "Task to execute",
  "actions": [
    {
      "name": "ACTION_NAME",
      "strict": true,
      "additionalProperties": false,
      "description": "Action description",
      "parameters": {
        "type": "object",
        "properties": {
          // Action specific parameters
        }
      }
    }
  ],
  "past_steps": [],
  "switched_task": false
}'
```

### Request Body Parameters

- `chat_history`: Array of chat messages with roles and content
- `task_definition`: Description of the task to execute
- `actions`: List of available actions with their parameters
- `past_steps`: Previous executed steps (empty array if none)
- `switched_task`: Boolean indicating if task has switched

### Response Format

```json
{
  "action": "ACTION_NAME",
  "parameters": {
    // Action specific parameters
  },
  "explanation": "Action explanation"
}
```

### Example Request

Here's a complete example for executing a token swap:

```bash
curl -X POST 'http://localhost:8080/plan' \
-H 'Content-Type: application/json' \
-d '{
  "chat_history": [
    {
      "role": "assistant",
      "content": "I attempted to analyze the token 'buzz' twice, but both attempts did not yield complete results. The analysis returned empty or incomplete data. If you have more specific information or another request, please let me know.",
      "attachments": null
    },
    {
      "role": "user",
      "content": "9DHe3pycTuymFk4H4bbPoAJ4hQrr2kaLDF6J6aAKpump",
      "attachments": []
    },
    {
      "role": "assistant",
      "content": "The analysis of the token associated with the contract address '9DHe3pycTuymFk4H4bbPoAJ4hQrr2kaLDF6J6aAKpump' has been completed. If you need further assistance or have another request, please let me know.",
      "attachments": null
    },
    {
      "role": "user",
      "content": "sell 4 swarms for SOL",
      "attachments": []
    }
  ],
  "task_definition": "sell 4 swarms for SOL",
  "actions": [
    {
      "name": "none",
      "strict": true,
      "additionalProperties": false,
      "description": "Normal conversation chat",
      "parameters": {
        "type": "null",
        "properties": {},
        "required": []
      }
    },
    {
      "name": "WALLET_PORTFOLIO",
      "strict": true,
      "additionalProperties": false,
      "description": "Get the wallet total balance or specific token balance in agent wallet",
      "parameters": {
        "type": "object",
        "properties": {
          "queryType": {
            "type": [
              "string",
              "null"
            ],
            "description": "The type of query, should be \"walletBalance\" or \"tokenBalance\", default is walletBalance"
          },
          "tokenSymbol": {
            "type": [
              "string",
              "null"
            ],
            "description": "The token symbol to query, at lease one of tokenSymbol or tokenAddress should be provided when queryType is \"tokenBalance\""
          },
          "tokenAddress": {
            "type": [
              "string",
              "null"
            ],
            "description": "The token contract address to query, at lease one of tokenSymbol or tokenAddress should be provided when queryType is \"tokenBalance\""
          }
        },
        "required": [
          "queryType",
          "tokenSymbol",
          "tokenAddress"
        ]
      }
    },
    {
      "name": "ANALYZE_TOKEN",
      "strict": true,
      "additionalProperties": false,
      "description": "Analyze the token trade info, twitter binding and news about the token by given symbol or contract address",
      "parameters": {
        "type": "object",
        "properties": {
          "tokenSymbol": {
            "type": [
              "string",
              "null"
            ],
            "description": "The token symbol to analyze, at least one of tokenSymbol or tokenAddress should be provided"
          },
          "tokenAddress": {
            "type": [
              "string",
              "null"
            ],
            "description": "The token contract address to analyze, should be a 44 character string, at least one of tokenSymbol or tokenAddress should be provided"
          },
          "analyze": {
            "type": [
              "array",
              "null"
            ],
            "description": "The types of analysis to perform, shoule be an array, items can be \"info\", \"news\", \"twitter\", default to \[\"info\", \"twitter\", \"news\"\]"
          }
        },
        "required": [
          "tokenSymbol",
          "tokenAddress",
          "analyze"
        ]
      }
    },
    {
      "name": "SEND_TOKEN",
      "strict": true,
      "additionalProperties": false,
      "description": "Transfer SPL tokens or SOL from agent wallet to another address",
      "parameters": {
        "type": "object",
        "properties": {
          "tokenSymbol": {
            "type": [
              "string",
              "null"
            ],
            "description": "The token symbol to transfer, at lease one of tokenSymbol or tokenAddress is provided"
          },
          "tokenAddress": {
            "type": [
              "string",
              "null"
            ],
            "description": "The token contract address to transfer, at lease one of tokenSymbol or tokenAddress is provided"
          },
          "recipient": {
            "type": "string",
            "description": "The recipient wallet address"
          },
          "amount": {
            "type": "string",
            "description": "The number amount of tokens to transfer"
          }
        },
        "required": [
          "tokenSymbol",
          "tokenAddress",
          "recipient",
          "amount"
        ]
      }
    },
    {
      "name": "EXECUTE_SWAP",
      "strict": true,
      "additionalProperties": false,
      "description": "Swap tokens on the Solana blockchain. When the user specifies 'buy <token>', the default input token is SOL. When the user specifies 'sell <token>', the default output token is SOL.",
      "parameters": {
        "type": "object",
        "properties": {
          "inputTokenSymbol": {
            "type": [
              "string",
              "null"
            ],
            "description": "Symbol of the token to sell. Defaults to 'SOL' when buying another token. Either inputTokenSymbol or inputTokenCA must be provided."
          },
          "inputTokenCA": {
            "type": [
              "string",
              "null"
            ],
            "description": "Contract address of the token to sell. Either inputTokenSymbol or inputTokenCA must be provided."
          },
          "outputTokenSymbol": {
            "type": [
              "string",
              "null"
            ],
            "description": "Symbol of the token to buy. Defaults to 'SOL' when selling another token. Either outputTokenSymbol or outputTokenCA must be provided."
          },
          "outputTokenCA": {
            "type": [
              "string",
              "null"
            ],
            "description": "Contract address of the token to buy. Either outputTokenSymbol or outputTokenCA must be provided."
          },
          "inputTokenAmount": {
            "type": [
              "number",
              "null"
            ],
            "description": "Exact amount of the input token to swap. Required if inputTokenPercentage is not provided."
          },
          "inputTokenPercentage": {
            "type": [
              "number",
              "null"
            ],
            "description": "Percentage of the input token balance to swap. Required if inputTokenAmount is not provided. When extracting percentages, convert values like \"50%\" into decimal form (e.g., 0.5 instead of 50)."
          },
          "outputTokenAmount": {
            "type": [
              "number",
              "null"
            ],
            "description": "Expected amount of the output token to receive."
          }
        },
        "required": [
          "inputTokenSymbol",
          "outputTokenSymbol",
          "inputTokenCA",
          "outputTokenCA",
          "inputTokenAmount",
          "inputTokenPercentage"
        ]
      }
    },
    {
      "name": "CREATE_TOKEN",
      "strict": true,
      "additionalProperties": false,
      "description": "Create a new token on pumpfun and buy a specified amount using SOL. Requires the token name, symbol and image url, buy amount after create in SOL.",
      "parameters": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "Name of the token to create"
          },
          "symbol": {
            "type": "string",
            "description": "Symbol of the token to create"
          },
          "imageUrl": {
            "type": [
              "string",
              "null"
            ],
            "description": "Image URL or attachment file of the token to create"
          },
          "description": {
            "type": [
              "string",
              "null"
            ],
            "description": "Description of the token to create"
          },
          "twitter": {
            "type": [
              "string",
              "null"
            ],
            "description": "Twitter URL of the token to create"
          },
          "website": {
            "type": [
              "string",
              "null"
            ],
            "description": "Website URL of the token to create"
          },
          "telegram": {
            "type": [
              "string",
              "null"
            ],
            "description": "Telegram URL of the token to create"
          },
          "buyAmountSol": {
            "type": [
              "number",
              "null"
            ],
            "description": "Amount of SOL to buy after token creation"
          }
        },
        "required": [
          "name",
          "symbol",
          "imageUrl",
          "description",
          "twitter",
          "website",
          "telegram",
          "buyAmountSol"
        ]
      }
    },
    {
      "name": "AUTO_TASK",
      "strict": true,
      "additionalProperties": false,
      "description": "Automatically executes a token swap when a specified condition is met, such as a price trigger or time delay. This function should only be used if the user specifies a condition like 'when price is above/below X', 'at X price', or 'after Y minutes'. If the user simply says 'sell token', this is NOT an auto task. When the user specifies 'buy <token> at certain condition', the default input token is SOL. When the user specifies 'sell <token> at certain condition', the default output token is SOL.",
      "parameters": {
        "type": "object",
        "properties": {
          "inputTokenSymbol": {
            "type": [
              "string",
              "null"
            ],
            "description": "Symbol of the token to sell. If omitted in a buy order, SOL will be used by default. Either inputTokenSymbol or inputTokenCA must be provided."
          },
          "inputTokenCA": {
            "type": [
              "string",
              "null"
            ],
            "description": "Contract address of the token to sell. Either inputTokenSymbol or inputTokenCA must be provided."
          },
          "outputTokenSymbol": {
            "type": [
              "string",
              "null"
            ],
            "description": "Symbol of the token to buy. Either outputTokenSymbol or outputTokenCA must be provided."
          },
          "outputTokenCA": {
            "type": [
              "string",
              "null"
            ],
            "description": "Contract address of the token to buy. If omitted in a sell order, SOL will be used by default. Either outputTokenSymbol or outputTokenCA must be provided."
          },
          "inputTokenAmount": {
            "type": [
              "number",
              "null"
            ],
            "description": "Exact amount of inputToken to swap. Either inputTokenAmount or inputTokenPercentage must be provided."
          },
          "inputTokenPercentage": {
            "type": [
              "number",
              "null"
            ],
            "description": "Percentage of inputToken balance to swap. convert 100% to 1 Either inputTokenAmount or inputTokenPercentage must be provided. When extracting percentages, convert values like \"50%\" into decimal form (e.g., 0.5 instead of 50)."
          },
          "priceCondition": {
            "type": [
              "string",
              "null"
            ],
            "description": "Defines whether the swap should be triggered when the target token's price is 'above' or 'below' the specified priceTarget."
          },
          "priceTarget": {
            "type": [
              "number",
              "null"
            ],
            "description": "Price target for the swap"
          },
          "tokenTarget": {
            "type": [
              "string",
              "null"
            ],
            "description": "Token symbol or contract address used for price trigger evaluation"
          },
          "delay": {
            "type": [
              "string",
              "null"
            ],
            "description": "Time Delay for the swap, e.g., \"after 5 minutes\" or \"below 0.00169\", Either delay or priceTarget must be provided."
          }
        },
        "required": [
          "inputTokenSymbol",
          "outputTokenSymbol",
          "inputTokenCA",
          "outputTokenCA",
          "inputTokenAmount",
          "inputTokenPercentage",
          "priceCondition",
          "priceTarget",
          "delay"
        ]
      }
    },
    {
      "name": "CLAIM_AIRDROP",
      "strict": true,
      "additionalProperties": false,
      "description": "Perform claim airdrop for the user agent account",
      "parameters": {
        "type": "object",
        "properties": {
          "programName": {
            "type": [
              "string",
              "null"
            ],
            "description": "The program name of the airdrop"
          }
        },
        "required": [
          "programName"
        ]
      }
    },
    {
      "name": "COPY_TRADE",
      "strict": true,
      "additionalProperties": false,
      "description": "Copy the trade of a given account",
      "parameters": {
        "type": "object",
        "properties": {
          "name": {
            "type": [
              "string",
              "null"
            ],
            "description": "The name user set to this copy trade"
          },
          "targetAddress": {
            "type": "string",
            "description": "The address of the account to copy trade from"
          },
          "mode": {
            "type": [
              "string"
            ],
            "description": "The mode of copying trade, enum can be \"fixed\" or \"percentage\""
          },
          "copySell": {
            "type": "boolean",
            "description": "Whether to copy sell trade, default value: true"
          },
          "fixedAmount": {
            "type": [
              "number",
              "null"
            ],
            "description": "The fixed input SOL amount to copy trade, Either this or \"percentage\" must be provided "
          },
          "percentage": {
            "type": [
              "number",
              "null"
            ],
            "description": "The percentage of the trade to copy, expressed as a decimal. for example, 1 = 100%, 0.5 = 50%. Either this or \"fixedAmount\" must be provided"
          }
        },
        "required": [
          "targetAddress",
          "fixedAmount",
          "percentage"
        ]
      }
    }
  ],
  "past_steps": [],
  "switched_task": false
}'
```
```