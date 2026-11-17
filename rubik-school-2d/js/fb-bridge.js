// ================= FIREBASE BRIDGE =================
// Khi game chạy ngoài claude.ai (Netlify, tên miền riêng), file này giả lập window.claude.use('db'|'user'|'room')
// bằng Firebase (Auth + Firestore), để đăng nhập, lưu tiến độ, bảng xếp hạng, chợ, chat và đấu online vẫn chạy.
// Trên claude.ai file này không làm gì.
(() => {
  const host = location.hostname;
  if (window.claude || /claude\.ai$|claudeusercontent\.com$|claude\.site$/.test(host)) return;

  const CONFIG = {
    apiKey: 'AIzaSyCyISNCJJq6P8KzgE67NXUjx4OB8UQMhcw',
    authDomain: 'haquan-rubikschool-2d.firebaseapp.com',
    projectId: 'haquan-rubikschool-2d',
    storageBucket: 'haquan-rubikschool-2d.firebasestorage.app',
    messagingSenderId: '774928850844',
    appId: '1:774928850844:web:b55269be5de3d0bb42b259'
  };
  const SDK = 'https://www.gstatic.com/firebasejs/10.12.2/';
  const loadScript = src => new Promise((ok, bad) => { const s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = () => bad(new Error('load ' + src)); document.head.appendChild(s); });

  let fs = null, auth = null;
  const ready = (async () => {
    await loadScript(SDK + 'firebase-app-compat.js');
    await Promise.all([loadScript(SDK + 'firebase-auth-compat.js'), loadScript(SDK + 'firebase-firestore-compat.js')]);
    firebase.initializeApp(CONFIG);
    auth = firebase.auth(); fs = firebase.firestore();
    // long polling: chạy được cả qua mạng trường học, proxy, phần mềm diệt virus chặn kết nối dạng stream
    fs.settings({ experimentalForceLongPolling: true });
    await auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL).catch(() => {});
    await new Promise(r => { const off = auth.onAuthStateChanged(() => { off(); r(); }); });
    if (!auth.currentUser) await auth.signInAnonymously().catch(e => console.warn('Chưa bật đăng nhập ẩn danh:', e && e.code));
    return true;
  })().catch(e => { console.warn('Firebase chưa kết nối được:', e); return false; });

  // ---------- tài khoản: tên đăng nhập + mật khẩu trong game → Email/Password của Firebase ----------
  const hex = s => Array.from(new TextEncoder().encode(s)).map(b => b.toString(16).padStart(2, '0')).join('');
  const emailOf = name => 'u' + hex(name.trim().toLowerCase()) + '@haquan-rubik.app';
  const pwOf = pass => 'hq#' + pass;
  async function account(name, pass, create) {
    if (!(await ready)) return 'offline';
    try {
      if (create) await auth.createUserWithEmailAndPassword(emailOf(name), pwOf(pass));
      else await auth.signInWithEmailAndPassword(emailOf(name), pwOf(pass));
      await auth.currentUser.getIdToken(true);
      await new Promise(r => setTimeout(r, 300));
      return 'ok';
    } catch (e) {
      const c = e && e.code || '';
      if (c === 'auth/email-already-in-use') return 'taken';
      if (c === 'auth/invalid-credential' || c === 'auth/wrong-password' || c === 'auth/user-not-found' || c === 'auth/invalid-login-credentials') return 'invalid';
      if (c === 'auth/too-many-requests') return 'busy';
      if (c === 'auth/network-request-failed') return 'offline';
      console.warn(e); return 'error';
    }
  }
  async function logout() { if (!(await ready)) return; try { await auth.signOut(); await auth.signInAnonymously(); } catch (e) {} }
  const uid = () => auth && auth.currentUser ? auth.currentUser.uid : null;

  // ---------- db: cùng kiểu gọi với claude.use('db') ----------
  const wrapSnap = s => ({ id: s.id, exists: s.exists, data: () => s.data(), metadata: s.metadata });
  const wrapQSnap = q => ({ docs: q.docs.map(wrapSnap), size: q.size, empty: q.empty });
  function docRef(path) {
    const r = fs.doc(path);
    return {
      id: r.id,
      get: () => r.get().then(wrapSnap),
      set: (d, o) => r.set(d, o || {}),
      update: d => r.update(d),
      delete: () => r.delete(),
      onSnapshot: (fn, err) => r.onSnapshot({ includeMetadataChanges: false }, s => fn(wrapSnap(s)), err),
      acquire: async () => ({ acquired: true, release: async () => {} })
    };
  }
  function queryRef(q) {
    return {
      where: (f, op, v) => queryRef(q.where(f, op, v)),
      orderBy: (f, d) => queryRef(q.orderBy(f, d)),
      limit: n => queryRef(q.limit(n)),
      get: () => q.get().then(wrapQSnap),
      onSnapshot: (fn, err) => q.onSnapshot(s => fn(wrapQSnap(s)), err),
      doc: id => docRef(q.path + '/' + id)
    };
  }
  const db = { doc: p => docRef(p), collection: p => Object.assign(queryRef(fs.collection(p)), { path: p }) };

  // ---------- user ----------
  const user = {
    id: async () => uid(),
    me: async () => ({ id: uid(), name: '' }),
    profiles: async ids => Object.fromEntries((ids || []).map(i => [i, { id: i, name: '' }])),
    search: async () => [],
    isOwner: () => false, canEdit: () => false, can: () => null
  };

  // ---------- room: có mặt + sự kiện thời gian thực qua Firestore ----------
  function makeRoom() {
    const peer = 'p' + Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
    const t0 = Date.now(), handlers = {}, peerFns = [];
    let myPres = {}, known = new Map(), lastDocs = [];
    const pRef = () => fs.collection('rt_presence').doc(peer);
    const beat = () => uid() && pRef().set({ uid: uid(), at: Date.now(), p: myPres }).catch(() => {});
    setInterval(beat, 25000);
    addEventListener('pagehide', () => { try { pRef().delete(); } catch (e) {} });
    function emitPeers() {
      const now = Date.now(), live = new Map();
      lastDocs.forEach(d => { const v = d.data(); if (v && now - (v.at || 0) < 70000) live.set(d.id, v); });
      const left = [...known.keys()].filter(k => !live.has(k)).map(k => ({ peer: k }));
      known = live;
      const peers = [...live.entries()].map(([k, v]) => ({ peer: k, sameTab: k === peer, kind: 'viewer', presence: v.p || {} }));
      if (!peers.some(p => p.sameTab)) peers.push({ peer, sameTab: true, kind: 'viewer', presence: myPres });
      peerFns.forEach(f => { try { f({ peers, left }); } catch (e) {} });
      lastDocs.forEach(d => { const v = d.data(); if (v && now - (v.at || 0) > 86400000) d.ref.delete().catch(() => {}); });
    }
    fs.collection('rt_presence').onSnapshot(s => { lastDocs = s.docs; emitPeers(); }, () => {});
    setInterval(emitPeers, 30000);
    fs.collection('rt_events').where('at', '>', t0).orderBy('at').onSnapshot(s => {
      s.docChanges().forEach(ch => {
        if (ch.type !== 'added') return; const v = ch.doc.data(); if (!v) return;
        (handlers[v.topic] || []).forEach(f => { try { f({ data: v.data, peer: v.peer, isMe: v.peer === peer }); } catch (e) {} });
      });
    }, () => {});
    return {
      emit: async (topic, data) => {
        const ref = await fs.collection('rt_events').add({ topic, data: data === undefined ? null : JSON.parse(JSON.stringify(data)), peer, uid: uid(), at: Date.now() });
        setTimeout(() => ref.delete().catch(() => {}), 90000);
      },
      on: (topic, fn) => { (handlers[topic] = handlers[topic] || []).push(fn); return () => { handlers[topic] = handlers[topic].filter(f => f !== fn); }; },
      presence: async patch => { myPres = JSON.parse(JSON.stringify(patch || {})); await beat(); },
      onPeers: fn => { peerFns.push(fn); setTimeout(emitPeers, 0); return () => {}; },
      join: () => makeRoom(), leave: async () => { try { await pRef().delete(); } catch (e) {} }
    };
  }
  let roomInst = null;

  window.HQFB = { ready, account, logout, uid };
  window.claude = {
    use: async name => {
      if (!(await ready)) return null;
      if (name === 'db') return db;
      if (name === 'user') return user;
      if (name === 'room') { if (!uid()) return null; return roomInst || (roomInst = makeRoom()); }
      return null; // sample, tts, dictation chỉ có trên claude.ai
    }
  };
})();
