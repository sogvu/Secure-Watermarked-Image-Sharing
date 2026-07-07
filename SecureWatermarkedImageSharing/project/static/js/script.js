const API = "";  // cùng origin với Flask, không cần URL tuyệt đối

let state = { imageId: null, filename: null, watermarkHash: null, wmType: "visible" };

function setBadge(txt, color) {
  const b = document.getElementById("statusBadge");
  b.textContent = txt;
  b.style.background = color || "#374151";
}

function setMeta(meta) {
  const keys = ["image_id","owner_id","receiver_id","watermark_hash","timestamp","nonce"];
  const rows = document.querySelectorAll("#metaDisplay .meta-row");
  keys.forEach((k, i) => {
    const val = meta[k] || "—";
    rows[i].children[1].textContent =
      (k === "watermark_hash" || k === "nonce") && val !== "—" ? val.slice(0,32)+"..." : val;
  });
}

function setStamp(cls, text) {
  const el = document.getElementById("stamp");
  el.className = "stamp " + cls; el.textContent = text;
}

async function refreshAudit() {
  if (!state.imageId) return;
  const res  = await fetch(`${API}/audit/${state.imageId}`);
  const data = await res.json();
  renderAudit(data.log || []);
}

function renderAudit(rows) {
  const tbody = document.getElementById("auditBody");
  if (!rows.length) { tbody.innerHTML = `<tr><td colspan="4" class="empty">Chưa có dữ liệu</td></tr>`; return; }
  tbody.innerHTML = rows.map(r => {
    const rc = r.result === "SUCCESS" ? "res-ok" : "res-fail";
    return `<tr>
      <td>${r.timestamp}</td>
      <td><span class="ev-badge ev-${r.event}">${r.event}</span></td>
      <td>${r.detail || "—"}</td>
      <td class="${rc}">${r.result}</td>
    </tr>`;
  }).join("");
}

function showResult(id, ok, msg) {
  const el = document.getElementById(id);
  el.style.display = "block";
  el.className = "result-box " + (ok ? "result-ok" : "result-fail");
  el.innerHTML = (ok ? "✅ " : "❌ ") + msg;
}

function previewFile() {
  const file = document.getElementById("fileInput").files[0];
  if (file) document.getElementById("previewOrig").src = URL.createObjectURL(file);
}

async function doUpload() {
  const file = document.getElementById("fileInput").files[0];
  if (!file) { alert("Hãy chọn ảnh trước"); return; }
  setBadge("Đang upload...", "#1D4ED8");
  const fd = new FormData(); fd.append("file", file);
  const res  = await fetch(`${API}/upload`, { method: "POST", body: fd });
  const data = await res.json();
  if (!res.ok || data.error) { setBadge("Upload thất bại", "#DC2626"); alert(data.error); return; }
  state.imageId  = data.image_id;
  state.filename = data.filename;
  document.getElementById("previewOrig").src = `${API}/uploads/${data.filename}?t=${Date.now()}`;
  document.getElementById("btnWm").disabled = false;
  setBadge("Đã upload — bước 02: Gắn watermark");
  refreshAudit();
}

async function doWatermark() {
  const owner    = document.getElementById("ownerId").value.trim();
  const receiver = document.getElementById("receiverId").value.trim();
  state.wmType   = document.getElementById("wmType").value;
  if (!owner)    { alert("Nhập Owner ID");    return; }
  if (!receiver) { alert("Nhập Receiver ID"); return; }
  setBadge("Đang gắn watermark...", "#854D0E");
  const res = await fetch(`${API}/watermark`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image_id: state.imageId, filename: state.filename,
      owner_id: owner, receiver_id: receiver, watermark_type: state.wmType })
  });
  const data = await res.json();
  if (!res.ok || data.error) { setBadge("Watermark thất bại", "#DC2626"); alert(data.error); return; }
  state.watermarkHash = data.watermark_hash;
  const fname = data.file.split(/[\\/]/).pop();
  document.getElementById("previewWm").src = `${API}/watermarked/${fname}?t=${Date.now()}`;
  setMeta({ image_id: state.imageId, owner_id: owner, receiver_id: receiver,
    watermark_hash: data.watermark_hash, timestamp: "—", nonce: "—" });
  document.getElementById("btnEnc").disabled = false;
  setBadge("Watermark OK — bước 03: Mã hóa");
  refreshAudit();
}

