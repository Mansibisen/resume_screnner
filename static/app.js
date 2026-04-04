/* Resume Screener - Frontend JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const jobUrl = document.getElementById('jobUrl');
    const jobDescription = document.getElementById('jobDescription');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const errorMessage = document.getElementById('errorMessage');
    const resultsPanel = document.getElementById('resultsPanel');
    const loadingText = document.getElementById('loadingText');

    // Analyze button click handler
    analyzeBtn.addEventListener('click', analyzeResume);

    // Download button click handler
    downloadBtn.addEventListener('click', downloadResults);

    // Enable/disable analyze button based on input
    [jobUrl, jobDescription].forEach(input => {
        input.addEventListener('input', updateAnalyzeButton);
    });

    function updateAnalyzeButton() {
        const hasJobInfo = jobUrl.value.trim().length > 0 || jobDescription.value.trim().length > 0;
        analyzeBtn.disabled = !hasJobInfo;
    }

    async function analyzeResume() {
        const url = jobUrl.value.trim();
        const desc = jobDescription.value.trim();

        // Validation - resume is already in RAG system
        if (!url && !desc) {
            showError('Please provide either a job URL or description');
            return;
        }

        // Show loading overlay
        showLoading(true);
        analyzeBtn.disabled = true;

        try {
            loadingText.textContent = 'Analyzing your resume against the job posting...';

            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    job_url: url,
                    job_description: desc
                })
            });

            const data = await response.json();

            if (!response.ok) {
                showError(data.error || 'An error occurred during analysis');
                return;
            }

            // Display results
            displayResults(data);

        } catch (error) {
            showError(`Network error: ${error.message}`);
        } finally {
            showLoading(false);
            analyzeBtn.disabled = false;
        }
    }

    function displayResults(data) {
        const fitScore = data.fit_score;
        const overallScore = fitScore.overall_score;

        // Update overall score
        document.getElementById('scoreValue').textContent = `${overallScore}%`;
        document.getElementById('scoreValue').style.color = 'white';

        // Update status
        let status = '🔴 Fair Match';
        let statusColor = 'danger';
        if (overallScore >= 75) {
            status = '🟢 Excellent Match';
            statusColor = 'success';
        } else if (overallScore >= 50) {
            status = '🟡 Good Match';
            statusColor = 'warning';
        }
        document.getElementById('scoreStatus').textContent = status;
        document.getElementById('scoreStatus').className = `score-status ${statusColor}`;

        // Update skill counts
        const matchedSkills = fitScore.matched_skills || [];
        const missingSkills = fitScore.missing_skills || [];
        document.getElementById('matchedCount').textContent = matchedSkills.length;
        document.getElementById('missingCount').textContent = missingSkills.length;

        // Display matched skills
        const matchedContainer = document.getElementById('matchedSkills');
        matchedContainer.innerHTML = matchedSkills
            .map(skill => `<span class="skill-tag skill-matched">${skill}</span>`)
            .join('');

        if (matchedSkills.length === 0) {
            matchedContainer.innerHTML = '<p style="color: #999;">No matched skills identified</p>';
        }

        // Display missing skills
        const missingContainer = document.getElementById('missingSkills');
        missingContainer.innerHTML = missingSkills
            .map(skill => `<span class="skill-tag skill-missing">${skill}</span>`)
            .join('');

        if (missingSkills.length === 0) {
            missingContainer.innerHTML = '<p style="color: #999;">No missing skills identified</p>';
        }

        // Display experience fit
        document.getElementById('experienceFit').textContent = fitScore.experience_fit || 'N/A';

        // Display requirement scores
        const reqScores = fitScore.requirement_scores || {};
        if (Object.keys(reqScores).length > 0) {
            const reqSection = document.getElementById('requirementSection');
            const reqContainer = document.getElementById('requirementScores');
            
            reqContainer.innerHTML = Object.entries(reqScores)
                .map(([req, score]) => {
                    let scoreClass = 'low';
                    if (score >= 75) scoreClass = 'high';
                    else if (score >= 50) scoreClass = 'medium';

                    return `
                        <div class="requirement-item">
                            <div class="requirement-name">
                                <span>${req}</span>
                                <span class="requirement-score ${scoreClass}">${score}%</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${score}%"></div>
                            </div>
                        </div>
                    `;
                })
                .join('');
            
            reqSection.style.display = 'block';
        }

        // Display suggestions
        const suggestionsContainer = document.getElementById('suggestions');
        suggestionsContainer.textContent = data.suggestions;

        // Store data for download
        window.lastAnalysisData = {
            ...data,
            jobInfo: jobUrl.value || 'Custom job description'
        };

        // Show results panel
        resultsPanel.style.display = 'block';
        resultsPanel.scrollIntoView({ behavior: 'smooth' });
    }

    function downloadResults() {
        if (!window.lastAnalysisData) return;

        const data = window.lastAnalysisData;
        const fitScore = data.fit_score;

        const content = `
RESUME SCREENING ANALYSIS RESULTS
Generated: ${data.timestamp}
=====================================

OVERALL FIT SCORE: ${fitScore.overall_score}%

MATCHED SKILLS (${fitScore.matched_skills.length}):
${fitScore.matched_skills.join(', ') || 'None'}

MISSING SKILLS (${fitScore.missing_skills.length}):
${fitScore.missing_skills.join(', ') || 'None'}

EXPERIENCE FIT:
${fitScore.experience_fit}

REQUIREMENT SCORES:
${Object.entries(fitScore.requirement_scores || {})
    .map(([req, score]) => `  • ${req}: ${score}%`)
    .join('\n')}

IMPROVEMENT SUGGESTIONS:
${data.suggestions}

=====================================
Resume Screener | Powered by LangGraph & Ollama
`;

        downloadFile(content, `resume_analysis_${new Date().getTime()}.txt`);
    }

    function downloadFile(content, filename) {
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
        element.setAttribute('download', filename);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }

    function showLoading(show) {
        loadingOverlay.style.display = show ? 'flex' : 'none';
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }

    // Initialize button state
    updateAnalyzeButton();
});
