document.getElementById('plugin-form').addEventListener('submit', async function (event) {
    event.preventDefault();

    const pluginType = document.getElementById('plugin_type').value;
    const target = document.getElementById('target').value;

    const response = await fetch('/run-plugin/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            plugin_type: pluginType,
            target: target
        })
    });

    const result = await response.json();
    const resultContainer = document.getElementById('result');

    // Clear previous results
    resultContainer.innerHTML = '';

    // If we have valid results, display them as cards
    if (result.results && result.results.length > 0) {
        const chartLabels = [];
        const chartData = [];
        const cyElements = [];

        // Main node representing the target
        cyElements.push({ data: { id: 'main', label: target, class: 'main-node' } });

        result.results.forEach((pluginResult, index) => {
            const card = document.createElement('div');
            card.classList.add('col-md-4');

            // Handle different types of data
            let dataContent = '';
            if (pluginResult.data && typeof pluginResult.data === 'object') {
                dataContent = `<pre>${JSON.stringify(pluginResult.data, null, 2)}</pre>`;
                // Optionally, push object values (e.g., number fields) into the chart
                chartData.push(Object.keys(pluginResult.data).length); // Example: count of keys in the data object
            } else {
                dataContent = pluginResult.data; // For any other type
            }

            const cardContent = `
                <div class="card mb-3 shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title">Result ${index + 1}</h5>
                        <p class="card-text"><strong>Plugin Name:</strong> ${pluginResult.plugin_name || 'N/A'}</p>
                        <p class="card-text"><strong>Data:</strong> ${dataContent}</p>
                    </div>
                </div>
            `;
            card.innerHTML = cardContent;
            resultContainer.appendChild(card);

            // For the chart
            chartLabels.push(`Result ${index + 1}`);

            // For the graph
            const nodeId = `node-${index}`;
            cyElements.push({ data: { id: nodeId, label: pluginResult.plugin_name || `Result ${index + 1}`, class: 'node' } });

            // Create edges from the main node to each plugin result node
            cyElements.push({ data: { source: 'main', target: nodeId } });
        });

        // Create Chart.js chart
        createChart(chartLabels, chartData);

        // Create Cytoscape graph
        createGraph(cyElements);
    } else {
        const errorCard = document.createElement('div');
        errorCard.classList.add('col-md-4');
        errorCard.innerHTML = `
            <div class="card mb-3 shadow-sm">
                <div class="card-body">
                    <h5 class="card-title text-danger">Error</h5>
                    <p class="card-text">${result.message}</p>
                </div>
            </div>
        `;
        resultContainer.appendChild(errorCard);
    }
});

function createChart(labels, data) {
    const ctx = document.getElementById('resultChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Plugin Results',
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function createGraph(elements) {
    cytoscape({
        container: document.getElementById('cy'),
        elements: elements,
        style: [
            {
                selector: 'node',
                style: {
                    'background-color': 'data(class)',
                    'label': 'data(label)',
                    'text-valign': 'center',
                    'color': '#fff',
                    'text-outline-width': 2,
                    'text-outline-color': '#007bff',
                    'border-width': 2,
                    'border-color': '#fff'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#ccc',
                    'target-arrow-color': '#ccc',
                    'target-arrow-shape': 'triangle'
                }
            }
        ],
        layout: {
            name: 'cose', // Using 'cose' for a more organic layout
            directed: true,
            padding: 10
        }
    });
}
