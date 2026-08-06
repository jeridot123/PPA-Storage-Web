// =========================================================
// WAREHOUSE STORAGE SYSTEM
// FRONTEND
// =========================================================


let currentMode = "IN";

let highlightedLocation = null;


// =========================================================
// ELEMENTS
// =========================================================

const modeBar =
    document.getElementById("modeBar");

const statusText =
    document.getElementById("statusText");

const productText =
    document.getElementById("productText");

const locationText =
    document.getElementById("locationText");

const barcodeInput =
    document.getElementById("barcodeInput");

const storageBody =
    document.getElementById("storageBody");

const capacityText =
    document.getElementById("capacityText");


// =========================================================
// LOAD WAREHOUSE
// =========================================================

async function loadWarehouse() {

    try {

        const response =
            await fetch("/api/warehouse");


        const data =
            await response.json();


        if (!data.success) {

            throw new Error(
                "Could not load warehouse."
            );

        }


        renderWarehouse(data);

    }

    catch (error) {

        console.error(error);


        statusText.textContent =
            "SERVER ERROR";


        statusText.style.color =
            "#D32F2F";


        locationText.textContent =
            "Cannot connect to warehouse server";

    }

}


// =========================================================
// RENDER WAREHOUSE
// =========================================================

function renderWarehouse(data) {

    storageBody.innerHTML = "";


    data.lanes.forEach(item => {

        const row =
            document.createElement("tr");


        // -------------------------------------------------
        // LANE
        // -------------------------------------------------

        const laneCell =
            document.createElement("td");


        laneCell.textContent =
            String(item.lane).padStart(
                2,
                "0"
            );


        laneCell.className =
            "lane-cell";


        // -------------------------------------------------
        // SLOT A
        // -------------------------------------------------

        const slotA =
            createSlotCell(
                item.lane,
                "A",
                item.A
            );


        // -------------------------------------------------
        // SLOT B
        // -------------------------------------------------

        const slotB =
            createSlotCell(
                item.lane,
                "B",
                item.B
            );


        row.appendChild(
            laneCell
        );


        row.appendChild(
            slotA
        );


        row.appendChild(
            slotB
        );


        storageBody.appendChild(
            row
        );

    });


    capacityText.innerHTML =
        `OCCUPIED : ${data.occupied}/${data.total}
         &nbsp;&nbsp;&nbsp;
         AVAILABLE : ${data.available}`;


    restoreHighlight();

}


// =========================================================
// CREATE SLOT CELL
// =========================================================

function createSlotCell(
    lane,
    slot,
    product
) {

    const cell =
        document.createElement("td");


    cell.id =
        `slot-${lane}-${slot}`;


    if (product === null) {

        cell.textContent =
            "EMPTY";


        cell.className =
            "slot-empty";

    }

    else {

        cell.textContent =
            product;


        cell.className =
            "slot-occupied";

    }


    return cell;

}


// =========================================================
// CLEAR HIGHLIGHT
// =========================================================

function clearHighlight() {

    highlightedLocation = null;


    document
        .querySelectorAll(
            ".slot-highlight"
        )
        .forEach(cell => {

            cell.classList.remove(
                "slot-highlight"
            );

        });

}


// =========================================================
// HIGHLIGHT
// =========================================================

function highlightLocation(
    lane,
    slot
) {

    clearHighlight();


    highlightedLocation = {
        lane: lane,
        slot: slot
    };


    restoreHighlight();

}


// =========================================================
// RESTORE HIGHLIGHT
// =========================================================

function restoreHighlight() {

    if (!highlightedLocation) {

        return;

    }


    const cell =
        document.getElementById(
            `slot-${highlightedLocation.lane}-${highlightedLocation.slot}`
        );


    if (cell) {

        cell.classList.add(
            "slot-highlight"
        );

    }

}


// =========================================================
// IN MODE
// =========================================================

function setInMode() {

    currentMode = "IN";


    clearHighlight();


    modeBar.textContent =
        "IN / STORE MODE";


    modeBar.className =
        "mode-bar in-mode";


    statusText.textContent =
        "READY TO STORE";


    statusText.style.color =
        "#1565C0";


    productText.textContent =
        "---";


    productText.style.color =
        "#212121";


    locationText.textContent =
        "Scan product to store";


    locationText.style.color =
        "#757575";


    barcodeInput.value = "";

    barcodeInput.focus();

}


// =========================================================
// OUT MODE
// =========================================================

function setOutMode() {

    currentMode = "OUT";


    clearHighlight();


    modeBar.textContent =
        "OUT / TAKE MODE";


    modeBar.className =
        "mode-bar out-mode";


    statusText.textContent =
        "READY TO TAKE";


    statusText.style.color =
        "#E65100";


    productText.textContent =
        "---";


    productText.style.color =
        "#212121";


    locationText.textContent =
        "Scan product to take";


    locationText.style.color =
        "#757575";


    barcodeInput.value = "";

    barcodeInput.focus();

}


