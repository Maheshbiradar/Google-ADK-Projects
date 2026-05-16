from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.genai import types

# ─────────────────────────────────────────────
# DATA LAYER — replace with DB calls in production
# ─────────────────────────────────────────────

PRODUCT_CATALOG = {
    "laptop":     {"name": "ProBook Laptop",       "price": 999.99,  "stock": 15, "category": "electronics"},
    "headphones": {"name": "SoundMax Headphones",  "price": 149.99,  "stock": 30, "category": "electronics"},
    "keyboard":   {"name": "MechType Keyboard",    "price": 89.99,   "stock": 25, "category": "electronics"},
    "mouse":      {"name": "PrecisionClick Mouse", "price": 49.99,   "stock": 40, "category": "electronics"},
    "monitor":    {"name": "UltraView Monitor",    "price": 399.99,  "stock": 10, "category": "electronics"},
    "desk":       {"name": "ErgoDesk Standing",    "price": 549.99,  "stock": 8,  "category": "furniture"},
    "chair":      {"name": "LumbarPro Chair",      "price": 299.99,  "stock": 12, "category": "furniture"},
    "webcam":     {"name": "ClearView Webcam",     "price": 79.99,   "stock": 20, "category": "electronics"},
    "microphone": {"name": "StudioMic USB",        "price": 119.99,  "stock": 18, "category": "audio"},
    "notebook":   {"name": "Premium Notebook",     "price": 12.99,   "stock": 100,"category": "stationery"},
}

DISCOUNT_CODES = {
    "SAVE10":  {"rate": 0.10, "scope": "all",         "label": "10% off everything"},
    "SAVE20":  {"rate": 0.20, "scope": "all",         "label": "20% off everything"},
    "TECH15":  {"rate": 0.15, "scope": "electronics", "label": "15% off electronics only"},
    "NEWUSER": {"rate": 0.25, "scope": "all",         "label": "25% off for new users"},
}

# ─────────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────────

def browse_products(category: str, tool_context: ToolContext) -> dict:
    """Browse available products filtered by category.

    Returns a list of products with names, prices, and stock.
    Use this when the user wants to see what is available to buy.

    Args:
        category: Filter products by this category.
                  Use "all" to see everything.
                  Other options: "electronics", "furniture",
                  "audio", "stationery"

    Returns:
        Dictionary with matching products and their details.
    """
    # Track which categories this user browsed — stored in state
    browsed = tool_context.state.get("browsed_categories", [])
    if category not in browsed:
        browsed.append(category)
    tool_context.state["browsed_categories"] = browsed

    # Filter catalog
    if category == "all":
        matched = PRODUCT_CATALOG
    else:
        matched = {
            k: v for k, v in PRODUCT_CATALOG.items()
            if v["category"] == category
        }

    if not matched:
        return {
            "status": "error",
            "message": f"No products in category '{category}'.",
            "valid_categories": ["all", "electronics",
                                 "furniture", "audio", "stationery"]
        }

    return {
        "status": "success",
        "category": category,
        "count": len(matched),
        "products": [
            {
                "id": k,
                "name": v["name"],
                "price": v["price"],
                "in_stock": v["stock"] > 0,
                "stock_remaining": v["stock"]
            }
            for k, v in matched.items()
        ]
    }

def add_to_cart(
    product_id: str,
    quantity: int,
    tool_context: ToolContext
) -> dict:
    """Adds a product to the shopping cart.

    Validates that the product exists and has enough stock,
    then adds it to the cart and updates the running total.
    If the product is already in the cart, increases its quantity.

    Args:
        product_id: The product key from the catalog.
                    Examples: "laptop", "headphones", "keyboard"
        quantity: Number of units to add. Must be 1 or more.

    Returns:
        Dictionary with updated cart contents and new total.
    """
    # Phase A: Validate inputs before touching state
    if product_id not in PRODUCT_CATALOG:
        return {
            "status": "error",
            "message": (
                f"Product '{product_id}' not found. "
                f"Use browse_products to see available items."
            )
        }

    product = PRODUCT_CATALOG[product_id]

    if quantity < 1:
        return {
            "status": "error",
            "message": "Quantity must be at least 1."
        }

    if quantity > product["stock"]:
        return {
            "status": "error",
            "message": (
                f"Only {product['stock']} units of "
                f"'{product['name']}' in stock."
            )
        }
    
    # Phase B: Load cart and update
    cart = tool_context.state.get("cart_items", [])

    # If already in cart — update quantity, don't duplicate
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = round(
                item["quantity"] * item["unit_price"], 2
            )
            cart_total = round(
                sum(i["subtotal"] for i in cart), 2
            )
            tool_context.state["cart_items"] = cart
            tool_context.state["cart_total"] = cart_total
            return {
                "status": "success",
                "action": "quantity_updated",
                "product": product["name"],
                "new_quantity": item["quantity"],
                "subtotal": item["subtotal"],
                "cart_total": cart_total
            }

    # Not in cart yet — add as new item
    new_item = {
        "product_id": product_id,
        "name": product["name"],
        "unit_price": product["price"],
        "quantity": quantity,
        "subtotal": round(product["price"] * quantity, 2),
        "category": product["category"]
    }
    cart.append(new_item)

    # Phase C: Commit cart and total to state
    cart_total = round(sum(i["subtotal"] for i in cart), 2)
    tool_context.state["cart_items"] = cart
    tool_context.state["cart_total"] = cart_total

    return {
        "status": "success",
        "action": "item_added",
        "product": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": new_item["subtotal"],
        "cart_total": cart_total,
        "cart_item_count": len(cart)
    }

