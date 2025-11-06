const statusLabels = ['Open', 'In Progress', 'Closed'];
const statusColors = ['green', 'orange', 'red'];

function fetchRequests() {
    fetch('/get_requests')
        .then(res => res.json())
        .then(data => {
            populateTable(data);
        });
}

document.getElementById('uploadBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById("fileUpload");
    const spinner = document.getElementById("spinner");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file first.");
        return;
    }

    spinner.style.display = "inline-block";
    document.getElementById("uploadBtn").disabled = true;

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/upload", {
        method: "POST",
        body: formData
        });

        const result = await response.json();
        alert(result.message);
        fetchUsers();
    } catch (error) {
        alert("Upload failed. Please try again.");
        console.error(error);
    } finally {
        spinner.style.display = "none";
        document.getElementById("uploadBtn").disabled = false;
    }
    });

async function fetchUsers() {
    const res = await fetch('/get_requests');
    const users = await res.json();

    const tbody = document.getElementById('userList');
    tbody.innerHTML = ''; // clear table body

    users.forEach(u => {
        // Main request row
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="toggle-btn">▶</td>
            <td class="non-editable">${u.id}</td>
            <td contenteditable="true" class="editable" data-field="requester_name">${u.requester_name}</td>
            <td contenteditable="true" class="editable" data-field="title">${u.title}</td>
            <td class="non-editable">${u.vendor_name}</td>
            <td class="non-editable">${u.vat_id}</td>
            <td class="non-editable">${u.commodity_group}</td>
            <td class="non-editable">${u.total_cost}</td>
            <td contenteditable="true" class="editable" data-field="department"=>${u.department}</td>
            <td class="non-editable">
            <button class="status-btn" data-status="${u.action}">${statusLabels[u.action]}</button>
            </td>
            `;
        tbody.appendChild(row);
        row.querySelectorAll('.editable').forEach(cell => {
            cell.addEventListener('blur', async () => {
                const newValue = cell.textContent;
                const field = cell.dataset.field;

                // Send update to server
                await fetch(`/update_request/${u.id}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ [field]: newValue })
                });
            });
        });
        const statusBtn = row.querySelector('.status-btn');

        // Set initial styles
        statusBtn.style.backgroundColor = statusColors[parseInt(statusBtn.dataset.status)];
        statusBtn.style.color = '#fff';
        statusBtn.style.border = 'none';
        statusBtn.style.padding = '4px 8px';
        statusBtn.style.borderRadius = '4px';
        statusBtn.style.cursor = 'pointer';

        // On click: cycle status
        statusBtn.addEventListener('click', () => {
            let currentStatus = parseInt(statusBtn.dataset.status);
            let nextStatus = (currentStatus + 1) % 3; // cycle 0 → 1 → 2 → 0

            statusBtn.dataset.status = nextStatus;
            statusBtn.textContent = statusLabels[nextStatus];
            statusBtn.style.backgroundColor = statusColors[nextStatus];

            fetch(`/update_action/${u.id}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ action: nextStatus })
            });
        });

        // Row to hold nested table
        const nestedRow = document.createElement('tr');
        nestedRow.style.display = 'none'; // initially hidden

        // Use one cell spanning all main columns
        const nestedCell = document.createElement('td');
        nestedCell.colSpan = 10;

        // Create nested table
        const nestedTable = document.createElement('table');
        nestedTable.style.width = '100%';
        nestedTable.style.borderCollapse = 'collapse';
        nestedTable.innerHTML = `
            <thead>
                <tr style="background:#f0f0f0;">
                    <th class="non-editable">Position Description</th>
                    <th class="non-editable">Unit Price</th>
                    <th class="non-editable">Amount</th>
                    <th class="non-editable">Total Price</th>
                </tr>
            </thead>
            <tbody>
                ${u.order_lines.map(line => `
                    <tr>
                        <td class="non-editable">${line.Product}</td>
                        <td class="non-editable">${line['Unit Price']}</td>
                        <td class="non-editable">${line.Quantity}</td>
                        <td class="non-editable">${line.Total}</td>
                    </tr>
                `).join('')}
            </tbody>
        `;

        nestedCell.appendChild(nestedTable);
        nestedRow.appendChild(nestedCell);
        tbody.appendChild(nestedRow);

        // Toggle click
        row.querySelector('.toggle-btn').addEventListener('click', () => {
            const isVisible = nestedRow.style.display !== 'none';
            nestedRow.style.display = isVisible ? 'none' : '';
            row.querySelector('.toggle-btn').textContent = isVisible ? '▶' : '▼';
        });
    });
}

document.addEventListener('DOMContentLoaded', fetchUsers);