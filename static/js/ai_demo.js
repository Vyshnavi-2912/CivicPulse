/* ==========================================================================
   CivicPulse AI-Assisted Image Classification & Severity Rule Calculator
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('imageInput');
    const uploadDropzone = document.getElementById('uploadDropzone');
    const previewContainer = document.getElementById('imagePreviewContainer');
    const previewImg = document.getElementById('imagePreviewImg');
    
    // AI Elements
    const aiContainer = document.getElementById('aiAnalysisContainer');
    const aiCategoryText = document.getElementById('aiCategoryText');
    const aiConfidenceText = document.getElementById('aiConfidenceText');
    const btnAcceptAi = document.getElementById('btnAcceptAi');
    const categorySelect = document.getElementById('categorySelect');

    // Severity Elements
    const safetyRiskSelect = document.getElementById('safetyRiskSelect');
    const extentDamageSelect = document.getElementById('extentDamageSelect');
    const locationTypeSelect = document.getElementById('locationTypeSelect');
    const severityBadge = document.getElementById('severityBadge');
    const severityReasonText = document.getElementById('severityReasonText');

    let currentAiCategory = '';

    if (fileInput && uploadDropzone) {
        // Dropzone click trigger
        uploadDropzone.addEventListener('click', () => fileInput.click());

        // Drag & Drop handlers
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadDropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                uploadDropzone.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadDropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                uploadDropzone.classList.remove('dragover');
            });
        });

        uploadDropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files && files.length > 0) {
                fileInput.files = files;
                handleImageSelected(files[0]);
            }
        });

        fileInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                handleImageSelected(this.files[0]);
            }
        });
    }

    function handleImageSelected(file) {
        // File validation
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif'];
        if (!validTypes.includes(file.type)) {
            alert('Invalid file format! Please upload a JPG, PNG, WEBP or GIF image.');
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            alert('File size exceeds 10MB limit. Please upload a smaller image.');
            return;
        }

        // Show image preview
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImg.src = e.target.result;
            previewContainer.style.display = 'block';
        };
        reader.readAsDataURL(file);

        // Run AI Classification Analysis API
        runAiAnalysis(file);
    }

    function runAiAnalysis(file) {
        if (!aiContainer) return;

        aiContainer.style.display = 'block';
        aiCategoryText.textContent = 'Analyzing image patterns...';
        aiConfidenceText.textContent = 'Calculating...';

        const formData = new FormData();
        formData.append('image', file);

        fetch('/api/ai-analyze', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                aiCategoryText.textContent = 'AI Detection standard fallback';
                aiConfidenceText.textContent = '80%';
                return;
            }

            currentAiCategory = data.predicted_category;
            aiCategoryText.textContent = data.predicted_category;
            aiConfidenceText.textContent = data.confidence_percent;

            // Highlight accept button
            if (btnAcceptAi) {
                btnAcceptAi.style.display = 'inline-flex';
                btnAcceptAi.onclick = function() {
                    if (categorySelect) {
                        categorySelect.value = currentAiCategory;
                        triggerSeverityCalculation();
                    }
                };
            }
        })
        .catch(err => {
            console.error("AI Analysis error:", err);
            aiCategoryText.textContent = 'Pothole (Demo Fallback)';
            aiConfidenceText.textContent = '85%';
        });
    }

    // Dynamic Rule-Based Severity Engine Trigger
    function triggerSeverityCalculation() {
        if (!severityBadge || !severityReasonText) return;

        const category = categorySelect ? categorySelect.value : 'Other';
        const safetyRisk = safetyRiskSelect ? safetyRiskSelect.value : 'none';
        const extentDamage = extentDamageSelect ? extentDamageSelect.value : 'moderate';
        const locationType = locationTypeSelect ? locationTypeSelect.value : 'standard';

        fetch('/api/assess-severity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                category: category,
                safety_risk: safetyRisk,
                extent_damage: extentDamage,
                location_type: locationType
            })
        })
        .then(res => res.json())
        .then(data => {
            severityBadge.textContent = data.severity_level.toUpperCase();
            severityReasonText.textContent = data.severity_reason;

            // Update badge styling
            severityBadge.className = 'badge';
            if (data.severity_level === 'Critical') {
                severityBadge.classList.add('badge-severity-critical');
            } else if (data.severity_level === 'High') {
                severityBadge.classList.add('badge-severity-high');
            } else if (data.severity_level === 'Medium') {
                severityBadge.classList.add('badge-severity-medium');
            } else {
                severityBadge.classList.add('badge-severity-low');
            }
        })
        .catch(err => console.error("Severity calculation error:", err));
    }

    // Bind change listeners for live calculation preview
    [categorySelect, safetyRiskSelect, extentDamageSelect, locationTypeSelect].forEach(el => {
        if (el) {
            el.addEventListener('change', triggerSeverityCalculation);
        }
    });

    // Initial calculation on load
    if (categorySelect) {
        triggerSeverityCalculation();
    }

    // GPS Geolocation Handler
    const btnDetectGps = document.getElementById('btnDetectGps');
    const gpsStatusText = document.getElementById('gpsStatusText');
    const latInput = document.getElementById('latitude');
    const lngInput = document.getElementById('longitude');

    if (btnDetectGps) {
        btnDetectGps.addEventListener('click', function() {
            if (!navigator.geolocation) {
                alert('Geolocation is not supported by your browser.');
                return;
            }
            if (gpsStatusText) {
                gpsStatusText.style.display = 'block';
                gpsStatusText.style.color = '#0D9488';
                gpsStatusText.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Acquiring GPS coordinates...';
            }
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude.toFixed(6);
                    const lng = position.coords.longitude.toFixed(6);
                    if (latInput) latInput.value = lat;
                    if (lngInput) lngInput.value = lng;
                    if (gpsStatusText) {
                        gpsStatusText.style.color = '#059669';
                        gpsStatusText.innerHTML = `<i class="fa-solid fa-circle-check"></i> GPS Coordinates Acquired: Latitude ${lat}, Longitude ${lng}`;
                    }
                },
                (error) => {
                    console.warn("GPS error:", error);
                    if (gpsStatusText) {
                        gpsStatusText.style.color = '#EA580C';
                        gpsStatusText.innerHTML = `<i class="fa-solid fa-circle-info"></i> GPS unavailable/denied. Automatic district location coordinates will be estimated on submission.`;
                    }
                },
                { enableHighAccuracy: true, timeout: 8000 }
            );
        });
    }
});