def remove_from_cart(
    product_id: str,
    tool_context: ToolContext
) -> dict:
    """Removes a product completely from the shopping cart.

    Removes all units of the specified product and
    recalculates the cart total automatically.

    Args:
        product_id: The product key to remove from cart.
                    Examples: "laptop", "headphones", "keyboard"

    Returns:
        Dictionary with updated cart and new total.
    """

    cart = tool_context.state.get("cart_items", [])

    # Find the item before filtering so we can confirm what was removed
    removed = next(
        (i for i in cart if i["product_id"] == product_id), None
    )

    if not removed:
        return {
            "status": "error",
            "message": (
                f"'{product_id}' is not in your cart. "
                f"Use view_cart to see what is currently in your cart."
            )
        }

    # Filter it out and recalculate
    cart = [i for i in cart if i["product_id"] != product_id]
    cart_total = round(sum(i["subtotal"] for i in cart), 2)

    tool_context.state["cart_items"] = cart
    tool_context.state["cart_total"] = cart_total

    # If a discount was applied, recalculate final_total
    # because the base has changed
    discount = tool_context.state.get("applied_discount")
    if discount:
        if discount["scope"] == "electronics":
            electronics_total = sum(
                i["subtotal"] for i in cart
                if i["category"] == "electronics"
            )
            discount_amount = round(
                electronics_total * discount["rate"], 2
            )
        else:
            discount_amount = round(
                cart_total * discount["rate"], 2
            )
        tool_context.state["final_total"] = round(
            cart_total - discount_amount, 2
        )

    return {
        "status": "success",
        "removed_product": removed["name"],
        "cart_total": cart_total,
        "cart_item_count": len(cart),
        "cart_empty": len(cart) == 0
    }

def view_cart(tool_context: ToolContext) -> dict:
    """Displays the current contents of the shopping cart.

    Shows all items, quantities, individual subtotals, the
    cart total, any applied discount, and the final total.
    Call this whenever the user asks what is in their cart
    or what their total is.

    Returns:
        Dictionary with complete cart contents and pricing.
    """
    cart = tool_context.state.get("cart_items", [])
    cart_total = tool_context.state.get("cart_total", 0.0)
    discount = tool_context.state.get("applied_discount")
    final_total = tool_context.state.get("final_total", cart_total)

    if not cart:
        return {
            "status": "success",
            "message": "Your cart is empty. Use browse_products to see what is available.",
            "cart_items": [],
            "cart_total": 0.0
        }

    return {
        "status": "success",
        "cart_items": cart,
        "item_count": len(cart),
        "cart_total": cart_total,
        "discount_applied": discount is not None,
        "discount_details": discount,
        "final_total": final_total,
        "savings": round(cart_total - final_total, 2) if discount else 0.0
    }

def apply_discount(
    discount_code: str,
    tool_context: ToolContext
) -> dict:
    """Applies a promotional discount code to the cart total.

    Validates the code and calculates the discounted price.
    Some codes apply to the full cart, others only to specific
    categories. Only one discount can be applied at a time.

    Args:
        discount_code: The promotional code to apply.
                       Examples: "SAVE10", "SAVE20",
                       "TECH15", "NEWUSER"

    Returns:
        Dictionary with original total, discount amount,
        and new final total.
    """
    # Guard: one discount at a time
    if tool_context.state.get("applied_discount"):
        return {
            "status": "error",
            "message": (
                "A discount is already applied to your cart. "
                "Only one discount code can be used per order."
            )
        }

    cart = tool_context.state.get("cart_items", [])
    cart_total = tool_context.state.get("cart_total", 0.0)

    if not cart:
        return {
            "status": "error",
            "message": "Your cart is empty. Add items before applying a discount."
        }

    # Normalize and validate
    code = discount_code.upper().strip()
    if code not in DISCOUNT_CODES:
        return {
            "status": "error",
            "message": (
                f"'{discount_code}' is not a valid discount code. "
                f"Please check the code and try again."
            )
        }

    discount = DISCOUNT_CODES[code]
    rate = discount["rate"]
    scope = discount["scope"]

    # Calculate discount based on scope from DISCOUNT_CODES data
    if scope == "all":
        discount_amount = round(cart_total * rate, 2)
        final_total = round(cart_total - discount_amount, 2)
        note = f"{int(rate * 100)}% off your entire order"

    elif scope == "electronics":
        electronics_total = sum(
            i["subtotal"] for i in cart
            if i["category"] == "electronics"
        )
        if electronics_total == 0:
            return {
                "status": "error",
                "message": (
                    "The TECH15 code applies to electronics only "
                    "but your cart has no electronics items."
                )
            }
        discount_amount = round(electronics_total * rate, 2)
        final_total = round(cart_total - discount_amount, 2)
        note = f"{int(rate * 100)}% off electronics items only"

    else:
        return {
            "status": "error",
            "message": f"Unknown discount scope '{scope}'."
        }

    # Save to state — two separate keys for clarity
    tool_context.state["applied_discount"] = {
        "code": code,
        "rate": rate,
        "scope": scope,
        "amount_saved": discount_amount,
        "label": discount["label"],
        "note": note
    }
    tool_context.state["final_total"] = final_total

    return {
        "status": "success",
        "code": code,
        "original_total": cart_total,
        "discount_amount": discount_amount,
        "final_total": final_total,
        "note": note
    }

