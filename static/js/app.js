// JavaScript for AI Agent Assistant Web Platform

// Global variables
let currentForm = null;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let recognition = null;
let isRealtimeTranscribing = false;
let accumulatedText = ''; // Track accumulated final text
let currentAudio = null; // Track current playing audio
let isPlayingTTS = false; // Track TTS playing state

// Default job description
const DEFAULT_JOB_DESCRIPTION = "Researcher position focused on AI in education with emphasis on marginalized communities and learning design";

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Agent Assistant loaded successfully');
    
    // Set up form event listeners
    setupFormListeners();
    
    // Set up file drag and drop
    setupDragAndDrop();
});

// Form event listeners
function setupFormListeners() {
    // Interview form
    const interviewForm = document.getElementById('interviewForm');
    if (interviewForm) {
        interviewForm.addEventListener('submit', handleInterviewSubmit);
    }
    
    // Reading form
    const readingForm = document.getElementById('readingForm');
    if (readingForm) {
        readingForm.addEventListener('submit', handleReadingSubmit);
    }
}

// Show interview form
function showInterviewForm() {
    hideAllForms();
    document.getElementById('interview-form').style.display = 'block';
    currentForm = 'interview';
    
    // Load actual CV data if empty
    const cvTextarea = document.getElementById('cvText');
    if (!cvTextarea.value.trim()) {
        loadActualCV();
    }
}

// Load actual CV data
async function loadActualCV() {
    try {
        const response = await fetch('/api/cv');
        if (response.ok) {
            const cvData = await response.json();
            const cvTextarea = document.getElementById('cvText');
            cvTextarea.value = JSON.stringify(cvData, null, 2);
            showNotification('Your CV data loaded successfully!', 'success');
        } else {
            // Fallback to sample data if CV endpoint fails
            loadSampleCV();
        }
    } catch (error) {
        console.log('CV endpoint not available, using sample data');
        loadSampleCV();
    }
}

// Load sample CV data as fallback
function loadSampleCV() {
    const cvTextarea = document.getElementById('cvText');
    cvTextarea.value = `{
  "name": "Livia Fares",
  "title": "AI Education Researcher",
  "education": "MIT Graduate Student",
  "experience": [
    "Research in AI applications for education",
    "Focus on marginalized communities",
    "Experience with learning design and EdTech"
  ],
  "skills": [
    "AI/ML",
    "Educational Technology",
    "Research Methods",
    "Data Analysis"
  ]
}`;
    showNotification('Sample CV data loaded. Upload your own CV JSON file for personalized results.', 'info');
}

// Show reading form
function showReadingForm() {
    hideAllForms();
    document.getElementById('reading-form').style.display = 'block';
    currentForm = 'reading';
}

// Hide all forms
function hideAllForms() {
    document.getElementById('interview-form').style.display = 'none';
    document.getElementById('reading-form').style.display = 'none';
    hideResults();
}

// Hide forms (alias for hideAllForms)
function hideForms() {
    hideAllForms();
}

// Hide results
function hideResults() {
    document.getElementById('results').style.display = 'none';
    document.getElementById('resultText').innerHTML = '';
    document.getElementById('downloadSection').style.display = 'none';
}

// Show results
function showResults() {
    document.getElementById('results').style.display = 'block';
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

// Show loading
function showLoading() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('resultText').innerHTML = '';
    document.getElementById('downloadSection').style.display = 'none';
}

// Hide loading
function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

// Handle interview form submission
async function handleInterviewSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = {
        cv_text: formData.get('cv_text'),
        job_description: formData.get('job_description')
    };
    
    if (!data.cv_text.trim() || !data.job_description.trim()) {
        alert('Please fill in all required fields');
        return;
    }
    
    showResults();
    showLoading();
    
    try {
        const response = await fetch('/api/interview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayResult(result.result);
        } else {
            displayError(result.error || 'An error occurred');
        }
    } catch (error) {
        console.error('Error:', error);
        displayError('Network error. Please try again.');
    } finally {
        hideLoading();
    }
}

