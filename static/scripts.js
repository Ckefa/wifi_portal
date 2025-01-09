const modal = document.getElementById("customModal");
const mainContent = document.getElementById("main-content");


var package = null;
var price = null;


function setPackage(packageValue, pprice) {
    package = packageValue;
    price = pprice;

     // Function to open the modal with all messages
    function openModal() {

        // Set the modal's content to include all messages
        const messages = [
            "NOTE:",
            "After paying click REFRESH STATUS.",
            "DO NOT CLOSE THIS PAGE UNTIL YOU ARE AUTOMATICALLY CONNECTED."
        ];
        document.getElementById("modal-message").innerHTML = messages
            .map((msg) => `<li>${msg}</li>`)
            .join("");

        modal.classList.add("show");
        mainContent.classList.add("blur");
    }

    openModal();
}

// Function to close the modal
function closeModal() {
        console.log("Closing Modal");

        modal.classList.remove("show");
    if (mainContent)
{
        mainContent.classList.remove("blur");
    }

    window.location.href = "/pay?package="+package+"&price="+price;
}
