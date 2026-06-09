// Vercel 서버리스 함수 — GPT로 페이지 내용 검증
// 브라우저가 보낸 화면 텍스트를 OpenAI에 보내 "의도한 내용으로 올바르게
// 구성됐는지" 판정한다. API 키는 이 서버 코드에서만 사용되며(환경변수
// GPT_API_KEY) 절대 브라우저로 내려가지 않는다.
module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ ok: false, reason: 'POST 요청만 허용됩니다.' });
    return;
  }

  var key = process.env.GPT_API_KEY || process.env.PT_API_KEY;
  if (!key) {
    res.status(500).json({ ok: false, reason: 'API 키가 설정되지 않았습니다. Vercel 환경변수 GPT_API_KEY를 등록하세요.' });
    return;
  }

  try {
    var body = req.body;
    if (typeof body === 'string') { try { body = JSON.parse(body || '{}'); } catch (e) { body = {}; } }
    if (!body || typeof body !== 'object') body = {};

    var page = String(body.page || '').slice(0, 80);
    var expected = String(body.expected || '').slice(0, 1200);
    var content = String(body.content || '').slice(0, 6000);

    if (!content) {
      res.status(200).json({ ok: false, reason: '화면에서 검증할 텍스트를 찾지 못했습니다.' });
      return;
    }

    var sys = '당신은 웹앱 QA 검증기입니다. 주어진 페이지의 실제 화면 텍스트가 ' +
      '의도한 구성/내용과 일치하는지 판정합니다. 핵심 요소가 비어 있거나 엉뚱한 ' +
      '내용이면 ok=false, 의도한 내용이 갖춰져 있으면 ok=true 입니다. ' +
      '반드시 JSON {"ok": boolean, "reason": "한국어 한 문장"} 형식으로만 답하세요.';

    var user = '페이지 이름: ' + page + '\n' +
      '이 페이지가 갖춰야 할 내용:\n' + expected + '\n\n' +
      '실제 화면 텍스트:\n"""\n' + content + '\n"""\n\n' +
      '위 화면이 의도한 내용으로 올바르게 구성되어 있는지 판정하세요.';

    var apiRes = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        temperature: 0,
        response_format: { type: 'json_object' },
        messages: [
          { role: 'system', content: sys },
          { role: 'user', content: user }
        ]
      })
    });

    if (!apiRes.ok) {
      var errText = await apiRes.text();
      res.status(502).json({ ok: false, reason: 'GPT 호출 실패 (' + apiRes.status + ')', detail: errText.slice(0, 300) });
      return;
    }

    var data = await apiRes.json();
    var raw = data && data.choices && data.choices[0] && data.choices[0].message ? data.choices[0].message.content : '';
    var parsed = { ok: false, reason: 'GPT 응답을 해석하지 못했습니다.' };
    try { parsed = JSON.parse(raw); } catch (e) { /* keep default */ }

    res.status(200).json({ ok: !!parsed.ok, reason: parsed.reason || (parsed.ok ? '정상' : '확인 필요') });
  } catch (e) {
    res.status(500).json({ ok: false, reason: '서버 오류: ' + (e && e.message ? e.message : String(e)) });
  }
};
