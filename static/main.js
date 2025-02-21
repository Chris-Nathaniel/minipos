document.addEventListener('DOMContentLoaded', function() {
    const cartButtons = document.querySelectorAll('.menu-card');

    cartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.closest('.menu-card').querySelector('.add-to-cart').getAttribute('data-item-id');
            const itemName = this.closest('.menu-card').querySelector('.add-to-cart').getAttribute('data-item-name');
            const itemQuantity = this.closest('.menu-card').querySelector('.add-to-cart').getAttribute('data-item-quantity');
            const itemPrice = this.closest('.menu-card').querySelector('.add-to-cart').getAttribute('data-item-price');
            const itemImage = this.closest('.menu-card').querySelector('.add-to-cart').getAttribute('data-item-image');

            // Call the function to add the item to the cart
            addToCart(itemId, itemName, itemQuantity, itemPrice, itemImage);
            console.log(itemId, itemName, itemQuantity, itemPrice, itemImage);
        });
    });
});

function addToCart(itemId, itemName, itemQuantty, itemPrice, itemImage) {
    fetch('/add_to_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            item_id: itemId,
            item_name: itemName,
            item_quantity: itemQuantty,
            item_price: itemPrice,
            item_image: itemImage
    
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
        console.log(data.tax)
        updateCartUI(data.cart, data.total, data.tax, data.cashPaid, data.voucher);
        updateCartCount(data.itemCount);
    })
    .catch(error => console.error('Error:', error));
}

function removeFromCart(itemId, itemName, itemPrice, itemImage, itemQuantity, itemTotal, orderTime) {
    fetch('/remove_from_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            item_id : itemId,
            item_image: itemImage,
            item_name: itemName,
            item_price: itemPrice,
            item_quantity: itemQuantity,
            total: itemTotal,
            ordertime: orderTime
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
        updateCartUI(data.cart, data.total, data.tax, data.cashPaid, data.voucher);
        updateCartCount(data.itemCount);
    })
    .catch(error => console.error('Error:', error));
}

function updateCartCount(count) {
    const counterElement = document.querySelector('.shoppingCart .counter');
    if (counterElement) {
        counterElement.textContent = count;
    }
}

