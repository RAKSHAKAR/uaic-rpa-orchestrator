
# ─────────────────────────────────────────────────────────────────────────────
# 1. MIAMI-DADE (miami.py)
# ─────────────────────────────────────────────────────────────────────────────
with open("backend/app/automation/florida/miami.py", encoding="utf-8") as f:
    m_content = f.read()

# Replace direct goto with navigate_via_address_bar in navigate_to_search
old_m_nav = """            if "ocs" not in curr_url.lower():
                await page.goto(self.base_url, wait_until="domcontentloaded", timeout=self.timeout_ms)
                await page.wait_for_timeout(1000)"""

new_m_nav = """            if "ocs" not in curr_url.lower():
                await self.navigate_via_address_bar(page, self.base_url, timeout_ms=self.timeout_ms)
                await page.wait_for_timeout(1000)"""

if old_m_nav in m_content:
    m_content = m_content.replace(old_m_nav, new_m_nav, 1)

# In ensure_authenticated, replace fill with interact_and_fill_field
old_m_auth = """            if await _safe_count(email_field) > 0:
                try:
                    await email_field.first.wait_for(state="visible", timeout=12000)
                except Exception:
                    pass
                logger.info(f"[{self.county_name}] Login Step b.ii: Filling saved account credentials...")
                await self.biometric_fill(email_field.first, self.username)
            if await _safe_count(pwd_field) > 0:
                await self.biometric_fill(pwd_field.first, self.password)"""

new_m_auth = """            if await _safe_count(email_field) > 0:
                logger.info(f"[{self.county_name}] Login Step b.ii: Filling saved account credentials...")
                await self.interact_and_fill_field(
                    page,
                    "input#txtUsername, input[name='txtUsername'], #txtUsername, input[type='email']",
                    self.username,
                    field_name="User ID (#txtUsername)",
                    timeout_ms=self.timeout_ms,
                )
            if await _safe_count(pwd_field) > 0:
                await self.interact_and_fill_field(
                    page,
                    "input#txtPassword, input[name='txtPassword'], #txtPassword, input[type='password']",
                    self.password,
                    field_name="Password (#txtPassword)",
                    timeout_ms=self.timeout_ms,
                )"""

if old_m_auth in m_content:
    m_content = m_content.replace(old_m_auth, new_m_auth, 1)

# In search_by_party_name, replace biometric_fill with interact_and_fill_field
old_m_fill = """            if await _safe_count(last_input) > 0:
                try:
                    await last_input.first.wait_for(state="visible", timeout=15000)
                except Exception:
                    pass
                await self.biometric_fill(last_input.first, l_name)

            if f_name and await _safe_count(first_input) > 0:
                await self.biometric_fill(first_input.first, f_name)"""

new_m_fill = """            if await _safe_count(last_input) > 0:
                await self.interact_and_fill_field(
                    page,
                    "input#partyLastName, #partyLastName, #txtLastName, input[name='partyLastName']",
                    l_name,
                    field_name="Last Name (#partyLastName)",
                    timeout_ms=self.timeout_ms,
                )

            if f_name and await _safe_count(first_input) > 0:
                await self.interact_and_fill_field(
                    page,
                    "input#partyFirstName, #partyFirstName, #txtFirstName, input[name='partyFirstName']",
                    f_name,
                    field_name="First Name (#partyFirstName)",
                    timeout_ms=self.timeout_ms,
                )"""

if old_m_fill in m_content:
    m_content = m_content.replace(old_m_fill, new_m_fill, 1)

with open("backend/app/automation/florida/miami.py", "w", encoding="utf-8") as f:
    f.write(m_content)
print("Miami-Dade scraper updated.")

# ─────────────────────────────────────────────────────────────────────────────
# 2. TRAVIS COUNTY (texas/travis.py)
# ─────────────────────────────────────────────────────────────────────────────
with open("backend/app/automation/texas/travis.py", encoding="utf-8") as f:
    tr_content = f.read()

old_tr_nav = """        logger.info(f"[{self.county_name}] Step A: Navigating to Travis County Odyssey portal: {nav_url}")
        try:
            resp = await page.goto(nav_url, wait_until="domcontentloaded", timeout=self.timeout_ms)"""

new_tr_nav = """        logger.info(f"[{self.county_name}] Step A: Navigating to Travis County Odyssey portal: {nav_url}")
        try:
            resp = await self.navigate_via_address_bar(page, nav_url, timeout_ms=self.timeout_ms)"""

if old_tr_nav in tr_content:
    tr_content = tr_content.replace(old_tr_nav, new_tr_nav, 1)

old_tr_fill = """            if await _safe_count(search_input) > 0:
                try:
                    await search_input.first.wait_for(state="visible", timeout=10000)
                except Exception:
                    pass
                await self.biometric_fill(search_input.first, query)
                logger.info(f"[{self.county_name}] Step D: Entered search query: {query}")
                await self.pace_action(page)"""

