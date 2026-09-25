import re

file_path = "/Users/inno/Desktop/quantum_pricing/control_tower/static/control_tower.js"
with open(file_path, "r") as f:
    content = f.read()

# 1. Fix placeholders
content = content.replace("req.customer_name || 'Google'", "req.customer_name || 'Unknown Customer'")
content = content.replace("req.service_product_name || \"Enterprise Platform Modernization\"", "req.service_product_name || 'Unknown Service'")
content = content.replace("req.service_product_name || 'Enterprise Platform Modernization'", "req.service_product_name || 'Unknown Service'")
content = content.replace("data.customer_name || activeReq?.customer_name || 'Google'", "data.customer_name || activeReq?.customer_name || 'Unknown Customer'")
content = content.replace("data.number || activeReq?.number || 'PRI0001021'", "data.number || activeReq?.number || 'PRI-UNKNOWN'")
content = content.replace("data.number || 'PRI0001021'", "data.number || 'PRI-UNKNOWN'")
content = content.replace("data.customer_name || 'Google'", "data.customer_name || 'Unknown Customer'")

# 2. Modify loadRequests
old_load = """async function loadRequests() {
  try {
    const r = await fetch("/api/requests");
    const data = await r.json();
    requests = data.requests || [];
    splitRequests();
    activeReq = null;
    activeSide = null;
    activeFannedData = null;
    
    const W = window.innerWidth;
    currentRootX = W / 2;
    currentLeftX = W / 2 - 320;
    currentRightX = W / 2 + 320;
    currentInactiveOpacity = 1.0;

    animateGraphToState('EXPANDED', null, 800);
  } catch (e) {
    console.error("Failed to load requests", e);
  }
}"""

new_load = """async function loadRequests(preserveState = false) {
  try {
    const r = await fetch("/api/requests");
    const data = await r.json();
    const newRequests = data.requests || [];
    
    if (preserveState && activeSide && graphState === 'SELECTED') {
      const currentIds = new Set(requests.map(req => req.sys_id));
      const added = newRequests.filter(req => !currentIds.has(req.sys_id));
      requests = newRequests;
      
      if (added.length > 0) {
        const newReq = added[0];
        if (activeSide === 'LEFT') {
          leftRequests.unshift(newReq);
          if (leftRequests.length > 3) leftRequests.pop();
        } else {
          rightRequests.unshift(newReq);
          if (rightRequests.length > 3) rightRequests.pop();
        }
      }
      renderGraphFrame();
    } else {
      requests = newRequests;
      splitRequests();
      activeReq = null;
      activeSide = null;
      activeFannedData = null;
      
      const W = window.innerWidth;
      currentRootX = W / 2;
      currentLeftX = W / 2 - 320;
      currentRightX = W / 2 + 320;
      currentInactiveOpacity = 1.0;

      animateGraphToState('EXPANDED', null, 800);
    }
  } catch (e) {
    console.error("Failed to load requests", e);
  }
}"""

content = content.replace(old_load, new_load)

# 3. Modify createBtn
old_create = """await loadRequests();"""
new_create = """const wasSelected = (graphState === 'SELECTED');
    await loadRequests(wasSelected);"""

# Carefully replace the specific createBtn occurrence
create_btn_block = """if ($("createBtn")) $("createBtn").onclick = async () => {
  $("createBtn").textContent = "Creating...";
  $("createBtn").disabled = true;
  try {
    const res = await fetch("/api/requests", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        customer_name: $("fCustomer").value,
        service_product_name: $("fService").value,
        commercial_objective: $("fObjective").value,
        additional_context: $("fContext").value
      })
    });
    if(!res.ok) throw new Error("Failed to create");
    $("modal").classList.add("hidden");
    await loadRequests();
  } catch(e) {
    alert(e.message);
  } finally {
    $("createBtn").textContent = "Create Analysis Request";
    $("createBtn").disabled = false;
  }
};"""

new_create_btn_block = create_btn_block.replace("await loadRequests();", new_create)
content = content.replace(create_btn_block, new_create_btn_block)


# 4. Add "Show More" functionality on Home page
# Inside renderGraphFrame()
# Let's inject after `hideNode('orb-add-btn');`
# wait, actually it's easier to inject at the end of the `if (graphState === 'INITIAL') return;` check, 
# or just after drawing RIGHT Column cards.

show_more_injection = """
  // Render RIGHT Column Cards (Odd - Max 3)
"""

show_more_code = """
  if (graphState !== 'SELECTED' && requests.length > 6) {
    const extraCount = requests.length - 6;
    renderNode('show-more', `
      <div class="orb-label" style="padding:4px 12px; border-radius:12px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.2); backdrop-filter:blur(10px); cursor:default; pointer-events:auto;">
        <span style="font-size:0.75rem; color:#94a3b8; font-weight:700; text-transform:uppercase;">+${extraCount} More Deals</span>
      </div>
    `, rootX, cy + 180, "node-orb", null, 1.0, 0);
  } else {
    hideNode('show-more');
  }

  // Render RIGHT Column Cards (Odd - Max 3)
"""
content = content.replace(show_more_injection, show_more_code)

with open(file_path, "w") as f:
    f.write(content)

print("JS patched.")