// Function to update the cart
function updateCartUI(cartItems, cartTotal, cartTax, cashPaid, voucher) {
    const cartItemsContainer = document.getElementById('cart-items');
    const cartTotalContainer = document.getElementById('cart-total');
    const cartOtherContainer = document.getElementById('cart-other');
    const editOrder = document.querySelector('.cart-menu').getAttribute('data-edit-order');
    const discountDiv = document.querySelector('.discount');

    cartItemsContainer.innerHTML = '';
    cartTotalContainer.innerHTML = '';
    cartOtherContainer.innerHTML = '';
    if (discountDiv) {
        discountDiv.innerHTML = " ";
    } else {
        console.warn("Element with class 'discount' not found.");
    }

    if (cashPaid != 0) {
        document.querySelector('.change').innerHTML = formatCurrency(parseCurrency(cashPaid) - parseInt(cartTotal.replace(/,/g, ''), 10));
    }

    // Check if cart is empty
    if (cartItems.length === 0) {
        // Append "Cart is empty" message
        const emptyCartMessage = document.createElement('div');
        emptyCartMessage.className = "d-flex justify-content-center align-items-center";
        emptyCartMessage.style.height = "100vh";
        emptyCartMessage.style.width = "auto";
        emptyCartMessage.style.padding = "5px";
        emptyCartMessage.style.border = "1px solid var(--lg)";
        emptyCartMessage.innerHTML = `
            <img src="/static/images/sadcat.png" style="width:100px; align-self: center;">
            <p class="text-center lead">Cart is empty..</p>
        `;
        cartItemsContainer.appendChild(emptyCartMessage);
    } else {
        // Separate orders into previous and additional orders
        const previousOrders = cartItems.filter(item => item.order_time);
        const additionalOrders = cartItems.filter(item => !item.order_time);

        // Function to create cart item elements
        function createCartItem(item) {
            const cartItem = document.createElement('div');
            cartItem.className = "list-group-item d-flex justify-content-between align-items-center";

            const listImg = document.createElement('div');
            listImg.className = "listimg";
            listImg.innerHTML = `<img src="${item.item_image}" alt="Item ${item.item_id}" class="img-thumbnail" style="width: 70px;">`;

            const listName = document.createElement('div');
            listName.className = "listname";
            listName.innerHTML = `<span class="mx-0">${item.item_name}</span>`;

            const listQuantity = document.createElement('div');
            listQuantity.className = "listquantity";
            listQuantity.innerHTML = `<span class="mx-0"> x ${item.item_quantity} </span>`;

            const listTotal = document.createElement('div');
            listTotal.className = "listtotal";
            listTotal.innerHTML = `<span class="mx-0">Rp ${item.total}</span>`;

            const listButton = document.createElement('div');
            listButton.className = "listbutton";

            // Create the remove button
            const removeButton = document.createElement('button');
            removeButton.className = "btn btn-sm remove-from-cart";
            removeButton.setAttribute('data-item-id', item.item_id);
            removeButton.setAttribute('data-item-image', item.item_image);
            removeButton.setAttribute('data-item-name', item.item_name);
            removeButton.setAttribute('data-item-price', item.item_price);
            removeButton.setAttribute('data-item-quantity', item.item_quantity);
            removeButton.setAttribute('data-item-total', item.total);
            removeButton.setAttribute('data-item-ordertime', item.order_time);
            removeButton.innerHTML = `<img src="static/icons/Cross.png" alt="Remove" style="width: 18px; height: 18px;"/>`;

            // Attach click event listener to the remove button
            removeButton.addEventListener('click', function(event) {
                event.preventDefault();
                const itemId = this.getAttribute('data-item-id');
                const itemImage = this.getAttribute('data-item-image');
                const itemName = this.getAttribute('data-item-name');
                const itemPrice = this.getAttribute('data-item-price');
                const itemQuantity = this.getAttribute('data-item-quantity');
                const itemTotal = this.getAttribute('data-item-total');
                const orderTime = this.getAttribute('data-item-ordertime');
                console.log(itemId, itemName, itemPrice, itemImage, itemQuantity, itemTotal);
                removeFromCart(itemId, itemName, itemPrice, itemImage, itemQuantity, itemTotal, orderTime);
            });

            listButton.appendChild(removeButton);

            // Append the elements to the cartItem
            cartItem.appendChild(listImg);
            cartItem.appendChild(listName);
            cartItem.appendChild(listQuantity);
            cartItem.appendChild(listTotal);
            cartItem.appendChild(listButton);

            return cartItem;
        }

        // Append previous orders
        if (previousOrders.length > 0) {
            const previousOrdersTitle = document.createElement('h5');
            previousOrdersTitle.innerText = 'Previous orders';
            cartItemsContainer.appendChild(previousOrdersTitle);
            previousOrders.forEach(item => cartItemsContainer.appendChild(createCartItem(item)));
        }

        // Append additional orders
        if (additionalOrders.length > 0) {
            if (editOrder){
                const additionalOrdersTitle = document.createElement('h5');
                additionalOrdersTitle.className = 'mt-4';
                additionalOrdersTitle.innerText = 'Additional orders';
                cartItemsContainer.appendChild(additionalOrdersTitle);

            }
            additionalOrders.forEach(item => cartItemsContainer.appendChild(createCartItem(item)));
        }
    }

    // Update cart other
    const otherItem = document.createElement('div');
    otherItem.innerHTML = `
                <div class="row">
                    <div class="col-12 d-flex justify-content-end align-items-end">
                        <div class="col d-flex justify-content-end align-items-end">
                            <span class="mx-2">Discount:</span>
                        </div>
                        <div class="col-md-4 d-flex justify-content-end align-items-end">
                            <span class="mx-2">${voucher.discount? voucher.discount + '%': 0}</span>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-12 d-flex justify-content-end align-items-end">
                        <div class="col d-flex justify-content-end align-items-end">
                            <span class="mx-2 mt-1">Tax:</span>
                        </div>
                        <div class="col-md-4 d-flex justify-content-end align-items-end">
                            <span class="mx-2 mt-1">${cartTax == 0? '0':formatCurrency(parseInt(cartTax.replace(',','')))}</span>
                        </div>
                    </div>
                </div>
    `;

    cartOtherContainer.appendChild(otherItem);

    // Update cart total
    const totalItem = document.createElement('div');
    totalItem.className = "list-group-item";
    totalItem.innerHTML = `
        <div class="row">
            <div class="d-flex justify-content-end align-items-end">
                <div class="col d-flex justify-content-end align-items-end">
                    <span class="mx-2 mt-1">Grand Total:</span>
                </div>
                <div class="col-md-4 d-flex justify-content-end align-items-end">
                    <span class="cartTotalValue mx-2 mt-1">${cartTotal == 0? '0':formatCurrency(parseInt(cartTotal.replace(',','')))}</span>
                </div>
            </div>
        </div>
    `;
    cartTotalContainer.appendChild(totalItem);


    // Create a new discount item
    const newDiscountSub = document.createElement('div'); // Use a new variable name
    newDiscountSub.className = "list-group-item";
    newDiscountSub.innerHTML = `
        <label class="text-hover" style="cursor: pointer;" onclick="showDiscount()">Discount</label>
    `;
    
    
    // Append the new discount item
    if (voucher){
        discountVouchers = createVoucherItem(voucher)
        discountDiv.appendChild(discountVouchers)
    } else{
        discountDiv.appendChild(newDiscountSub);
    }

}

