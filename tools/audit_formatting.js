// Formatting audit of the downloadable deliverables (Word, Markdown and text), run in the browser console of a running ARIA with data loaded.
//
//   1. Open ARIA (http://localhost:8080/), wait until the fleet has loaded, open the browser console and paste this whole file.
//   2. Run:  await ariaAudit.run()          (every customer; takes a few minutes for a large fleet; it works in short slices)
//            ariaAudit.one('Customer name') (one customer; returns the list of issues)
//   3. ariaAudit.summary() counts issues by document and kind; ariaAudit.results holds the details.
//
// What it flags per document: NaN / undefined / [object] / Infinity / null, literal "\n", HTML entities and tags, placeholders (TBD, TODO),
// empty punctuation, empty or very short documents, empty or duplicated headings, ALL-CAPS headings that were not tidied, a heading with nothing under
// it, a document that ends with a heading, tables whose rows differ in width or that have an empty column or header cell, a paragraph that is only a
// number, empty list items and decision-card rows, and a failure to build the .docx. Very long paragraphs (lists of hundreds of systems) are normal
// for very large accounts and are not flagged.
window.ariaAudit = (() => {
  const RX = [[/\bNaN\b/, 'NaN'], [/\bundefined\b/, 'undefined'], [/\[object /, '[object]'], [/\bInfinity\b/, 'Infinity'], [/\bnull%|\bnull\b(?!\))/, 'null'],
    [/\\n/, 'literal backslash-n'], [/&amp;|&lt;|&gt;|&#\d+;/, 'html entity'], [/<\/?(div|span|br|b|i|table|tr|td)\b/i, 'html tag'],
    [/\$X|\bTODO\b|lorem|\bTBD\b/i, 'placeholder'], [/, ,|,,|\( *\)|\[ *\]|: *,/, 'empty punctuation']];
  const generate = cust => {
    const ts = cust ? state.systems.filter(s => s.customerName === cust) : state.systems; const R = [], U = [], C = [], K = [];
    ts.forEach(sys => {
      (sys.risks || []).forEach(r => R.push({ systemName: sys.systemName, serialNumber: sys.serialNumber, ...r }));
      if (sys.upgrades && sys.upgrades.targetVersion !== 'Up to Date') U.push({ systemName: sys.systemName, serialNumber: sys.serialNumber, platform: sys.platform, currentVersion: sys.upgrades.currentVersion, targetVersion: sys.upgrades.targetVersion, urgency: sys.upgrades.urgency || 'medium' });
      (sys.supportCases || []).forEach(sc => K.push({ systemName: sys.systemName, customerName: sys.customerName, serialNumber: sys.serialNumber, ...sc }));
    });
    const d = compileExtendedDeliverables(ts, R, U, C, K, 'Customer: ' + (cust || 'All')); const o = {};
    for (const [k, v] of Object.entries(d)) if (typeof v === 'string') o[k] = v;
    return o;
  };
  const one = cust => {
    const issues = []; const add = (doc, type, ex) => issues.push({ doc, type, ex: String(ex || '').slice(0, 90) });
    let d; try { d = generate(cust); } catch (e) { add('(generate)', 'exception', e.message); return issues; }
    for (const [k, txt] of Object.entries(d)) {
      if (k === '_fleetProfile') continue;
      if (!txt || txt.length < 200) add(k, 'empty or very short document', txt && txt.length);
      for (const [rx, name] of RX) { const m = txt.match(rx); if (m) add(k, name, txt.slice(Math.max(0, m.index - 30), m.index + 40)); }
      let doc; try { doc = _dxParse(txt, /^#\s/.test(txt.trimStart()), { customer: '' }); } catch (e) { add(k, 'parse exception', e.message); continue; }
      const bl = doc.blocks || []; let prev = null;
      bl.forEach((b, i) => {
        if (b.t === 'h') {
          const ht = _dxHeadText(b.text || '');
          if (!ht.trim()) add(k, 'empty heading', b.text);
          if (/^[A-Z0-9 &\/\-(),#:]{12,}$/.test(ht) && /[A-Z]{3}/.test(ht)) add(k, 'ALL-CAPS heading after tidy', ht);
          if (prev && prev.t === 'h' && prev.text === b.text) add(k, 'duplicate consecutive heading', b.text);
          if (i === bl.length - 1) add(k, 'document ends with a heading', b.text);
          if (bl[i + 1] && bl[i + 1].t === 'h' && bl[i + 1].lvl <= b.lvl) add(k, 'heading with no content', b.text);
        }
        if (b.t === 'table') {
          const rows = b.rows || []; const widths = new Set(rows.map(r => r.length));
          if (widths.size > 1) add(k, 'table row width differs', [...widths].join('/') + ' ' + String(rows[0]).slice(0, 50));
          if (rows.length > 1) { const cols = Math.max(...rows.map(r => r.length)); for (let c = 0; c < cols; c++) if (rows.every(r => !String(r[c] == null ? '' : r[c]).trim())) add(k, 'table column entirely empty', c); }
          if (!rows.length) add(k, 'table with no rows', '');
          if (b.header && (rows[0] || []).some(h => !String(h).trim())) add(k, 'table header cell empty', '');
        }
        if (b.t === 'p' && /^[\d.,%\-–—\s]{1,12}$/.test((b.text || '').trim()) && (b.text || '').trim()) add(k, 'paragraph is only a number', b.text);
        if ((b.t === 'bullet' || b.t === 'num') && !(b.text || '').trim()) add(k, 'empty list item', '');
        if (b.t === 'fix') (b.rows || []).forEach(r => { if (!(r[1] || []).join('').trim()) add(k, 'decision card row empty', r[0]); });
        if (b.t === 'kv' && !String(b.v || '').trim()) add(k, 'key with empty value', b.k);
        prev = b;
      });
      try { if (!_buildDocx(k, txt, {})) add(k, 'docx build returned nothing', ''); } catch (e) { add(k, 'docx build exception', e.message); }
    }
    return issues;
  };
  const api = { results: {}, one, generate };
  api.run = async () => {
    const custs = [...new Set(state.systems.map(s => s.customerName).filter(Boolean))];
    for (const c of custs) { api.results[c] = one(c); await new Promise(r => setTimeout(r, 0)); }
    return api.summary();
  };
  api.summary = () => {
    const all = [].concat(...Object.values(api.results)); const by = {};
    all.forEach(x => { const k = x.doc + ' | ' + x.type; by[k] = (by[k] || 0) + 1; });
    return { scopes: Object.keys(api.results).length, issues: all.length, byKind: Object.entries(by).sort((a, b) => b[1] - a[1]) };
  };
  return api;
})();
