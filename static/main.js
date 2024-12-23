document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const menButton = document.querySelector("#men-catalog-button");
    const womenButton = document.querySelector("#women-catalog-button");
    const bothButton = document.querySelector("#both-catalog-button");
    const mainPage = document.querySelector("#main-division");
    const womenPage = document.querySelector("#main-division-women");
    const addToCartButtons = document.querySelectorAll(".add-to-cart-item-page");

    // Local Storage Functions
    function saveRecentlyViewedItem(itemId) {
        let recentItems = (localStorage.getItem('recentlyViewed') || '').split(',').filter(Boolean);
        if (recentItems.includes(itemId)) {
            recentItems = recentItems.filter(id => id !== itemId);
        }
        recentItems.push(itemId);
        if (recentItems.length > 5) {
            recentItems.shift();
        }
        localStorage.setItem('recentlyViewed', recentItems.join(','));
    }

    // Utility Functions
    function scrollToTop() {
        window.scrollTo({
            top: 0,
            left: 0,
            behavior: "smooth"
        });
    }

    function setupSortButtons(items, displayItems) {
        const sortLowToHighButton = document.getElementById("ltohButton");
        const sortHighToLowButton = document.getElementById("htolButton");

        sortLowToHighButton.addEventListener("click", () => {
            displayItems(items.sort((a, b) => a.price - b.price));
            console.log("sorting");
        });
        
        sortHighToLowButton.addEventListener("click", () => {
            displayItems(items.sort((a, b) => b.price - a.price));
            console.log("sorting");
        });
    }

    function createDisplayItemsFunction(itemsContainer) {
        return function displayItems(sortedItems) {
            itemsContainer.innerHTML = '';
            sortedItems.forEach(item => {
                itemsContainer.innerHTML += `
                    <a class="item" href="/item/${item.id}" id="item${item.id}">
                        <img src="${item.image_path}" alt="">
                        <span class="name">${item.name}</span>
                        <span class="price">${item.price}$</span>
                        <button id="addTo-cart${item.id}" class="add-to-cart-button">Add to cart</button>
                    </a>
                `;
            });

            const itemsToClick = document.querySelectorAll(".item");
            itemsToClick.forEach((item) => {
                item.addEventListener("click", (e) => {
                    e.preventDefault();
                    const itemId = item.id.replace('item', '');
                    saveRecentlyViewedItem(itemId);
                    window.location.href = `/item/${itemId}`;
                    console.log(window.localStorage);
                });
            });
        }
    }

    // Catalog Display Functions
    function setupCatalogDisplay(type) {
            mainPage.style.display = "none";
            womenPage.style.display = "flex";
            scrollToTop();

            const itemsContainer = document.querySelector(".main-division-bottom-part");
            itemsContainer.innerHTML = '';

            fetch(`/getitems/${type}`)
                .then(res => res.json())
                .then(items => {
                    document.querySelector("#items_type").innerText = type.toUpperCase();
                    const displayItems = createDisplayItemsFunction(itemsContainer);
                    setupSortButtons(items, displayItems);
                    displayItems(items);
                });
        
    }

    function handleOtherPaths(type) {
        // Return the event handler function instead of executing it
        return function(e) {
            e.preventDefault();
            if (window.location.pathname !== "/") {
                window.localStorage.setItem("showItems", type);
                window.location.href = "/";
            } else {
                setupCatalogDisplay(type);
            }
        };
    }
    
    // Move localStorage check into a function that runs when the page loads
    function checkStoredHandler() {
        const handler = localStorage.getItem("showItems");
        if (handler) {
            setupCatalogDisplay(handler);
            localStorage.removeItem("showItems");
        }
    }
    // Event Listeners
    womenButton.addEventListener("click", handleOtherPaths('female'));
    menButton.addEventListener("click", handleOtherPaths('male'));
    bothButton.addEventListener("click", handleOtherPaths('both'));
    checkStoredHandler()
    // Add to Cart Functionality
    addToCartButtons.forEach((button) => {
        button.addEventListener("click", (e) => {
            e.preventDefault();
            let itemId = e.target.id;
            fetch(`/addtocart/${itemId}`)
                .then(res => res.json())
                .then(final => {
                    const errorItemPage = document.querySelector("#error-item-page");
                    if (final[0].error) {
                        errorItemPage.innerText = final[0].error;
                        errorItemPage.style.display = "block";
                    } else {
                        errorItemPage.style.color = "#00ff00";
                        errorItemPage.style.display = "block";
                        errorItemPage.innerText = "Added successfully";
                    }
                });
        });
    });
});