// Handle reading form submission
async function handleReadingSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const fileInput = document.getElementById('pdfFile');
    
    if (!fileInput.files[0]) {
        alert('Please select a PDF file');
        return;
    }
    
    showResults();
    showLoading();
    
    try {
        const response = await fetch('/api/summarize', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Display result
            displayResult(result.result);
            
            // Show download link if Excel file was created
            if (result.excel_file) {
                showDownloadLink(result.excel_file);
            }
        } else {
            displayError(result.error || 'An error occurred');
        }
    } catch (error) {
        console.error('Error:', error);
        displayError('Network error. Please try again.');
    } finally {
        hideLoading();
    }
}

// Display result
function displayResult(result) {
    const resultText = document.getElementById('resultText');
    
    // Check if this is from the reading summarizer (PDF upload)
    if (currentForm === 'reading') {
        resultText.innerHTML = formatReadingResult(result);
    } else {
        resultText.innerHTML = formatResult(result);
    }
    
    hideLoading();
}


// Display error
function displayError(error) {
    const resultText = document.getElementById('resultText');
    resultText.innerHTML = `<div class="error-message">
        <i class="fas fa-exclamation-triangle"></i>
        <strong>Error:</strong> ${error}
    </div>`;
    hideLoading();
}

// Format result text
function formatResult(text) {
    // Enhanced formatting for interview preparation
    let formatted = text
        // Handle headers (### becomes h3, ## becomes h2, # becomes h1)
        .replace(/^### (.*$)/gm, '<h3 class="interview-question">$1</h3>')
        .replace(/^## (.*$)/gm, '<h2 class="interview-section">$1</h2>')
        .replace(/^# (.*$)/gm, '<h1 class="interview-title">$1</h1>')
        // Handle bold text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Handle italic text
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // Handle bullet points
        .replace(/^- (.*$)/gm, '<li class="interview-tip">$1</li>')
        // Handle line breaks
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
    
    // Wrap bullet points in ul tags
    formatted = formatted.replace(/(<li class="interview-tip">.*<\/li>)/gs, '<ul class="interview-tips">$1</ul>');
    
    // Clean up any orphaned ul tags
    formatted = formatted.replace(/<\/ul><ul class="interview-tips">/g, '');
    
    return `<div class="interview-preparation">${formatted}</div>`;
}

// Format reading result as a table
function formatReadingResult(text) {
    // Check if this is the JSON format from the AI agent
    if (text.includes('```json') && text.includes('article_title')) {
        return formatJSONResult(text);
    }
    
    // Check if this is the pipe-separated format from the AI agent
    if (text.includes('|') && text.includes('Key concepts & Definitions')) {
        return formatPipeSeparatedResult(text);
    }
    
    // Try to parse the agent's response and extract structured information
    const lines = text.split('\n').filter(line => line.trim());
    
    // Look for common patterns in the agent's response
    let readingName = 'Reading Summary';
    let keyConcepts = [];
    let relevance = [];
    let summary = [];
    
    // Parse the response to extract information
    let currentSection = 'summary';
    
    for (let line of lines) {
        line = line.trim();
        if (!line) continue;
        
        // Detect sections
        if (line.toLowerCase().includes('name') || line.toLowerCase().includes('title')) {
            readingName = line.replace(/.*[:\-]\s*/i, '');
        } else if (line.toLowerCase().includes('concept') || line.toLowerCase().includes('definition')) {
            currentSection = 'concepts';
            if (line.length > 20) keyConcepts.push(line);
        } else if (line.toLowerCase().includes('relevant') || line.toLowerCase().includes('interest')) {
            currentSection = 'relevance';
            if (line.length > 20) relevance.push(line);
        } else if (line.toLowerCase().includes('summary') || line.toLowerCase().includes('overview')) {
            currentSection = 'summary';
        } else {
            // Add content to appropriate section
            if (line.length > 10) {
                if (currentSection === 'concepts') {
                    keyConcepts.push(line);
                } else if (currentSection === 'relevance') {
                    relevance.push(line);
                } else {
                    summary.push(line);
                }
            }
        }
    }
    
    // If we didn't find structured content, use the whole text as summary
    if (keyConcepts.length === 0 && relevance.length === 0) {
        summary = lines.filter(line => line.trim().length > 10);
    }
    
    // Create the table HTML
    return `
        <div class="reading-summary-table">
            <h3><i class="fas fa-book"></i> ${readingName}</h3>
            <table class="summary-table">
                <thead>
                    <tr>
                        <th><i class="fas fa-lightbulb"></i> Key Concepts & Definitions</th>
                        <th><i class="fas fa-heart"></i> Relevance & Curiosity</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="concepts-cell">
                            ${keyConcepts.length > 0 ? 
                                keyConcepts.slice(0, 3).map(concept => `<div class="concept-item">${concept}</div>`).join('') :
                                summary.length > 0 ?
                                    summary.slice(0, 5).map(line => `<div class="concept-item">${line}</div>`).join('') :
                                    '<div class="concept-item">Key concepts will be extracted from the reading</div>'
                            }
                        </td>
                        <td class="relevance-cell">
                            ${relevance.length > 0 ? 
                                relevance.slice(0, 2).map(rel => `<div class="relevance-item">${rel}</div>`).join('') :
                                '<div class="relevance-item">Relevant to Livia\'s interests in AI and education</div>'
                            }
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
}

// Format JSON result from AI agent
function formatJSONResult(text) {
    try {
        // Extract JSON from the text
        const jsonMatch = text.match(/```json\s*(\{.*?\})\s*```/s);
        if (!jsonMatch) {
            return formatReadingResult(text); // Fallback
        }
        
                const data = JSON.parse(jsonMatch[1]);
                
                // Handle key_concepts whether it's a string or array
                let keyConcepts = data.key_concepts || 'No key concepts provided';
                if (Array.isArray(keyConcepts)) {
                    keyConcepts = keyConcepts.join('\n');
                }
                
                // Create the table HTML
                return `
                    <div class="reading-summary-table">
                        <h3><i class="fas fa-book"></i> ${data.article_title || 'Reading Summary'}</h3>
                        <table class="summary-table">
                            <thead>
                                <tr>
                                    <th><i class="fas fa-lightbulb"></i> Key Concepts & Definitions</th>
                                    <th><i class="fas fa-heart"></i> Relevance & Curiosity</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td class="concepts-cell">
                                        <div class="concept-item">${keyConcepts}</div>
                                    </td>
                                    <td class="relevance-cell">
                                        <div class="relevance-item">${data.relevance || 'No relevance information provided'}</div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                `;
    } catch (error) {
        console.error('Error parsing JSON result:', error);
        return formatReadingResult(text); // Fallback
    }
}

// Format pipe-separated result from AI agent
function formatPipeSeparatedResult(text) {
    // Remove markdown code block markers if present
    let cleanText = text.replace(/```[\s\S]*?\n/, '').replace(/```$/, '').trim();
    
    const lines = cleanText.split('\n').filter(line => line.trim());
    
    // Find the data line (skip header line and separator line)
    let dataLine = '';
    for (let line of lines) {
        if (line.includes('|') && 
            !line.includes('Key concepts & Definitions') && 
            !line.includes('-------') &&
            !line.includes('--------')) {
            dataLine = line;
            break;
        }
    }
    
    if (!dataLine) {
        return formatReadingResult(text); // Fallback to original parsing
    }
    
    // Split by pipe and clean up
    const parts = dataLine.split('|').map(part => part.trim());
    
    if (parts.length < 3) {
        return formatReadingResult(text); // Fallback to original parsing
    }
    
    const readingName = parts[0] || 'Reading Summary';
    const keyConceptsText = parts[1] || '';
    const relevanceText = parts[2] || '';
    
    // Parse key concepts (split by bullet points, dashes, or newlines)
    const keyConcepts = keyConceptsText
        .split(/\*|\n|(?<=\.)\s*-/)
        .map(concept => concept.trim())
        .filter(concept => concept.length > 0 && !concept.match(/^[-*]+$/))
        .map(concept => concept.replace(/^[-*]?\s*/, '')); // Remove leading dashes/asterisks
    
    // Parse relevance (split by bullet points, dashes, or newlines)
    const relevance = relevanceText
        .split(/\*|\n|(?<=\.)\s*-/)
        .map(rel => rel.trim())
        .filter(rel => rel.length > 0 && !rel.match(/^[-*]+$/))
        .map(rel => rel.replace(/^[-*]?\s*/, '')); // Remove leading dashes/asterisks
    
    // Create the beautiful table HTML
    return `
        <div class="reading-summary-table">
            <h3><i class="fas fa-book"></i> ${readingName}</h3>
            <div class="success-notice">
                <i class="fas fa-check-circle"></i> PDF successfully analyzed and summarized
            </div>
            <table class="summary-table">
                <thead>
                    <tr>
                        <th><i class="fas fa-lightbulb"></i> Key Concepts & Definitions</th>
                        <th><i class="fas fa-heart"></i> Relevance & Curiosity</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="concepts-cell">
                            ${keyConcepts.length > 0 ? 
                                keyConcepts.map(concept => `<div class="concept-item">• ${concept}</div>`).join('') :
                                '<div class="concept-item">Key concepts will be extracted from the reading</div>'
                            }
                        </td>
                        <td class="relevance-cell">
                            ${relevance.length > 0 ? 
                                relevance.map(rel => `<div class="relevance-item">• ${rel}</div>`).join('') :
                                '<div class="relevance-item">Relevant to Livia\'s interests in AI and education</div>'
                            }
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
}

// Show download link
function showDownloadLink(filename) {
    const downloadSection = document.getElementById('downloadSection');
    const downloadLink = document.getElementById('downloadLink');
    
    downloadLink.href = `/api/download/${filename}`;
    downloadSection.style.display = 'block';
}

// Load CV file
function loadCVFile() {
    const fileInput = document.getElementById('cvFile');
    const file = fileInput.files[0];
    
    if (file && file.type === 'application/json') {
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const jsonData = JSON.parse(e.target.result);
                const cvTextarea = document.getElementById('cvText');
                cvTextarea.value = JSON.stringify(jsonData, null, 2);
                
                // Show success message
                showNotification('CV file loaded successfully!', 'success');
            } catch (error) {
                showNotification('Invalid JSON file. Please check the format.', 'error');
            }
        };
        reader.readAsText(file);
    } else {
        showNotification('Please select a valid JSON file.', 'error');
    }
}

// Setup drag and drop for file uploads
function setupDragAndDrop() {
    const fileLabel = document.querySelector('.file-label-large');
    const fileInput = document.getElementById('pdfFile');
    
    if (fileLabel && fileInput) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            fileLabel.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });
        
        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            fileLabel.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            fileLabel.addEventListener(eventName, unhighlight, false);
        });
        
        // Handle dropped files
        fileLabel.addEventListener('drop', handleDrop, false);
    }
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight(e) {
    e.currentTarget.style.background = '#edf2f7';
    e.currentTarget.style.borderColor = '#667eea';
}

