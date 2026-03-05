/* Polymarket Overlay Mode — vanilla JS, no deps */
(function () {
  var _pollTimer = null;
  var _active = false;

  // ── CAUSAL KEYWORDS ──
  // Maps headline keywords to market search terms that are causally relevant
  // Generic matching: extract first 4 meaningful words for search
  function extractSearchTerms(text) {
    if (!text) return '';
    // Remove common filler words
    var stops = ['the','a','an','and','or','but','in','on','at','to','for','of','is','are','was','were',
                 'has','have','had','with','from','by','as','its','it','this','that','no','not','may',
                 'new','will','could','would','should','can','do','does','did','be','been','being'];
    var words = text.replace(/[^\w\s]/g, ' ').split(/\s+/).filter(function(w) {
      return w.length > 2 && stops.indexOf(w.toLowerCase()) === -1;
    });
    return words.slice(0, 4).join(' ');
  }

  // Simple causal relevance check — server already scores, so just do light validation
  function isCausallyRelevant(headline, marketQuestion) {
    if (!headline || !marketQuestion) return false;
    // Server already does causal scoring; just check there's ANY word overlap
    var h = headline.toLowerCase();
    var q = marketQuestion.toLowerCase();
    var hWords = h.replace(/[^\w\s]/g, ' ').split(/\s+/).filter(function(w) { return w.length > 3; });
    var overlap = hWords.some(function(w) { return q.indexOf(w) !== -1; });
    return overlap; // At least one meaningful word overlap
  }

  function initPolymarketMode() {
    var saved = localStorage.getItem('intel-pm-mode');
    _active = saved === 'on';
    updateButton();
    if (_active) enableMode();
  }

  function updateButton() {
    var btn = document.getElementById('pm-toggle');
    if (!btn) return;
    btn.style.opacity = _active ? '1' : '0.5';
    btn.title = _active ? 'Polymarket ON — click to disable' : 'Toggle Polymarket mode';
  }

  window.setPolymarketMode = function () {
    _active = !_active;
    localStorage.setItem('intel-pm-mode', _active ? 'on' : 'off');
    updateButton();
    if (_active) {
      enableMode();
    } else {
      disableMode();
    }
  };

  function enableMode() {
    document.body.classList.add('pm-mode');
    loadAllOverlays();
    _pollTimer = setInterval(loadAllOverlays, 30000);
  }

  function disableMode() {
    document.body.classList.remove('pm-mode');
    if (_pollTimer) { clearInterval(_pollTimer); _pollTimer = null; }
    // Remove all overlays
    document.querySelectorAll('.pm-overlay, .pm-no-market').forEach(function (el) { el.remove(); });
  }

  function loadAllOverlays() {
    var cards = document.querySelectorAll('.ecard, .fcard, .hero-banner');
    cards.forEach(function (card) {
      var search = card.getAttribute('data-search') || '';
      var terms = extractSearchTerms(search);
      if (!terms) {
        injectNoMarket(card);
        return;
      }
      fetchMarket(card, terms, search);
    });
  }

  function fetchMarket(card, terms, headline) {
    // Extract domain from card badge text (e.g. "war", "crypto")
    var badge = card.querySelector('[class*="badge"],[class*="pill"],[class*="domain"]');
    var domain = (badge ? badge.textContent : (card.getAttribute('data-domain') || '')).toLowerCase()
      .replace(/[^a-z-]/g, '').trim();
    var url = '/api/polymarket/market?q=' + encodeURIComponent(terms) + '&domain=' + encodeURIComponent(domain);
    fetch(url)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data || !data.question) {
          injectNoMarket(card);
          return;
        }
        // Causal relevance check
        if (!isCausallyRelevant(headline, data.question)) {
          injectNoMarket(card);
          return;
        }
        injectOverlay(card, data);
        // Fetch chart for first outcome
        if (data.outcomes && data.outcomes[0] && data.outcomes[0].token_id) {
          fetchChart(card, data.outcomes[0].token_id);
        }
      })
      .catch(function () { injectNoMarket(card); });
  }

  function fetchChart(card, tokenId) {
    fetch('/api/polymarket/chart?token_id=' + encodeURIComponent(tokenId))
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data.points || !data.points.length) return;
        var svg = card.querySelector('.pm-chart');
        if (svg) drawSparkline(svg, data.points);
      })
      .catch(function () {});
  }

  function injectNoMarket(card) {
    // Ensure card is positioned
    if (getComputedStyle(card).position === 'static') card.style.position = 'relative';
    // Remove existing
    var existing = card.querySelector('.pm-no-market');
    if (existing) return; // already there
    var old = card.querySelector('.pm-overlay');
    if (old) old.remove();
    var el = document.createElement('div');
    el.className = 'pm-no-market';
    el.textContent = '\u2014';
    card.appendChild(el);
  }

  function injectOverlay(card, data) {
    if (getComputedStyle(card).position === 'static') card.style.position = 'relative';
    // Remove old overlay/badge
    var oldOverlay = card.querySelector('.pm-overlay');
    var oldBadge = card.querySelector('.pm-no-market');
    if (oldBadge) oldBadge.remove();

    var question = data.question || '';
    if (question.length > 40) question = question.substring(0, 40) + '\u2026';

    var outcomesHtml = '';
    (data.outcomes || []).slice(0, 3).forEach(function (o) {
      var pct = Math.round(o.price * 100);
      var pctStr = pct + '%';
      outcomesHtml +=
        '<div class="pm-outcome">' +
          '<span class="pm-name">' + escHtml(o.name).substring(0, 4).toUpperCase() + '</span>' +
          '<span class="pm-pct" data-pct="' + pct + '">' + pctStr + '</span>' +
          '<div class="pm-bar"><div class="pm-fill" style="width:' + pct + '%"></div></div>' +
        '</div>';
    });

    var html =
      '<div class="pm-question">\uD83D\uDCCA This finding may affect:</div>' +
      '<div class="pm-question" style="margin-top:1px;opacity:1;font-weight:600">' + escHtml(question) + '</div>' +
      '<svg class="pm-chart" viewBox="0 0 80 28" preserveAspectRatio="none"></svg>' +
      '<div class="pm-outcomes">' + outcomesHtml + '</div>' +
      '<div class="pm-live-dot"></div>';

    if (oldOverlay) {
      // Update in place — animate pct changes
      var oldPcts = oldOverlay.querySelectorAll('.pm-pct');
      oldOverlay.innerHTML = html;
      // Highlight changed values
      var newPcts = oldOverlay.querySelectorAll('.pm-pct');
      newPcts.forEach(function (el, i) {
        var oldVal = oldPcts[i] ? oldPcts[i].getAttribute('data-pct') : '';
        if (oldVal && oldVal !== el.getAttribute('data-pct')) {
          el.style.transition = 'color .3s';
          el.style.color = '#4ade80';
          setTimeout(function () { el.style.color = ''; }, 1200);
        }
      });
    } else {
      var overlay = document.createElement('div');
      overlay.className = 'pm-overlay';
      overlay.innerHTML = html;
      card.appendChild(overlay);
    }
  }

  function drawSparkline(svg, points) {
    if (!points.length) return;
    var W = 80, H = 28;
    var prices = points.map(function (p) { return p.p; });
    var min = Math.min.apply(null, prices);
    var max = Math.max.apply(null, prices);
    var range = max - min || 0.01;

    var coords = points.map(function (p, i) {
      var x = (i / (points.length - 1 || 1)) * W;
      var y = H - ((p.p - min) / range) * (H - 4) - 2;
      return x.toFixed(1) + ',' + y.toFixed(1);
    });

    var polyline = coords.join(' ');
    // Fill area
    var fillCoords = '0,' + H + ' ' + polyline + ' ' + W + ',' + H;
    var last = coords[coords.length - 1].split(',');

    svg.innerHTML =
      '<polygon points="' + fillCoords + '" fill="rgba(255,255,255,0.08)" />' +
      '<polyline points="' + polyline + '" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="1.2" />' +
      '<circle cx="' + last[0] + '" cy="' + last[1] + '" r="2" fill="#4ade80" opacity="0.9">' +
        '<animate attributeName="opacity" values="0.9;0.4;0.9" dur="2s" repeatCount="indefinite" />' +
      '</circle>';
  }

  function escHtml(s) {
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  // Init on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPolymarketMode);
  } else {
    initPolymarketMode();
  }
})();