function createVoucherItem(voucherDetail) {
    const listItem = document.createElement("div");
    listItem.classList.add("list-group-item");

    const offerItem = document.createElement("div");
    offerItem.classList.add("offer-item", "border-0");

    const img = document.createElement("img");
    img.src = voucherDetail.image;
    img.alt = "Discount Icon";

    const offerDetails = document.createElement("div");
    offerDetails.classList.add("offer-details");

    const title = document.createElement("div");
    title.classList.add("title");
    title.textContent = `${voucherDetail.title} | ${voucherDetail.discount}% off`;

    const voucher = document.createElement("div");
    voucher.classList.add("Voucher");
    voucher.textContent = `Voucher: ${voucherDetail.voucher}`;

    const removeBtn = document.createElement("button");
    removeBtn.classList.add("btn", "btn-sm", "remove-discount");
    removeBtn.innerHTML = "<span>Remove</span>";
    removeBtn.addEventListener("click", (event) => {
        listItem.remove();
        event.preventDefault();
        fetch("/removeDiscount", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
        })
        .then(response => response.json())
        .then(data => {
            console.log("Discount removed successfully:", data);

            const discountDiv = document.querySelector(".discount");
            discountDiv.innerHTML = `
                <div class="list-group-item">
                    <label class="text-hover" style="cursor: pointer;" onclick="showDiscount()">Discount</label>
                </div>
            `;
            updateDiscountDisplay(0, data.originalTotal);
        })
        .catch(error => {
            console.error("Error removing discount:", error);
            alert("Failed to remove the discount. Please try again.");
        }); 
    });
    function updateDiscountDisplay(discount, total) {
        const discountDisplay = document.querySelector(".row .col-md-4 span");
        const cartTotal = document.querySelector(".cartTotalValue");
        if (discountDisplay) discountDisplay.textContent = discount + "%";
        if (cartTotal) cartTotal.textContent = formatCurrency(total);
    }

    offerDetails.appendChild(title);
    offerDetails.appendChild(voucher);
    offerItem.appendChild(img);
    offerItem.appendChild(offerDetails);
    offerItem.appendChild(removeBtn);
    listItem.appendChild(offerItem);

    return listItem;
}

function addCashPaid(cashPaid){
    fetch('/add_cash_paid', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
},
    body: JSON.stringify({cashPaid: cashPaid})
    }).then(response => response.json())
    .then(data =>{
        console.log(data.message);
    })

}

document.addEventListener('DOMContentLoaded', function() {
    const removeButton = document.querySelectorAll('.remove-from-cart')
    
    removeButton.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const itemId = this.getAttribute('data-item-id');
            const itemImage = this.getAttribute('data-item-image');
            const itemName = this.getAttribute('data-item-name');
            const itemPrice = this.getAttribute('data-item-price');
            const itemQuantity = this.getAttribute('data-item-quantity');
            const itemTotal = this.getAttribute('data-item-total');
            const orderTime = this.getAttribute('data-item-ordertime')

            // Call the function to add the item to the cart
            console.log(itemName,  itemPrice, itemImage);
            removeFromCart(itemId, itemName, itemPrice, itemImage, itemQuantity, itemTotal, orderTime)

        });
    });
    
});


document.addEventListener("DOMContentLoaded", function() {
    // Get all view buttons
    const viewButtons = document.querySelectorAll('.view-button');
    const printOrder = document.querySelectorAll('.print-order');
    // Add click event listeners to each button
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get the order number from the data attribute
            const orderNumber = this.getAttribute('data-order');

            retrieveOrderDetails(orderNumber,'view');
        });
    });
    printOrder.forEach(button => {
        button.addEventListener('click', function() {
            // Get the order number from the data attribute
            const orderNumber = this.getAttribute('data-order');

            retrieveOrderDetails(orderNumber,'view');
            retrieveOrderDetails(orderNumber,'view', "hidden");
            setTimeout(()=>{printTheReceipt()}, 500);
        });
    });
});

document.addEventListener("DOMContentLoaded", function() {
    // Get all view buttons
    const viewButtons = document.querySelectorAll('.receipt-button');
    const printReceipt = document.querySelectorAll('.print-receipt');
    // Add click event listeners to each button
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get the order number from the data attribute
            const orderNumber = this.getAttribute('data-order');

            retrieveOrderDetails(orderNumber,'receipt');
        });
    });
    printReceipt.forEach(button => {
        button.addEventListener('click', function() {
            // Get the order number from the data attribute
            const orderNumber = this.getAttribute('data-order');

            retrieveOrderDetails(orderNumber,'receipt', "hidden");
            setTimeout(()=>{printTheReceipt()}, 500);
        });
    });
});


function retrieveOrderDetails(orderNumber, actionType, display="show") {
    fetch('/retrieve_details', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            order_number: orderNumber
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
        console.log(data.items)
        console.log(data.number)
        console.log(document.title)
        if (document.title =='thankyou')
            updateDetails2(data.items, data.number);
        else{
            updateDetails(data.items, data.number, actionType, display);
        }

    })
    .catch(error => console.error('Error:', error));
}

