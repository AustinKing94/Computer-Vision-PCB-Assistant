// --- DASHBOARD LOGIC ---
document.addEventListener('DOMContentLoaded', function() {
    const captureBtn = document.getElementById('btn-capture');
    const saveBtn = document.getElementById('btn-save'); // The save button
    const thermalToggle = document.getElementById('toggle-thermal');
    const pcbDisplay = document.getElementById('pcb-display');

    if (captureBtn && pcbDisplay) {
        
        // ACTION 1: Fire the camera and update the screen
        captureBtn.addEventListener('click', function() {
            const originalText = captureBtn.innerHTML;
            captureBtn.disabled = true;
            captureBtn.innerHTML = 'Taking Picture...';
            
            fetch('/api/capture', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Force the browser to load the newly taken picture
                    const cacheBuster = new Date().getTime();
                    // Keep the thermal state if it's toggled on
                    if (thermalToggle && thermalToggle.checked) {
                        pcbDisplay.src = `/get_current_thermal?t=${cacheBuster}`;
                    } else {
                        pcbDisplay.src = `/get_current_image?t=${cacheBuster}`;
                    }
                } else {
                    alert('Camera failed to capture');
                }
                captureBtn.innerHTML = originalText;
                captureBtn.disabled = false;
            });
        });

        // ACTION 2: Save the current screen to the data folder
        if (saveBtn) {
            saveBtn.addEventListener('click', function() {
                const originalText = saveBtn.innerHTML;
                saveBtn.disabled = true;
                saveBtn.innerHTML = 'Saving...';

                fetch('/api/save', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        saveBtn.innerHTML = '✓ Saved!';
                    } else {
                        alert('Failed to save to files');
                        saveBtn.innerHTML = originalText;
                    }
                    setTimeout(() => {
                        saveBtn.innerHTML = originalText;
                        saveBtn.disabled = false;
                    }, 2000);
                });
            });
        }

        // Handle Thermal Toggle (Frontend only swap)
        if (thermalToggle) {
            thermalToggle.addEventListener('change', function() {
                const cacheBuster = new Date().getTime();
                if (this.checked) {
                    pcbDisplay.src = `/get_current_thermal?t=${cacheBuster}`;
                } else {
                    pcbDisplay.src = `/get_current_image?t=${cacheBuster}`;
                }
            });
        }
    }
});

// --- GALLERY LOGIC ---
function loadCapture(filename) {
    fetch('/api/load_capture', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: filename })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Redirect back to the main dashboard
            window.location.href = '/'; 
        } else {
            alert('Failed to load capture');
        }
    });
}

function exportCapture(filename) {
    // Navigating to this route triggers the 'as_attachment=True' download in Flask
    window.location.href = `/api/capture/${filename}`;
}

function deleteCapture(filename) {
    if (confirm('Delete this capture?')) {
        fetch('/api/delete_capture', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: filename })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload(); 
            } else {
                alert('Failed to delete');
            }
        });
    }
}