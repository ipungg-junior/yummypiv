const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;        
// Variable to track if user has scrolled at least 30% of the page
let hasScrolledEnough = false;
// Set countdown in seconds (for example, 7 seconds)
let countdown = 4;
let countdownTimer;
var fetchManager = new FetchManager(csrfToken);

// Function to handle countdown
function startCountdown() {
    countdownTimer = setInterval(() => {
        countdown--;

        if (countdown <= 0) {
            if (hasScrolledEnough) {
                clearInterval(countdownTimer);
                reportUserActivity();
            } else {
                countdown = 4;
            }
        }
    }, 2000);
}

// Function to handle scroll detection
function handleScroll() {
    const totalPageHeight = document.documentElement.scrollHeight;
    const viewportHeight = window.innerHeight;
    const scrolledDistance = window.scrollY;

    // Calculate how much the user has scrolled in percentage
    const scrollPercentage = (scrolledDistance + viewportHeight) / totalPageHeight * 100;

    if (scrollPercentage >= 45 && !hasScrolledEnough) {
        hasScrolledEnough = true;
    }
}

// Function to report that user actively visited the page
function reportUserActivity() {

    // Retrieve the "visit_id" cookie
    const visitId = CookieManager.getCookie("visit_id");
    const formData = new FormData();
    formData.append('path', '/');
    
    if (visitId === null){
        // Request and record new visit_id
        fetchManager.post('/api/visitor/request/', formData)
        .then(response => {
            const message = response.data.msg;
            if (response.status === true) {
                CookieManager.setCookie("visit_id", response.data.visit_id, 6);
            }
        });
    }

    else{
        // Request and record new visit_id
        formData.append('visit_id', visitId);
        fetchManager.post('/api/reporter/', formData)
        .then(response => {
            const message = response.data.msg;
            if (response.status === true) {
                console.log('True');
            }
            else {
                console.log('False');
            }
        });
    }
}



// Detect scroll event
window.addEventListener('scroll', handleScroll);
startCountdown();