function updateDetails2(orderItems, orderNumber){
    const result = document.querySelector('.data');
    let orderDetailsHTML = `
                <div class="d-flex justify-content-center py-5">
                    <div class="card mb-3" style="width: 100%; max-width: 350px; font-family: monospace; border: 1px dashed #000;">
                        <div class="card-header text-center" style="border-bottom: 1px dashed #000; font-size: 10px;">
                            <h5 class="mb-0">${orderItems[0].payment_method?'Mini Cafe':'Temporary Invoice'}</h5>
                            ${orderItems[0].payment_method ? `
                                <p>Jl. Kembang Harum XI xy-2</p>
                                <p>Phone: 1234567890</p>
                                <p>Jakarta Barat</p>
                            ` : ''}
                        </div>
                        <div class="card-body p-2" style="text-align:left; font-size: 11px;">
                            <p class="mb-0">Order #${orderNumber}</p>
                            <p class="mb-0">Invoice Number: ${orderItems[0].invoice_number}</p>
                            <hr style="border-top: 1px dashed #000; margin-bottom:3px; margin-top: 4px;">

                            <div class="detailWrapper" style="display:flex; flex-direction:row; padding: 5px 5px;">
                                <div class="col" style="max-width:100%; text-align:left; font-size: 11px;">
                                    <p class="mb-1">Items</p>
                                    ${orderItems.map((order, i) => `
                                        <p style="margin-bottom:2px;">${i+1}.${order.item_name}</p>
                                        <small style="position:relative; top:-8px; text-align:left">${formatCurrency(order.price)}/pcs x ${order.quantity}</small>
                                    `).join('')}
                                    <p class="mt-2 mb-0">Tax:</p>
                                    <p class="mt-0 mb-0">Payment method:</p>
                                    <p class="mt-0 mb-0">Paid amount:</p>
                                    <p class="mt-0 mb-0">Change:</p>
                                    <p class="mt-0 mb-0">Discount:</p>
                                    <p class="mt-0 mb-0">Grand Total:</p>
                                </div>
                                <div class="col" style="max-width:30%; text-align:end; font-size: 11px;">
                                    <p class="mb-1">Total</p>
                                    ${orderItems.map(order => `
                                        <p style="margin-bottom:23px;">${formatCurrency(order.total)}</p>
                                    `).join('')}
                                    <hr style="margin-bottom: 5px;">
                                    <p class="mb-0">${formatCurrency(orderItems.reduce((sum, order) => sum + order.total, 0)*0.10)}</p>
                                    <p class="mb-0">${orderItems[0].payment_method?orderItems[0].payment_method:"-"}</p>
                                    <p class="mb-0">${orderItems[0].payment_method?formatCurrency(orderItems[0].payment_amount): "-"}</p>
                                    <p class="mb-0">${orderItems[0].payment_method?formatCurrency(orderItems[0].change): "-"}</p>
                                    <p class="mb-0">${orderItems[0].discount}%</p>
                                    <p class="mb-0">${formatCurrency(orderItems[0].total_amount)}</p>
                                </div>
                            </div>
                        </div>
                        <hr style="border-top: 1px dashed #000; margin-bottom:5px;">
                        <small class="mb-0 text-center d-block">Thank you, please come again!</small>
                    </div>
                </div>

        `;
    result.innerHTML = orderDetailsHTML
}

function updateDetails(orderItems, orderNumber, actionType, display){
    const tbody = document.querySelector('tbody');
    var rows = Array.from(document.querySelectorAll('.orderitem'));
    const storedDataItem = localStorage.getItem('data-item');
    const prevActionType = localStorage.getItem('actionType');
    try {
        const element = document.getElementById(`collapseOrder${storedDataItem}`);
        const currentElement = document.getElementById(`collapseOrder${orderNumber}`)
        // close the selected element
        if (element && currentElement && prevActionType == actionType && display == "show"){
            element.remove();
        // open the selected element and close the previous element if exist
        }else if (element){
            element.remove()
            if (actionType == "receipt"){
                createReceipt(orderItems, orderNumber, tbody, rows, actionType, display);
            }else{
                createOrderDetails(orderItems, orderNumber, tbody, rows, actionType, display);
            }

        // open the selected element
        }else{
            if (actionType == "receipt"){
                createReceipt(orderItems, orderNumber, tbody, rows, actionType, display);
            }else{
                createOrderDetails(orderItems, orderNumber, tbody, rows, actionType, display);
            }
        }

    } catch (error) {
        console.error("Element not found or another error occurred:", error);
    }

}

