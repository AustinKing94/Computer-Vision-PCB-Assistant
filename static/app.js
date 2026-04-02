// --- DASHBOARD ---
document.addEventListener('DOMContentLoaded', function () {
    const captureBtn  = document.getElementById('btn-capture');
    const saveBtn     = document.getElementById('btn-save');
    const thermal     = document.getElementById('toggle-thermal');
    const display     = document.getElementById('pcb-display');
    const statusText  = document.getElementById('status-text');
    const bomContent  = document.getElementById('bom-content');

    function setStatus(msg, color) {
        if (!statusText) return;
        statusText.textContent = msg;
        statusText.style.color = color || 'var(--accent)';
    }

    function renderBOM(bom) {
        if (!bomContent) return;
        if (!bom || bom.length === 0) {
            bomContent.innerHTML = '<p class="bom-empty">No components detected.</p>';
            return;
        }
        const rows = bom.map(item =>
            `<tr>
                <td>${item.component}</td>
                <td class="bom-count">${item.count}</td>
            </tr>`
        ).join('');
        bomContent.innerHTML = `
            <table class="bom-table">
                <thead><tr><th>Component</th><th style="text-align:right">Count</th></tr></thead>
                <tbody>${rows}</tbody>
            </table>`;
    }

    if (captureBtn) {
        captureBtn.addEventListener('click', function () {
            captureBtn.disabled = true;
            setStatus('Capturing...', 'var(--muted)');

            fetch('/api/capture', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        const t = Date.now();
                        display.src = thermal && thermal.checked
                            ? `/get_current_thermal?t=${t}`
                            : `/get_current_image?t=${t}`;
                        setStatus('Ready', 'var(--accent)');
                        renderBOM(data.bom);
                    } else {
                        setStatus('Error', 'var(--danger)');
                        alert('Capture failed: ' + (data.error || 'Unknown error'));
                    }
                })
                .catch(err => {
                    setStatus('Error', 'var(--danger)');
                    alert('Network error: ' + err);
                })
                .finally(() => { captureBtn.disabled = false; });
        });
    }

    if (saveBtn) {
        saveBtn.addEventListener('click', function () {
            saveBtn.disabled = true;
            fetch('/api/save', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    setStatus(data.success ? 'Saved!' : 'Save failed', data.success ? 'var(--accent)' : 'var(--danger)');
                    setTimeout(() => setStatus('Ready', 'var(--accent)'), 2000);
                })
                .finally(() => { saveBtn.disabled = false; });
        });
    }

    if (thermal) {
        thermal.addEventListener('change', function () {
            const t = Date.now();
            display.src = this.checked
                ? `/get_current_thermal?t=${t}`
                : `/get_current_image?t=${t}`;
        });
    }
});

// --- GALLERY ---
function loadCapture(filename) {
    fetch('/api/load_capture', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename })
    })
    .then(r => r.json())
    .then(data => { if (data.success) window.location.href = '/'; });
}

function exportCapture(filename) {
    window.location.href = `/api/capture/${filename}`;
}

function deleteCapture(filename) {
    if (!confirm('Delete this capture?')) return;
    fetch('/api/delete_capture', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename })
    })
    .then(r => r.json())
    .then(data => { if (data.success) location.reload(); });
}