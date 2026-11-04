"""Surgically integrate security block detection and real WAF cooldowns into all 8 county bots with exact indentation."""

# Fix Dallas
dallas_path = "backend/app/automation/texas/dallas.py"
with open(dallas_path, encoding="utf-8") as f:
    dl_code = f.read()

bad_dl = """                t_sub_end = datetime.now()
                self.record_stage("submit", "Search Submit", t_sub_start, t_sub_end)

        is_blocked, reason, cooldown_secs = await self.detect_security_block(page)
        if is_blocked:
            raise SecurityBlockException(reason, cooldown_seconds=cooldown_secs, portal_key=self.county_name)
                break"""

good_dl = """                t_sub_end = datetime.now()
                self.record_stage("submit", "Search Submit", t_sub_start, t_sub_end)

                is_blocked, reason, cooldown_secs = await self.detect_security_block(page)
                if is_blocked:
                    raise SecurityBlockException(reason, cooldown_seconds=cooldown_secs, portal_key=self.county_name)
                break"""

if bad_dl in dl_code:
    dl_code = dl_code.replace(bad_dl, good_dl, 1)
    with open(dallas_path, "w", encoding="utf-8") as f:
        f.write(dl_code)
    print("Fixed dallas.py indentation")

# Fix Travis
travis_path = "backend/app/automation/texas/travis.py"
with open(travis_path, encoding="utf-8") as f:
    tr_code = f.read()

bad_tr = """                t_sub_end = datetime.now()
                self.record_stage("submit", "Search Submit", t_sub_start, t_sub_end)

        is_blocked, reason, cooldown_secs = await self.detect_security_block(page)
        if is_blocked:
            raise SecurityBlockException(reason, cooldown_seconds=cooldown_secs, portal_key=self.county_name)
                break"""

good_tr = """                t_sub_end = datetime.now()
                self.record_stage("submit", "Search Submit", t_sub_start, t_sub_end)

                is_blocked, reason, cooldown_secs = await self.detect_security_block(page)
                if is_blocked:
                    raise SecurityBlockException(reason, cooldown_seconds=cooldown_secs, portal_key=self.county_name)
                break"""

if bad_tr in tr_code:
    tr_code = tr_code.replace(bad_tr, good_tr, 1)
    with open(travis_path, "w", encoding="utf-8") as f:
        f.write(tr_code)
    print("Fixed travis.py indentation")

# Fix Harris JP
hjp_path = "backend/app/automation/texas/harris_jp.py"
with open(hjp_path, encoding="utf-8") as f:
    hjp_code = f.read()

bad_hjp = """                t_sub_end = datetime.now()
                self.record_stage("submit", "Search Submit", t_sub_start, t_sub_end)

        is_blocked, reason, cooldown_secs = await self.detect_security_block(page)
        if is_blocked:
            raise SecurityBlockException(reason, cooldown_seconds=cooldown_secs, portal_key=self.county_name)
                break"""

good_hjp = """                t_sub_end = datetime.now()
                self.record_stage("submit", "Search Submit", t_sub_start, t_sub_end)

                is_blocked, reason, cooldown_secs = await self.detect_security_block(page)
                if is_blocked:
                    raise SecurityBlockException(reason, cooldown_seconds=cooldown_secs, portal_key=self.county_name)
                break"""

if bad_hjp in hjp_code:
    hjp_code = hjp_code.replace(bad_hjp, good_hjp, 1)
    with open(hjp_path, "w", encoding="utf-8") as f:
        f.write(hjp_code)
    print("Fixed harris_jp.py indentation")
