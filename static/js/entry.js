const barcodeInput = document.getElementById("barcode");
const storeButton = document.getElementById("storeButton");

const resultProduct = document.getElementById("resultProduct");
const resultLine = document.getElementById("resultLine");
const resultPosition = document.getElementById("resultPosition");
const resultStatus = document.getElementById("resultStatus");

async function storeProduct() {

    const product = barcodeInput.value.trim();

    if (product === "") return;

    try {

        const response = await fetch("/api/store", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                product_code: product
            })

        });

        const data = await response.json();

        if (data.success) {

            resultProduct.textContent = data.product_code;
            resultLine.textContent = data.line;
            resultPosition.textContent = data.position;
            resultStatus.textContent = "✓ Successfully Stored";

        } else {

            resultProduct.textContent = "-";
            resultLine.textContent = "-";
            resultPosition.textContent = "-";
            resultStatus.textContent = data.message;

        }

    } catch {

        resultStatus.textContent = "Connection Error";

    }

    barcodeInput.value = "";
    barcodeInput.focus();

}

storeButton.addEventListener("click", storeProduct);

barcodeInput.addEventListener("keydown", function(e){

    if(e.key === "Enter"){

        storeProduct();

    }

});