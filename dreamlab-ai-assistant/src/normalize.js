// Chuẩn hóa payload webhook thành danh sách sự kiện thống nhất:
// { id, channel, kind: 'comment'|'message', text, senderId, senderName, threadRef, raw }
// channel: facebook_comment | messenger | instagram_comment | instagram_dm | zalo

export function normalizeMeta(body, { pageId = '', igUserId = '' } = {}) {
  const out = [];
  if (!body || !Array.isArray(body.entry)) return out;

  for (const entry of body.entry) {
    // Facebook Page feed: bình luận mới
    if (body.object === 'page' && Array.isArray(entry.changes)) {
      for (const ch of entry.changes) {
        const v = ch.value || {};
        if (ch.field !== 'feed' || v.item !== 'comment' || v.verb !== 'add') continue;
        if (v.from?.id && (v.from.id === pageId || v.from.id === entry.id)) continue; // bình luận của chính Page
        out.push({
          id: `fbc:${v.comment_id}`, channel: 'facebook_comment', kind: 'comment',
          text: v.message || '', senderId: v.from?.id || '', senderName: v.from?.name || '',
          threadRef: { commentId: v.comment_id, postId: v.post_id }, raw: v,
        });
      }
    }
    // Messenger / Instagram DM
    if (Array.isArray(entry.messaging)) {
      for (const m of entry.messaging) {
        const msg = m.message;
        if (!msg || msg.is_echo || !msg.mid) continue; // bỏ tin do chính Page gửi
        const isIg = body.object === 'instagram';
        if (isIg && m.sender?.id === (igUserId || entry.id)) continue;
        out.push({
          id: `${isIg ? 'igm' : 'fbm'}:${msg.mid}`, channel: isIg ? 'instagram_dm' : 'messenger', kind: 'message',
          text: msg.text || '', senderId: m.sender?.id || '', senderName: '',
          threadRef: { recipientId: m.sender?.id }, raw: m,
        });
      }
    }
    // Instagram: bình luận
    if (body.object === 'instagram' && Array.isArray(entry.changes)) {
      for (const ch of entry.changes) {
        const v = ch.value || {};
        if (ch.field !== 'comments' || !v.id) continue;
        if (v.from?.id && v.from.id === (igUserId || entry.id)) continue;
        out.push({
          id: `igc:${v.id}`, channel: 'instagram_comment', kind: 'comment',
          text: v.text || '', senderId: v.from?.id || '', senderName: v.from?.username || '',
          threadRef: { commentId: v.id, mediaId: v.media?.id }, raw: v,
        });
      }
    }
  }
  return out;
}

export function normalizeZalo(body) {
  if (!body || body.event_name !== 'user_send_text') return [];
  const mid = body.message?.msg_id;
  if (!mid) return [];
  return [{
    id: `zl:${mid}`, channel: 'zalo', kind: 'message',
    text: body.message?.text || '', senderId: body.sender?.id || '', senderName: '',
    threadRef: { userId: body.sender?.id }, raw: body,
  }];
}
