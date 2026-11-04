with open("backend/app/automation/florida/hillsborough.py", encoding="utf-8") as f:
    content = f.read()

# 1. Update navigation to address bar navigation
old_nav = """                logger.info(f"[{self.county_name}] Step a: Opening Hillsborough portal base: {landing_url}")
                await page.goto(landing_url, wait_until="domcontentloaded", timeout=self.timeout_ms)"""

new_nav = """                logger.info(f"[{self.county_name}] Step a: Opening Hillsborough portal base: {landing_url}")
                await self.navigate_via_address_bar(page, landing_url, timeout_ms=self.timeout_ms)"""

if old_nav in content:
    content = content.replace(old_nav, new_nav, 1)

# 2. Update step d filling
old_fill = """            # 1. First Name
            if f_name:
                if await _safe_count(first_input) > 0:
                    await self.biometric_fill(first_input.first, f_name)
                else:
                    try:
                        await page.evaluate(\"\"\"(val) => {
                            const el = document.querySelector('#spFirstName') || document.querySelector("input[name='partyFirstName']");
                            if (el) {
                                el.value = val;
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                            }
                        }\"\"\", f_name)
                    except Exception:
                        pass
                await page.wait_for_timeout(100)

            # 2. Last Name
            if await _safe_count(last_input) == 0:
                await self.select_party_search_tab(page)
            if await _safe_count(last_input) > 0:
                await self.biometric_fill(last_input.first, l_name)
            else:
                try:
                    await page.evaluate(\"\"\"(val) => {
                        const el = document.querySelector('#spLastName') || document.querySelector("input[name='partyLastName']");
                        if (el) {
                            el.value = val;
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }\"\"\", l_name)
                except Exception:
                    pass
            await page.wait_for_timeout(100)

            # 3. On or After (spDateFiledAfter with readonly removal)
            if date_of_loss and await _safe_count(dol_input) > 0:
                clean_dol = _normalize_court_date(date_of_loss) or date_of_loss.strip()
                try:
                    await page.evaluate(
                        \"\"\"(val) => {
                            const el = document.querySelector('#spDateFiledAfter') || document.querySelector("input[name='date']") || document.querySelector("input[name='spDateFiledAfter']");
                            if (el) {
                                el.removeAttribute('readonly');
                                el.value = val;
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                                el.dispatchEvent(new Event('blur', { bubbles: true }));
                            }
                            if (typeof window.$ !== 'undefined' && window.$('#spDateFiledAfter').datepicker) {
                                try { window.$('#spDateFiledAfter').datepicker('setDate', val); } catch(e) {}
                            }
                        }\"\"\",
                        clean_dol,
                    )
                    logger.info(f"[{self.county_name}] Step d: Filled spDateFiledAfter with DOL: {clean_dol}")
                except Exception as e:
                    logger.warning(f"[{self.county_name}] DOM date fill note: {e}, falling back to biometric_fill")
                    try:
                        await self.biometric_fill(dol_input.first, clean_dol)
                    except Exception as ex:
                        logger.warning(f"[{self.county_name}] Could not fill datepicker: {ex}")"""

new_fill = """            # 1. First Name
            if f_name:
                await self.interact_and_fill_field(
                    page,
                    "input#spFirstName, #spFirstName, input[name='partyFirstName']",
                    f_name,
                    field_name="First Name (#spFirstName)",
                    timeout_ms=self.timeout_ms,
                )
                await page.wait_for_timeout(100)

            # 2. Last Name
            if await _safe_count(last_input) == 0:
                await self.select_party_search_tab(page)
            await self.interact_and_fill_field(
                page,
                "input#spLastName, #spLastName, input[name='partyLastName']",
                l_name,
                field_name="Last Name (#spLastName)",
                timeout_ms=self.timeout_ms,
            )
            await page.wait_for_timeout(100)

            # 3. On or After Date
            if date_of_loss:
                clean_dol = _normalize_court_date(date_of_loss) or date_of_loss.strip()
                await self.interact_and_fill_field(
                    page,
                    "input#spDateFiledAfter, #spDateFiledAfter, input[name='spDateFiledAfter'], input[name='date']",
                    clean_dol,
                    field_name="On or After Date (#spDateFiledAfter)",
                    timeout_ms=self.timeout_ms,
                )"""

if old_fill in content:
    content = content.replace(old_fill, new_fill, 1)
    print("Replaced old_fill in hillsborough.py")
else:
    # try with CRLF
    old_fill_cr = old_fill.replace("\n", "\r\n")
    if old_fill_cr in content:
        content = content.replace(old_fill_cr, new_fill.replace("\n", "\r\n"), 1)
        print("Replaced old_fill_cr in hillsborough.py")
    else:
        print("Could not match old_fill in hillsborough.py")

with open("backend/app/automation/florida/hillsborough.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Hillsborough scraper patched successfully.")

