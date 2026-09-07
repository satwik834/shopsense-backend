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
    StoreDiagnosticInsight,
    AIGenerateListingResponse,
    AIPriceOptimizerResponse
)

class AIService:
    @staticmethod
    def _call_gemini_api(prompt: str) -> Optional[str]:
        api_key = settings.GEMINI_API_KEY
        if not api_key or not api_key.strip():
            return None

        # Call Google Gemini REST API
        model = settings.GEMINI_MODEL or "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key.strip()}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
        except Exception as e:
            print(f"Gemini API invocation error: {e}")
            return None

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

    @staticmethod
    def generate_product_listing(
        raw_notes: str,
        category: str,
        target_price: Optional[float] = None
    ) -> AIGenerateListingResponse:
        prompt = f"""You are the ShopSense AI E-Commerce Copywriter.
Given the following raw product notes: "{raw_notes}"
Category: "{category}"
Target Price: INR {target_price if target_price else 'N/A'}

Generate a JSON object with:
- "title": Compelling product title (max 70 chars)
- "description": Engaging 2-paragraph product description
- "tags": Array of 5 SEO search tags
- "bullets": Array of 3 feature bullet points

Do not use emojis."""

        gemini_text = AIService._call_gemini_api(prompt)

        if gemini_text:
            try:
                # Parse JSON output from Gemini response
                clean_json = gemini_text.strip().strip("```json").strip("```").strip()
                parsed = json.loads(clean_json)
                return AIGenerateListingResponse(
                    suggested_title=parsed.get("title", f"Premium {category} Item"),
                    detailed_description=parsed.get("description", raw_notes),
                    seo_tags=parsed.get("tags", [category.lower(), "shop", "quality", "bestseller", "deal"]),
                    marketing_bullets=parsed.get("bullets", ["Premium build quality", "Fast delivery", "100% genuine guaranteed"]),
                    is_gemini_powered=True
                )
            except Exception:
                pass

        # Fallback listing generator
        title_word = raw_notes.split()[0].title() if raw_notes else "Pro"
        return AIGenerateListingResponse(
            suggested_title=f"ShopSense {title_word} {category} Edition",
            detailed_description=f"Experience exceptional performance with our latest {category} listing. Designed built with premium durability and customer-focused quality.",
            seo_tags=[category.lower(), "quality", "trending", "verified", "top-rated"],
            marketing_bullets=[
                f"Engineered for maximum utility in {category}",
                "Optimized ergonomics and reliable durability",
                "Includes official manufacturer warranty coverage"
            ],
            is_gemini_powered=False
        )

    @staticmethod
    def optimize_product_price(db: Session, product_id: int) -> AIPriceOptimizerResponse:
        p = db.query(Product).filter(Product.id == product_id).first()
        if not p:
            raise HTTPException(status_code=404, detail=f"Product #{product_id} not found")

        tx_count = db.query(Transaction).filter(
            Transaction.product_id == p.id,
            Transaction.status == "completed"
        ).count()

        cat_prods = db.query(Product).filter(Product.category == p.category).all()
        cat_prices = [item.price for item in cat_prods]
        avg_cat_price = sum(cat_prices) / max(len(cat_prices), 1)

        # Basic pricing heuristic
        if tx_count >= 3:
            rec_price = round(p.price * 1.05, 2)
            elasticity = "MODERATE"
            impact = "Projected 4.5% increase in total profit margins without volume drop."
            rationale = f"High transactional velocity detected ({tx_count} sales). Demand is inelastic enough to absorb a modest 5% price optimization."
        elif p.price > avg_cat_price * 1.2:
            rec_price = round(avg_cat_price * 1.05, 2)
            elasticity = "HIGH"
            impact = "Projected 18% increase in conversion velocity by aligning closer to category average."
            rationale = f"Current price (INR {p.price:.2f}) is significantly above category average (INR {avg_cat_price:.2f}). Adjusting downward will stimulate order volume."
        else:
            rec_price = round(p.price, 2)
            elasticity = "STABLE"
            impact = "Current pricing maintains optimal conversion balance."
            rationale = f"Pricing (INR {p.price:.2f}) is closely calibrated to category baseline (INR {avg_cat_price:.2f})."

        min_bound = round(rec_price * 0.85, 2)
        max_bound = round(rec_price * 1.20, 2)

        prompt = f"""You are the ShopSense AI Pricing Analyst.
Analyze product pricing for '{p.name}' in category '{p.category}':
- Current Price: INR {p.price:.2f}
- Completed Sales: {tx_count}
- Category Average Price: INR {avg_cat_price:.2f}
- Heuristic Recommended Price: INR {rec_price:.2f}

Provide a 2-sentence executive pricing rationale explaining why this price maximizes revenue. Do not use emojis."""

        gemini_text = AIService._call_gemini_api(prompt)
        if gemini_text:
            rationale = gemini_text
            is_gemini = True
        else:
            is_gemini = False

        return AIPriceOptimizerResponse(
            product_id=p.id,
            product_name=p.name,
            current_price=round(p.price, 2),
            recommended_price=rec_price,
            min_price_bound=min_bound,
            max_price_bound=max_bound,
            elasticity_rating=elasticity,
            pricing_strategy_rationale=rationale,
            projected_revenue_impact=impact,
            is_gemini_powered=is_gemini
        )