new_tr_fill = """            if await _safe_count(search_input) > 0:
                await self.interact_and_fill_field(
                    page,
                    "input#caseCriteria_SearchCriteria, #caseCriteria_SearchCriteria, #SearchCriteria",
                    query,
                    field_name="Smart Search Query (#caseCriteria_SearchCriteria)",
                    timeout_ms=self.timeout_ms,
                )
                logger.info(f"[{self.county_name}] Step D: Entered search query: {query}")
                await self.pace_action(page)"""

if old_tr_fill in tr_content:
    tr_content = tr_content.replace(old_tr_fill, new_tr_fill, 1)

with open("backend/app/automation/texas/travis.py", "w", encoding="utf-8") as f:
    f.write(tr_content)
print("Travis County scraper updated.")

# ─────────────────────────────────────────────────────────────────────────────
# 3. DALLAS COUNTY (texas/dallas.py)
# ─────────────────────────────────────────────────────────────────────────────
with open("backend/app/automation/texas/dallas.py", encoding="utf-8") as f:
    dl_content = f.read()

old_dl_nav = """        try:
            logger.info(f"[{self.county_name}] Step A: Navigating to Dallas portal: {nav_url}")
            await page.goto(nav_url, wait_until="domcontentloaded")"""

new_dl_nav = """        try:
            logger.info(f"[{self.county_name}] Step A: Navigating to Dallas portal: {nav_url}")
            await self.navigate_via_address_bar(page, nav_url, timeout_ms=self.timeout_ms)"""

if old_dl_nav in dl_content:
    dl_content = dl_content.replace(old_dl_nav, new_dl_nav, 1)

old_dl_fill = """            if await _safe_count(search_input) > 0:
                try:
                    await search_input.first.wait_for(state="visible", timeout=10000)
                except Exception:
                    pass
                await self.biometric_fill(search_input.first, query)
                logger.info(f"[{self.county_name}] Step D: Entered search query: {query}")
                await self.pace_action(page)"""

new_dl_fill = """            if await _safe_count(search_input) > 0:
                await self.interact_and_fill_field(
                    page,
                    "input#caseCriteria_SearchCriteria, #caseCriteria_SearchCriteria, #SearchCriteria",
                    query,
                    field_name="Smart Search Query (#caseCriteria_SearchCriteria)",
                    timeout_ms=self.timeout_ms,
                )
                logger.info(f"[{self.county_name}] Step D: Entered search query: {query}")
                await self.pace_action(page)"""

if old_dl_fill in dl_content:
    dl_content = dl_content.replace(old_dl_fill, new_dl_fill, 1)

with open("backend/app/automation/texas/dallas.py", "w", encoding="utf-8") as f:
    f.write(dl_content)
print("Dallas County scraper updated.")

# ─────────────────────────────────────────────────────────────────────────────
# 4. HARRIS JP (texas/harris_jp.py)
# ─────────────────────────────────────────────────────────────────────────────
with open("backend/app/automation/texas/harris_jp.py", encoding="utf-8") as f:
    jp_content = f.read()

old_jp_nav = """        try:
            logger.info(f"[{self.county_name}] Step A: Navigating to Harris JP portal: {nav_url}")
            await page.goto(nav_url, wait_until="domcontentloaded")"""

new_jp_nav = """        try:
            logger.info(f"[{self.county_name}] Step A: Navigating to Harris JP portal: {nav_url}")
            await self.navigate_via_address_bar(page, nav_url, timeout_ms=self.timeout_ms)"""

if old_jp_nav in jp_content:
    jp_content = jp_content.replace(old_jp_nav, new_jp_nav, 1)

old_jp_fill = """            if await _safe_count(search_input) > 0:
                try:
                    await search_input.first.wait_for(state="visible", timeout=10000)
                except Exception:
                    pass
                await self.biometric_fill(search_input.first, query)
                logger.info(f"[{self.county_name}] Step D: Entered search query: {query}")
                await self.pace_action(page)"""

new_jp_fill = """            if await _safe_count(search_input) > 0:
                await self.interact_and_fill_field(
                    page,
                    "input#caseCriteria_SearchCriteria, #caseCriteria_SearchCriteria, #SearchCriteria",
                    query,
                    field_name="Smart Search Query (#caseCriteria_SearchCriteria)",
                    timeout_ms=self.timeout_ms,
                )
                logger.info(f"[{self.county_name}] Step D: Entered search query: {query}")
                await self.pace_action(page)"""

if old_jp_fill in jp_content:
    jp_content = jp_content.replace(old_jp_fill, new_jp_fill, 1)

with open("backend/app/automation/texas/harris_jp.py", "w", encoding="utf-8") as f:
    f.write(jp_content)