function createReceipt(orderItems, orderNumber, tbody, rows, actionType, display){
    rows.forEach((row) => {
        const selectedRow = row.getAttribute('data-item');
        const collapseRow = document.createElement('tr');
        if (display == "hidden"){
            collapseRow.className = 'order-details-row theReceipt d-none';
        }else{
            collapseRow.className = 'order-details-row theReceipt';
        }
        collapseRow.id = `collapseOrder${orderNumber}`;
        let orderDetailsHTML = `
            <td colspan="6">
                <div class="d-flex justify-content-center">
                    <div class="card mb-3" style="width: 100%; max-width: 350px; font-family: monospace; border: 1px dashed #000;">
                        <div class="card-header text-center" style="border-bottom: 1px dashed #000; font-size: 10px;">
                            <h5 class="mb-0">${orderItems[0].payment_method?'Mini Cafe':'Temporary Invoice'}</h5>
                            ${orderItems[0].payment_method ? `
                                <p>Jl. Kembang Harum XI xy-2</p>
                                <p>Phone: 1234567890</p>
                                <p>Jakarta Barat</p>
                            ` : ''}
                        </div>
                        <div class="card-body p-2" style="text-align:left; font-size: 11px;">
                            <p class="mb-0">Order #${orderNumber}</p>
                            <p class="mb-0">Invoice Number: ${orderItems[0].invoice_number}</p>
                            <hr style="border-top: 1px dashed #000; margin-bottom:3px; margin-top: 4px;">

                            <div class="detailWrapper" style="display:flex; flex-direction:row; padding: 5px 5px;">
                                <div class="col" style="max-width:100%; text-align:left; font-size: 11px;">
                                    <p class="mb-1">Items</p>
                                    ${orderItems.map((order, i) => `
                                        <p style="margin-bottom:2px;">${i+1}.${order.item_name}</p>
                                        <small style="position:relative; top:-8px; text-align:left">${formatCurrency(order.price)}/pcs x ${order.quantity}</small>
                                    `).join('')}
                                    <p class="mt-2 mb-0">Tax:</p>
                                    <p class="mt-0 mb-0">Payment method:</p>
                                    <p class="mt-0 mb-0">Paid amount:</p>
                                    <p class="mt-0 mb-0">Change:</p>
                                    <p class="mt-0 mb-0">Discount:</p>
                                    <p class="mt-0 mb-0">Grand Total:</p>
                                </div>
                                <div class="col" style="max-width:30%; text-align:end; font-size: 11px;">
                                    <p class="mb-1">Total</p>
                                    ${orderItems.map(order => `
                                        <p style="margin-bottom:23px;">${formatCurrency(order.total)}</p>
                                    `).join('')}
                                    <hr style="margin-bottom: 5px;">
                                    <p class="mb-0">${formatCurrency(orderItems.reduce((sum, order) => sum + order.total, 0)*0.10)}</p>
                                    <p class="mb-0">${orderItems[0].payment_method?orderItems[0].payment_method:"-"}</p>
                                    <p class="mb-0">${orderItems[0].payment_method?formatCurrency(orderItems[0].payment_amount): "-"}</p>
                                    <p class="mb-0">${orderItems[0].payment_method?formatCurrency(orderItems[0].change): "-"}</p>
                                    <p class="mb-0">${orderItems[0].discount}%</p>
                                    <p class="mb-0">${formatCurrency(orderItems[0].total_amount)}</p>
                                </div>
                            </div>
                        </div>
                        <hr style="border-top: 1px dashed #000; margin-bottom:5px;">
                        <small class="mb-0 text-center d-block">Thank you, please come again!</small>
                    </div>
                </div>
            </td>
        `;

        collapseRow.innerHTML = orderDetailsHTML;


        if (selectedRow == orderNumber) {
            tbody.insertBefore(collapseRow, row.nextSibling);
            localStorage.setItem('data-item', selectedRow);
            localStorage.setItem('actionType', actionType);
            return 0;
        }

    });
}

function createOrderDetails(orderItems, orderNumber, tbody, rows, actionType, display){
    rows.forEach((row) => {
        const selectedRow = row.getAttribute('data-item');
        const collapseRow = document.createElement('tr');
        if (display == "hidden"){
            collapseRow.className = 'order-details-row  d-none';
        }else{
            collapseRow.className = 'order-details-row';
        }
        collapseRow.id = `collapseOrder${orderNumber}`;

        let orderDetailsHTML = `
            <td colspan="6">
                <div class="d-flex justify-content-center">
                    <div class="card mb-3" style="width: 100%; max-width: 400px; font-family: monospace; border: 1px dashed #000;">
                        <div class="card-header text-center" style="border-bottom: 1px dashed #000;">
                            <h5 class="mb-0">Order Summary</h5>
                        </div>
                        <div class="card-body p-3" style="text-align:left;">
                            <p class="mb-2">Order #${orderNumber}</p>
                            <hr style="border-top: 1px dashed #000; margin-bottom:3px;">

                            <div class="detailWrapper" style="display:flex; flex-direction:row; padding: 5px 5px;">
                                <div class="col" style="max-width:100%; text-align:left">
                                    <p>Items</p>
                                    ${orderItems.map((order, i) => `
                                        <p style="margin-bottom:2px;">${i+1}.${order.item_name} <small>x ${order.quantity}</small></p>

                                    `).join('')}
                                </div>
                            </div>
                        </div>
                        <hr style="border-top: 1px dashed #000;">
                        <small class="mb-0 text-center d-block">This is not a receipt!</small>
                    </div>
                </div>
            </td>
        `;

        collapseRow.innerHTML = orderDetailsHTML;


        if (selectedRow == orderNumber) {
            tbody.insertBefore(collapseRow, row.nextSibling);
            localStorage.setItem('data-item', selectedRow);
            localStorage.setItem('actionType', actionType);
            return 0;
        }
    });

}

