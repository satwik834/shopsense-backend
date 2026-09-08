import json
import httpx
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.config import settings
from app.models.product import Product
from app.models.vendor import Vendor
from app.models.transaction import Transaction
from app.schemas.ai_features import (
    AIShoppingQueryResponse,
    GroundedProductResult,
    AIStoreAdvisorResponse,
    StoreDiagnosticInsight
)

import os

class AIService:
    @staticmethod
    def _call_gemini_api(prompt: str) -> Optional[str]:
        # Read API key dynamically from environment or settings
        api_key = (os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None) or "").strip()
        if not api_key:
            return None

        # Models to attempt in order of preference
        primary_model = (os.getenv("GEMINI_MODEL") or getattr(settings, "GEMINI_MODEL", None) or "gemini-3.5-flash").strip()
        models_to_try = [primary_model, "gemini-3.5-flash", "gemini-2.5-flash", "gemini-1.5-flash", "gemini-pro"]
        # Deduplicate while preserving order
        seen = set()
        models = [m for m in models_to_try if not (m in seen or seen.add(m))]

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        with httpx.Client(timeout=20.0) as client:
            for model in models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                try:
                    res = client.post(url, headers=headers, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                text = parts[0].get("text", "").strip()
                                if text:
                                    return text
                    elif res.status_code == 404:
                        # Model not found, fallback to next model
                        continue
                    else:
                        print(f"Gemini API ({model}) response code {res.status_code}: {res.text}")
                except Exception as e:
                    print(f"Gemini API ({model}) request exception: {e}")

        return None

    @staticmethod
    def answer_shopping_query(
        db: Session,
        query: str,
        max_price: Optional[float] = None,
        category: Optional[str] = None
    ) -> AIShoppingQueryResponse:
        # Step 1: Perform Grounded RAG Catalog Search
        prod_query = db.query(Product)

        if max_price is not None:
            prod_query = prod_query.filter(Product.price <= max_price)
        if category and category.strip():
            prod_query = prod_query.filter(Product.category.iloc(category.strip()))

        terms = [t.strip().lower() for t in query.split() if len(t.strip()) > 2]
        all_products = prod_query.all()

        scored_products = []
        for p in all_products:
            score = 0
            reasons = []
            p_text = f"{p.name} {p.category} {p.description or ''}".lower()

            for t in terms:
                if t in p_text:
                    score += 25
                    reasons.append(f"Matched search term '{t}'")

            if max_price and p.price <= max_price:
                score += 20
                reasons.append(f"Price INR {p.price:.2f} within budget <= INR {max_price:.2f}")

            if category and p.category and category.lower() in p.category.lower():
                score += 30
                reasons.append(f"Category match ({p.category})")

            if p.stock_quantity > 0:
                score += 15
            else:
                score -= 50  # Deprioritize out of stock

            if score > 0 or not terms:
                status_str = "IN_STOCK" if p.stock_quantity > 10 else ("LOW_STOCK" if p.stock_quantity > 0 else "OUT_OF_STOCK")
                reason_str = ", ".join(reasons) if reasons else "Product matches query parameters."
                scored_products.append({
                    "product": p,
                    "score": max(score, 10),
                    "reason": reason_str,
                    "status": status_str
                })

        scored_products.sort(key=lambda x: x["score"], reverse=True)
        top_matches = scored_products[:4]

        suggested_results = [
            GroundedProductResult(
                product_id=m["product"].id,
                product_name=m["product"].name,
                category=m["product"].category or "General",
                price=round(m["product"].price, 2),
                vendor_name=m["product"].vendor.name if m["product"].vendor else "Marketplace Vendor",
                stock_status=m["status"],
                match_score=min(m["score"], 100),
                match_reason=m["reason"]
            ) for m in top_matches
        ]

        # Step 2: RAG Context Assembly for Gemini Prompt
        catalog_context_str = "\n".join([
            f"- Product ID {r.product_id}: '{r.product_name}' ({r.category}) by {r.vendor_name} - Price: INR {r.price}, Stock: {r.stock_status}"
            for r in suggested_results
        ])

        prompt = f"""You are the ShopSense AI Shopping Assistant. A customer asked: "{query}"

Available Verified Catalog Items:
{catalog_context_str if catalog_context_str else "No direct catalog match found."}

Provide a helpful, friendly, and concise recommendation response guiding the customer to the best match. Reference exact prices in INR and highlight key product qualities.
Do not use emojis."""

        gemini_text = AIService._call_gemini_api(prompt)

        if gemini_text:
            ai_response = gemini_text
            is_gemini = True
        else:
            is_gemini = False
            if suggested_results:
                best = suggested_results[0]
                ai_response = f"Based on your query '{query}', I recommend the {best.product_name} in {best.category} priced at INR {best.price:.2f} from {best.vendor_name}. It has a high relevance score of {best.match_score}/100 and is currently {best.stock_status.replace('_', ' ').title()}."
            else:
                ai_response = f"I searched the ShopSense catalog for '{query}', but no items directly matched your query parameters. Try broadening your price range or category search."

        return AIShoppingQueryResponse(
            query=query,
            ai_response=ai_response,
            suggested_products=suggested_results,
            is_gemini_powered=is_gemini
        )

    @staticmethod
    def generate_store_advisor_report(db: Session, vendor_id: int) -> AIStoreAdvisorResponse:
        vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            store_name = f"Vendor #{vendor_id}"
        else:
            store_name = vendor.store_name or vendor.name

        prods = db.query(Product).filter(Product.vendor_id == vendor_id).all()
        txs = db.query(Transaction).filter(Transaction.vendor_id == vendor_id, Transaction.status == "completed").all()

        tot_rev = sum(t.total_amount for t in txs)
        tot_orders = len(txs)
        tot_prods = len(prods)
        low_stock_prods = [p for p in prods if p.stock_quantity <= 10]

        # Generate Diagnostics
        diagnostics = []

        if low_stock_prods:
            p_names = ", ".join([p.name for p in low_stock_prods[:2]])
            diagnostics.append(
                StoreDiagnosticInsight(
                    category="Inventory Risk",
                    title="Safety Stock Breach Warning",
                    finding=f"{len(low_stock_prods)} of your {tot_prods} products have breached safety thresholds ({p_names}).",
                    impact_level="HIGH",
                    actionable_recommendation="Reorder inventory immediately to prevent stockouts and preserve search ranking."
                )
            )

        if tot_orders > 0:
            aov = tot_rev / tot_orders
            if aov < 150.0:
                diagnostics.append(
                    StoreDiagnosticInsight(
                        category="Pricing Strategy",
                        title="Low Average Order Value (AOV)",
                        finding=f"Your current AOV is INR {aov:.2f}, which is below optimal revenue density benchmarks.",
                        impact_level="MEDIUM",
                        actionable_recommendation="Introduce multi-item bundles or minimum order thresholds to increase basket size."
                    )
                )
            else:
                diagnostics.append(
                    StoreDiagnosticInsight(
                        category="Sales Performance",
                        title="Strong Order Basket Value",
                        finding=f"Your store maintains a healthy AOV of INR {aov:.2f} across {tot_orders} completed orders.",
                        impact_level="LOW",
                        actionable_recommendation="Capitalize on high basket size by introducing premium catalog variants."
                    )
                )
        else:
            diagnostics.append(
                StoreDiagnosticInsight(
                    category="Sales Activation",
                    title="No Transaction Velocity",
                    finding="Your store catalog has recorded 0 completed orders.",
                    impact_level="HIGH",
                    actionable_recommendation="Run targeted promotions and review product pricing competitive positioning."
                )
            )

        # Prompt for Gemini
        prompt = f"""You are the ShopSense AI Executive Data Analyst advising the merchant store '{store_name}'.

Store Metrics Summary:
- Total Products: {tot_prods}
- Total Revenue: INR {tot_rev:.2f}
- Completed Orders: {tot_orders}
- Low Stock Items: {len(low_stock_prods)}

Write a concise 3-paragraph executive diagnostic strategy report advising the merchant on how to increase revenue, manage inventory, and optimize customer retention.
Do not use emojis."""

        gemini_text = AIService._call_gemini_api(prompt)

        if gemini_text:
            exec_summary = f"Executive Store Advisory for {store_name}: Active catalog monitoring across {tot_prods} products and INR {tot_rev:.2f} total revenue."
            strategy = gemini_text
            is_gemini = True
        else:
            exec_summary = f"Automated Store Advisory for {store_name}: Analyzed {tot_prods} catalog products and {tot_orders} completed customer orders."
            strategy = (
                f"Store Advisory Strategy for {store_name}:\n\n"
                f"1. Inventory Governance: You have {len(low_stock_prods)} item(s) below recommended safety stock thresholds. Immediate purchase order reordering is advised to maintain product availability.\n"
                f"2. Revenue Growth: Your current total revenue stands at INR {tot_rev:.2f} across {tot_orders} orders. Focus on optimizing high-velocity product listings to increase overall store conversion.\n"
                f"3. Customer Retention: Cross-sell related items to buyers in your top-performing categories to build long-term repeat customer loyalty."
            )
            is_gemini = False

        return AIStoreAdvisorResponse(
            vendor_id=vendor_id,
            store_name=store_name,
            executive_summary=exec_summary,
            diagnostics=diagnostics,
            ai_generated_strategy=strategy,
            is_gemini_powered=is_gemini
        )
