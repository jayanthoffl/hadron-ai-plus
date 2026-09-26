import json
import sys
import time
from orchestrator import HadronOrchestrator
from schemas import HadronRequest

def run_sandbox():
    print("=" * 80)
    print("      HADRON AI++ SANDBOX BENCHMARK & REGRESSION TEST SUITE")
    print("=" * 80)
    print("Mode: SAFE ISOLATED SANDBOX (Zero production ServiceNow mutation)")
    print("Evaluating Cataloged (FOUND) vs Uncataloged (INFERRED) Deal Pipelines\n")

    orch = HadronOrchestrator()

    test_cases = [
        {
            "id": "TC-01",
            "type": "CATALOGED (FOUND)",
            "customer": "Tata Consultancy Services",
            "service": "Advanced Routing Service for Fleet",
            "objective": "Optimize route efficiency and minimize fleet fuel consumption",
            "context": "Fleet operations with 12,000 active delivery vehicles nationwide."
        },
        {
            "id": "TC-02",
            "type": "CATALOGED (FOUND)",
            "customer": "Infosys",
            "service": "Quantum based ERP System Migration",
            "objective": "Legacy ERP cloud modernization with quantum dependency mapping",
            "context": "Enterprise SAP ECC migration across 4 global operating hubs."
        },
        {
            "id": "TC-03",
            "type": "CATALOGED (FOUND)",
            "customer": "Wipro",
            "service": "Cybersecurity Zero Trust Modernization",
            "objective": "Zero-trust identity mesh architecture implementation",
            "context": "Distributed corporate perimeter with hybrid multi-cloud access."
        },
        {
            "id": "TC-04",
            "type": "UNCATALOGED (INFERRED)",
            "customer": "Infosys",
            "service": "Implement Quantum secured GRC System",
            "objective": "Post-quantum cryptography governance, risk, and compliance platform",
            "context": "Financial regulatory compliance for post-quantum transaction ledger."
        },
        {
            "id": "TC-05",
            "type": "UNCATALOGED (INFERRED)",
            "customer": "Acme FinTech Global",
            "service": "Autonomous LLM Multi-Agent Fraud Interceptor",
            "objective": "Real-time sub-millisecond payment fraud detection with generative agents",
            "context": "High frequency payments routing handling 45,000 TPS."
        },
        {
            "id": "TC-06",
            "type": "UNCATALOGED (INFERRED)",
            "customer": "Apex Healthcare",
            "service": "Real-Time GenAI Clinical Triage Assistant",
            "objective": "Automate emergency triage classification and clinical notes summarization",
            "context": "HIPAA-compliant hospital network across 18 trauma centers."
        }
    ]

    results_summary = []

    for tc in test_cases:
        print("-" * 80)
        print(f"RUNNING {tc['id']}: [{tc['type']}]")
        print(f"Customer: {tc['customer']}")
        print(f"Service:  {tc['service']}")
        print(f"Objective: {tc['objective']}")
        print("-" * 80)

        start_time = time.time()
        req = HadronRequest(
            customer_name=tc["customer"],
            service_product_name=tc["service"],
            commercial_objective=tc["objective"],
            additional_context=tc["context"],
            record_sys_id=f"sandbox_{tc['id'].lower()}"
        )

        res = orch.run(req)
        elapsed = time.time() - start_time

        si = json.loads(res["service_intelligence"])
        ie = json.loads(res["internal_economics"])
        mi = json.loads(res["market_intelligence"])
        ci = json.loads(res["customer_intelligence"])
        offers = res.get("offer_set", [])
        qaoa = res.get("quantum_optimization", {})
        precedents = res.get("historical_comparables", {})
        rec_price = res.get("recommended_price", "0")
        status = res.get("intelligence_status", "0")

        # Checks
        has_positive_cost = ie.get("estimated_cost", 0) > 0
        has_positive_mvp = ie.get("minimum_viable_price", 0) > 0
        has_4_offers = len(offers) == 4
        ready_status = status == "2"

        passed = has_positive_cost and has_positive_mvp and has_4_offers and ready_status

        cost_val = ie.get("estimated_cost", 0)
        mvp_val = ie.get("minimum_viable_price", 0)
        rec_price_float = float(rec_price) if rec_price and rec_price != "0" else 0.0

        print(f" -> Execution Time:    {elapsed:.2f}s")
        print(f" -> Customer Intel:    {ci.get('data_availability')} (Rev: ${ci.get('revenue', 0):,})")
        print(f" -> Service Intel:     {si.get('data_availability')} (Complexity: {si.get('complexity')}, Duration: {si.get('estimated_duration_months')} mo)")
        print(f" -> Staffing Pod:      {si.get('resource_requirements')}")
        print(f" -> Economics Source:  {ie.get('economics_source')}")
        print(f" -> Delivery Cost:     ${cost_val:,.2f}")
        print(f" -> MVP Floor:         ${mvp_val:,.2f}")
        print(f" -> Market Intel:      {mi.get('data_availability')} (Ref: ${mi.get('market_reference_price', 0):,.2f})")
        print(f" -> Precedent Matches: {precedents.get('matched_deals_count', 0)} deals (Median: ${precedents.get('median_price', 0):,.2f})")
        
        q_sol = qaoa.get("quantum_solution", {})
        if q_sol:
            print(f" -> QAOA Optimization: Tier '{q_sol.get('name')}' | Price: ${q_sol.get('price', 0):,.2f} | Margin: {q_sol.get('margin', 0):.1%}")
        
        print(" -> Commercial Tiers:")
        for o in offers:
            p = o.get("price", 0)
            m = o.get("margin", 0)
            print(f"      [{o.get('name')}] ${p:,.2f} (Margin: {m:.1%})")

        print(f" -> Final Recommend:   ${rec_price_float:,.2f}")
        print(f" -> Intelligence Status: {status} (READY FOR SERVICENOW)")
        print(f" -> RESULT:             {'[PASSED]' if passed else '[FAILED]'}\n")

        results_summary.append({
            "id": tc["id"],
            "type": tc["type"],
            "customer": tc["customer"],
            "service": tc["service"],
            "service_status": si.get("data_availability"),
            "econ_source": ie.get("economics_source"),
            "cost": cost_val,
            "mvp": mvp_val,
            "recommended_price": rec_price_float,
            "offers_count": len(offers),
            "passed": passed
        })

    # Summary table
    print("=" * 80)
    print("                         SANDBOX EXECUTION SUMMARY")
    print("=" * 80)
    print(f"{'ID':<6} | {'Type':<22} | {'Service Intel':<14} | {'Econ Source':<20} | {'MVP Floor':<14} | {'Offers':<6} | {'Status'}")
    print("-" * 80)
    all_passed = True
    for r in results_summary:
        if not r["passed"]:
            all_passed = False
        print(f"{r['id']:<6} | {r['type']:<22} | {r['service_status']:<14} | {r['econ_source']:<20} | ${r['mvp']:>11,.0f} | {r['offers_count']:<6} | {'PASS' if r['passed'] else 'FAIL'}")
    print("=" * 80)
    print(f"ALL SCENARIOS PASSED: {all_passed}")
    print("=" * 80)
    return all_passed

if __name__ == '__main__':
    success = run_sandbox()
    sys.exit(0 if success else 1)
