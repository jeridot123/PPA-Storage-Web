let selectedProduct = null;

const barcode = document.getElementById("barcode");
const searchButton = document.getElementById("searchButton");
const takeButton = document.getElementById("takeButton");

const resultProduct = document.getElementById("resultProduct");
const resultLine = document.getElementById("resultLine");
const resultPosition = document.getElementById("resultPosition");
const resultStatus = document.getElementById("resultStatus");

// =======================================
// SEARCH PRODUCT
// =======================================

async function searchProduct(){

    const product = barcode.value.trim().toUpperCase();

    if(product === "") return;

    resultStatus.textContent = "Searching...";

    try{

        const response = await fetch("/api/warehouse");

        const data = await response.json();

        let found = null;

        for(const line of data.lines){

            for(const item of line.items){

                if(item.product_code === product){

                    found = {
                        product_code: item.product_code,
                        line: line.line_id,
                        position: item.position
                    };

                    break;

                }

            }

            if(found) break;

        }

        if(found){

            selectedProduct = found;

            resultProduct.textContent = found.product_code;
            resultLine.textContent = found.line;
            resultPosition.textContent = found.position;
            resultStatus.textContent = "Ready to Take";

            takeButton.disabled = false;

        }
        else{

            selectedProduct = null;

            resultProduct.textContent = "-";
            resultLine.textContent = "-";
            resultPosition.textContent = "-";
            resultStatus.textContent = "Product Not Found";

            takeButton.disabled = true;

        }

    }

    catch(error){

        console.error(error);

        resultStatus.textContent = "Connection Error";

    }

}

// =======================================
// TAKE PRODUCT
// =======================================

async function takeProduct(){

    if(!selectedProduct) return;

    try{

        const response = await fetch("/api/take",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                product_code:selectedProduct.product_code
            })

        });

        const result = await response.json();

        if(result.success){

            resultStatus.textContent = "✓ Product Taken";

            barcode.value = "";

            takeButton.disabled = true;

            selectedProduct = null;

            resultProduct.textContent="-";
            resultLine.textContent="-";
            resultPosition.textContent="-";

            barcode.focus();

        }
        else{

            resultStatus.textContent = result.message;

        }

    }

    catch(error){

        console.error(error);

        resultStatus.textContent = "Connection Error";

    }

}

// =======================================

searchButton.addEventListener("click", searchProduct);

takeButton.addEventListener("click", takeProduct);

barcode.addEventListener("keydown",(e)=>{

    if(e.key==="Enter"){

        if(takeButton.disabled){

            searchProduct();

        }else{

            takeProduct();

        }

    }

});