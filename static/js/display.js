// ==========================================
// Warehouse Configuration
// ==========================================

const warehouse = document.getElementById("warehouseMap");

const lines = [
    "1A",
    "2A",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15"
];

const POSITIONS = 9;

// ==========================================
// Build Warehouse Grid
// ==========================================

function buildWarehouse() {

    warehouse.innerHTML = "";

    // Header Row
    const header = document.createElement("div");
    header.className = "warehouse-header";

    // Empty corner
    const empty = document.createElement("div");
    empty.className = "corner-cell";
    header.appendChild(empty);

    // Line Names
    lines.forEach(line => {

        const cell = document.createElement("div");

        cell.className = "line-header";

        cell.textContent = line;

        header.appendChild(cell);

    });

    warehouse.appendChild(header);

    // Position Rows
    for(let pos = 1; pos <= POSITIONS; pos++){

        const row = document.createElement("div");

        row.className = "warehouse-row";

        // Position Label
        const label = document.createElement("div");

        label.className = "position-label";

        label.textContent = "P" + pos;

        row.appendChild(label);

        // Warehouse Cells
        lines.forEach(line=>{

            const cell = document.createElement("div");

            cell.className = "warehouse-cell";

            cell.dataset.line = line;
            cell.dataset.position = pos;

            row.appendChild(cell);

        });

        warehouse.appendChild(row);

    }

}

// ==========================================
// Load Warehouse
// ==========================================

async function loadWarehouse(){

    try{

        const response = await fetch("/api/warehouse");

        const data = await response.json();

        // Reset all cells
        document.querySelectorAll(".warehouse-cell").forEach(cell=>{

            cell.innerHTML = "";

            cell.className = "warehouse-cell";

        });

        // Fill occupied cells
        data.lines.forEach(line=>{

            line.items.forEach(item=>{

                const cell = document.querySelector(

                    `.warehouse-cell[data-line="${line.line_id}"][data-position="${item.position}"]`

                );

                if(!cell) return;

                cell.innerHTML = `
    <div class="product-code">
        ${item.product_code}
    </div>
`;

cell.dataset.product = item.product_code;
cell.dataset.batch = item.batch ?? "-";
cell.dataset.time = item.created_at ?? "-";
cell.dataset.line = line.line_id;
cell.dataset.position = item.position;

                if(item.product_code.startsWith("PE")){

                    cell.classList.add("pe");

                }

                else if(item.product_code.startsWith("NY")){

                    cell.classList.add("ny");

                }

                else if(item.product_code.startsWith("IMP")){

                    cell.classList.add("imp");

                }

            });

        });

    }

    catch(err){

        console.error(err);

    }

}

// ==========================================

buildWarehouse();

loadWarehouse();

setInterval(loadWarehouse,5000);

// ==========================================
// INFORMATION PANEL
// ==========================================

const infoPanel = document.getElementById("infoPanel");

const infoProduct = document.getElementById("infoProduct");
const infoBatch = document.getElementById("infoBatch");
const infoTime = document.getElementById("infoTime");
const infoLine = document.getElementById("infoLine");
const infoPosition = document.getElementById("infoPosition");

const closeInfo = document.getElementById("closeInfo");

// Open panel when clicking a warehouse cell
document.addEventListener("click", (event) => {

    const cell = event.target.closest(".warehouse-cell");

    if (!cell) return;

    // Ignore empty cells
    if (!cell.dataset.product) return;

    infoProduct.textContent = cell.dataset.product;
    infoBatch.textContent = cell.dataset.batch || "-";

    // Format the timestamp
    if (cell.dataset.time && cell.dataset.time !== "-") {

        const date = new Date(cell.dataset.time);

        infoTime.textContent = date.toLocaleString();

    } else {

        infoTime.textContent = "-";

    }

    infoLine.textContent = cell.dataset.line;
    infoPosition.textContent = "P" + cell.dataset.position;

    infoPanel.classList.add("open");

});

// Close panel
closeInfo.addEventListener("click", () => {

    infoPanel.classList.remove("open");

});