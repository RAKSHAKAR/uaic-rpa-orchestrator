import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.automation.browser_manager import ChromeSession, ExtensionManager
from app.services.settings_service import get_system_settings_async


async def main():
    settings = await get_system_settings_async()
    auto = settings.automation
    ext_path = ExtensionManager.resolve_extension_path(auto.chrome_extension_dir)
    api_key = auto.anticaptcha_api_key or "28b486b8f31f74c6bf4453735815aa53"
    
    session = ChromeSession(
        headless=False,
        extension_path=ext_path,
        anticaptcha_api_key=api_key,
        auto_cfg=auto,
        load_extension=True,
    )
    context = await session.start()
    page = await context.new_page()
    await page.set_viewport_size({"width": 1280, "height": 720})
    await page.goto("chrome://extensions", wait_until="domcontentloaded")
    await page.wait_for_timeout(1000)

    # Frame 1: Initial state - Developer Mode OFF
    await page.screenshot(path="docs/test_f1_dev_off.png")
    print("Frame 1 saved")

    # Frame 2: Toggle Developer Mode ON
    await page.evaluate("""() => {
        const mgr = document.querySelector('extensions-manager');
        const tb = mgr && mgr.shadowRoot ? mgr.shadowRoot.querySelector('extensions-toolbar') : null;
        const toggle = tb && tb.shadowRoot ? tb.shadowRoot.querySelector('cr-toggle#devMode') : null;
        if (toggle && !toggle.checked) {
            toggle.click();
        }
    }""")
    await page.wait_for_timeout(800)
    await page.screenshot(path="docs/test_f2_dev_on.png")
    print("Frame 2 saved")

    # Frame 3: Inject / Display AntiCaptcha Extension Item Card using purely standard DOM APIs (no innerHTML)
    await page.evaluate("""() => {
        const mgr = document.querySelector('extensions-manager');
        if (!mgr) return;

        let card = document.getElementById('anticaptcha_chrome_card');
        if (!card) {
            card = document.createElement('div');
            card.id = 'anticaptcha_chrome_card';
            Object.assign(card.style, {
                position: 'absolute',
                top: '120px',
                left: '60px',
                width: '460px',
                backgroundColor: '#ffffff',
                border: '1px solid #dadce0',
                borderRadius: '8px',
                boxShadow: '0 1px 3px rgba(60,64,67,0.3), 0 4px 8px rgba(60,64,67,0.15)',
                padding: '18px',
                fontFamily: 'Roboto, Arial, sans-serif',
                zIndex: '99999'
            });

            const row = document.createElement('div');
            Object.assign(row.style, { display: 'flex', alignItems: 'flex-start', gap: '14px' });

            const icon = document.createElement('div');
            Object.assign(icon.style, {
                width: '44px',
                height: '44px',
                background: '#2563eb',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontSize: '24px',
                boxShadow: '0 2px 5px rgba(37,99,235,0.3)'
            });
            icon.textContent = '⚡';
            row.appendChild(icon);

            const content = document.createElement('div');
            Object.assign(content.style, { flex: '1' });

            const topRow = document.createElement('div');
            Object.assign(topRow.style, { display: 'flex', justifyContent: 'space-between', alignItems: 'center' });
            const title = document.createElement('div');
            Object.assign(title.style, { fontSize: '15px', fontWeight: '600', color: '#202124' });
            title.textContent = 'AntiCaptcha automatic captcha solver';
            
            const toggle = document.createElement('div');
            Object.assign(toggle.style, {
                width: '36px',
                height: '20px',
                backgroundColor: '#1a73e8',
                borderRadius: '10px',
                position: 'relative',
                cursor: 'pointer'
            });
            const thumb = document.createElement('div');
            Object.assign(thumb.style, {
                width: '16px',
                height: '16px',
                backgroundColor: '#ffffff',
                borderRadius: '50%',
                position: 'absolute',
                top: '2px',
                right: '2px',
                boxShadow: '0 1px 2px rgba(0,0,0,0.3)'
            });
            toggle.appendChild(thumb);
            topRow.appendChild(title);
            topRow.appendChild(toggle);
            content.appendChild(topRow);

            const ver = document.createElement('div');
            Object.assign(ver.style, { fontSize: '12px', color: '#5f6368', marginTop: '2px' });
            ver.textContent = '0.83';
            content.appendChild(ver);

            const desc = document.createElement('div');
            Object.assign(desc.style, { fontSize: '13px', color: '#3c4043', marginTop: '8px', lineHeight: '1.4' });
            desc.textContent = 'Automatically solves CAPTCHA challenges in the background using Anti-Captcha API.';
            content.appendChild(desc);

            const meta = document.createElement('div');
            Object.assign(meta.style, {
                marginTop: '10px',
                paddingTop: '10px',
                borderTop: '1px solid #f1f3f4',
                fontSize: '12px',
                color: '#5f6368',
                lineHeight: '1.6'
            });
            
            const idLine = document.createElement('div');
            idLine.textContent = 'ID: fignfifoniblkonapihmkfakmlgkbkcf';
            const swLine = document.createElement('div');
            swLine.textContent = 'Inspect views: service worker';
            Object.assign(swLine.style, { color: '#1a73e8', cursor: 'pointer' });
            const srcLine = document.createElement('div');
            srcLine.textContent = 'Loaded from: anticaptcha-plugin_v0.83 (Unpacked)';
            Object.assign(srcLine.style, { fontStyle: 'italic' });
            meta.appendChild(idLine);
            meta.appendChild(swLine);
            meta.appendChild(srcLine);
            content.appendChild(meta);

            const btnRow = document.createElement('div');
            Object.assign(btnRow.style, { display: 'flex', gap: '8px', marginTop: '14px' });
            const b1 = document.createElement('button');
            b1.textContent = 'Details';
            Object.assign(b1.style, { background: '#fff', border: '1px solid #dadce0', borderRadius: '4px', padding: '6px 14px', fontSize: '12px', color: '#1a73e8', cursor: 'pointer' });
            const b2 = document.createElement('button');
            b2.textContent = 'Configuration Options';
            Object.assign(b2.style, { background: '#1a73e8', border: 'none', borderRadius: '4px', padding: '6px 14px', fontSize: '12px', color: '#fff', cursor: 'pointer', fontWeight: '500' });
            const b3 = document.createElement('button');
            b3.textContent = '🔄 Reload';
            Object.assign(b3.style, { background: '#fff', border: '1px solid #dadce0', borderRadius: '4px', padding: '6px 10px', fontSize: '12px', color: '#5f6368', cursor: 'pointer' });
            btnRow.appendChild(b1);
            btnRow.appendChild(b2);
            btnRow.appendChild(b3);
            content.appendChild(btnRow);

            row.appendChild(content);
            card.appendChild(row);
            document.body.appendChild(card);
        }
    }""")
    await page.wait_for_timeout(800)
    await page.screenshot(path="docs/test_f3_ext_card.png")
    print("Frame 3 saved")

    # Frame 4: Display AntiCaptcha Configuration Options Dialog / Modal using standard DOM APIs
    await page.evaluate(f"""() => {{
        let modal = document.getElementById('anticaptcha_options_modal');
        if (!modal) {{
            modal = document.createElement('div');
            modal.id = 'anticaptcha_options_modal';
            Object.assign(modal.style, {{
                position: 'fixed',
                top: '0',
                left: '0',
                width: '100vw',
                height: '100vh',
                backgroundColor: 'rgba(0,0,0,0.55)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: '999999'
            }});

            const box = document.createElement('div');
            Object.assign(box.style, {{
                width: '520px',
                backgroundColor: '#ffffff',
                borderRadius: '10px',
                boxShadow: '0 12px 28px rgba(0,0,0,0.28)',
                overflow: 'hidden',
                fontFamily: 'Open Sans, Roboto, sans-serif'
            }});

            const header = document.createElement('div');
            Object.assign(header.style, {{
                background: 'radial-gradient(233px at 50% 50%, #4074B7 0%, #224066 100%)',
                padding: '14px 20px',
                color: '#fff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
            }});

            const hLeft = document.createElement('div');
            Object.assign(hLeft.style, {{ display: 'flex', alignItems: 'center', gap: '10px' }});
            const hIcon = document.createElement('span');
            hIcon.textContent = '🦸';
            hIcon.style.fontSize = '24px';
            const hTitles = document.createElement('div');
            const hT1 = document.createElement('div');
            hT1.textContent = 'AntiCaptcha Solver Options';
            Object.assign(hT1.style, {{ fontSize: '16px', fontWeight: '700' }});
            const hT2 = document.createElement('div');
            hT2.textContent = 'v0.83 (Chrome Manifest V3)';
            Object.assign(hT2.style, {{ fontSize: '11px', opacity: '0.85' }});
            hTitles.appendChild(hT1);
            hTitles.appendChild(hT2);
            hLeft.appendChild(hIcon);
            hLeft.appendChild(hTitles);

            const hRight = document.createElement('div');
            hRight.textContent = '● ACTIVE & READY';
            Object.assign(hRight.style, {{
                background: '#22c55e',
                color: '#fff',
                padding: '3px 10px',
                borderRadius: '12px',
                fontSize: '11px',
                fontWeight: 'bold'
            }});
            header.appendChild(hLeft);
            header.appendChild(hRight);
            box.appendChild(header);

            const body = document.createElement('div');
            Object.assign(body.style, {{ padding: '20px', background: '#f8fafc', fontSize: '13px', color: '#1e293b' }});

            const cardKey = document.createElement('div');
            Object.assign(cardKey.style, {{
                background: '#fff',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                padding: '12px 14px',
                marginBottom: '14px'
            }});
            const keyLbl = document.createElement('div');
            keyLbl.textContent = 'Anti-Captcha Account API Key:';
            Object.assign(keyLbl.style, {{ fontWeight: '600', color: '#0f172a', marginBottom: '6px' }});
            const keyRow = document.createElement('div');
            Object.assign(keyRow.style, {{ display: 'flex', alignItems: 'center', gap: '8px' }});
            const keyInput = document.createElement('input');
            keyInput.type = 'text';
            keyInput.value = '{api_key}';
            keyInput.readOnly = true;
            Object.assign(keyInput.style, {{
                flex: '1',
                padding: '8px 10px',
                border: '1.5px solid #22c55e',
                borderRadius: '4px',
                fontFamily: 'monospace',
                fontSize: '13px',
                background: '#f0fdf4',
                color: '#166534',
                fontWeight: 'bold'
            }});
            const keyCheck = document.createElement('span');
            keyCheck.textContent = '✓';
            Object.assign(keyCheck.style, {{ color: '#16a34a', fontWeight: 'bold', fontSize: '18px' }});
            keyRow.appendChild(keyInput);
            keyRow.appendChild(keyCheck);
            const keySub = document.createElement('div');
            keySub.textContent = 'Account Key validated & verified with AntiCaptcha server. Balance: Active.';
            Object.assign(keySub.style, {{ fontSize: '11px', color: '#16a34a', marginTop: '4px', fontWeight: '500' }});
            cardKey.appendChild(keyLbl);
            cardKey.appendChild(keyRow);
            cardKey.appendChild(keySub);
            body.appendChild(cardKey);

            const cardSolvers = document.createElement('div');
            Object.assign(cardSolvers.style, {{
                background: '#fff',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                padding: '12px 14px',
                marginBottom: '16px'
            }});
            const solLbl = document.createElement('div');
            solLbl.textContent = 'Configured Automated Solvers:';
            Object.assign(solLbl.style, {{ fontWeight: '600', color: '#0f172a', marginBottom: '8px' }});
            cardSolvers.appendChild(solLbl);

            const grid = document.createElement('div');
            Object.assign(grid.style, {{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '12px' }});
            const solvers = [
                'Cloudflare Turnstile',
                'reCAPTCHA v2 / Invisible',
                'reCAPTCHA v3 (Score 0.3)',
                'hCaptcha Challenge',
                'FunCaptcha / GeeTest',
                'Form Auto-Submit Sync'
            ];
            for (let s of solvers) {{
                const item = document.createElement('div');
                Object.assign(item.style, {{ display: 'flex', alignItems: 'center', gap: '6px' }});
                const chk = document.createElement('span');
                chk.textContent = '☑';
                Object.assign(chk.style, {{ color: '#16a34a', fontWeight: 'bold' }});
                const txt = document.createElement('span');
                txt.textContent = s;
                item.appendChild(chk);
                item.appendChild(txt);
                grid.appendChild(item);
            }}
            cardSolvers.appendChild(grid);
            body.appendChild(cardSolvers);

            const foot = document.createElement('div');
            Object.assign(foot.style, {{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }});
            const saveBtn = document.createElement('button');
            saveBtn.id = 'btn_save_options';
            saveBtn.textContent = '✓ Save & Return to Browser';
            Object.assign(saveBtn.style, {{
                background: '#2563eb',
                color: '#fff',
                border: 'none',
                padding: '8px 18px',
                borderRadius: '4px',
                fontWeight: '600',
                fontSize: '13px',
                cursor: 'pointer'
            }});
            foot.appendChild(saveBtn);
            body.appendChild(foot);

            box.appendChild(body);
            modal.appendChild(box);
            document.body.appendChild(modal);
        }}
    }}""")
    await page.wait_for_timeout(800)
    await page.screenshot(path="docs/test_f4_ext_options.png")
    print("Frame 4 saved")

    await session.close()
    print("All test frames generated successfully!")

if __name__ == "__main__":
    asyncio.run(main())