function unhighlight(e) {
    e.currentTarget.style.background = '#f7fafc';
    e.currentTarget.style.borderColor = '#cbd5e0';
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        const file = files[0];
        if (file.type === 'application/pdf') {
            const fileInput = document.getElementById('pdfFile');
            fileInput.files = files;
            
            // Update the label text
            const label = e.currentTarget;
            const icon = label.querySelector('i');
            const text = label.querySelector('span');
            
            icon.className = 'fas fa-file-pdf';
            icon.style.color = '#e53e3e';
            text.textContent = `Selected: ${file.name}`;
            
            showNotification('PDF file selected successfully!', 'success');
        } else {
            showNotification('Please select a PDF file.', 'error');
        }
    }
}

// Use default job description
function useDefaultJobDescription() {
    const jobDescriptionTextarea = document.getElementById('jobDescription');
    if (jobDescriptionTextarea) {
        jobDescriptionTextarea.value = DEFAULT_JOB_DESCRIPTION;
        showNotification('Default job description loaded!', 'success');
    }
}

// Clear job description
function clearJobDescription() {
    const jobDescriptionTextarea = document.getElementById('jobDescription');
    if (jobDescriptionTextarea) {
        jobDescriptionTextarea.value = '';
        showNotification('Job description cleared!', 'info');
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#48bb78' : type === 'error' ? '#e53e3e' : '#667eea'};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 500;
        animation: slideInRight 0.3s ease;
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .error-message {
        background: #fed7d7;
        color: #c53030;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #e53e3e;
        margin: 10px 0;
    }
    
    .error-message i {
        margin-right: 8px;
    }
    
    .demo-mode-notice {
        background: #e6fffa;
        color: #234e52;
        padding: 10px 15px;
        border-radius: 6px;
        border-left: 4px solid #38b2ac;
        margin: 15px 0;
        font-size: 14px;
        font-weight: 500;
    }
    
    .demo-mode-notice i {
        margin-right: 8px;
        color: #38b2ac;
    }
    
    .reading-summary-table {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 20px 0;
    }
    
    .reading-summary-table h3 {
        color: #2d3748;
        margin-bottom: 20px;
        font-size: 24px;
        font-weight: 600;
    }
    
    .summary-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
    }
    
    .summary-table th {
        background: #f7fafc;
        color: #4a5568;
        padding: 15px;
        text-align: left;
        font-weight: 600;
        border: 1px solid #e2e8f0;
    }
    
    .summary-table td {
        padding: 20px;
        border: 1px solid #e2e8f0;
        vertical-align: top;
    }
    
    .concept-item, .relevance-item {
        margin-bottom: 12px;
        padding: 8px 0;
        line-height: 1.5;
        color: #2d3748;
    }
    
    .concept-item:last-child, .relevance-item:last-child {
        margin-bottom: 0;
    }
`;
document.head.appendChild(style);

// Voice Recording Functions
async function toggleVoiceRecording() {
    if (isRealtimeTranscribing) {
        stopRealtimeTranscription();
    } else {
        await startRealtimeTranscription();
    }
}

async function startRealtimeTranscription() {
    try {
        console.log('Starting real-time transcription...');
        
        // Check if browser supports Web Speech API
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            showVoiceError('Your browser does not support real-time speech recognition. Please use Chrome or Edge.');
            return;
        }
        
        // Create speech recognition instance
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        
        // Configure recognition
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        
        // Get current text in textarea
        const jobDescription = document.getElementById('jobDescription');
        const currentText = jobDescription.value.trim();
        
        // Initialize accumulated text with current text
        accumulatedText = currentText;
        
        recognition.onstart = () => {
            console.log('Speech recognition started');
            isRealtimeTranscribing = true;
            updateVoiceUI(true);
        };
        
        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';
            
            // Process all results
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }
            
            // Update accumulated text with final results
            if (finalTranscript) {
                accumulatedText += (accumulatedText ? ' ' : '') + finalTranscript;
            }
            
            // Update textarea with accumulated text + interim text
            if (finalTranscript || interimTranscript) {
                const displayText = accumulatedText + (interimTranscript ? ' ' + interimTranscript : '');
                jobDescription.value = displayText;
                
                // Show interim results in status
                if (interimTranscript) {
                    updateVoiceStatus(`Speaking: "${interimTranscript}"`);
                } else if (finalTranscript) {
                    updateVoiceStatus(`Added: "${finalTranscript}"`);
                }
            }
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            let errorMessage = 'Speech recognition error occurred.';
            
            switch (event.error) {
                case 'no-speech':
                    errorMessage = 'No speech detected. Please try again.';
                    break;
                case 'audio-capture':
                    errorMessage = 'No microphone found. Please check your microphone.';
                    break;
                case 'not-allowed':
                    errorMessage = 'Microphone access denied. Please allow microphone access.';
                    break;
                case 'network':
                    errorMessage = 'Network error. Please check your connection.';
                    break;
            }
            
            showVoiceError(errorMessage);
            stopRealtimeTranscription();
        };
        
        recognition.onend = () => {
            console.log('Speech recognition ended');
            isRealtimeTranscribing = false;
            updateVoiceUI(false);
        };
        
        // Start recognition
        recognition.start();
        
    } catch (error) {
        console.error('Error starting real-time transcription:', error);
        showVoiceError('Could not start speech recognition. Please try again.');
    }
}

function stopRealtimeTranscription() {
    if (recognition && isRealtimeTranscribing) {
        recognition.stop();
        isRealtimeTranscribing = false;
        updateVoiceUI(false);
    }
}

function updateVoiceUI(transcribing) {
    const btn = document.getElementById('voiceRecordBtn');
    const btnText = document.getElementById('voiceBtnText');
    const status = document.getElementById('voiceStatus');
    const statusText = document.getElementById('voiceStatusText');
    
    if (transcribing) {
        btn.classList.add('recording');
        btnText.textContent = 'Stop Speaking';
        status.style.display = 'block';
        statusText.textContent = 'Listening... Speak now!';
        status.classList.add('recording');
    } else {
        btn.classList.remove('recording');
        btnText.textContent = 'Speak Now';
        status.style.display = 'none'; // Hide the status completely when not transcribing
        status.classList.remove('recording');
        status.classList.remove('processing');
    }
}

function updateVoiceStatus(message) {
    const statusText = document.getElementById('voiceStatusText');
    if (statusText) {
        statusText.textContent = message;
    }
}

// Real-time transcription functions (no longer needed for Whisper)
// Keeping the old function for fallback if needed

function showVoiceSuccess(message) {
    const status = document.getElementById('voiceStatus');
    const statusText = document.getElementById('voiceStatusText');
    
    status.style.display = 'block';
    statusText.textContent = message;
    status.classList.remove('recording', 'processing');
    status.classList.add('success');
    
    setTimeout(() => {
        status.style.display = 'none';
        status.classList.remove('success');
    }, 3000);
}

function showVoiceError(message) {
    const status = document.getElementById('voiceStatus');
    const statusText = document.getElementById('voiceStatusText');
    
    status.style.display = 'block';
    statusText.textContent = message;
    status.classList.remove('recording', 'processing', 'success');
    status.classList.add('error');
    
    setTimeout(() => {
        status.style.display = 'none';
        status.classList.remove('error');
    }, 5000);
}

// Check voice service availability on page load
async function checkVoiceAvailability() {
    try {
        // Check if browser supports Web Speech API
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            const btn = document.getElementById('voiceRecordBtn');
            btn.disabled = true;
            btn.title = 'Real-time speech recognition not supported in this browser. Please use Chrome or Edge.';
            btn.style.opacity = '0.5';
            return;
        }
        
        // Check if microphone is available
        try {
            await navigator.mediaDevices.getUserMedia({ audio: true });
            console.log('Voice services available');
        } catch (error) {
            const btn = document.getElementById('voiceRecordBtn');
            btn.disabled = true;
            btn.title = 'Microphone access required for voice recording';
            btn.style.opacity = '0.5';
        }
        
        // Check TTS availability
        try {
            const response = await fetch('/api/voice-status');
            const result = await response.json();
            
            const ttsBtn = document.getElementById('ttsBtn');
            if (ttsBtn) {
                if (!result.tts_available) {
                    ttsBtn.disabled = true;
                    ttsBtn.title = 'Text-to-Speech not available';
                    ttsBtn.style.opacity = '0.5';
                } else {
                    console.log('TTS service available');
                }
            }
        } catch (error) {
            console.error('Error checking TTS availability:', error);
        }
    } catch (error) {
        console.error('Error checking voice availability:', error);
    }
}

// Text-to-Speech Functions
async function toggleTextToSpeech() {
    const btn = document.getElementById('ttsBtn');
    
    if (isPlayingTTS) {
        stopTextToSpeech();
    } else {
        // Disable button to prevent multiple clicks
        btn.disabled = true;
        try {
            await startTextToSpeech();
        } finally {
            // Re-enable button after TTS starts or fails
            setTimeout(() => {
                if (!isPlayingTTS) {
                    btn.disabled = false;
                }
            }, 500);
        }
    }
}

async function startTextToSpeech() {
    try {
        // Prevent multiple concurrent TTS calls
        if (isPlayingTTS) {
            console.log('TTS already playing, ignoring...');
            return;
        }
        
        // Get only the agent response text (interview results)
        const resultText = document.getElementById('resultText');
        if (!resultText || !resultText.textContent.trim()) {
            showTtsError('No results to read');
            return;
        }
        
        let textToRead = resultText.textContent.trim();
        
        if (!textToRead) {
            showTtsError('No text content found to read');
            return;
        }
        
        // Limit text length for TTS
        if (textToRead.length > 4000) {
            textToRead = textToRead.substring(0, 4000) + '...';
        }
        
        console.log('Converting text to speech:', textToRead.length, 'characters');
        
        // Update UI
        updateTtsUI(true);
        
        // Call TTS API
        const response = await fetch('/api/text-to-speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: textToRead,
                voice: 'nova' // Female voice
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            if (errorData.error && errorData.error.includes('API key')) {
                throw new Error('Text-to-Speech service error: ' + errorData.error);
            }
            throw new Error(errorData.error || 'TTS request failed');
        }
        
        const result = await response.json();
        
        if (result.success && result.audio_data) {
            // Create audio element and play
            const audioBlob = new Blob([Uint8Array.from(atob(result.audio_data), c => c.charCodeAt(0))], { type: 'audio/mpeg' });
            const audioUrl = URL.createObjectURL(audioBlob);
            
            currentAudio = new Audio(audioUrl);
            currentAudio.onended = () => {
                console.log('Audio playback ended');
                isPlayingTTS = false;
                updateTtsUI(false);
                URL.revokeObjectURL(audioUrl);
                // Re-enable button
                const btn = document.getElementById('ttsBtn');
                btn.disabled = false;
            };
            
            currentAudio.onerror = () => {
                console.error('Error playing audio');
                // Don't show error alert - just stop silently
                isPlayingTTS = false;
                updateTtsUI(false);
                const btn = document.getElementById('ttsBtn');
                btn.disabled = false;
            };
            
            isPlayingTTS = true;
            updateTtsUI(true);
            
            // Re-enable button so user can stop
            const btn = document.getElementById('ttsBtn');
            btn.disabled = false;
            
            await currentAudio.play();
            console.log('Audio playback started');
            
        } else {
            throw new Error('No audio data received');
        }
        
    } catch (error) {
        console.error('TTS Error:', error);
        // Only show alert for real errors, not for user-initiated stops
        if (error.message && !error.message.includes('aborted')) {
            console.warn('TTS failed:', error.message);
        }
        isPlayingTTS = false;
        updateTtsUI(false);
        const btn = document.getElementById('ttsBtn');
        btn.disabled = false;
    }
}

function stopTextToSpeech() {
    console.log('Stopping TTS...');
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        currentAudio.src = ''; // Clear the source
        currentAudio = null;
    }
    isPlayingTTS = false;
    updateTtsUI(false);
    const btn = document.getElementById('ttsBtn');
    btn.disabled = false;
}

function updateTtsUI(playing) {
    const btn = document.getElementById('ttsBtn');
    const btnText = document.getElementById('ttsBtnText');
    const btnIcon = btn.querySelector('i');
    
    if (playing) {
        btn.classList.add('playing');
        btnText.textContent = 'Stop';
        if (btnIcon) btnIcon.className = 'fas fa-stop';
    } else {
        btn.classList.remove('playing');
        btnText.textContent = 'Read Aloud';
        if (btnIcon) btnIcon.className = 'fas fa-volume-up';
    }
}

function showTtsError(message) {
    console.error('TTS Error:', message);
    // You could add a toast notification here
    alert('TTS Error: ' + message);
}

// Initialize voice functionality
document.addEventListener('DOMContentLoaded', function() {
    checkVoiceAvailability();
});
