// touch.js - Touch and gesture handling for PinePhone
(function(){
    // Guard for DOM
    if (typeof document === 'undefined') return;

    const activityFeed = document.getElementById('activity-feed');
    const app = document.getElementById('app') || document.body;
    const cmdButtons = Array.from(document.querySelectorAll('.cmd-btn'));

    // Config
    const SWIPE_THRESHOLD = 50; // px
    const SWIPE_VELOCITY = 0.3; // px/ms
    const LONGPRESS_MS = 600;
    const DOUBLE_TAP_MS = 300;
    const PULL_REFRESH_THRESHOLD = 60;

    // State
    let startX = 0, startY = 0, startTime = 0;
    let lastTap = 0;
    let longPressTimer = null;
    let isPulling = false;
    let pullDistance = 0;
    let initialScale = 1;
    let pinchStartDist = null;
    let isPinching = false;

    function emitHaptic() {
        if (navigator.vibrate) navigator.vibrate(10);
    }

    function sendCommand(name, payload={}) {
        try { window.sendCommand && window.sendCommand(name); }
        catch(e) { console.warn('sendCommand missing', e); }
    }

    // Utility
    function getDist(t1, t2) {
        const dx = t2.clientX - t1.clientX;
        const dy = t2.clientY - t1.clientY;
        return Math.sqrt(dx*dx + dy*dy);
    }

    // Touch start
    function onTouchStart(e) {
        if (!e.touches || e.touches.length === 0) return;
        const t = e.touches[0];
        startX = t.clientX; startY = t.clientY; startTime = Date.now();
        pinchStartDist = (e.touches.length > 1) ? getDist(e.touches[0], e.touches[1]) : null;
        isPinching = !!pinchStartDist;

        // Long-press
        longPressTimer = setTimeout(() => {
            emitHaptic();
            // Long-press action
            sendCommand('long_press');
            // Visual feedback
            app.classList.add('touch-longpress');
        }, LONGPRESS_MS);

        // Double-tap detection
        const now = Date.now();
        if (now - lastTap < DOUBLE_TAP_MS) {
            emitHaptic();
            sendCommand('quick_action');
            lastTap = 0; // reset
        } else {
            lastTap = now;
        }
    }

    // Touch move
    function onTouchMove(e) {
        if (!e.touches || e.touches.length === 0) return;

        // If pinching, handle scale
        if (e.touches.length > 1) {
            const dist = getDist(e.touches[0], e.touches[1]);
            if (pinchStartDist && Math.abs(dist - pinchStartDist) > 8) {
                isPinching = true;
                const scale = Math.max(0.7, Math.min(2, initialScale * (dist / pinchStartDist)));
                if (activityFeed) activityFeed.style.transform = `scale(${scale})`;
            }
            // Prevent other gestures while pinching
            clearTimeout(longPressTimer);
            return;
        }

        const t = e.touches[0];
        const dx = t.clientX - startX;
        const dy = t.clientY - startY;

        // Pull-to-refresh: when at top of feed and dragging down
        if (activityFeed && activityFeed.scrollTop <= 0 && dy > 0 && Math.abs(dy) > Math.abs(dx)) {
            // prevent overscroll native
            e.preventDefault();
            pullDistance = dy;
            if (pullDistance > 0) {
                isPulling = true;
                activityFeed.style.transform = `translateY(${Math.min(pullDistance, 120)}px)`;
                if (pullDistance > PULL_REFRESH_THRESHOLD) {
                    activityFeed.classList.add('pull-ready');
                } else {
                    activityFeed.classList.remove('pull-ready');
                }
            }
            clearTimeout(longPressTimer);
        }
    }

    // Touch end
    function onTouchEnd(e) {
        clearTimeout(longPressTimer);
        app.classList.remove('touch-longpress');

        if (isPinching) {
            // finalize pinch
            const t = e.changedTouches && e.changedTouches[0];
            initialScale = parseFloat(getComputedStyle(activityFeed).transform.split(',')[0] || 1) || initialScale;
            pinchStartDist = null;
            isPinching = false;
            return;
        }

        // If pull-to-refresh was active
        if (isPulling) {
            activityFeed.style.transition = 'transform 220ms ease-out';
            if (pullDistance > PULL_REFRESH_THRESHOLD) {
                // Trigger refresh
                emitHaptic();
                sendCommand('status'); // use status as a state refresh
                activityFeed.classList.remove('pull-ready');
                activityFeed.style.transform = 'translateY(0px)';
            } else {
                activityFeed.style.transform = 'translateY(0px)';
            }
            setTimeout(() => {
                activityFeed.style.transition = '';
                activityFeed.style.transform = '';
            }, 250);
            isPulling = false; pullDistance = 0;
            return;
        }

        // No pinch or pull: handle swipe
        const now = Date.now();
        const dt = now - startTime;
        const touch = (e.changedTouches && e.changedTouches[0]) || null;
        if (!touch) return;
        const dx = touch.clientX - startX;
        const dy = touch.clientY - startY;

        const absX = Math.abs(dx), absY = Math.abs(dy);
        if (Math.max(absX, absY) < SWIPE_THRESHOLD) return; // not a swipe

        // Determine direction
        if (absY > absX) {
            if (dy < -SWIPE_THRESHOLD) {
                // Swipe up
                emitHaptic();
                // Move activity feed up (older)
                if (activityFeed) activityFeed.scrollBy({ top: -200, behavior: 'smooth' });
                sendCommand('swipe_up');
            } else if (dy > SWIPE_THRESHOLD) {
                // Swipe down
                emitHaptic();
                if (activityFeed) activityFeed.scrollBy({ top: 200, behavior: 'smooth' });
                sendCommand('swipe_down');
            }
        } else {
            if (dx < -SWIPE_THRESHOLD) {
                // Swipe left
                emitHaptic();
                sendCommand('swipe_left');
            } else if (dx > SWIPE_THRESHOLD) {
                // Swipe right
                emitHaptic();
                sendCommand('swipe_right');
            }
        }
    }

    // Attach to app root to capture gestures globally
    app.addEventListener('touchstart', onTouchStart, { passive: true });
    app.addEventListener('touchmove', onTouchMove, { passive: false });
    app.addEventListener('touchend', onTouchEnd, { passive: true });
    app.addEventListener('touchcancel', onTouchEnd, { passive: true });

    // Button visual feedback and haptics
    cmdButtons.forEach(btn => {
        // ensure minimum touch target
        btn.style.minHeight = btn.style.minHeight || '44px';
        btn.addEventListener('touchstart', (e) => {
            btn.classList.add('touch-active');
            emitHaptic();
        }, { passive: true });
        btn.addEventListener('touchend', (e) => {
            btn.classList.remove('touch-active');
        });
        btn.addEventListener('touchcancel', (e) => {
            btn.classList.remove('touch-active');
        });
    });

    // Make activity items respond to touch for quick interactions (double-tap handled globally)
    function enhanceActivityItems(){
        const items = document.querySelectorAll('.activity-item');
        items.forEach(it => {
            it.addEventListener('touchstart', () => it.classList.add('touch-active'));
            it.addEventListener('touchend', () => it.classList.remove('touch-active'));
            it.addEventListener('touchcancel', () => it.classList.remove('touch-active'));
        });
    }

    // Observe activity feed for new items
    const observer = new MutationObserver(enhanceActivityItems);
    if (activityFeed) observer.observe(activityFeed, { childList: true, subtree: true });

    // Expose some helpers for debugging
    window._touch = {
        sendCommand: sendCommand
    };

})();
