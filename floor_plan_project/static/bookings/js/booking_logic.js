// static/bookings/js/booking_logic.js

document.addEventListener('DOMContentLoaded', function() {
    // This script runs only on the "Create Booking" page
    const form = document.querySelector('.booking-form');
    if (!form) {
        return;
    }

    const startTimeInput = document.getElementById('id_start_time');
    const endTimeInput = document.getElementById('id_end_time');
    const endRecurrenceInput = document.getElementById('id_end_recurrence');

    function setMinDateTime() {
        // Get current date and time in YYYY-MM-DDTHH:MM format
        const now = new Date();
        // Offset for timezone, otherwise it might be in UTC
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        const nowISO = now.toISOString().slice(0, 16);

        // Set the minimum allowed value for start and end time pickers
        if (startTimeInput) {
            startTimeInput.min = nowISO;
        }
        if (endTimeInput) {
            endTimeInput.min = nowISO;
        }

        // Also set min for the recurrence date picker
        if(endRecurrenceInput) {
            endRecurrenceInput.min = now.toISOString().slice(0, 10);
        }
    }

    // When a start time is chosen, ensure the end time cannot be before it
    if (startTimeInput && endTimeInput) {
        startTimeInput.addEventListener('change', function() {
            if (startTimeInput.value) {
                endTimeInput.min = startTimeInput.value;
                // Automatically set end time to be 1 hour after start time for convenience
                const startTime = new Date(startTimeInput.value);
                startTime.setHours(startTime.getHours() + 1);
                endTimeInput.value = startTime.toISOString().slice(0, 16);
            }
        });
    }
    
    // Initialize the fields when the page loads
    setMinDateTime();
});

// --- NEW: LOGIC FOR THE USAGE REPORT PAGE ---
const usageReportTable = document.getElementById('usage-report-table');
if (usageReportTable) {
    fetch('/bookings/api/reports/usage/')
        .then(response => response.json())
        .then(data => {
            const tbody = usageReportTable.querySelector('tbody');
            tbody.innerHTML = ''; // Clear the "Loading..." message

            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="2">No usage data for this month.</td></tr>';
                return;
            }

            data.forEach(item => {
                const row = `
                    <tr>
                        <td>Office ${item.office_number}</td>
                        <td>${item.total_hours} hours</td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
        })
        .catch(error => {
            console.error("Error fetching usage report:", error);
            const tbody = usageReportTable.querySelector('tbody');
            tbody.innerHTML = '<tr><td colspan="2">Could not load the report.</td></tr>';
        });
}