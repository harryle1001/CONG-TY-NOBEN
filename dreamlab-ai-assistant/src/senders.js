// Gửi ra ngoài (Meta Graph API, Zalo OA API). CHỈ được gọi khi DRY_RUN=false.
export class DryRunError extends Error {}

export function createSenders(cfg, { fetchImpl = globalThis.fetch } = {}) {
  const guard = () => { if (cfg.dryRun) throw new DryRunError('DRY_RUN đang bật: không được gửi ra ngoài'); };
  const graph = async (pathname, body) => {
    guard();
    const url = `https://graph.facebook.com/${cfg.meta.graphVersion}/${pathname}`;
    const res = await fetchImpl(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${cfg.meta.pageAccessToken}` },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`Meta API ${res.status}: ${await res.text()}`);
    return res.json();
  };

  return {
    // Trả lời công khai dưới bình luận
    replyComment: (event, text) => event.channel === 'instagram_comment'
      ? graph(`${event.threadRef.commentId}/replies`, { message: text })
      : graph(`${event.threadRef.commentId}/comments`, { message: text }),
    // Nhắn riêng cho người bình luận (private reply, dùng comment_id làm người nhận)
    privateReply: (event, text) => graph('me/messages', { recipient: { comment_id: event.threadRef.commentId }, message: { text } }),
    // Trả lời tin nhắn Messenger / Instagram / Zalo
    sendMessage: async (event, text) => {
      if (event.channel === 'zalo') {
        guard();
        const res = await fetchImpl('https://openapi.zalo.me/v3.0/oa/message/cs', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', access_token: cfg.zalo.oaAccessToken },
          body: JSON.stringify({ recipient: { user_id: event.threadRef.userId }, message: { text } }),
        });
        const json = await res.json();
        if (!res.ok || json.error) throw new Error(`Zalo API: ${JSON.stringify(json)}`);
        return json;
      }
      return graph('me/messages', { recipient: { id: event.threadRef.recipientId }, messaging_type: 'RESPONSE', message: { text } });
    },
  };
}
