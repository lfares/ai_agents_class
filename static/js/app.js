// JavaScript for AI Agent Assistant Web Platform

// Global variables
let currentForm = null;

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
    // Basic formatting for better readability
    let formatted = text
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    return `<p>${formatted}</p>`;
}

// Format reading result as a table
function formatReadingResult(text) {
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
            ${summary.length > 0 ? `
                <div class="summary-section">
                    <h4><i class="fas fa-clipboard-list"></i> Summary</h4>
                    <div class="summary-content">
                        ${summary.slice(0, 5).map(line => `<p>${line}</p>`).join('')}
                    </div>
                </div>
            ` : ''}
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
`;
document.head.appendChild(style);