def generate_checkout_summary(
    shipping_address: str,
    tool_context: ToolContext
) -> dict:
    """Generates a complete order summary ready for checkout.

    Compiles all cart items, pricing, any discounts applied,
    and shipping cost into a final order. Orders over 500
    dollars receive free shipping.

    Args:
        shipping_address: The full delivery address for this order.

    Returns:
        Dictionary with the complete order details and order ID.
    """
    import random
    import datetime

    cart = tool_context.state.get("cart_items", [])
    if not cart:
        return {
            "status": "error",
            "message": "Cannot checkout with an empty cart. Add items first."
        }

    cart_total = tool_context.state.get("cart_total", 0.0)
    final_total = tool_context.state.get("final_total", cart_total)
    discount = tool_context.state.get("applied_discount")

    # Shipping logic — free over $500
    shipping_cost = 0.0 if final_total > 500 else 9.99
    order_total = round(final_total + shipping_cost, 2)

    # Generate order ID and timestamp
    order_id = f"ORD-{random.randint(100000, 999999)}"
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    order_summary = {
        "order_id": order_id,
        "created_at": created_at,
        "items": cart,
        "subtotal": cart_total,
        "discount": discount,
        "total_after_discount": final_total,
        "shipping_cost": shipping_cost,
        "shipping_note": (
            "Free shipping on orders over $500"
            if shipping_cost == 0.0
            else "Standard shipping"
        ),
        "order_total": order_total,
        "shipping_address": shipping_address,
        "estimated_delivery": "3-5 business days"
    }

    # Mark checkout complete in state
    tool_context.state["order_summary"] = order_summary
    tool_context.state["checkout_complete"] = True

    return {
        "status": "success",
        "order_summary": order_summary
    }

# ─────────────────────────────────────────────
# AGENT DEFINITION
# ─────────────────────────────────────────────

root_agent = Agent(
    model="gemini-flash-latest",
    name="shopping_assistant",
    description=(
        "An e-commerce shopping assistant that maintains a persistent "
        "cart across the conversation, browses products by category, "
        "applies discount codes, and guides users through checkout."
    ),
    instruction="""
You are ShopBot, a friendly and knowledgeable shopping assistant
for a tech and home office store.

[TOOLS AND WHEN TO USE THEM]
- browse_products : when user asks what is available or wants
                   to see products in a category
- add_to_cart     : immediately when user says they want
                   to buy or add any item — no confirmation needed
- remove_from_cart: when user wants to remove an item
- view_cart       : when user asks what is in their cart,
                   what their total is, or before checkout
- apply_discount  : when user provides a discount code
- generate_checkout_summary: when user is ready to place
                             the order and provides an address

[BEHAVIOUR RULES]
1. Always use a tool — never guess product prices or availability
2. After adding an item, confirm it and mention the new cart total
3. Proactively suggest accessories:
   - laptop    → suggest keyboard, mouse, monitor
   - webcam    → suggest microphone, headphones
   - desk      → suggest chair
4. If the user asks about their total, use view_cart —
   do not try to calculate from memory
5. Never apply a discount without the user providing a code

[AVAILABLE DISCOUNT CODES — mention these exist but not the rates]
SAVE10, SAVE20, TECH15, NEWUSER

[CHECKOUT FLOW]
When user wants to checkout:
  Step 1 → call view_cart to confirm contents
  Step 2 → ask for shipping address if not provided
  Step 3 → call generate_checkout_summary
  Step 4 → present the full order clearly

[FORMATTING CART DISPLAYS]
When showing cart contents always format like this — 
use plain text, no markdown tables:

  YOUR CART
  ─────────────────────────
  ProBook Laptop x1         $999.99
  SoundMax Headphones x2    $299.98
  ─────────────────────────
  Subtotal:               $1,299.97
  Discount (SAVE10 -10%):  -$130.00
  ─────────────────────────
  Total:                  $1,169.97
  Shipping:                   $0.00  (free over $500)

[TONE]
Friendly and efficient. Never pushy.
You are helping someone make a good purchase decision.
""",
tools=[
        browse_products,
        add_to_cart,
        remove_from_cart,
        view_cart,
        apply_discount,
        generate_checkout_summary,
    ],

    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=2048,
    ),
)