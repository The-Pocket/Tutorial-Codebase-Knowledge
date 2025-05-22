document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('tutorial_form');
    const generateButton = document.getElementById('generate_button');
    const statusArea = document.getElementById('status_area');
    let pollingInterval;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        clearTimeout(pollingInterval); // Clear any existing polling

        statusArea.innerHTML = '<p class="processing-message">Processing... Please wait.</p>';
        generateButton.disabled = true;

        const formData = new FormData(form);
        const requestData = {};
        formData.forEach((value, key) => {
            if (value || key === 'use_cache') { // Special handling for checkbox which might be false
                if (key === 'include_patterns' || key === 'exclude_patterns') {
                    requestData[key] = value.split(',').map(s => s.trim()).filter(s => s);
                } else if (key === 'max_file_size' || key === 'max_abstractions') {
                    requestData[key] = parseInt(value, 10);
                } else if (key === 'use_cache') {
                    requestData[key] = document.getElementById('use_cache').checked;
                } else {
                    requestData[key] = value;
                }
            }
        });
        
        // Ensure use_cache is always present if it wasn't explicitly set (e.g. if form field was missing)
        if (!('use_cache' in requestData)) {
             requestData['use_cache'] = document.getElementById('use_cache').checked;
        }
        // Remove empty arrays for patterns if no input was given, so backend uses defaults
        if (requestData.include_patterns && requestData.include_patterns.length === 0) {
            delete requestData.include_patterns;
        }
        if (requestData.exclude_patterns && requestData.exclude_patterns.length === 0) {
            delete requestData.exclude_patterns;
        }


        try {
            const response = await fetch('/generate-tutorial/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
            }

            const result = await response.json();
            statusArea.innerHTML = `<p class="processing-message">Request submitted. Task ID: ${result.task_id}. Waiting for completion...</p>`;
            pollStatus(result.task_id, result.results_url, result.status_url); // Pass full URLs

        } catch (error) {
            statusArea.innerHTML = `<p class="error-message">Error: ${error.message}</p>`;
            generateButton.disabled = false;
        }
    });

    function pollStatus(taskId, resultsUrl, statusUrl) { // Use full URLs passed from initial response
        pollingInterval = setTimeout(async () => {
            try {
                const response = await fetch(statusUrl); // Use the full status URL
                if (!response.ok) {
                    if (response.status === 404) {
                        statusArea.innerHTML = `<p class="error-message">Task ID ${taskId} not found. It might have expired or was invalid.</p>`;
                        generateButton.disabled = false;
                        clearTimeout(pollingInterval);
                        return;
                    }
                    throw new Error(`Status check failed! Status: ${response.status}`);
                }

                const data = await response.json();

                if (data.status === 'completed') {
                    clearTimeout(pollingInterval);
                    statusArea.innerHTML = \`
                        <p style="color: green; font-weight: bold;">Tutorial Ready!</p>
                        <p>Task ID: ${data.task_id}</p>
                        <a href="${resultsUrl}" download>Download Tutorial (.zip)</a>
                    \`;
                    generateButton.disabled = false;
                } else if (data.status === 'failed') {
                    clearTimeout(pollingInterval);
                    let errorDetails = data.error_details ? \`Details: ${data.error_details}\` : 'No specific error details reported.';
                    statusArea.innerHTML = \`
                        <p class="error-message">Tutorial Generation Failed.</p>
                        <p>Task ID: ${data.task_id}</p>
                        <p>${errorDetails}</p>
                    \`;
                    generateButton.disabled = false;
                } else { // 'processing'
                    statusArea.innerHTML = `<p class="processing-message">Task ${data.task_id} is still ${data.status || 'processing'}. Checking again in 5 seconds...</p>`;
                    pollStatus(taskId, resultsUrl, statusUrl); // Continue polling
                }
            } catch (error) {
                statusArea.innerHTML = `<p class="error-message">Error checking status: ${error.message}. Will try again.</p>`;
                // Decide if to continue polling on error or stop
                // For robustness, let's continue polling a few times or with backoff, but for simplicity here, we'll just poll again.
                pollStatus(taskId, resultsUrl, statusUrl); 
                // generateButton.disabled = false; // Consider re-enabling button on persistent polling errors
            }
        }, 5000); // Poll every 5 seconds
    }
});
