document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const videoFileInput = document.getElementById('videoFile');
    const fileNameSpan = document.getElementById('fileName');
    const uploadBtn = document.getElementById('uploadBtn');
    const progressSection = document.getElementById('progressSection');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const resultsSection = document.getElementById('resultsSection');

    // Update file name display
    videoFileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            const fileName = e.target.files[0].name;
            fileNameSpan.textContent = fileName;
            fileNameSpan.style.color = '#667eea';
        }
    });

    // Handle form submission
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData(uploadForm);
        const file = videoFileInput.files[0];

        if (!file) {
            showError('Please select a video file');
            return;
        }

        // Validate file size (100MB max)
        if (file.size > 100 * 1024 * 1024) {
            showError('File size exceeds 100MB limit');
            return;
        }

        // Show progress
        uploadBtn.disabled = true;
        progressSection.style.display = 'block';
        progressText.textContent = 'Uploading video...';
        progressFill.style.width = '10%';

        try {
            // Upload video first
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Upload failed');
            }

            const result = await response.json();
            
            if (result.success) {
                // Start streaming processing
                progressText.textContent = 'Processing video...';
                progressFill.style.width = '20%';
                
                // Add live preview
                addLivePreview();
                
                streamVideoProcessing(result.filename, result.detection_method);
            } else {
                throw new Error(result.error || 'Upload failed');
            }

        } catch (error) {
            showError('Error: ' + error.message);
            uploadBtn.disabled = false;
            progressSection.style.display = 'none';
        }
    });

    function addLivePreview() {
        if (!document.getElementById('livePreview')) {
            const previewDiv = document.createElement('div');
            previewDiv.id = 'livePreview';
            previewDiv.style.marginTop = '20px';
            previewDiv.style.textAlign = 'center';
            previewDiv.innerHTML = `
                <h3 style="color: #1a202c; margin-bottom: 10px;">🎬 Live Processing</h3>
                <img id="previewImage" style="max-width: 60%; max-height: 400px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);" />
                <p id="liveStats" style="margin-top: 10px; color: #718096; font-weight: bold;"></p>
            `;
            progressSection.after(previewDiv);
        }
    }

    function streamVideoProcessing(filename, detectionMethod) {
        const eventSource = new EventSource(`/process_stream/${filename}?method=${detectionMethod}`);
        
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            if (data.type === 'info') {
                progressText.textContent = `Processing ${data.total_frames} frames...`;
            } else if (data.type === 'progress') {
                progressFill.style.width = data.progress + '%';
                progressText.textContent = `Frame ${data.frame}/${data.total_frames} - Objects: ${data.objects_current}`;
                
                // Update live preview
                const previewImg = document.getElementById('previewImage');
                const liveStats = document.getElementById('liveStats');
                if (previewImg && data.preview) {
                    previewImg.src = 'data:image/jpeg;base64,' + data.preview;
                }
                if (liveStats) {
                    liveStats.textContent = `Current: ${data.objects_current} | Max: ${data.objects_max} | Progress: ${data.progress}%`;
                }
            } else if (data.type === 'complete') {
                progressFill.style.width = '100%';
                progressText.textContent = 'Processing complete!';
                eventSource.close();
                
                setTimeout(() => {
                    displayResults({
                        success: true,
                        output_video: data.output_video,
                        statistics: data.statistics
                    });
                }, 1000);
            }
        };
        
        eventSource.onerror = function(error) {
            eventSource.close();
            showError('Processing failed. Please try again.');
            uploadBtn.disabled = false;
            progressSection.style.display = 'none';
        };
    }

    function displayResults(result) {
        const stats = result.statistics;

        // Hide upload section, progress and show results
        document.querySelector('.upload-section').style.display = 'none';
        progressSection.style.display = 'none';
        const livePreview = document.getElementById('livePreview');
        if (livePreview) livePreview.style.display = 'none';
        resultsSection.style.display = 'block';

        // Update statistics
        document.getElementById('totalFrames').textContent = stats.total_frames.toLocaleString();
        document.getElementById('maxObjects').textContent = stats.max_objects_per_frame;
        document.getElementById('avgObjects').textContent = stats.average_objects_per_frame;

        // Set up video
        const videoElement = document.getElementById('resultVideo');
        const videoPath = `/static/outputs/${result.output_video}`;
        videoElement.src = videoPath;

        // Set up download link
        const downloadLink = document.getElementById('downloadVideo');
        downloadLink.href = videoPath;
        downloadLink.download = result.output_video;

        // Display object types
        displayObjectTypes(stats.object_counts);

        // Create timeline chart
        createTimelineChart(stats.timeline);

        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    function displayObjectTypes(objectCounts) {
        const container = document.getElementById('objectTypesList');
        container.innerHTML = '';

        if (!objectCounts || Object.keys(objectCounts).length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #718096;">No objects detected</p>';
            return;
        }

        for (const [objectType, count] of Object.entries(objectCounts)) {
            const item = document.createElement('div');
            item.className = 'object-type-item';
            item.innerHTML = `
                <div class="object-type-name">${objectType.replace('_', ' ')}</div>
                <div class="object-type-count">${count.toLocaleString()}</div>
            `;
            container.appendChild(item);
        }
    }

    function createTimelineChart(timeline) {
        const ctx = document.getElementById('timelineChart').getContext('2d');

        const labels = timeline.map(point => `Frame ${point.frame}`);
        const data = timeline.map(point => point.count);

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Object Count',
                    data: data,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: '#667eea',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },
                        title: {
                            display: true,
                            text: 'Number of Objects'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Timeline'
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }

    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        const uploadCard = document.querySelector('.upload-card');
        uploadCard.insertBefore(errorDiv, uploadCard.firstChild);

        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
});
