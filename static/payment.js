const apiURL = "https://ckefa.com:8000/check"; const
    statusMessage = document.getElementById("statusMessage"); const spinner = document.getElementById("loadingSpinner");
const phoneInputContainer = document.getElementById("phoneInputContainer"); const
    btLogin = document.getElementById("btLogin"); const pay = document.getElementById("payNowButton"); const
        id = document.getElementById("msg"); const tok = "{{ tok }}"; let stopCheck = false; const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function payNow() {
    const phone = document.getElementById("phone").value;
    if (phone.length < 10) {
        alert("Enter a valid phone number");
    } else {
        window.location.href = `/packages?phone=${phone}`;
    }
}

async function forceCheck(ms = 0, lg = false, incognito = false) {
    let endPoint = `?tok=${tok}`; // Default to token-based endpoint
    const phone = lg ? document.getElementById("phone").value : null;

    // Validate phone number if 'lg' is true
    if (lg) {
        if (!phone || phone.length < 10) {
            alert("Enter a valid phone number");
            return;
        }
        endPoint = `?phone=${phone}`;
    } else {
        try {
            const response = await fetch("https://ckefa.com:8000/getphone");
            const data = await response.json();
            console.log("phone data", data);
            if (data.phone) {
                endPoint = `?phone=${data.phone}`;
            }
        } catch (error) {
            console.error("Error fetching phone data:", error);
        }
    }

    spinner.style.display = "flex";
    phoneInputContainer.style.display = "none";

    try {
        const response = await fetch(`${apiURL}${endPoint}`);
        const data = await response.json();
        console.log("API Response:", data);

        await delay(ms); // Wait for specified delay
        if (!incognito) spinner.style.display = "none";

        if (data.payment) {
            // Redirect if payment is valid
            window.location.href = `http://192.168.1.1:2050/nodogsplash_auth/?tok=${tok}`;
        } else {
            console.log("icognito value", incognito);
            if (incognito) return;
            // Show phone input if payment is invalid
            phoneInputContainer.style.display = "flex";
            if (lg) {
                pay.style.display = "block";
                id.style.display = "block";
            }
        }
    } catch (error) {
        console.error("Error:", error);
        await delay(4000); // Allow time for recovery
        spinner.style.display = "none";
        phoneInputContainer.style.display = "flex";
    }
}

{% if pay == "check" %}
document.addEventListener("DOMContentLoaded", () => {
    statusMessage.innerHTML = "Validating Payment...";
    autoCheckPaymentStatus();
});
{% else %}
document.addEventListener("DOMContentLoaded", () => {
    statusMessage.innerHTML = "Checking Payment...";
    forceCheck(4000);
});
{% endif %}

function autoCheckPaymentStatus() {
    const interval = setInterval(checkPayment, 5000); // Check every 5 seconds

    // Stop the interval after 1 minute and force check
    setTimeout(() => {
        stopCheck = true;
        clearInterval(interval); // Stop further interval checks
        forceCheck(2000); // Perform a final force check
    }, 60000);

    function checkPayment() {
        if (stopCheck) return; // Exit if stopCheck is true

        fetch(`${apiURL}?tok=${tok}`)
            .then((response) => response.json())
            .then((data) => {
                console.log("API Response:", data);

                if (data.payment) {
                    clearInterval(interval); // Stop interval if payment is successful
                    window.location.href = `http://192.168.1.1:2050/nodogsplash_auth/?tok=${tok}`;
                } else {
                    forceCheck(0, false, true);
                    statusMessage.textContent = "Checking payment status...";
                    setTimeout(() => {
                        statusMessage.textContent = "Please wait...";
                    }, 2000);
                }
            })
            .catch((error) => {
                console.error("Error checking payment status:", error);
            });
    }
}

