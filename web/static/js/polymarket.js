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
    // Try to load from pre-fetched cache first (much faster, no rate limits)
    // Extract rid + date from URL path e.g. /domain/war/2026-03-05
    var pathParts = window.location.pathname.split('/');
    var rid = '';
    var dateStr = '';
    if (pathParts[1] === 'domain' && pathParts[2]) {
      rid = pathParts[2];
      dateStr = pathParts[3] || '';
    }
    // Also check for sub query param
    var sub = new URLSearchParams(window.location.search).get('sub') || '';
    if (sub) rid = sub;

    if (rid && dateStr) {
      // Domain page — try batch cache
      fetch('/api/polymarket/cached?rid=' + encodeURIComponent(rid) + '&date=' + encodeURIComponent(dateStr))
        .then(function(r) { return r.json(); })
        .then(function(cache) {
          cards.forEach(function(card, idx) {
            var cached = cache[String(idx)];
            if (cached && cached.question) {
              injectOverlay(card, cached);
              var tokens = (cached.chart_tokens || []).filter(Boolean);
              var outcomeTokens = (cached.outcomes || []).map(function(o){ return o.token_id; }).filter(Boolean);
              var allTokens = tokens.concat(outcomeTokens).slice(0, 6).join(',');
              if (allTokens) fetchChart(card, allTokens);
            } else {
              // Fall back to live API for this card
              var search = card.getAttribute('data-search') || '';
              var terms = extractSearchTerms(search);
              if (terms) fetchMarket(card, terms, search);
              else injectNoMarket(card);
            }
          });
        })
        .catch(function() {
          // Cache unavailable — fall back to live API for all cards
          cards.forEach(function(card) {
            var search = card.getAttribute('data-search') || '';
            var terms = extractSearchTerms(search);
            if (terms) fetchMarket(card, terms, search);
            else injectNoMarket(card);
          });
        });
      return;
    }

    // Homepage — use live API per card
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
    // Use data-domain attribute (always English id like "war", "crypto")
    var domain = card.getAttribute('data-domain') || '';
    // Use full headline for better scoring (always English via data-search)
    var q = headline || terms;
    var url = '/api/polymarket/market?q=' + encodeURIComponent(q) + '&domain=' + encodeURIComponent(domain);
    fetch(url)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data || !data.question) {
          injectNoMarket(card);
          return;
        }
        // Light relevance check — trust server scoring
        if (!isCausallyRelevant(headline, data.question)) {
          injectNoMarket(card);
          return;
        }
        injectOverlay(card, data);
        // Use chart_tokens (high-vol siblings) first, then fall back to outcome tokens
        var chartTokens = (data.chart_tokens || []).filter(Boolean);
        var outcomeTokens = (data.outcomes || []).map(function(o) { return o.token_id; }).filter(Boolean);
        var allTokens = chartTokens.concat(outcomeTokens);
        if (allTokens.length) fetchChart(card, allTokens.slice(0, 6).join(','));
      })
      .catch(function () { injectNoMarket(card); });
  }

  function fetchChart(card, tokenIds) {
    fetch('/api/polymarket/chart?token_id=' + encodeURIComponent(tokenIds))
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data.points || data.points.length < 3) return; // Skip if not enough history
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
    if (question.length > 55) question = question.substring(0, 55) + '\u2026';

    // Right column: outcomes stacked vertically
    var outcomesHtml = '';
    (data.outcomes || []).slice(0, 3).forEach(function (o) {
      var pct = Math.round(o.price * 100);
      outcomesHtml +=
        '<div class="pm-outcome">' +
          '<div class="pm-outcome-row">' +
            '<span class="pm-name">' + escHtml(o.name).substring(0, 4).toUpperCase() + '</span>' +
            '<span class="pm-pct" data-pct="' + pct + '">' + pct + '%</span>' +
          '</div>' +
          '<div class="pm-bar"><div class="pm-fill" style="width:' + pct + '%"></div></div>' +
        '</div>';
    });

    // Background: Polymarket event image (grayscale + dark tint via CSS)
    var bgHtml = '';
    if (data.event_image) {
      bgHtml = '<div class="pm-bg" style="background-image:url(' + escHtml(data.event_image) + ')"></div>';
    }

    // Full-bleed layout: [bg] left (question + chart) | right (outcomes)
    var html =
      bgHtml +
      '<div class="pm-left">' +
        '<div class="pm-question">' + escHtml(question) + '</div>' +
        '<svg class="pm-chart" viewBox="0 0 120 44" preserveAspectRatio="none"></svg>' +
      '</div>' +
      '<div class="pm-right">' + outcomesHtml + '</div>' +
      '<div class="pm-live-dot"></div>';

    if (oldOverlay) {
      // Update in place — flash changed pct values
      var oldPcts = oldOverlay.querySelectorAll('.pm-pct');
      oldOverlay.innerHTML = html;
      var newPcts = oldOverlay.querySelectorAll('.pm-pct');
      newPcts.forEach(function (el, i) {
        var oldVal = oldPcts[i] ? oldPcts[i].getAttribute('data-pct') : '';
        if (oldVal && oldVal !== el.getAttribute('data-pct')) {
          el.classList.add('flash');
          setTimeout(function () { el.classList.remove('flash'); }, 1200);
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
    var W = 120, H = 40;
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
    var last = coords[coords.length - 1].split(',');
    // Bright gray-white line — bold, visible against dark bg
    var lineColor = 'rgba(230,230,230,0.92)';
    var glowColor = 'rgba(255,255,255,0.25)';

    // Bold line + soft glow duplicate behind it + pulsing end dot
    svg.innerHTML =
      '<polyline points="' + polyline + '" fill="none" stroke="' + glowColor + '" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" />' +
      '<polyline points="' + polyline + '" fill="none" stroke="' + lineColor + '" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />' +
      '<circle cx="' + last[0] + '" cy="' + last[1] + '" r="3" fill="#fff" opacity="0.95">' +
        '<animate attributeName="opacity" values="0.95;0.4;0.95" dur="2s" repeatCount="indefinite" />' +
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
