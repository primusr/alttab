<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSV Event Summarizer</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- PapaParse CDN for efficient CSV parsing -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.3.0/papaparse.min.js"></script>
    <!-- Inter Font -->
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
    </style>
</head>
<body class="bg-gray-100 flex items-center justify-center min-h-screen p-4">
    <div class="bg-white rounded-lg shadow-xl p-8 max-w-4xl w-full">
        <h1 class="text-3xl font-bold text-center text-gray-800 mb-6">CSV Event Summarizer</h1>
        <p class="text-center text-gray-600 mb-6">Upload a CSV file to count specific events per student.</p>

        <!-- File Input and Drag/Drop Area -->
        <div id="drop-area" class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center transition-colors duration-200 hover:border-blue-400 cursor-pointer">
            <input type="file" id="file-input" class="hidden" accept=".csv">
            <p class="text-lg text-gray-500">Drag & Drop a CSV file here, or <span class="text-blue-500 font-semibold">click to browse</span></p>
            <p class="text-sm text-gray-400 mt-2">The app will automatically process your file.</p>
        </div>

        <!-- Status Message Box -->
        <div id="status-box" class="mt-6 hidden p-4 rounded-lg text-sm" role="alert"></div>

        <!-- Results Table Container -->
        <div id="results-container" class="mt-8 hidden">
            <h2 class="text-xl font-semibold text-gray-700 mb-4">Summary of Events</h2>
            <div class="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
                <table id="summary-table" class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Student ID</th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">page_blurred</th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">page_focused</th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">question_answered</th>
                        </tr>
                    </thead>
                    <tbody id="table-body" class="bg-white divide-y divide-gray-200">
                        <!-- Table rows will be inserted here by JavaScript -->
                    </tbody>
                </table>
            </div>
            
            <!-- Download Button -->
            <div class="flex justify-center mt-6">
                <button id="download-button" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-full shadow-lg transition-colors duration-200 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
                    Download Summary CSV
                </button>
            </div>
        </div>

    </div>

    <script>
        // --- Core Application Logic ---

        // Get DOM elements
        const dropArea = document.getElementById('drop-area');
        const fileInput = document.getElementById('file-input');
        const statusBox = document.getElementById('status-box');
        const resultsContainer = document.getElementById('results-container');
        const tableBody = document.getElementById('table-body');
        const downloadButton = document.getElementById('download-button');

        // Configuration
        const STUDENT_COL = 1; // Column B (index 1)
        const EVENT_COL = 5;   // Column F (index 5)
        const EVENTS_TO_COUNT = ['page_blurred', 'page_focused', 'question_answered'];

        let summaryData = []; // To store the processed data for the table and download

        // Function to show a status message to the user
        function showStatus(message, type = 'info') {
            statusBox.textContent = message;
            statusBox.className = `mt-6 p-4 rounded-lg text-sm transition-opacity duration-300 ${type === 'error' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`;
            statusBox.classList.remove('hidden');
        }

        // Main function to process the CSV file
        function processCsvFile(file) {
            // Check if file is a CSV
            if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
                showStatus('Please upload a valid CSV file.', 'error');
                return;
            }

            // Hide previous results
            resultsContainer.classList.add('hidden');
            tableBody.innerHTML = '';
            showStatus('Processing file...', 'info');

            // Use PapaParse to efficiently parse the CSV
            Papa.parse(file, {
                header: false,
                skipEmptyLines: true,
                complete: function(results) {
                    const data = results.data;
                    if (data.length <= 1) { // Check for at least a header and one row
                        showStatus('The CSV file is empty or malformed.', 'error');
                        return;
                    }

                    // A dictionary to hold the counts for each student
                    const studentSummary = {};

                    // Loop through the data, skipping the header row
                    for (let i = 1; i < data.length; i++) {
                        const row = data[i];

                        // Ensure row has enough columns
                        if (row.length > Math.max(STUDENT_COL, EVENT_COL)) {
                            const student = row[STUDENT_COL].trim();
                            const event = row[EVENT_COL].trim();

                            // Initialize student's entry if it doesn't exist
                            if (!studentSummary[student]) {
                                studentSummary[student] = {
                                    'page_blurred': 0,
                                    'page_focused': 0,
                                    'question_answered': 0
                                };
                            }

                            // If the event is one we are tracking, increment the count
                            if (EVENTS_TO_COUNT.includes(event)) {
                                studentSummary[student][event]++;
                            }
                        }
                    }

                    // Store the processed data
                    summaryData = Object.entries(studentSummary).map(([student, counts]) => ({
                        student,
                        ...counts
                    }));

                    // Display the results
                    displayResults(summaryData);
                    showStatus(`Successfully processed "${file.name}".`, 'success');
                },
                error: function(err) {
                    showStatus(`An error occurred while parsing the file: ${err.message}`, 'error');
                }
            });
        }

        // Function to display the processed data in the table
        function displayResults(data) {
            tableBody.innerHTML = ''; // Clear previous data
            if (data.length === 0) {
                showStatus('No trackable events were found in the file.', 'error');
                return;
            }

            data.forEach(item => {
                const row = document.createElement('tr');
                row.className = "hover:bg-gray-50 transition-colors duration-150";
                row.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${item.student}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item.page_blurred}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item.page_focused}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item.question_answered}</td>
                `;
                tableBody.appendChild(row);
            });

            resultsContainer.classList.remove('hidden');
        }

        // Function to handle downloading the summary CSV
        function downloadCsv() {
            if (summaryData.length === 0) {
                showStatus('No data to download. Please process a file first.', 'error');
                return;
            }

            // Create a CSV string from the summary data
            const header = ["Student ID", "page_blurred", "page_focused", "question_answered"];
            let csvContent = header.join(',') + '\n';
            summaryData.forEach(row => {
                csvContent += `${row.student},${row.page_blurred},${row.page_focused},${row.question_answered}\n`;
            });

            // Create a blob and a download link
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement("a");
            const url = URL.createObjectURL(blob);
            link.setAttribute("href", url);
            link.setAttribute("download", "student_summary.csv");
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        // --- Event Listeners ---

        // Click on the drop area to open the file dialog
        dropArea.addEventListener('click', () => fileInput.click());

        // Handle file selection from the file input
        fileInput.addEventListener('change', (event) => {
            if (event.target.files.length > 0) {
                processCsvFile(event.target.files[0]);
            }
        });

        // Handle drag and drop functionality
        dropArea.addEventListener('dragover', (event) => {
            event.preventDefault();
            dropArea.classList.add('border-blue-400', 'bg-blue-50');
        });

        dropArea.addEventListener('dragleave', () => {
            dropArea.classList.remove('border-blue-400', 'bg-blue-50');
        });

        dropArea.addEventListener('drop', (event) => {
            event.preventDefault();
            dropArea.classList.remove('border-blue-400', 'bg-blue-50');
            const file = event.dataTransfer.files[0];
            if (file) {
                processCsvFile(file);
            }
        });

        // Handle download button click
        downloadButton.addEventListener('click', downloadCsv);

    </script>
</body>
</html>
