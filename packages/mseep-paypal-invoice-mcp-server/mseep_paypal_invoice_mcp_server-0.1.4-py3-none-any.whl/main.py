import sys
import os
import traceback
from typing import Dict, Any
import paypalrestsdk
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# create a .env file in the same directory with the following content:
# PAYPAL_SB_CLIENT_ID=your_paypal_client_id
# PAYPAL_SB_CLIENT_SECRET=your_paypal_client_secret
load_dotenv()
PAYPAL_SB_CLIENT_ID = os.getenv('PAYPAL_SB_CLIENT_ID')
PAYPAL_SB_CLIENT_SECRET = os.getenv('PAYPAL_SB_CLIENT_SECRET')

def generate_paypal_invoice(invoice_details: Dict[str, Any]) -> str:
    paypalrestsdk.configure({
            "mode": "sandbox",  # or "live" for production
            "client_id": PAYPAL_SB_CLIENT_ID,
            "client_secret": PAYPAL_SB_CLIENT_SECRET
        })
    
    invoice = paypalrestsdk.Invoice({
        "merchant_info": {
            "email": "biju74nair-facilitator@gmail.com"
        },
        "billing_info": [{
            "email": invoice_details['recipient_email']
        }],
        "items": [{
            "name": invoice_details['description'],
            "quantity": 1,
            "unit_price": {
                "currency": "USD",
                "value": invoice_details['amount']
            }
        }],
        "payment_term": {
            "term_type": "NET_45"
        },
    })

    
    if invoice.create():
        if invoice.send():  # return True or False
            print("Invoice[%s] send successfully" % (invoice.id))
            return f'https://www.sandbox.paypal.com/invoice/payerView/details/{invoice.id}'
        else:
            print(invoice.error)
        return invoice.permalink
    else:
        raise ValueError(f"Invoice creation failed: {invoice.error}")



# Initialize FastMCP server
mcp = FastMCP("paypal-invoice")
 
@mcp.tool()
async def create_paypal_invoice(invoice_details: Dict[str, Any]) -> str:
    print("Creating PayPal invoice...")
    urls = []
    url = generate_paypal_invoice(invoice_details)
    print("Invoice URL:", url)
    urls.append(url)
    return "\n---\n".join(urls)

# print(generate_paypal_invoice({
#     "amount": 1,
#     "due_date": "2025-04-01",
#     "description": "Music Service",
#     "recipient_email": "test@gmail.com"
#   }))

def main():
    """Start the MCP server."""
    try:
        print("Running MCP Server ...")
        mcp.run(transport="stdio")
    except Exception as e:
        print(f"Fatal Error in MCP Server: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)