function formatCurrency(amount) {
    return amount.toLocaleString('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).replace(/\./g, ',');
}

function parseCurrency(currencyStr) {
    let numberStr = currencyStr.replace(/[^\d]/g, '');

    return parseInt(numberStr, 10);
}

function printTheReceipt(){
    // Locate the dynamically injected order details row
    const orderDetailsRow = document.querySelector('.order-details-row');
    const data = document.querySelector('.data')

    if (orderDetailsRow || data) {
        // Open a new window
        const printWindow = window.open('', 'Print', 'width=600,height=600');

        // Write the HTML for the new window, including the necessary styles
        printWindow.document.write(`
            <html>
            <head>
                <title>Print Order</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>POS System Cafe</title>
                <link href="/static/styles.css" rel="stylesheet">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
                <style>
                    /* Include necessary styles here or link to your CSS */
                    body { font-family: Arial, sans-serif; display:flex; justify-content:center;}
                    table {width: 280px;}
                </style>
            </head>
            <body>
                <div class="container mt-0 mx-0 py-5">
                    ${data?data.innerHTML:""}
                    <div class="orderstable table-responsive">
                        <table table order-table>
                            <tbody>
                                ${orderDetailsRow?orderDetailsRow.innerHTML:""}
                            </tbody>
                        </table>
                    </div>
                </div>
            </body>
            </html>
        `);

        // Trigger print
        printWindow.document.close();
        printWindow.focus();
        printWindow.print();

    } else {
        alert('No order details found to print!');
    }


}

function showDiscount(){
    var myModal = new bootstrap.Modal(document.getElementById('discountSelection'));
    myModal.show();
}

function payment(){
    showpayment();
    showModal();
    paymentSubmission();
};

document.addEventListener("DOMContentLoaded", function(){
    var check = localStorage.getItem('form-check');
    var cashAmount = document.querySelector('.cash_payment').textContent;
    if (check === 'open' && cashAmount != 0) {
        showpayment();
        showModal();
        paymentSubmission();
    }
});

function showpayment(){
    var paymethod = document.querySelectorAll(".form-check");
    localStorage.setItem('form-check', 'open');
    if (typeof paymentOpen == 'undefined'){
        paymentOpen = false;
    }
    if (paymentOpen == false){
        paymethod.forEach(method=>{
            method.classList.remove('d-none');
            paymentOpen = true;
        })
    }else{
        paymethod.forEach(method=>{
            method.classList.add('d-none');
            paymentOpen = false;
        })
    }
}

function showModal(){
    document.getElementById('cash').addEventListener('click', function() {
        if (this.checked) {
            var myModal = new bootstrap.Modal(document.getElementById('paidAmount'));
            myModal.show();
        }
    });
}

function paymentSubmission(){
    document.getElementById('cashAmountForm').addEventListener('submit', function(event) {
        event.preventDefault();
        var cashAmount = parseInt(document.getElementById('cashAmount').value);
        var formatted_cashAmount = formatCurrency(parseInt(cashAmount));
        var totalValue = parseCurrency(document.querySelector("#cart-total .list-group-item .row .col-md-4 span").textContent.trim());
        var change = formatCurrency(cashAmount - totalValue);
        var paymentMethodSelection = document.querySelector('.form-check');
        var cashInput = paymentMethodSelection.querySelector('input[name="cashValue"]');

        // Set the HTML of the "Paid Amount" span to the input value
        document.querySelector('.cash_payment').innerHTML = formatted_cashAmount;
        document.querySelector('.change').innerHTML = change;
        cashInput.value = cashAmount;
        addCashPaid(formatted_cashAmount);

        // Close the modal
        bootstrap.Modal.getInstance(document.getElementById('paidAmount')).hide();
    });
}


function confirm_changes(){
    const confirmSaveButton = document.getElementById('confirmSaveButton');
    var myModal = new bootstrap.Modal(document.getElementById('saveChangesModal'));
    myModal.show();

    document.getElementById('saveChangesButton').setAttribute('form','editForm');

     // Handle the confirmation button click
    confirmSaveButton.addEventListener('click', function() {
        // Submit the form
        form.submit();
    });
}

document.addEventListener('DOMContentLoaded', function(){
    const saveChangesButton = document.querySelector('.confirm-changes');
    const confirmSaveButton = document.getElementById('confirmSaveButton');
    saveChangesButton.addEventListener('click', function(event){
        event.preventDefault()
        var myModal = new bootstrap.Modal(document.getElementById('saveChangesModal'));
        myModal.show();

    })
     // Handle the confirmation button click
     confirmSaveButton.addEventListener('click', function() {
        // Submit the form
        form.submit();
    });

})


window.onload = function() {
    // Get the full text content of the paragraph
    const orderNumberText = document.getElementById('pro-order-number').textContent;

    // Extract the actual order number by trimming and removing the label part
    const orderNumber = orderNumberText.replace('Order ID:', '').trim();
    console.log('Getting order number...');
    console.log('Order Number:', orderNumber); // Output the order number to console
    startPolling(orderNumber); // Start polling with the extracted order number

};


// Function to start polling for payment status
function startPolling(orderNumber) {
    setInterval(() => checkPaymentStatus(orderNumber), 5000);
    console.log('start polling...');
}


function checkPaymentStatus(orderNumber) {
    fetch(`/payment_status/${orderNumber}`)
        .then(response => response.json())
        .then(data => {
            const status = data.payment_status;
            if (status === 'paid') {
                console.log(`status is:${status}`);
                document.getElementById('payment-process-title').innerText = 'Payment Successful!'
                document.getElementById('payment-status').innerText = 'Payment Successful! Thank you for your order.';
                document.getElementById('message').innerText = 'You will soon be redirected automatically..';
                document.getElementById('proceed').innerText = 'Continue';
                document.querySelector('.loading-animation').classList.add('complete'); // Add complete class
            } else if (status === 'pending') {
                console.log(`status is:${status}`);
                document.getElementById('payment-status').innerText = 'Your payment is still being processed.';
                document.getElementById('message').style.display = 'block'; // Show pending message
                document.querySelector('.loading-animation').classList.remove('complete'); // Remove complete class
            } else {
                console.log(`status is:${status}`);
                document.getElementById('payment-status').innerText = 'Payment Failed or Not Found.';
                document.getElementById('message').style.display = 'block'; // Show error message
                document.querySelector('.loading-animation').classList.remove('complete'); // Remove complete class
            }
        })
        .catch(error => console.error('Error:', error));
}

function toggleForm() {
    const choice = document.getElementById('choice').value;
    const addMenuForm = document.getElementById('addMenuForm');
    const addCategoryForm = document.getElementById('addCategoryForm');
    const editMenuForm = document.getElementById('editMenuForm');
    const rightMenuHeader = document.querySelector('.right-menu-header');
    rightMenuHeader.innerHTML = choice;
    if (choice === 'Add Menu') {
        addMenuForm.classList.remove('d-none');
        addCategoryForm.classList.add('d-none');
        editMenuForm.classList.add('d-none');
    } else if (choice === 'Add Category') {
        addCategoryForm.classList.remove('d-none');
        addMenuForm.classList.add('d-none');
        editMenuForm.classList.add('d-none');
    } else if (choice === 'Edit Menu' ){
        editMenuForm.classList.remove('d-none');
        addMenuForm.classList.add('d-none');
        addCategoryForm.classList.add('d-none');
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const editButtons = document.querySelectorAll('.edit');
    const secondCol = document.querySelector(".secondcol");
    const backButton = document.querySelector(".back-button");

    editButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();

            // Extract the menu item details from the clicked row
            const row = button.closest('tr');
            const id = row.querySelector('.id').textContent.split('ID: ')[1].trim();
            const itemName = row.querySelector('td:nth-child(3)').firstChild.textContent.trim();
            const category = row.querySelector('td:nth-child(4)').textContent.trim();
            const price = parseCurrency(row.querySelector('td:nth-child(5)').textContent);
            const imageUrl = row.querySelector('.card-image img').src;
            const cardImage = document.querySelector('.preview-image');

            cardImage.innerHTML = '';
            // Populate the form fields with the menu item data
            document.getElementById('edit-id').value = id;
            document.getElementById('edit-item-name').value = itemName;
            document.getElementById('edit-category').value = category;
            document.getElementById('edit-price').value = price;
            document.getElementById('current-image').value = imageUrl;
            let imageTag = document.createElement('img');
            imageTag.id = 'image-preview';
            imageTag.src = imageUrl;
            imageTag.alt = 'Current image';
            imageTag.style.maxWidth = '200px';
            imageTag.style.height = 'auto';
            imageTag.style.display = 'block';
            imageTag.style.marginBottom = '10px';

            cardImage.append(imageTag);

            // Set the choice to "Edit Menu" and show the form
            document.getElementById('choice').value = "Edit Menu";
            toggleForm();
            secondCol.classList.toggle('clicked')
            if (backButton){
                backButton.addEventListener('click', () => {
                    secondCol.classList.remove('clicked');
            })};
        });
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const secondCol = document.querySelector(".secondcol");
    const shoppingCart = document.querySelector(".shoppingCart");
    const closeButton = document.querySelector(".close-button-wrapper");
    if (shoppingCart) {
        shoppingCart.addEventListener('click', () => {
            secondCol.classList.toggle('clicked');
            shoppingCart.classList.add('d-none');
        });
    }

    if (closeButton){
        closeButton.addEventListener('click', () => {
            secondCol.classList.toggle('clicked');
            shoppingCart.classList.remove('d-none');
    })};
});