// =========================================================
// PROCESS BARCODE
// =========================================================

async function processBarcode() {

    const productCode =
        barcodeInput
            .value
            .trim()
            .toUpperCase();


    barcodeInput.value = "";


    if (productCode === "") {

        barcodeInput.focus();

        return;

    }


    if (currentMode === "IN") {

        await storeProduct(
            productCode
        );

    }

    else {

        await takeProduct(
            productCode
        );

    }


    barcodeInput.focus();

}


// =========================================================
// STORE PRODUCT
// =========================================================

async function storeProduct(
    productCode
) {

    try {

        const response =
            await fetch(
                "/api/store",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(
                        {
                            product_code:
                                productCode
                        }
                    )
                }
            );


        const data =
            await response.json();


        // -------------------------------------------------
        // ERROR
        // -------------------------------------------------

        if (!data.success) {

            showError(
                productCode,
                data.message
            );

            return;

        }


        // -------------------------------------------------
        // SUCCESS
        // -------------------------------------------------

        statusText.textContent =
            data.message;


        statusText.style.color =
            "#2E7D32";


        productText.textContent =
            data.product_code;


        productText.style.color =
            "#212121";


        locationText.textContent =
            `STORE AT  LANE ${String(
                data.lane
            ).padStart(2, "0")} - SLOT ${data.slot}`;


        locationText.style.color =
            "#1565C0";


        highlightLocation(
            data.lane,
            data.slot
        );


        await loadWarehouse();

    }

    catch (error) {

        serverError(error);

    }

}


// =========================================================
// TAKE PRODUCT
// =========================================================

async function takeProduct(
    productCode
) {

    try {

        const response =
            await fetch(
                "/api/take",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(
                        {
                            product_code:
                                productCode
                        }
                    )
                }
            );


        const data =
            await response.json();


        // -------------------------------------------------
        // ERROR
        // -------------------------------------------------

        if (!data.success) {

            showError(
                productCode,
                data.message
            );

            return;

        }


        // -------------------------------------------------
        // SUCCESS
        // -------------------------------------------------

        statusText.textContent =
            data.message;


        statusText.style.color =
            "#E65100";


        productText.textContent =
            data.product_code;


        productText.style.color =
            "#212121";


        locationText.textContent =
            `TAKE FROM  LANE ${String(
                data.lane
            ).padStart(2, "0")} - SLOT ${data.slot}`;


        locationText.style.color =
            "#E65100";


        highlightLocation(
            data.lane,
            data.slot
        );


        await loadWarehouse();

    }

    catch (error) {

        serverError(error);

    }

}


// =========================================================
// DISPLAY ERROR
// =========================================================

function showError(
    productCode,
    message
) {

    statusText.textContent =
        message;


    statusText.style.color =
        "#D32F2F";


    productText.textContent =
        productCode;


    productText.style.color =
        "#D32F2F";


    if (
        message === "WAREHOUSE FULL"
    ) {

        locationText.textContent =
            "NO AVAILABLE STORAGE";

    }

    else if (
        message === "PRODUCT NOT FOUND"
    ) {

        locationText.textContent =
            "PRODUCT NOT AVAILABLE";

    }

    else {

        locationText.textContent =
            "PRODUCT CODE NOT RECOGNIZED";

    }


    locationText.style.color =
        "#D32F2F";

}


// =========================================================
// SERVER ERROR
// =========================================================

function serverError(error) {

    console.error(error);


    statusText.textContent =
        "SERVER ERROR";


    statusText.style.color =
        "#D32F2F";


    locationText.textContent =
        "Cannot connect to warehouse server";


    locationText.style.color =
        "#D32F2F";

}


// =========================================================
// BARCODE ENTER
// =========================================================

barcodeInput.addEventListener(
    "keydown",
    async function (event) {

        if (event.key === "Enter") {

            event.preventDefault();

            await processBarcode();

        }

    }
);


// =========================================================
// SHORTCUTS
// =========================================================

document.addEventListener(
    "keydown",
    function (event) {

        // F1 = STORE

        if (event.key === "F1") {

            event.preventDefault();

            setInMode();

        }


        // F2 = TAKE

        if (event.key === "F2") {

            event.preventDefault();

            setOutMode();

        }

    }
);


// =========================================================
// KEEP SCANNER FOCUSED
// =========================================================

document.addEventListener(
    "click",
    function () {

        barcodeInput.focus();

    }
);


// =========================================================
// START APPLICATION
// =========================================================

async function initializeApplication() {

    await loadWarehouse();

    setInMode();

    barcodeInput.focus();

}


initializeApplication();