
# PayPal Invoice MCP Server

A Model Context Protocol server that creates PayPal Invoice capabilities. This server enables LLMs to create invoice.

### Available Tools

- `create_paypal_invoice` - Create Invoice
  - Required arguments:
    - `invoice_details` (Dict[str, Any]): Invoice Details
    
## Installation

### Using uv (recommended)

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will
use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *paypal-invoice-mcp-server*.

### Using PIP

Alternatively you can install `paypal-invoice-mcp-server` via pip:

```bash
pip install paypal-invoice-mcp-server
```

After installation, you can run it as a script using:

```bash
python -m paypal-invoice-mcp-server
```

## Configuration

### Configure for Claude.app

Add to your Claude settings:

<details>
<summary>Using uvx</summary>

```json
"mcpServers": {
  "time": {
    "command": "uvx",
    "args": ["paypal-invoice-mcp-server"]
  }
}
```
</details>


<details>
<summary>Using pip installation</summary>

```json
"mcpServers": {
  "time": {
    "command": "python",
    "args": ["-m", "paypal-invoice-mcp-server"]
  }
}
```
</details>


## Example Interactions

1. Create Invoice:
```json
{
     "amount": 1,
     "due_date": "2025-04-01",
     "description": "Music Service",
     "recipient_email": "test@gmail.com"
   }
```

## Debugging

You can use the MCP inspector to debug the server. For uvx installations:

```bash
npx @modelcontextprotocol/inspector uvx paypal-invoice-mcp-server
```

Or if you've installed the package in a specific directory or are developing on it:

```bash
cd path/to/servers/src/time
npx @modelcontextprotocol/inspector uv run paypal-invoice-mcp-server
```

## Examples of Questions for Claude

1. "Create a paypal invoice for joe@gmail.com for $200 for a Music Class, show me the invoice link"

## Build



## Contributing

We encourage contributions to help expand and improve paypal-invoice-mcp-server. Whether you want to add new time-related tools, enhance existing functionality, or improve documentation, your input is valuable.

For examples of other MCP servers and implementation patterns, see:
https://github.com/modelcontextprotocol/servers

Pull requests are welcome! Feel free to contribute new ideas, bug fixes, or enhancements to make paypal-invoice-mcp-server even more powerful and useful.

## License

paypal-invoice-mcp-server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.