async function doEncrypt() {
  setBadge("Đang mã hóa AES-GCM...", "#7E22CE");
  const res = await fetch(`${API}/encrypt`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image_id: state.imageId, filename: state.filename,
      watermark_hash: state.watermarkHash })
  });
  const data = await res.json();
  if (!res.ok || data.error) { setBadge("Mã hóa thất bại", "#DC2626"); alert(data.error); return; }
  if (data.metadata) setMeta(data.metadata);
  const cname = data.file.split(/[\\/]/).pop();
  document.getElementById("pkgCipher").textContent = `${cname}`;
  document.getElementById("pkgMeta").textContent   = `${state.imageId}.json`;
  document.getElementById("packageBox").style.display = "block";
  document.getElementById("btnDec").disabled    = false;
  document.getElementById("btnVerify").disabled = false;
  document.getElementById("receiverIdDec").value = document.getElementById("receiverId").value;
  setBadge("Đã mã hóa — gói sẵn sàng gửi đi");
  refreshAudit();
}

async function doDecrypt() {
  const receiver = document.getElementById("receiverIdDec").value.trim();
  setBadge("Đang giải mã...", "#0369A1");
  const res = await fetch(`${API}/decrypt`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image_id: state.imageId, receiver_id: receiver })
  });
  const data = await res.json();
  const ok = res.ok && !data.error;
  showResult("decResult", ok, ok ? "Giải mã thành công — AES-GCM xác thực OK" : (data.error || "Giải mã thất bại"));
  if (ok) {
    const fname = data.file.split(/[\\/]/).pop();
    document.getElementById("previewDec").src = `${API}/decrypted/${fname}?t=${Date.now()}`;
    document.getElementById("decImgBox").style.display = "block";
    document.getElementById("btnTamper").disabled = false;
    setBadge("Giải mã OK — bước 05: Kiểm tra watermark");
  } else { setBadge("Giải mã thất bại", "#DC2626"); }
  refreshAudit();
}

async function doVerify() {
  const res = await fetch(`${API}/verify`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image_id: state.imageId, watermark_type: state.wmType })
  });
  const data = await res.json();
  const vr = document.getElementById("verifyResult");
  vr.style.display = "block";
  setStamp(data.valid ? "ok" : "bad", data.valid ? "XÁC\nTHỰC" : "NGHI\nVẤN");
  vr.innerHTML = `<div class="result-box ${data.valid ? "result-ok" : "result-fail"}">
    ${data.valid ? "✅" : "❌"} ${data.message || ""}
    ${data.owner_id ? `<br>Chủ sở hữu: <strong>${data.owner_id}</strong>` : ""}
    ${data.metadata_intact !== undefined ? `<br>Metadata: ${data.metadata_intact ? "✅ Toàn vẹn" : "❌ Bị sửa đổi"}` : ""}
  </div>`;
  setBadge(data.valid ? "✅ Watermark hợp lệ" : "❌ Không hợp lệ", data.valid ? "#16A34A" : "#DC2626");
  refreshAudit();
}

async function doTamper() {
  const res = await fetch(`${API}/verify/tamper`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image_id: state.imageId })
  });
  const data = await res.json();
  const vr = document.getElementById("verifyResult");
  vr.style.display = "block";
  const items = Object.entries(data.checks || {}).map(([k,c]) =>
    `<div class="check-item ${c.ok?"ok":"fail"}"><span>${c.ok?"✅":"❌"}</span><div><strong>${k}</strong><br>${c.detail||""}</div></div>`
  ).join("");
  vr.innerHTML = `<div class="result-box " + (data.passed ? "result-ok" : "result-fail")>
    ${data.passed ? "✅ Không phát hiện sửa đổi" : "❌ Phát hiện sửa đổi — Báo cáo &amp; Log"}
  </div><div class="check-list">${items}</div>`;
  setBadge(data.passed ? "✅ Toàn vẹn" : "❌ Bị sửa đổi", data.passed ? "#16A34A" : "#DC2626");
  refreshAudit();
}