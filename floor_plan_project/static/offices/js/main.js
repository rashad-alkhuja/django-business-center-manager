// static/offices/js/main.js

document.addEventListener('DOMContentLoaded', () => {

    // --- SHARED FUNCTION TO RENDER THE PIE CHART ---
    // This will be called on any page that has a chart canvas.
    function renderOccupancyChart() {
        const chartCanvas = document.getElementById('occupancyChart');
        // If the chart canvas doesn't exist on the current page, do nothing.
        if (!chartCanvas) {
            return;
        }

        fetch('/floor-plan/api/statistics/')
            .then(response => response.json())
            .then(data => {
                const total = data.available_count + data.rented_count;
                new Chart(chartCanvas.getContext('2d'), {
                    type: 'pie',
                    data: {
                        labels: ['Rented', 'Available'],
                        datasets: [{
                            label: 'Office Occupancy',
                            data: [data.rented_count, data.available_count],
                            backgroundColor: ['rgba(231, 76, 60, 0.8)', 'rgba(39, 174, 96, 0.8)'],
                            borderColor: ['#e74c3c', '#27ae60'],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'top' },
                            title: { display: true, text: 'Office Occupancy Status' },
                            tooltip: {
                                callbacks: {
                                    label: function (tooltipItem) {
                                        const count = tooltipItem.raw;
                                        const percentage = total > 0 ? (count / total * 100).toFixed(1) : 0;
                                        return `${tooltipItem.label}: ${count} offices (${percentage}%)`;
                                    }
                                }
                            }
                        }
                    }
                });
            })
            .catch(error => console.error("Error fetching statistics data:", error));
    }

    // --- FLOOR PLAN SPECIFIC LOGIC ---
    // This entire block will only run if we are on the floor plan page.
    const floorPlan = document.querySelector('.floor-plan');
    if (floorPlan) {
        const tooltip = document.getElementById('tooltip');
        const modalOverlay = document.getElementById('tenant-modal-overlay');
        const modalCloseButton = document.getElementById('modal-close-button');
        const loadingIndicator = document.getElementById('loading-indicator');

        fetch('/floor-plan/api/offices/')
            .then(response => response.json())
            .then(offices => {
                if (loadingIndicator) loadingIndicator.style.display = 'none';

                // Your single source of truth for the office layout.
                const officePositions = {
                    '1': { top: '468px', left: '714px', width: '64px', height: '50px' },
                    '2': { top: '546px', left: '737px', width: '64px', height: '50px' },
                    '3': { top: '627px', left: '737px', width: '64px', height: '50px' },
                    '4': { top: '490px', left: '625px', width: '41px', height: '61px' },
                    '5': { top: '581px', left: '625px', width: '41px', height: '61px' },
                    '6': { top: '490px', left: '574px', width: '41px', height: '61px' },
                    '7': { top: '581px', left: '533px', width: '41px', height: '61px' },
                    '8': { top: '500px', left: '533px', width: '31px', height: '51px' },
                    '9': { top: '445px', left: '533px', width: '31px', height: '51px' },
                    '10': { top: '389px', left: '533px', width: '31px', height: '51px' },
                    '11': { top: '354px', left: '533px', width: '31px', height: '31px' },
                    '12': { top: '430px', left: '574px', width: '41px', height: '56px' },
                    '13': { top: '430px', left: '625px', width: '41px', height: '56px' },
                    '14': { top: '400px', left: '714px', width: '51px', height: '35px' },
                    '15': { top: '344px', left: '625px', width: '71px', height: '51px' },
                    '16': { top: '288px', left: '625px', width: '71px', height: '51px' },
                    '17': { top: '227px', left: '625px', width: '71px', height: '51px' },
                    '18': { top: '214px', left: '461px', width: '46px', height: '51px' },
                    '19': { top: '159px', left: '461px', width: '46px', height: '51px' },
                    '20': { top: '149px', left: '553px', width: '46px', height: '51px' },
                    '21': { top: '76px', left: '461px', width: '46px', height: '46px' },
                    '22': { top: '159px', left: '409px', width: '46px', height: '51px' },
                    '23': { top: '214px', left: '409px', width: '46px', height: '51px' },
                    '24': { top: '214px', left: '358px', width: '46px', height: '51px' },
                    '25': { top: '159px', left: '358px', width: '46px', height: '51px' },
                    '26': { top: '76px', left: '358px', width: '46px', height: '46px' },
                    '27': { top: '159px', left: '307px', width: '46px', height: '51px' },
                    '28': { top: '76px', left: '302px', width: '46px', height: '46px' },
                    '29': { top: '214px', left: '307px', width: '46px', height: '51px' },
                    '30': { top: '270px', left: '307px', width: '46px', height: '46px' },
                    '31': { top: '272px', left: '236px', width: '46px', height: '46px' },
                    '32': { top: '323px', left: '236px', width: '46px', height: '46px' },
                    '33': { top: '374px', left: '236px', width: '46px', height: '46px' },
                    '34': { top: '373px', left: '307px', width: '46px', height: '46px' },
                    '35': { top: '425px', left: '307px', width: '46px', height: '46px' },
                    '36': { top: '374px', left: '184px', width: '46px', height: '46px' },
                    '37': { top: '476px', left: '307px', width: '46px', height: '46px' },
                    '38': { top: '425px', left: '184px', width: '46px', height: '46px' },
                    '39': { top: '527px', left: '307px', width: '46px', height: '46px' },
                    '41': { top: '577px', left: '307px', width: '46px', height: '46px' },
                    '44': { top: '582px', left: '82px', width: '46px', height: '46px' },
                    '46': { top: '527px', left: '82px', width: '46px', height: '46px' },
                    '47': { top: '527px', left: '133px', width: '46px', height: '46px' },
                    '48': { top: '470px', left: '82px', width: '46px', height: '46px' },
                    '49': { top: '470px', left: '133px', width: '46px', height: '46px' },
                    '50': { top: '323px', left: '184px', width: '46px', height: '46px' },
                    '51': { top: '415px', left: '82px', width: '46px', height: '46px' },
                    '52': { top: '272px', left: '184px', width: '46px', height: '46px' },
                    '53': { top: '360px', left: '82px', width: '46px', height: '46px' },
                    '54': { top: '272px', left: '82px', width: '46px', height: '46px' },
                    '55': { top: '217px', left: '82px', width: '46px', height: '46px' },
                    '56': { top: '126px', left: '82px', width: '46px', height: '46px' },
                    '57': { top: '76px', left: '159px', width: '46px', height: '46px' },
                    '58': { top: '76px', left: '210px', width: '46px', height: '46px' },
                    '60': { top: '678px', left: '466px', width: '46px', height: '46px' },
                    '61': { top: '729px', left: '307px', width: '46px', height: '46px' },
                    '62': { top: '729px', left: '364px', width: '46px', height: '46px' },
                    '63': { top: '785px', left: '307px', width: '46px', height: '46px' },
                    '64': { top: '729px', left: '415px', width: '46px', height: '46px' },
                    '67': { top: '785px', left: '645px', width: '46px', height: '46px' },
                    '68': { top: '785px', left: '589px', width: '46px', height: '46px' },
                    '69': { top: '785px', left: '533px', width: '46px', height: '46px' }
                };

                offices.forEach(office => {
                    const position = officePositions[office.office_number];
                    if (!position) return;

                    const officeDiv = document.createElement('div');
                    officeDiv.id = `office-${office.office_number}`;
                    officeDiv.className = `office ${office.status}`;
                    officeDiv.textContent = office.office_number;
                    Object.assign(officeDiv.style, position);

                    officeDiv.dataset.sqft = office.size_sqft;
                    officeDiv.dataset.rent = office.annual_rent;
                    officeDiv.dataset.expiry = office.expiry_date;
                    officeDiv.dataset.company = office.company_name;
                    officeDiv.dataset.person = office.contact_person;
                    officeDiv.dataset.email = office.contact_email;
                    officeDiv.dataset.phone = office.contact_phone;

                    floorPlan.appendChild(officeDiv);
                });


            })
            .catch(error => {
                console.error("Error fetching office data:", error);
                if (loadingIndicator) loadingIndicator.textContent = 'Error: Could not load office data.';
            });

        floorPlan.addEventListener('mouseover', (event) => {
            const office = event.target;
            if (office.classList.contains('office')) {
                let html = `<strong>Office:</strong> ${office.id.replace('office-', '')}<br><strong>Size:</strong> ${office.dataset.sqft} sqft<br><strong>Rent:</strong> ${office.dataset.rent}`;
                if (office.classList.contains('rented') && office.dataset.expiry && office.dataset.expiry !== 'null') {
                    html += `<br><strong>Expires:</strong> ${office.dataset.expiry}`;
                }
                tooltip.innerHTML = html;
                tooltip.classList.add('visible');
            }
        });

        floorPlan.addEventListener('mousemove', (event) => {
            tooltip.style.left = (event.pageX + 15) + 'px';
            tooltip.style.top = (event.pageY + 15) + 'px';
        });

        floorPlan.addEventListener('mouseout', (event) => {
            if (event.target.classList.contains('office')) {
                tooltip.classList.remove('visible');
            }
        });

        floorPlan.addEventListener('click', (event) => {
            const officeDiv = event.target;
            if (!officeDiv.classList.contains('office')) return;

            const officeId = officeDiv.id.replace('office-', '');

            if (officeDiv.classList.contains('available')) {
                window.location.href = `/floor-plan/proposal/create/${officeId}/`;
            } else if (officeDiv.classList.contains('rented')) {
                document.getElementById('modal-office-number').textContent = officeId;
                document.getElementById('modal-company-name').textContent = officeDiv.dataset.company || 'N/A';
                document.getElementById('modal-contact-person').textContent = officeDiv.dataset.person || 'N/A';
                document.getElementById('modal-email').textContent = officeDiv.dataset.email || 'N/A';
                document.getElementById('modal-phone').textContent = officeDiv.dataset.phone || 'N/A';
                document.getElementById('modal-expiry').textContent = officeDiv.dataset.expiry || 'N/A';
                modalOverlay.classList.add('visible');
            }
        });

        if (modalCloseButton) {
            modalCloseButton.addEventListener('click', () => {
                modalOverlay.classList.remove('visible');
            });
        }

        if (modalOverlay) {
            modalOverlay.addEventListener('click', (event) => {
                if (event.target === modalOverlay) {
                    modalOverlay.classList.remove('visible');
                }
            });
        }
    }

    // --- INITIALIZE THE PAGE ---
    // This will run on every page, but the functions inside have checks
    // to make sure they only execute if the required elements are present.
    renderOccupancyChart();
});