document.addEventListener("DOMContentLoaded", function() {
    const secondCol = document.querySelector(".secondcol");
    const moreMenu = document.querySelector(".moreMenu");
    const backButton = document.querySelector(".back-button");
    if (moreMenu) {
        moreMenu.addEventListener('click', () => {
            secondCol.classList.toggle('clicked');
            moreMenu.classList.add('d-none');
        });
    }

    if (backButton){
        backButton.addEventListener('click', () => {
            secondCol.classList.toggle('clicked');
            moreMenu.classList.remove('d-none');
    })};
});

document.addEventListener("DOMContentLoaded", function () {
    const selectAll = document.getElementById("select-all");
    const deleteButton = document.querySelector(".deleteselected");
    const checkboxes = document.querySelectorAll(".allcheckbox");

    function toggleDeleteButton() {
        const anyChecked = selectAll.checked || Array.from(checkboxes).some(cb => cb.checked);
        deleteButton.classList.toggle("showdeletebutton", anyChecked);
        deleteButton.classList.toggle("hidedeletebutton", !anyChecked);
    }

    selectAll.addEventListener("click", function () {
        checkboxes.forEach(checkbox => checkbox.checked = selectAll.checked);
        toggleDeleteButton();
    });

    checkboxes.forEach(checkbox => checkbox.addEventListener("click", toggleDeleteButton));
});

