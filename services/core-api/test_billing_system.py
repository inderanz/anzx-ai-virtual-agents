#!/usr/bin/env python3
"""
Billing system test script
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.config.billing import billing_config
from app.services.usage_service import usage_service
from app.middleware.usage_tracking import UsageTracker


async def test_billing_config():
    """Test billing configuration"""
    print("🧪 Testing Billing Configuration")
    print("=" * 50)
    
    # Test plan configurations
    for plan_name in ["freemium", "pro", "enterprise"]:
        config = billing_config.get_plan_config(plan_name)
        print(f"✅ {plan_name.title()} Plan:")
        print(f"   Price: ${config['price']} {config['currency'].upper()}")
        print(f"   Messages: {config['limits']['messages_per_month']:,}")
        print(f"   Tokens: {config['limits']['tokens_per_month']:,}")
        print(f"   Features: {len(config['features'])} features")
        print()
    
    # Test overage calculation
    usage = {"messages": 1500, "tokens": 150000}
    limits = {"messages_per_month": 1000, "tokens_per_month": 100000}
    overage_cost = billing_config.calculate_overage_cost(usage, limits)
    
    print(f"📊 Overage Calculation Test:")
    print(f"   Usage: {usage}")
    print(f"   Limits: {limits}")
    print(f"   Overage Cost: ${overage_cost:.6f} AUD")
    print()


def test_usage_tracker():
    """Test usage tracking utilities"""
    print("📈 Testing Usage Tracker")
    print("=" * 50)
    
    # Test cost calculation
    models = ["gemini-pro", "gemini-ultra", "text-embedding-004"]
    
    for model in models:
        cost = UsageTracker.calculate_token_cost(1000, 2000, model)
        print(f"✅ {model}:")
        print(f"   1K input + 2K output tokens = ${cost:.6f} AUD")
    
    print()


def test_plan_comparisons():
    """Test plan comparison logic"""
    print("🔄 Testing Plan Comparisons")
    print("=" * 50)
    
    plans = ["freemium", "pro", "enterprise"]
    usage_scenarios = [
        {"messages": 500, "tokens": 50000, "name": "Light Usage"},
        {"messages": 5000, "tokens": 500000, "name": "Medium Usage"},
        {"messages": 50000, "tokens": 5000000, "name": "Heavy Usage"}
    ]
    
    for scenario in usage_scenarios:
        print(f"📋 {scenario['name']} Scenario:")
        print(f"   Usage: {scenario['messages']:,} messages, {scenario['tokens']:,} tokens")
        
        for plan in plans:
            limits = billing_config.get_plan_limits(plan)
            config = billing_config.get_plan_config(plan)
            
            over_limit = billing_config.is_usage_over_limit(scenario, limits)
            overage_cost = billing_config.calculate_overage_cost(scenario, limits)
            total_cost = config["price"] + overage_cost
            
            status = "❌ Over Limit" if over_limit else "✅ Within Limit"
            print(f"   {plan.title()}: {status} - ${total_cost:.2f}/month")
        
        print()


def test_notification_thresholds():
    """Test notification threshold logic"""
    print("🔔 Testing Notification Thresholds")
    print("=" * 50)
    
    limit = 10000
    thresholds = billing_config.USAGE_WARNING_THRESHOLDS
    
    print(f"Limit: {limit:,}")
    print(f"Warning Thresholds: {[f'{t*100:.0f}%' for t in thresholds]}")
    print()
    
    test_usages = [7500, 8500, 9000, 9500, 10500]
    
    for usage in test_usages:
        percentage = (usage / limit) * 100
        warnings = []
        
        for threshold in thresholds:
            if percentage >= threshold * 100:
                warnings.append(f"{threshold*100:.0f}%")
        
        status = "🚨 OVER LIMIT" if usage > limit else "✅ Within Limit"
        warning_text = f" (Warnings: {', '.join(warnings)})" if warnings else ""
        
        print(f"Usage {usage:,} ({percentage:.1f}%): {status}{warning_text}")
    
    print()


def test_gst_calculation():
    """Test GST calculation"""
    print("💰 Testing GST Calculation")
    print("=" * 50)
    
    base_prices = [79, 299, 500]  # Example prices
    gst_rate = billing_config.GST_RATE
    
    for base_price in base_prices:
        if billing_config.INCLUDE_GST:
            # Price includes GST
            gst_amount = base_price * gst_rate / (1 + gst_rate)
            price_ex_gst = base_price - gst_amount
        else:
            # Price excludes GST
            gst_amount = base_price * gst_rate
            price_inc_gst = base_price + gst_amount
        
        print(f"Base Price: ${base_price:.2f}")
        if billing_config.INCLUDE_GST:
            print(f"  Price (ex GST): ${price_ex_gst:.2f}")
            print(f"  GST Amount: ${gst_amount:.2f}")
            print(f"  Total (inc GST): ${base_price:.2f}")
        else:
            print(f"  Price (ex GST): ${base_price:.2f}")
            print(f"  GST Amount: ${gst_amount:.2f}")
            print(f"  Total (inc GST): ${price_inc_gst:.2f}")
        print()


async def main():
    """Run all billing system tests"""
    print("🏦 ANZx.ai Billing System Test Suite")
    print("=" * 60)
    print()
    
    try:
        await test_billing_config()
        test_usage_tracker()
        test_plan_comparisons()
        test_notification_thresholds()
        test_gst_calculation()
        
        print("✅ All billing system tests completed successfully!")
        print()
        print("🔧 Next Steps:")
        print("1. Configure Stripe API keys in environment variables")
        print("2. Set up webhook endpoints for production")
        print("3. Test payment flows with Stripe test cards")
        print("4. Configure email notification service")
        print("5. Set up monitoring and alerting")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())