print("Harris JP scraper updated.")

# ─────────────────────────────────────────────────────────────────────────────
# 5. HARRIS COUNTY CLERK (texas/harris_cclerk.py)
# ─────────────────────────────────────────────────────────────────────────────
with open("backend/app/automation/texas/harris_cclerk.py", encoding="utf-8") as f:
    hc_content = f.read()

old_hc_nav = """        try:
            logger.info(f"[{self.county_name}] Step A: Navigating to Harris County Clerk portal: {self.base_url}")
            await page.goto(self.base_url, wait_until="domcontentloaded")"""

new_hc_nav = """        try:
            logger.info(f"[{self.county_name}] Step A: Navigating to Harris County Clerk portal: {self.base_url}")
            await self.navigate_via_address_bar(page, self.base_url, timeout_ms=self.timeout_ms)"""

if old_hc_nav in hc_content:
    hc_content = hc_content.replace(old_hc_nav, new_hc_nav, 1)

old_hc_fill = """            if await _safe_count(last_input) > 0:
                try:
                    await last_input.first.wait_for(state="visible", timeout=10000)
                except Exception:
                    pass
                await self.biometric_fill(last_input.first, l_name)

            if f_name and await _safe_count(first_input) > 0:
                await self.biometric_fill(first_input.first, f_name)"""

new_hc_fill = """            if await _safe_count(last_input) > 0:
                await self.interact_and_fill_field(
                    page,
                    "input#ctl00_ContentPlaceHolder1_txtLastName, #ctl00_ContentPlaceHolder1_txtLastName, input[name*='txtLastName']",
                    l_name,
                    field_name="Last Name (#txtLastName)",
                    timeout_ms=self.timeout_ms,
                )

            if f_name and await _safe_count(first_input) > 0:
                await self.interact_and_fill_field(
                    page,
                    "input#ctl00_ContentPlaceHolder1_txtFirstName, #ctl00_ContentPlaceHolder1_txtFirstName, input[name*='txtFirstName']",
                    f_name,
                    field_name="First Name (#txtFirstName)",
                    timeout_ms=self.timeout_ms,
                )"""

if old_hc_fill in hc_content:
    hc_content = hc_content.replace(old_hc_fill, new_hc_fill, 1)

with open("backend/app/automation/texas/harris_cclerk.py", "w", encoding="utf-8") as f:
    f.write(hc_content)
print("Harris County Clerk scraper updated.")

# ─────────────────────────────────────────────────────────────────────────────
# 6. HARRIS DISTRICT CLERK (texas/harris_district.py)
# ─────────────────────────────────────────────────────────────────────────────
with open("backend/app/automation/texas/harris_district.py", encoding="utf-8") as f:
    hd_content = f.read()

old_hd_nav = """        try:
            logger.info(f"[{self.county_name}] Step A: Navigating to Harris District portal: {self.base_url}")
            await page.goto(self.base_url, wait_until="domcontentloaded")"""

new_hd_nav = """        try:
            logger.info(f"[{self.county_name}] Step A: Navigating to Harris District portal: {self.base_url}")
            await self.navigate_via_address_bar(page, self.base_url, timeout_ms=self.timeout_ms)"""

if old_hd_nav in hd_content:
    hd_content = hd_content.replace(old_hd_nav, new_hd_nav, 1)

old_hd_fill = """            if await _safe_count(last_input) > 0:
                try:
                    await last_input.first.wait_for(state="visible", timeout=10000)
                except Exception:
                    pass
                await self.biometric_fill(last_input.first, l_name)

            if f_name and await _safe_count(first_input) > 0:
                await self.biometric_fill(first_input.first, f_name)"""

new_hd_fill = """            if await _safe_count(last_input) > 0:
                await self.interact_and_fill_field(
                    page,
                    "input#ctl00_ContentPlaceHolder1_txtLastName, #ctl00_ContentPlaceHolder1_txtLastName, input[name*='txtLastName']",
                    l_name,
                    field_name="Last Name (#txtLastName)",
                    timeout_ms=self.timeout_ms,
                )

            if f_name and await _safe_count(first_input) > 0:
                await self.interact_and_fill_field(
                    page,
                    "input#ctl00_ContentPlaceHolder1_txtFirstName, #ctl00_ContentPlaceHolder1_txtFirstName, input[name*='txtFirstName']",
                    f_name,
                    field_name="First Name (#txtFirstName)",
                    timeout_ms=self.timeout_ms,
                )"""

if old_hd_fill in hd_content:
    hd_content = hd_content.replace(old_hd_fill, new_hd_fill, 1)

with open("backend/app/automation/texas/harris_district.py", "w", encoding="utf-8") as f:
    f.write(hd_content)
print("Harris District Clerk scraper updated.")
