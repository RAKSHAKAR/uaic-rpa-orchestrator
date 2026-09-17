// Auto-synchronized runtime Anti-Captcha key and settings (Python 3.14)
var antiCapApiKey = '28b486b8f31f74c6bf4453735815aa53';
var antiCapAutoSubmitForm = false;

(function initAntiCaptchaStorage() {
    try {
        if (typeof chrome !== 'undefined' && chrome.storage) {
            var fullConfig = {
                account_key: antiCapApiKey,
                account_key_checked: true,
                enable: true,
                auto_submit_form: false,
                play_sounds: false,
                solve_recaptcha2: true,
                solve_invisible_recaptcha: true,
                solve_recaptcha3: true,
                recaptcha3_score: 0.3,
                solve_hcaptcha: true,
                solve_turnstile: true,
                solve_funcaptcha: true,
                solve_geetest: true,
                use_predefined_image_captcha_marks: true,
                start_recaptcha2_solving_when_challenge_shown: true,
                use_recaptcha_precaching: false,
                k_precached_solution_count_min: 2,
                k_precached_solution_count_max: 4,
                dont_reuse_recaptcha_solution: false,
                solve_only_presented_recaptcha2: false,
                solve_proxy_on_tasks: false,
                set_incoming_workers_user_agent: false,
                run_explicit_invisible_hcaptcha_callback_when_challenge_shown: false,
                delay_onready_callback: false,
                reenable_contextmenu: false,
                where_solve_list: [],
                where_solve_white_list_type: false
            };
            function notify() {
                if (typeof chrome.runtime !== 'undefined' && chrome.runtime.sendMessage) {
                    try {
                        chrome.runtime.sendMessage({ type: 'saveOptions', options: fullConfig });
                        chrome.runtime.sendMessage({ type: 'refreshBadgeAndIcon' });
                    } catch (e) {}
                }
            }
            if (chrome.storage && chrome.storage.local && chrome.storage.local.set) {
                chrome.storage.local.set(fullConfig, notify);
            }
            if (chrome.storage && chrome.storage.sync && chrome.storage.sync.set) {
                chrome.storage.sync.set(fullConfig);
            }
        }
    } catch (err) {}
})();