document.addEventListener("DOMContentLoaded", function(){
    const voucherSearchForm = document.getElementById("voucherSearch")
    voucherSearchForm.addEventListener('submit', function(e){
        e.preventDefault();
        const code = document.getElementById('codeSearch').value;

        fetch('/searchVoucher', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({code: code})
        }).then(response => response.json())
        .then(data =>{
            discountVouchers(data.tickets)
        })

    })
})
function discountVouchers(tickets) {
    const modalBody = document.querySelector("#discountSelection .modal-body");


    // Clear previous content
    const existingOffers = modalBody.querySelectorAll('.offer-item');
    existingOffers.forEach(item => item.remove());

    const existingNoOffers = modalBody.querySelector('.no-offers');
    if (existingNoOffers) {
        existingNoOffers.remove();
    }

    // Add tickets to the modal
    if (tickets.length > 0) {
        tickets.forEach(ticket => {
            const offerItem = document.createElement('div');
            offerItem.classList.add('offer-item');

            offerItem.innerHTML = `
                <img src="${ticket.image}" alt="Discount Icon">
                <div class="offer-details">
                    <div class="title">${ticket.title} | ${ticket.discount}% off</div>
                    <div class="Voucher">Voucher: ${ticket.discount_code}</div>
                    <div class="description">${ticket.description}</div>
                </div>
                <div class="offer-action">+</div>
            `;

            modalBody.appendChild(offerItem);
        });
    } else {
        // Display a message if no tickets are found
        const noOffers = document.createElement('div');
        noOffers.classList.add('no-offers');
        noOffers.textContent = "No discounts found.";
        modalBody.appendChild(noOffers);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    // Select all offer items
    const voucherList = document.querySelectorAll(".modal .offer-item");

    // Add click event listener to each offer item
    voucherList.forEach(item => {
        item.addEventListener("click", function () {
            // Extract the discount value from the data attribute
            const discount = this.querySelector(".title").getAttribute("data-item-discount");
            const title = this.querySelector(".title").getAttribute("data-item-title");
            const image = this.querySelector(".title").getAttribute("data-item-image");
            const voucher = this.querySelector(".title").getAttribute("data-item-voucher");

            // Send the discount value to the server via POST request
            fetch("/addDiscount", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ 
                    discount: discount,
                    title: title,
                    image: image,
                    voucher: voucher
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log("Discount added successfully:", data);
                console.log(formatCurrency(data.discountedTotal));

                const discountDiv = document.querySelector(".discount");
                // Update the discount display
                discountDiv.innerHTML = `
                    <div class="list-group-item">
                        <div class="offer-item border-0">
                            <img src="${image}" alt="Discount Icon">
                            <div class="offer-details">
                                <div class="title">${title} | ${discount}% off</div>
                                <div class="Voucher">Voucher: ${voucher}</div>
                            </div>
                            <button class="btn btn-sm remove-discount">
                                <span>Remove</span>
                            </button>
                        </div>
                    </div>
                `;

                var myModal = document.getElementById('discountSelection');
                var backdrop = document.querySelector('.modal-backdrop.show');
                if (myModal) myModal.classList.remove('show');
                if (backdrop) backdrop.classList.remove('show');
                
                myModal.style.display = 'none';
                backdrop.style.display = 'none';
                
                // Update the discount display in the DOM
                const discountDisplay = document.querySelector(".row .col-md-4 span");
                const cartTotal = document.querySelector('.cartTotalValue');
                if (discountDisplay) {
                    discountDisplay.textContent = discount + "%";
                    cartTotal.textContent = formatCurrency(data.discountedTotal);
                }

                // Attach event listener to the remove button
                removeDiscountListener();
            })
            .catch(error => {
                console.error("Error adding discount:", error);
                alert("Failed to apply the discount. Please try again.");
            });
        });
    });
    removeDiscountListener();
    
});
function updateDiscountDisplay(discount, total) {
    const discountDisplay = document.querySelector(".row .col-md-4 span");
    const cartTotal = document.querySelector(".cartTotalValue");
    if (discountDisplay) discountDisplay.textContent = discount + "%";
    if (cartTotal) cartTotal.textContent = formatCurrency(total);
}
 // Function to attach event listener to remove discount button
function removeDiscountListener() {
    const removeBtn = document.querySelector(".remove-discount");
    if (removeBtn) {
        removeBtn.addEventListener("click", function (event) {
            event.preventDefault(); 

            fetch("/removeDiscount", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            })
            .then(response => response.json())
            .then(data => {
                console.log("Discount removed successfully:", data);

                const discountDiv = document.querySelector(".discount");
                discountDiv.innerHTML = `
                    <div class="list-group-item">
                        <label class="text-hover" style="cursor: pointer;" onclick="showDiscount()">Discount</label>
                    </div>
                `;
                updateDiscountDisplay(0, data.originalTotal);
            })
            .catch(error => {
                console.error("Error removing discount:", error);
                alert("Failed to remove the discount. Please try again.");
            });
        });
    }
}
document.addEventListener("DOMContentLoaded", function() {
    let toastElements = document.querySelectorAll('.toast');
    toastElements.forEach(toast => new bootstrap.Toast(toast, { delay: 3000 }).show());
});


